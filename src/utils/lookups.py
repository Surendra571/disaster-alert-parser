import csv
from typing import Dict, Optional, Tuple
from src.models import Severity, HazardType, Urgency, Certainty

class ReferenceLookups:
    def __init__(self, loc_csv: str, sev_csv: str):
        self.locations: Dict[str, str] = {}
        self.severities: Dict[str, Severity] = {}
        
        # Load Location Map
        try:
            with open(loc_csv, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.locations[row["location_name"].strip().lower()] = row["location_id"].strip()
        except Exception:
            pass

        # Load Severity Map
        try:
            with open(sev_csv, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    term = row["raw_severity_term"].strip().lower()
                    canonical = row["canonical_severity"].strip()
                    self.severities[term] = Severity(canonical)
        except Exception:
            pass

    def resolve_location_id(self, location_name: str) -> Optional[str]:
        if not location_name:
            return None
        return self.locations.get(location_name.strip().lower())

    def resolve_severity(self, raw_sev: str) -> Tuple[Severity, Optional[str]]:
        if not raw_sev:
            return Severity.UNKNOWN, "Missing severity field"
        
        cleaned = raw_sev.strip().lower()
        if cleaned in self.severities:
            return self.severities[cleaned], None
        
        # Fallback substring matching
        for term, canonical in self.severities.items():
            if term in cleaned:
                return canonical, None

        return Severity.UNKNOWN, f"Unrecognized severity term '{raw_sev}' mapped to Unknown"

def normalize_hazard(raw_hazard: str) -> Tuple[HazardType, Optional[str]]:
    if not raw_hazard:
        return HazardType.OTHER, "Missing hazard type"
    
    val = raw_hazard.strip().lower()
    if "flood" in val or "rain" in val:
        return HazardType.FLOOD, None
    elif "heat" in val or "heatwave" in val:
        return HazardType.HEATWAVE, None
    elif "cyclone" in val or "wind" in val:
        return HazardType.CYCLONE, None
    elif "landslide" in val:
        return HazardType.LANDSLIDE, None
    elif "lightning" in val:
        return HazardType.LIGHTNING, None
    elif "earthquake" in val:
        return HazardType.EARTHQUAKE, None
    
    return HazardType.OTHER, None

def resolve_severity(self, raw_sev: str) -> Tuple[Severity, Optional[str]]:
        if not raw_sev or not raw_sev.strip():
            return Severity.UNKNOWN, "Missing severity field"
        
        cleaned = raw_sev.strip().lower()

        # Check loaded CSV mappings first
        if cleaned in self.severities:
            return self.severities[cleaned], None
        
        for term, canonical in self.severities.items():
            if term in cleaned:
                return canonical, None

        # Fallback to standard Enum matching if CSV is not loaded
        try:
            return Severity(raw_sev.strip().capitalize()), None
        except ValueError:
            pass

        return Severity.UNKNOWN, f"Unrecognized severity term '{raw_sev}' mapped to Unknown"