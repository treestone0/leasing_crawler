"""Filter model for car search criteria."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class Filter(BaseModel):
    """Search filter for leasing offers."""

    id: str = Field(..., description="Filter ID, used as Excel sheet name")
    source: str = Field(..., description="'deals' or 'listing'")
    brand: str = Field(default="", description="Brand name, empty = all")
    model: str = Field(default="", description="Model name, empty = all")
    brand_blank_ok: bool = Field(default=True, description="Allow blank brand = all")
    model_blank_ok: bool = Field(default=True, description="Allow blank model = all")
    km_per_year_min: Optional[int] = Field(default=None, description="Min km/year")
    km_per_year_max: Optional[int] = Field(default=None, description="Max km/year")
    price_per_month_max: Optional[float] = Field(default=None, description="Max monthly rate in EUR")
    einmalige_kosten_max: Optional[float] = Field(
        default=None, description="Max one-time upfront cost in EUR"
    )
    blacklist_brands: List[str] = Field(default_factory=list)
    blacklist_models: List[str] = Field(default_factory=list)

    @field_validator("source")
    @classmethod
    def source_must_be_deals_or_listing(cls, v: str) -> str:
        if v not in ("deals", "listing"):
            raise ValueError("source must be 'deals' or 'listing'")
        return v


def load_filters_from_file(path: Union[str, Path]) -> List[Filter]:
    """Load a list of filters from a JSON file.

    Expects a JSON array of filter objects matching the Filter schema.
    """
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [Filter.model_validate(item) for item in data]
