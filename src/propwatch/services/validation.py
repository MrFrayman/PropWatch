# Goal: Coarse schema validation before normalization. Fail fast on missing/malformed required fields.
# Deep conversion + value constraints live in normalizer. This stays lightweight.

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ValidationError(ValueError):
    """Schema validation error. Field missing or type incompatible."""
    pass


def validate_transaction_schema(raw_transaction: Dict[str, Any]) -> None:
    """
    Coarse schema validation. Check required fields exist + rough type compatibility.
    Deep validation (conversion, range checks, unit parsing) is normalizer's job.
    
    Args:
        raw_transaction: Raw transaction dict from source.
    
    Raises:
        ValidationError: If required field missing or type clearly wrong.
    """
    
    if not isinstance(raw_transaction, dict):
        raise ValidationError(f"Expected dict, got {type(raw_transaction).__name__}")
    
    # building_id required
    if 'building_id' not in raw_transaction:
        logger.warning("building_id missing from raw transaction")
        raise ValidationError("building_id required")
    
    # price required, must be number-like
    if 'price' not in raw_transaction:
        logger.warning("price missing from raw transaction")
        raise ValidationError("price required")
    
    price = raw_transaction['price']
    if not isinstance(price, (int, float, str)):
        raise ValidationError(f"price must be number or string, got {type(price).__name__}")
    
    # area required: either normalized_sqft_value OR (raw_area_value + raw_unit)
    has_normalized = 'normalized_sqft_value' in raw_transaction
    has_raw = 'raw_area_value' in raw_transaction
    
    if not (has_normalized or has_raw):
        logger.warning("Neither normalized_sqft_value nor raw_area_value provided")
        raise ValidationError("Area required: provide normalized_sqft_value or raw_area_value+raw_unit")
    
    if has_raw:
        raw_area = raw_transaction['raw_area_value']
        if not isinstance(raw_area, (int, float, str)):
            raise ValidationError(f"raw_area_value must be number or string, got {type(raw_area).__name__}")
    
    if has_normalized:
        norm_area = raw_transaction['normalized_sqft_value']
        if not isinstance(norm_area, (int, float, str)):
            raise ValidationError(f"normalized_sqft_value must be number or string, got {type(norm_area).__name__}")
    
    # transaction_date required
    if 'transaction_date' not in raw_transaction:
        logger.warning("transaction_date missing from raw transaction")
        raise ValidationError("transaction_date required")
    
    tx_date = raw_transaction['transaction_date']
    if not isinstance(tx_date, (str, dict)):  # Allow str (ISO format), date obj, or already parsed
        # Relax type check - normalizer will handle conversion
        pass
    
    logger.debug(f"Schema validation passed for building_id={raw_transaction.get('building_id')}")
    
