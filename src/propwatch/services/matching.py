# Start with a simple matching ladder: exact normalized name match, then cleaned-name match, then fuzzy match with a threshold. Return a match object with confidence instead of forcing a yes/no answer in ambiguous cases. This matters because the building is the source of truth for location and valuation context, and the system should fail safely when evidence is weak.

from dataclasses import dataclass
from typing import Optional
from rapidfuzz import fuzz

@dataclass
class MatchResult:
    building_id: Optional[int]
    confidence: float
    match_type: str

def match_building_to_property(building, property, fuzzy_threshold=80) -> MatchResult:
    # Normalize names for exact match
    def normalize(name):
        return ''.join(e for e in name.lower() if e.isalnum())
    
    building_name_normalized = normalize(building.name)
    property_name_normalized = normalize(property.name)

    if building_name_normalized == property_name_normalized:
        return MatchResult(building_id=building.id, confidence=1.0, match_type='exact_normalized')

    # Clean names for a more lenient match (remove common words, punctuation, etc.)
    def clean(name):
        common_words = {'the', 'and', 'of', 'in', 'at'}
        return ' '.join(word for word in name.lower().split() if word not in common_words)

    building_name_cleaned = clean(building.name)
    property_name_cleaned = clean(property.name)

    if building_name_cleaned == property_name_cleaned:
        return MatchResult(building_id=building.id, confidence=0.9, match_type='cleaned')

    # Fuzzy match with a threshold
    fuzzy_score = fuzz.ratio(building.name, property.name)
    if fuzzy_score >= fuzzy_threshold:
        confidence = fuzzy_score / 100.0  # Convert to a 0-1 scale
        return MatchResult(building_id=building.id, confidence=confidence, match_type='fuzzy')

    # No match found
    return MatchResult(building_id=None, confidence=0.0, match_type='none')

# testing terminal output

# if __name__ == "__main__":
#     class Building:
#         def __init__(self, id, name):
#             self.id = id
#             self.name = name

#     class Property:
#         def __init__(self, name):
#             self.name = name

#     building = Building(id=1, name="The Grand Hotel")
#     property = Property(name="Grand Hotel")

#     result = match_building_to_property(building, property)
#     print(result)