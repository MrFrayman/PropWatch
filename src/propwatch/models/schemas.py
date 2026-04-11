from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import date

class Building(BaseModel):
    name: str
    location: str
    emirate: str
    coordinates: Optional[Dict[str, float]] = None  # e.g., {"lat": 25.276987, "lon": 55.296249}
    metadata: Optional[Dict[str, str]] = None  # Additional info like year built, architect, etc.

class Unit(BaseModel):
    building_reference: str
    floor: int
    unit_type: str
    area: float
    fingerprint: str

class Transaction(BaseModel):
    unit_fingerprint: str
    transaction_date: date
    price: float
    source: str
    normalized_area: Optional[float] = None  # Normalized SqFt for comparison

class Verdict(BaseModel):
    transaction_fingerprint: str
    valuation: float
    confidence_score: Optional[float] = None  # Confidence in the valuation, e.g., 0.85 for 85% confidence
    rationale: Optional[str] = None  # Explanation for the verdict, if needed

