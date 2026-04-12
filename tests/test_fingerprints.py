# Test for src\propwatch\services\fingerprint.py
# Feed in multiple similar units and confirm they produce compatible fingerprints, while clearly different units do not collide too often.

import pytest

from propwatch.services.fingerprint import generate_fingerprint

def test_generate_fingerprint():
    # Test similar units
    fp1 = generate_fingerprint("Sunset Towers", "Medium", "Apartment", "1-5")
    fp2 = generate_fingerprint("Sunset Towers", "Medium", "Apartment", "1-5")
    assert fp1 == fp2, "Similar units should produce the same fingerprint"

    # Test different buildings
    fp3 = generate_fingerprint("Sunrise Apartments", "Medium", "Apartment", "1-5")
    assert fp1 != fp3, "Different buildings should produce different fingerprints"

    # Test different size bands
    fp4 = generate_fingerprint("Sunset Towers", "Large", "Apartment", "1-5")
    assert fp1 != fp4, "Different size bands should produce different fingerprints"

    # Test different unit types
    fp5 = generate_fingerprint("Sunset Towers", "Medium", "Condo", "1-5")
    assert fp1 != fp5, "Different unit types should produce different fingerprints"

    # Test different floor ranges
    fp6 = generate_fingerprint("Sunset Towers", "Medium", "Apartment", "6-10")
    assert fp1 != fp6, "Different floor ranges should produce different fingerprints"