from pydantic import BaseModel, Field
from typing import Optional

class Listing(BaseModel):
    portal_source: str = Field(..., description="The source portal of the listing")
    asking_price: float = Field(..., description="The asking price of the listing")
    area_raw: str = Field(..., description="The raw area value as extracted from the listing")
    area_normalized: Optional[float] = Field(None, description="The normalized area value in square meters")
    building_match: Optional[str] = Field(None, description="The matched building identifier if available")
    integrity_fields: Optional[dict] = Field(None, description="Additional fields for integrity checks and auditability")

