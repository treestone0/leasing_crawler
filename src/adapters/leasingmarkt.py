"""Leasingmarkt.de adapter for /deals and /listing."""

from __future__ import annotations

import re
from bs4 import BeautifulSoup

from src.adapters.base import BaseAdapter, Offer
from src.core.crawler import PoliteHttpClient
from src.core.filters import Filter


BASE = "https://www.leasingmarkt.de"


def _parse_price(text: str) -> float:
    """Extract numeric price from text like '133,95 €'."""
    m = re.search(r"([\d.,]+)\s*€", text)
    if not m:
        return 0.0
    s = m.group(1).replace(".", "").replace(",", ".")
    return float(s)


def _parse_km_year(text: str) -> int:
    """Extract km/year from text like '10.000 km/Jahr'."""
    m = re.search(r"([\d.]+)\s*km", text)
    if not m:
        return 0
    return int(m.group(1).replace(".", ""))


def _parse_months(text: str) -> int:
    """Extract months from text like '36 Monate'."""
    m = re.search(r"(\d+)\s*Monat", text)
    return int(m.group(1)) if m else 0


def _parse_einmalige_kosten(card) -> float:
    """Extract one-time cost from additional-info tags."""
    add_info = card.find(id=lambda x: x and "additional-info-content" in str(x))
    if not add_info:
        return 0.0
    text = add_info.get_text()
    if "Ohne Anzahlung" in text or "ohne Anzahlung" in text:
        return 0.0
    m = re.search(r"(\d+[.,]?\d*)\s*€\s*Anzahlung", text)
    if m:
        s = m.group(1).replace(".", "").replace(",", ".")
        return float(s)
    return 0.0


def _slug_to_brand_model(slug: str) -> tuple[str, str]:
    """Convert 'volkswagen-tiguan' to ('Volkswagen', 'Tiguan')."""
    parts = slug.replace("_", " ").split("-")
    if not parts:
        return ("", "")
    brand = parts[0].title() if parts[0] else ""
    model = "-".join(parts[1:]).title() if len(parts) > 1 else ""
    return (brand, model)


class LeasingmarktAdapter(BaseAdapter):
    """Adapter for leasingmarkt.de /deals and /listing pages."""

    def __init__(self, http_client: PoliteHttpClient | None = None) -> None:
        self._client = http_client or PoliteHttpClient()

    def supports_source(self, source: str) -> bool:
        return source in ("deals", "listing")

    def fetch_offers(self, filter_config: Filter) -> list[Offer]:
        if filter_config.source == "deals":
            return self._fetch_deals(filter_config)
        return self._fetch_listing(filter_config)

    def _parse_cards(self, html: str) -> list[Offer]:
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.find_all(
            "div",
            class_=lambda x: x
            and "cursor-pointer" in str(x)
            and "rounded-lg" in str(x)
            and "border-grey-200" in str(x),
        )
        offers: list[Offer] = []
        seen_links: set[str] = set()

        for card in cards:
            link_el = card.find("a", href=lambda h: h and "/leasing/pkw/" in h)
            if not link_el:
                continue
            href = link_el.get("href", "")
            if href.startswith("/"):
                link = f"{BASE}{href}"
            else:
                link = href
            if link in seen_links:
                continue
            seen_links.add(link)

            match = re.search(r"/leasing/pkw/([^/]+)/", link)
            slug = match.group(1) if match else ""
            brand, model = _slug_to_brand_model(slug)
            variant = link_el.get_text(separator=" ", strip=True).split("|")[0].strip()
            if " " in variant and (brand or model):
                variant = variant.replace(brand, "").replace(model, "").strip()

            price_div = card.find(id=lambda x: x and "price-info-content" in str(x))
            price = 0.0
            if price_div:
                aria = price_div.find(attrs={"aria-label": True})
                if aria and "Leasingrate" in aria.get("aria-label", ""):
                    price = _parse_price(aria["aria-label"])
                if price == 0:
                    price = _parse_price(price_div.get_text())

            details = card.find(id=lambda x: x and "listing-mileage-content" in str(x))
            km = _parse_km_year(details.get_text()) if details else 0

            duration = card.find(id=lambda x: x and "listing-duration-content" in str(x))
            months = _parse_months(duration.get_text()) if duration else 0

            einmalige = _parse_einmalige_kosten(card)

            offers.append(
                Offer(
                    brand=brand,
                    model=model,
                    variant=variant or "",
                    km_per_year=km,
                    laufzeit_months=months,
                    price_per_month=price,
                    einmalige_kosten=einmalige,
                    link=link,
                )
            )
        return offers

    def _fetch_deals(self, filter_config: Filter) -> list[Offer]:
        resp = self._client.get("/deals/")
        return self._parse_cards(resp.text)

    def _fetch_listing(self, filter_config: Filter) -> list[Offer]:
        all_offers: list[Offer] = []
        page = 1
        max_pages = 5
        while page <= max_pages:
            resp = self._client.get("/listing/", params={"p": page, "tg": "ALL"})
            offers = self._parse_cards(resp.text)
            if not offers:
                break
            all_offers.extend(offers)
            if len(offers) < 15:
                break
            page += 1
        return all_offers
