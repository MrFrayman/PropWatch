# Plan:
# Map each transaction into core transaction model, preserving raw source fields, storing normalized SqFt.
# Include transaction date, price, building reference, source metadata.
# Supports building-level pricing analysis.

import logging
from datetime import datetime, date
from typing import Dict, Any

from propwatch.models.transaction import Transaction
from propwatch.core.constants import AREA_UNIT

logger = logging.getLogger(__name__)

class TransactionNormalizationError(Exception):
    """Raised when transaction normalization fails validation gates."""
    pass

def normalize_transaction(raw_transaction: Dict[str, Any]) -> Transaction:
    """
    Normalize raw transaction into core Transaction model.
    Preserves raw source values alongside normalized canonical SqFt.
    
    Args:
        raw_transaction: Raw transaction dict from source (must have building_id, price, 
                        normalized_sqft_value or raw_area_value+raw_unit, transaction_date).
    
    Returns:
        Transaction: Validated, normalized transaction model.
    
    Raises:
        TransactionNormalizationError: If required fields missing, invalid, or fail validation gates.
    """
    
    # Extract and validate building_id (required, gates downstream analysis)
    building_id = raw_transaction.get('building_id')
    if building_id is None:
        raise TransactionNormalizationError("building_id required, missing or null.")
    
    # Extract and validate price (required, must be positive)
    try:
        price = float(raw_transaction.get('price'))
    except (TypeError, ValueError) as e:
        raise TransactionNormalizationError(f"price invalid or missing: {e}")
    
    if price <= 0:
        raise TransactionNormalizationError(f"price must be positive, got {price}")
    
    # Extract and validate area fields
    raw_area_value = raw_transaction.get('raw_area_value')
    raw_unit = raw_transaction.get('raw_unit', 'SQFT')  # Default to SQFT per spec
    normalized_sqft_value = raw_transaction.get('normalized_sqft_value')
    
    # If normalized SqFt missing, compute from raw area + unit
    if normalized_sqft_value is None and raw_area_value is not None:
        try:
            normalized_sqft_value = _to_sqft(raw_area_value, raw_unit)
        except ValueError as e:
            raise TransactionNormalizationError(f"area conversion failed: {e}")
    
    if normalized_sqft_value is None:
        raise TransactionNormalizationError("normalized_sqft_value required: either provide it or provide raw_area_value+raw_unit.")
    
    try:
        normalized_sqft_value = float(normalized_sqft_value)
    except (TypeError, ValueError) as e:
        raise TransactionNormalizationError(f"normalized_sqft_value invalid: {e}")
    
    if normalized_sqft_value <= 0:
        raise TransactionNormalizationError(f"normalized_sqft_value must be positive, got {normalized_sqft_value}")
    
    # Extract and validate transaction_date
    try:
        tx_date_raw = raw_transaction.get('transaction_date')
        if isinstance(tx_date_raw, date):
            transaction_date = tx_date_raw
        elif isinstance(tx_date_raw, datetime):
            transaction_date = tx_date_raw.date()
        else:
            transaction_date = datetime.strptime(str(tx_date_raw), '%Y-%m-%d').date()
    except (TypeError, ValueError) as e:
        raise TransactionNormalizationError(f"transaction_date invalid or missing: {e}")
    
    # Preserve raw area if not already set
    if raw_area_value is None:
        raw_area_value = normalized_sqft_value  # Fallback: raw = normalized if raw unavailable
    
    # Build transaction model
    transaction = Transaction(
        building_id=building_id,
        raw_area_value=raw_area_value,
        raw_unit=raw_unit,
        normalized_sqft_value=normalized_sqft_value,
        price=price,
        transaction_date=transaction_date
    )
    
    logger.debug(f"Normalized transaction: building={building_id}, price={price}, "
                 f"sqft={normalized_sqft_value}, price_per_sqft={transaction.price_per_sqft:.2f}")
    
    return transaction


def _to_sqft(value: float, unit: str) -> float:
    """Convert area to SqFt. Spec: SqFt canonical unit."""
    unit_upper = str(unit).upper().strip()
    
    if unit_upper in ('SQFT', 'SQ FT', 'SF'):
        return value
    elif unit_upper in ('SQM', 'SQ M', 'M2', 'M²'):
        return value * 10.764  # 1 sqm ≈ 10.764 sqft
    else:
        raise ValueError(f"Unsupported area unit: {unit}")

    
