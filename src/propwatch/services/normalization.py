# Write helper functions that convert square meters to SqFt and keep both the raw value and raw unit alongside the normalized field. For example, a transaction or listing should store raw_area_value, raw_area_unit, and normalized_area_sqft. This is a core project rule, not a convenience, because the locked design requires raw-plus-normalized storage for future re-normalization and auditability.
# Built a src/propwatch/core/units.py file that contains the conversion logic for area units. This file has functions like convert_area_to_sqft(value, unit) that take a raw value and its unit and return the normalized value in square feet. The function should handle common area units such as square meters (sqm), square feet (sqft), and acres.

from propwatch.core.units import convert_area_to_sqft

def normalize_area(raw_area_value, raw_area_unit):
    """
    Normalize the area value to square feet (sqft) while keeping the raw value and unit.

    Parameters:
    raw_area_value (float): The raw area value.
    raw_area_unit (str): The raw area unit. Supported units are 'sqm', 'sqft', and 'acres'.

    Returns:
    dict: A dictionary containing the raw area value, raw area unit, and normalized area in square feet.
    """
    normalized_area_sqft = convert_area_to_sqft(raw_area_value, raw_area_unit)
    
    return {
        'raw_area_value': raw_area_value,
        'raw_area_unit': raw_area_unit,
        'normalized_area_sqft': normalized_area_sqft
    }

# Terminal outputs to verify the function works as expected
# if __name__ == "__main__":
#     # Test cases
#     test_cases = [
#         (100, 'sqm'),
#         (200, 'sqft'),
#         (1, 'acres'),
#         (50, 'unknown')  # This should raise an error
#     ]

#     for value, unit in test_cases:
#         try:
#             result = normalize_area(value, unit)
#             print(result)
#         except ValueError as e:
#             print(e)
