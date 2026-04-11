# Canonical area unit: SQFT.
AREA_UNIT = "SQFT"

# Integrity-first verdict behavior.
INTEGRITY_FIRST_VERDICT = "integrity_first"

# Default confidence thresholds.
DEFAULT_CONFIDENCE_THRESHOLDS = {
    "integrity_first": 0.9,
    "default": 0.7,
}

# Source labels for Dubai and Sharjah.
SOURCE_LABELS = {
    "dubai": "Dubai Municipality",
    "sharjah": "Sharjah Municipality",
}

# Shared numeric caps, such as the integrity ceiling.
INTEGRITY_CEILING = 0.95