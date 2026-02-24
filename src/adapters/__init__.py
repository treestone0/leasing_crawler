"""Site-specific adapters for leasing offers."""

from src.adapters.base import BaseAdapter, Offer
from src.adapters.leasingmarkt import LeasingmarktAdapter

__all__ = ["BaseAdapter", "Offer", "LeasingmarktAdapter"]
