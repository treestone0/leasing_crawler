"""Default settings and configuration."""

import os
from dataclasses import dataclass


@dataclass
class CrawlerConfig:
    """Crawler politeness and behavior settings."""

    request_delay_seconds: float = 1.5
    user_agent: str = "LeasingCrawler/1.0 (+https://github.com/leasing-crawler)"
    max_retries: int = 3
    respect_robots_txt: bool = True


@dataclass
class AppConfig:
    """Application configuration."""

    crawler: CrawlerConfig
    output_dir: str = "output"
    input_dir: str = "input"

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Build config from environment variables."""
        delay = float(os.environ.get("CRAWLER_DELAY", "1.5"))
        return cls(
            crawler=CrawlerConfig(request_delay_seconds=delay),
            output_dir=os.environ.get("OUTPUT_DIR", "output"),
            input_dir=os.environ.get("INPUT_DIR", "input"),
        )
