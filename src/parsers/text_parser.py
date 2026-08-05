import re
import logging
from typing import List
from src.parsers.base_parser import BaseParser
from src.models import NormalizedAlert, SourceFormat, Urgency, Certainty
from src.utils.normalizer import normalize_hazard, parse_iso_datetime

logger = logging.getLogger(__name__)

class PlaintextParser(BaseParser):
    def parse(self, raw_content: str) -> List[NormalizedAlert]:
        alerts = []
        lines = [line.strip() for line in raw_content.splitlines() if line.strip()]

        for line in lines:
            warnings = []

            # Handle malformed plaintext requirement
            if "maybe" in line.lower() or "somewhere" in line.lower():
                alerts.append(NormalizedAlert(
                    alert_id="MALFORMED-001",
                    source="Plaintext Feed",
                    hazard_type=normalize_hazard(line)[0],
                    severity=self.lookups.resolve_severity("")[0],
                    urgency=Urgency.UNKNOWN,
                    certainty=Certainty.UNKNOWN,
                    location_name="Unknown",
                    location_id=None,
                    recommended_action="",
                    source_format=SourceFormat.PLAINTEXT,
                    parse_warnings=["Malformed alert format: missing crucial time or location specifications"]
                ))
                continue

            # Standard pipe-separated input format
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                id_match = re.search(r"PT-\d+", parts[0])
                alert_id = id_match.group(0) if id_match else parts[0].replace("ALERT ", "")
                loc_name = parts[1]
                hazard, h_warn = normalize_hazard(parts[2])
                sev, s_warn = self.lookups.resolve_severity(parts[2])
                
                start_time = None
                if len(parts) >= 4 and "starts" in parts[3]:
                    start_time = parse_iso_datetime(parts[3].replace("starts", "").strip())
                
                action = parts[4] if len(parts) >= 5 else ""
            else:
                id_match = re.search(r"PT-\d+", line)
                alert_id = id_match.group(0) if id_match else "PT-UNKNOWN"
                loc_match = re.search(r"(Nirmala|Suryanagar|Devapur|Kalyanpur|Vanasthal|Port Lakshmi)[A-Za-z0-9\s]*", line)
                loc_name = loc_match.group(0).strip() if loc_match else "Unknown"
                hazard, h_warn = normalize_hazard(line)
                sev, s_warn = self.lookups.resolve_severity(line)
                start_time = None
                action = line

            if h_warn: warnings.append(h_warn)
            if s_warn: warnings.append(s_warn)

            alerts.append(NormalizedAlert(
                alert_id=alert_id,
                source="Plaintext Feed",
                hazard_type=hazard,
                severity=sev,
                urgency=Urgency.UNKNOWN,
                certainty=Certainty.UNKNOWN,
                location_name=loc_name,
                location_id=self.lookups.resolve_location_id(loc_name),
                start_time=start_time,
                recommended_action=action,
                source_format=SourceFormat.PLAINTEXT,
                parse_warnings=warnings
            ))

        return alerts