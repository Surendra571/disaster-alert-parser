import json
import logging
from typing import List
from src.parsers.base_parser import BaseParser
from src.models import NormalizedAlert, SourceFormat
from src.utils.normalizer import (
    normalize_hazard, normalize_urgency, normalize_certainty, parse_iso_datetime
)

logger = logging.getLogger(__name__)

class JSONParser(BaseParser):
    def parse(self, raw_content: str) -> List[NormalizedAlert]:
        alerts = []
        try:
            data = json.loads(raw_content)
            if isinstance(data, dict):
                data = [data]

            for item in data:
                warnings = []
                alert_id = str(item.get("id") or item.get("identifier") or item.get("alertCode") or "JSON-UNKNOWN")
                source = str(item.get("source") or "JSON Feed")
                
                # Field Mappings
                raw_hazard = item.get("hazard") or item.get("event") or item.get("warningType") or ""
                hazard, h_warn = normalize_hazard(raw_hazard)
                if h_warn: warnings.append(h_warn)

                raw_sev = item.get("severity") or item.get("severity_text") or item.get("level") or ""
                sev, s_warn = self.lookups.resolve_severity(raw_sev)
                if s_warn: warnings.append(s_warn)

                urgency = normalize_urgency(item.get("urgency", ""))
                certainty = normalize_certainty(item.get("certainty", ""))
                
                loc_name = str(item.get("area") or item.get("district") or item.get("location") or "Unknown")
                loc_id = self.lookups.resolve_location_id(loc_name)

                start_time = parse_iso_datetime(item.get("valid_from") or item.get("onset") or item.get("startTime"))
                end_time = parse_iso_datetime(item.get("valid_to") or item.get("expires") or item.get("endTime"))

                action = str(item.get("advice") or item.get("instruction") or item.get("recommended_action") or "")

                alerts.append(NormalizedAlert(
                    alert_id=alert_id,
                    source=source,
                    hazard_type=hazard,
                    severity=sev,
                    urgency=urgency,
                    certainty=certainty,
                    location_name=loc_name,
                    location_id=loc_id,
                    start_time=start_time,
                    end_time=end_time,
                    recommended_action=action,
                    source_format=SourceFormat.JSON,
                    parse_warnings=warnings
                ))
        except Exception as e:
            logger.error(f"Error parsing JSON file: {e}")
        return alerts