"""Abstract base adapter for leasing sites."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.filters import Filter


@dataclass
class Offer:
    """Single leasing offer."""

    brand: str
    model: str
    variant: str
    km_per_year: int
    laufzeit_months: int
    price_per_month: float
    einmalige_kosten: float
    link: str
    notes: str = ""


class BaseAdapter(ABC):
    """Abstract base for site-specific adapters."""

    @abstractmethod
    def fetch_offers(self, filter_config: Filter) -> list[Offer]:
        """Fetch offers matching the filter. Must be implemented by subclasses."""
        ...

    @abstractmethod
    def supports_source(self, source: str) -> bool:
        """Return True if this adapter handles the given source (e.g. 'deals', 'listing')."""
        ...

