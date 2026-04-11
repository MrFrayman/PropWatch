from pydantic import BaseModel
from datetime import date

class Transaction(BaseModel):
    building_id: int  # Reference to the Building model
    raw_area_value: float
    raw_unit: str
    normalized_sqft_value: float
    price: float
    transaction_date: date

