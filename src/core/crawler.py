"""HTTP client with politeness for crawling."""

from __future__ import annotations

import time
import urllib.robotparser
from typing import Optional

import httpx

from src.config import CrawlerConfig


class PoliteHttpClient:
    """HTTP client that respects robots.txt, rate limits, and retries."""

    def __init__(self, config: Optional[CrawlerConfig] = None) -> None:
        self.config = config or CrawlerConfig()
        self._rp: Optional[urllib.robotparser.RobotFileParser] = None
        self._base_url = "https://www.leasingmarkt.de"

    def _ensure_robots_parsed(self) -> None:
        if not self.config.respect_robots_txt or self._rp is not None:
            return
        self._rp = urllib.robotparser.RobotFileParser()
        self._rp.set_url(f"{self._base_url}/robots.txt")
        try:
            self._rp.read()
        except Exception:
            self._rp = None

    def can_fetch(self, path: str) -> bool:
        """Return True if path is allowed by robots.txt."""
        if not self.config.respect_robots_txt:
            return True
        self._ensure_robots_parsed()
        if self._rp is None:
            return True
        return self._rp.can_fetch(self.config.user_agent, f"{self._base_url}{path}")

    def get(self, path: str, params: Optional[dict] = None) -> httpx.Response:
        """GET with politeness: robots.txt check, delay, retries."""
        if not self.can_fetch(path):
            raise PermissionError(f"robots.txt disallows: {path}")

        url = f"{self._base_url}{path}"
        headers = {"User-Agent": self.config.user_agent}

        last_error: Optional[Exception] = None
        for attempt in range(self.config.max_retries):
            try:
                if attempt > 0:
                    time.sleep(2**attempt)  # Exponential backoff
                with httpx.Client(timeout=30.0, follow_redirects=True) as client:
                    resp = client.get(url, params=params, headers=headers)
                    resp.raise_for_status()
                    time.sleep(self.config.request_delay_seconds)
                    return resp
            except (httpx.HTTPError, httpx.RequestError) as e:
                last_error = e

        raise last_error or RuntimeError("Request failed")
