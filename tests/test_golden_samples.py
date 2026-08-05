import os
import pytest
from src.utils.lookups import ReferenceLookups
from src.parsers.json_parser import JSONParser
from src.parsers.cap_parser import CAPParser
from src.parsers.text_parser import PlaintextParser
from src.models import SourceFormat, Severity, HazardType

@pytest.fixture
def lookups():
    # Primary path check with fallback to root data directory
    loc_path = "data/raw/location_reference.csv" if os.path.exists("data/raw/location_reference.csv") else "data/location_reference.csv"
    sev_path = "data/raw/severity_mapping_reference.csv" if os.path.exists("data/raw/severity_mapping_reference.csv") else "data/severity_mapping_reference.csv"
    return ReferenceLookups(loc_path, sev_path)

def test_json_001_extraction(lookups):
    parser = JSONParser(lookups)
    sample = '[{"id": "JSON-001", "event": "Urban Flood", "area": "Nirmala", "severity": "Moderate", "valid_from": "2025-07-17 03:00", "valid_to": "2025-07-18 15:00", "advice": "Avoid low-lying roads."}]'
    alerts = parser.parse(sample)
    assert len(alerts) == 1
    assert alerts[0].alert_id == "JSON-001"
    assert alerts[0].hazard_type == HazardType.FLOOD
    assert alerts[0].severity == Severity.MODERATE
    assert alerts[0].location_name == "Nirmala"
    assert alerts[0].location_id == "DIST-01"

def test_plaintext_malformed_warning(lookups):
    parser = PlaintextParser(lookups)
    malformed_input = "Malformed alert: heavy rain maybe somewhere soon"
    results = parser.parse(malformed_input)
    assert len(results) == 1
    assert results[0].source_format == SourceFormat.PLAINTEXT
    assert len(results[0].parse_warnings) > 0
    assert "Malformed alert format" in results[0].parse_warnings[0]