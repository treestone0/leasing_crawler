"""Tests for LeasingmarktAdapter."""

from unittest.mock import MagicMock

import pytest

from src.adapters.leasingmarkt import LeasingmarktAdapter
from src.core.filters import Filter


@pytest.fixture
def sample_card_html():
    """Minimal HTML for one offer card matching site structure."""
    return """
    <div class="relative flex cursor-pointer flex-col gap-4 rounded-lg border border-grey-200 bg-white">
        <a href="https://www.leasingmarkt.de/leasing/pkw/volkswagen-golf/12345?adVariant=1">
            Volkswagen Golf 1.0 TSI | Privat | Bestellfahrzeug
        </a>
        <div id="12345-price-info-content">
            <span aria-label="Leasingrate: ab 189,99 € inkl. MwSt. monatlich">ab 189,99 €</span>
        </div>
        <span id="x-listing-mileage-content">15.000 km/Jahr</span>
        <span id="x-listing-duration-content">36 Monate</span>
        <div id="x-additional-info-content">
            <span>Rate inkl. 1.500 € Anzahlung</span>
        </div>
    </div>
    """


@pytest.fixture
def adapter_with_mock_client():
    """Adapter with mocked HTTP client."""
    mock = MagicMock()
    adapter = LeasingmarktAdapter(http_client=mock)
    return adapter, mock


def test_supports_deals_and_listing(adapter_with_mock_client):
    adapter, _ = adapter_with_mock_client
    assert adapter.supports_source("deals") is True
    assert adapter.supports_source("listing") is True
    assert adapter.supports_source("other") is False


def test_parse_cards_extracts_offer(adapter_with_mock_client, sample_card_html):
    adapter, mock_client = adapter_with_mock_client
    mock_client.get.return_value.text = f"<html><body><div class='flex flex-col gap-y-4'>{sample_card_html}</div></body></html>"

    filt = Filter(id="t1", source="deals")
    offers = adapter.fetch_offers(filt)

    assert len(offers) >= 1
    offer = next(o for o in offers if "golf" in o.link.lower())
    assert offer.brand == "Volkswagen"
    assert offer.model == "Golf"
    assert offer.price_per_month == 189.99
    assert offer.km_per_year == 15000
    assert offer.laufzeit_months == 36
    assert offer.einmalige_kosten == 1500.0
    assert "12345" in offer.link
