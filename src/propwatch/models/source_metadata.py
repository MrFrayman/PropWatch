# Define models for raw listings, raw transactions, (in raw_record.py) and... source metadata (in source_metadata.py). These should keep original text, original units, source URL or file path, parse timestamp, and confidence score. The reason is simple: this project must keep a full audit trail from raw source to final verdict, not just the cleaned output.
# Source metadata in source_metadata.py should include fields like source name, type, last updated timestamp, and any relevant notes about the source.

from pyparsing import Optional

from pydantic import BaseModel, Field
from datetime import datetime, timezone

# Model for source metadata
class SourceMetadata(BaseModel):
    source_name: str = Field(..., description="Name of the data source")
    source_type: str = Field(..., description="Type of the data source (e.g., website, API, file)")
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp when the source was last updated")
    notes: Optional[str] = Field(None, description="Any relevant notes about the source")

# Instantiate a sample source metadata record and confirm the values are correct.
if __name__ == "__main__":
    sample_source_metadata = SourceMetadata(
        source_name="Example Real Estate API",
        source_type="API",
        notes="This API provides real estate listings and transactions data."
    )
    
    print(sample_source_metadata)
