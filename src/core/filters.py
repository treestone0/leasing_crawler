"""Filter model for car search criteria."""

from pydantic import BaseModel, Field


class Filter(BaseModel):
    """Search filter for leasing offers."""

    id: str = Field(..., description="Filter ID, used as Excel sheet name")
    source: str = Field(..., description="'deals' or 'listing'")
    brand: str = Field(default="", description="Brand name, empty = all")
    model: str = Field(default="", description="Model name, empty = all")
    brand_blank_ok: bool = Field(default=True, description="Allow blank brand = all")
    model_blank_ok: bool = Field(default=True, description="Allow blank model = all")
    km_per_year_min: int | None = Field(default=None, description="Min km/year")
    km_per_year_max: int | None = Field(default=None, description="Max km/year")
    price_per_month_max: float | None = Field(default=None, description="Max monthly rate in EUR")
    einmalige_kosten_max: float | None = Field(
        default=None, description="Max one-time upfront cost in EUR"
    )
    blacklist_brands: list[str] = Field(default_factory=list)
    blacklist_models: list[str] = Field(default_factory=list)
