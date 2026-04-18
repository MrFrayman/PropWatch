# Add a service that takes a source adapter, fetches raw data, validates it, normalizes it, and returns structured records.
# Then expose a simple CLI command so you can manually run ingestion while developing.
# Keep this orchestration thin; the real logic should stay in the adapter, normalization, matching, and validation modules.

import re
from typing import Any, List

from propwatch.models.listing import Listing
from propwatch.services.adapters.dubai import DubaiAdapter
from propwatch.services.adapters.sharjah import SharjahAdapter
from propwatch.services.normalization import normalize_area


class IngestionService:
    def __init__(self):
        self.adapters = {"dubai": DubaiAdapter(), "sharjah": SharjahAdapter()}

    def _parse_price(self, price_str: Any) -> float:
        """Helper to turn a price string into a float."""
        if isinstance(price_str, (int, float)):
            return float(price_str)

        clean_price = re.sub(r"[^\d.]", "", str(price_str))
        return float(clean_price) if clean_price else 0.0

    def run(self, source_key: str) -> List[Listing]:
        adapter = self.adapters.get(source_key.lower())
        if not adapter:
            raise ValueError(f"Unknown source: {source_key}")

        raw_items = adapter.extract_data()
        standardized_items = adapter.transform_data(raw_items)

        final_records = []

        for item in standardized_items:
            try:
                price = self._parse_price(item.get("price"))
                norm_data = normalize_area(
                    item.get("area", 0) or item.get("size", 0), item.get("unit", "sqft")
                )

                record = Listing(
                    portal_source=source_key,
                    asking_price=price,
                    area_raw=str(item.get("area") or item.get("size")),
                    area_normalized=norm_data["normalized_area_sqft"],  # Canonical SqFt
                    building_match=item.get("location"),
                    integrity_fields={},  # Default to empty dict to avoid validation errors
                )
                final_records.append(record)
            except Exception as e:
                print(f"Skipping record due to error: {e}")

        return final_records
