# Write a function that generates a coarse fingerprint from stable attributes like building, size band, unit type, and floor range. Don’t make it too precise, because the fingerprint is supposed to help with clustering and historical matching, not create fake certainty. That aligns with the plan’s emphasis on a conservative bridge between marketing data and the historical ledger.

def generate_fingerprint(building, size_band, unit_type, floor_range):
    def normalize(text):
        return ''.join(ch for ch in text.upper() if ch.isalnum())

    building_segment = normalize(building)[:5]
    unit_segment = normalize(unit_type)[:3]
    fingerprint = f"{building_segment}-{size_band}-{unit_segment}-{floor_range}"
    return fingerprint

# # Example usage:
# building = "Sunset Towers"
# size_band = "Medium"
# unit_type = "Apartment"
# floor_range = "1-5"
# fingerprint = generate_fingerprint(building, size_band, unit_type, floor_range)
# print(fingerprint)  # Output: SUN-MED-APA-1-5
