from propwatch.core import constants
import pytest

def test_imports():
    assert constants

def test_sqft_constant():
    assert constants.AREA_UNIT.lower() == 'sqft'