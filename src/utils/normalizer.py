import re
from typing import Tuple, Optional
from datetime import datetime
from dateutil import parser as date_parser
from src.models import HazardType, Urgency, Certainty

def normalize_hazard(raw_hazard: str) -> Tuple[HazardType, Optional[str]]:
    if not raw_hazard or not raw_hazard.strip():
        return HazardType.OTHER, "Missing hazard type"
    
    val = raw_hazard.strip().lower()
    if any(k in val for k in ["flood", "rain", "urban flood"]):
        return HazardType.FLOOD, None
    elif "heat" in val or "heatwave" in val or "heat wave" in val:
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

def normalize_urgency(raw_urgency: str) -> Urgency:
    if not raw_urgency:
        return Urgency.UNKNOWN
    val = raw_urgency.strip().capitalize()
    try:
        return Urgency(val)
    except ValueError:
        return Urgency.UNKNOWN

def normalize_certainty(raw_certainty: str) -> Certainty:
    if not raw_certainty:
        return Certainty.UNKNOWN
    val = raw_certainty.strip().capitalize()
    try:
        return Certainty(val)
    except ValueError:
        return Certainty.UNKNOWN

def parse_iso_datetime(dt_str: str) -> Optional[str]:
    if not dt_str:
        return None
    try:
        dt = date_parser.parse(str(dt_str))
        return dt.isoformat()
    except (ValueError, TypeError):
        return None