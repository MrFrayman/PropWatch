# Run a few sample rows through the normalizer and confirm the output shape is identical every time.

import pytest

from propwatch.services.transaction_normalizer import normalize_transaction, TransactionNormalizationError
from propwatch.models.transaction import Transaction

def test_normalize_transaction_valid_input():
    raw_transaction = {
        'building_id': 1,
        'raw_area_value': 1000,
        'raw_unit': 'SQFT',
        'price': 500000,
        'transaction_date': '2024-01-01'
    }
    
    transaction = normalize_transaction(raw_transaction)
    
    assert isinstance(transaction, Transaction)
    assert transaction.building_id == 1
    assert transaction.raw_area_value == 1000
    assert transaction.raw_unit == 'SQFT'
    assert transaction.normalized_sqft_value == 1000
    assert transaction.price == 500000
    assert transaction.transaction_date.isoformat() == '2024-01-01'

def test_normalize_transaction_missing_building_id():
    raw_transaction = {
        'raw_area_value': 1000,
        'raw_unit': 'SQFT',
        'price': 500000,
        'transaction_date': '2024-01-01'
    }
    
    with pytest.raises(TransactionNormalizationError) as exc_info:
        normalize_transaction(raw_transaction)
    
    assert "building_id required" in str(exc_info.value)

def test_normalize_transaction_invalid_price():
    raw_transaction = {
        'building_id': 1,
        'raw_area_value': 1000,
        'raw_unit': 'SQFT',
        'price': -500000,  # Invalid negative price
        'transaction_date': '2024-01-01'
    }
    
    with pytest.raises(TransactionNormalizationError) as exc_info:
        normalize_transaction(raw_transaction)
    
    assert "price must be positive" in str(exc_info.value)

def test_normalize_transaction_missing_area():
    raw_transaction = {
        'building_id': 1,
        'price': 500000,
        'transaction_date': '2024-01-01'
    }
    
    with pytest.raises(TransactionNormalizationError) as exc_info:
        normalize_transaction(raw_transaction)
    
    assert "normalized_sqft_value required" in str(exc_info.value)

def test_normalize_transaction_invalid_date():
    raw_transaction = {
        'building_id': 1,
        'raw_area_value': 1000,
        'raw_unit': 'SQFT',
        'price': 500000,
        'transaction_date': 'invalid-date'  # Invalid date format
    }
    
    with pytest.raises(TransactionNormalizationError) as exc_info:
        normalize_transaction(raw_transaction)
    
    assert "transaction_date invalid" in str(exc_info.value)
