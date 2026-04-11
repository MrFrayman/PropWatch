from pydantic import BaseModel

class Unit(BaseModel):
    building_reference: str
    floor: int
    unit_type: str
    area: float
    fingerprint: str
