# Testing matching.py in src/propwatch/services/matching.py
# Test exact matches, near matches, and intentionally ambiguous names to make sure low-confidence cases remain unresolved.

import pytest

from dataclasses import dataclass
from rapidfuzz import fuzz
from propwatch.services.matching import match_building_to_property


@dataclass
class Building:
    id: int
    name: str


@dataclass
class Property:
    name: str


def test_exact_normalized_match():
    building = Building(id=1, name="Grand Hotel")
    property = Property(name="Grand Hotel")
    result = match_building_to_property(building, property)
    assert result.building_id == 1
    assert result.confidence == 1.0
    assert result.match_type == 'exact_normalized'


def test_cleaned_match():
    building = Building(id=2, name="The Grand Hotel")
    property = Property(name="Grand Hotel")
    result = match_building_to_property(building, property)
    assert result.building_id == 2
    assert result.confidence == 0.9
    assert result.match_type == 'cleaned'


def test_fuzzy_match():
    building = Building(id=3, name="Grand Hotel Tower A")
    property = Property(name="Grand Hotel Tower B")
    result = match_building_to_property(building, property)
    assert result.building_id == 3
    expected_confidence = fuzz.ratio(building.name, property.name) / 100.0
    assert result.confidence == pytest.approx(expected_confidence)
    assert result.match_type == 'fuzzy'


def test_no_match():
    building = Building(id=4, name="The Grand Hotel")
    property = Property(name="Small Motel")
    result = match_building_to_property(building, property)
    assert result.building_id is None
    assert result.confidence == 0.0
    assert result.match_type == 'none'


def test_ambiguous_match():
    building = Building(id=5, name="Grand Hotel Tower")
    property = Property(name="Grand Hotel Towers")
    result = match_building_to_property(building, property, fuzzy_threshold=99)
    assert result.building_id is None
    assert result.confidence == 0.0
    assert result.match_type == 'none'
