# Define models for raw listings, raw transactions, and source metadata (in source_metadata.py). These should keep original text, original units, source URL or file path, parse timestamp, and confidence score. The reason is simple: this project must keep a full audit trail from raw source to final verdict, not just the cleaned output.

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Base model for raw records
class RawRecord(BaseModel):
    source_url: str = Field(..., description="URL or file path of the raw data source")
    original_text: str = Field(..., description="Original text as extracted from the source")
    original_units: Optional[str] = Field(None, description="Original units if applicable")
    parse_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the record was parsed")
    confidence_score: Optional[float] = Field(None, description="Confidence score of the parsing process")

# Model for raw listings
class RawListing(RawRecord):
    pass  # Additional fields specific to listings can be added here

# Model for raw transactions
class RawTransaction(RawRecord):
    pass  # Additional fields specific to transactions can be added here

# Instantiate one sample record from each source and confirm the raw values are untouched.
if __name__ == "__main__":
    sample_listing = RawListing(
        source_url="https://example.com/listing/123",
        original_text="3 bed, 2 bath, 1500 sqft",
        original_units="sqft",
        confidence_score=0.95
    )
    
    sample_transaction = RawTransaction(
        source_url="https://example.com/transaction/456",
        original_text="$500,000 for a 3 bed, 2 bath house",
        original_units="USD",
        confidence_score=0.90
    )
    
    print(sample_listing)
    print(sample_transaction)