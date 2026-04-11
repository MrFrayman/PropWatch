from datetime import date
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest
from propwatch.models import building, listing, transaction, unit


def test_package_imports():
    """Ensure the core model modules can be imported."""
    module_names = [
        "propwatch.models.building",
        "propwatch.models.unit",
        "propwatch.models.transaction",
        "propwatch.models.listing",
    ]
    for module_name in module_names:
        module = importlib.import_module(module_name)
        assert module is not None


def test_core_models_validate_sample_payload():
    """Drive each model with a representative payload."""
    building_payload = {
        "name": "Marina Tower",
        "location": "Dubai Marina",
        "emirate": "Dubai",
        "coordinates": {"lat": 25.1304, "lon": 55.1885},
        "metadata": {"developer": "Emaar"},
    }
    building_model = building.Building(**building_payload)
    assert building_model.name == building_payload["name"]

    unit_payload = {
        "building_reference": "marina-tower-2",
        "floor": 20,
        "unit_type": "2BR",
        "area": 1350.0,
        "fingerprint": "fingerprint-hash",
    }
    unit_model = unit.Unit(**unit_payload)
    assert unit_model.unit_type == "2BR"

    transaction_payload = {
        "building_id": 1,
        "raw_area_value": 1350.0,
        "raw_unit": "SqFt",
        "normalized_sqft_value": 1350.0,
        "price": 1750000.0,
        "transaction_date": date(2026, 4, 1),
    }
    transaction_model = transaction.Transaction(**transaction_payload)
    assert transaction_model.price == transaction_payload["price"]

    listing_payload = {
        "portal_source": "Bayut",
        "asking_price": 1800000.0,
        "area_raw": "1,350 SqFt",
        "area_normalized": 1350.0,
        "building_match": "marina-tower-2",
        "integrity_fields": {"madmoun_passed": True},
    }
    listing_model = listing.Listing(**listing_payload)
    assert listing_model.portal_source == "Bayut"


def test_listing_area_fields_coexist():
    """Verify raw and normalized area fields live together."""
    payload = {
        "portal_source": "Dubizzle",
        "asking_price": 1250000.0,
        "area_raw": "120 sq m",
        "area_normalized": 1291.67,
    }
    listing_model = listing.Listing(**payload)
    assert listing_model.area_raw.startswith("120")
    assert listing_model.area_normalized == pytest.approx(1291.67)
