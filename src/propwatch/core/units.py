# Build a src/propwatch/core/units.py file that contains the conversion logic for area units. This file should have functions like convert_area_to_sqft(value, unit) that take a raw value and its unit and return the normalized value in square feet. The function should handle common area units such as square meters (sqm), square feet (sqft), and acres.

def convert_area_to_sqft(value, unit):
    """
    Convert area from the given unit to square feet (sqft).

    Parameters:
    value (float): The raw area value.
    unit (str): The raw area unit. Supported units are 'sqm', 'sqft', and 'acres'.

    Returns:
    float: The normalized area in square feet.
    """
    unit = unit.lower()
    
    if unit == 'sqm':
        return value * 10.7639  # 1 square meter = 10.7639 square feet
    elif unit == 'sqft':
        return value  # Already in square feet
    elif unit == 'acres':
        return value * 43560  # 1 acre = 43,560 square feet
    else:
        raise ValueError(f"Unsupported area unit: {unit}")
