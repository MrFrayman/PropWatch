import pytest

from propwatch.services.normalization import normalize_area


def test_normalize_area_sqm():
    result = normalize_area(100.0, 'sqm')
    assert result['raw_area_value'] == 100.0
    assert result['raw_area_unit'] == 'sqm'
    assert result['normalized_area_sqft'] == pytest.approx(1076.39)


def test_normalize_area_acres():
    result = normalize_area(0.5, 'acres')
    assert result['raw_area_value'] == 0.5
    assert result['raw_area_unit'] == 'acres'
    assert result['normalized_area_sqft'] == pytest.approx(21780)


def test_normalize_area_unknown_unit():
    with pytest.raises(ValueError):
        normalize_area(1.0, 'hectare')
