from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class HazardType(str, Enum):
    FLOOD = "flood"
    HEATWAVE = "heatwave"
    CYCLONE = "cyclone"
    LANDSLIDE = "landslide"
    LIGHTNING = "lightning"
    EARTHQUAKE = "earthquake"
    OTHER = "other"

class Severity(str, Enum):
    MINOR = "Minor"
    MODERATE = "Moderate"
    SEVERE = "Severe"
    EXTREME = "Extreme"
    UNKNOWN = "Unknown"

class Urgency(str, Enum):
    IMMEDIATE = "Immediate"
    EXPECTED = "Expected"
    FUTURE = "Future"
    PAST = "Past"
    UNKNOWN = "Unknown"

class Certainty(str, Enum):
    OBSERVED = "Observed"
    LIKELY = "Likely"
    POSSIBLE = "Possible"
    UNKNOWN = "Unknown"

class SourceFormat(str, Enum):
    JSON = "json"
    CAP_XML = "cap_xml"
    RSS = "rss"
    PLAINTEXT = "plaintext"

class NormalizedAlert(BaseModel):
    alert_id: str
    source: str
    hazard_type: HazardType
    severity: Severity
    urgency: Urgency
    certainty: Certainty
    location_name: str
    location_id: Optional[str] = None
    start_time: Optional[str] = Field(default=None, description="ISO-8601 datetime or null")
    end_time: Optional[str] = Field(default=None, description="ISO-8601 datetime or null")
    recommended_action: str
    source_format: SourceFormat
    is_duplicate: bool = False
    parse_warnings: List[str] = Field(default_factory=list)