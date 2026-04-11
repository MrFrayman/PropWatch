from pydantic import BaseModel
from typing import Optional, Dict

class Building(BaseModel):
    name: str
    location: str
    emirate: str
    coordinates: Optional[Dict[str, float]] = None  # e.g., {"lat": 25.276987, "lon": 55.296249}
    metadata: Optional[Dict[str, str]] = None  # Additional info like year built, architect, etc.

