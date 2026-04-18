from pydantic import BaseModel, computed_field
from datetime import date

class Transaction(BaseModel):
    building_id: int  # Reference to the Building model
    raw_area_value: float
    raw_unit: str
    normalized_sqft_value: float
    price: float
    transaction_date: date
    
    @computed_field
    @property
    def price_per_sqft(self) -> float:
        """Derived price per SqFt. Spec: Should be derived, not manually entered."""
        return self.price / self.normalized_sqft_value


