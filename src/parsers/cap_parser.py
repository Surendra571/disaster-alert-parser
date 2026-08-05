import xml.etree.ElementTree as ET
import logging
from typing import List
from src.parsers.base_parser import BaseParser
from src.models import NormalizedAlert, SourceFormat
from src.utils.normalizer import (
    normalize_hazard, normalize_urgency, normalize_certainty, parse_iso_datetime
)

logger = logging.getLogger(__name__)

class CAPParser(BaseParser):
    def parse(self, raw_content: str) -> List[NormalizedAlert]:
        alerts = []
        try:
            root = ET.fromstring(raw_content)
            # Handle XML namespaces
            for elem in root.iter():
                if '}' in elem.tag:
                    elem.tag = elem.tag.split('}', 1)[1]

            alerts_node = root.findall("alert") if root.tag == "alerts" else [root]

            for alert_elem in alerts_node:
                warnings = []
                alert_id = alert_elem.findtext("identifier", default="CAP-UNKNOWN")
                source = alert_elem.findtext("sender", default="CAP Feed")

                info = alert_elem.find("info")
                if info is not None:
                    hazard, h_warn = normalize_hazard(info.findtext("event", default=""))
                    if h_warn: warnings.append(h_warn)

                    sev, s_warn = self.lookups.resolve_severity(info.findtext("severity", default=""))
                    if s_warn: warnings.append(s_warn)

                    urgency = normalize_urgency(info.findtext("urgency", default=""))
                    certainty = normalize_certainty(info.findtext("certainty", default=""))

                    area = info.find("area")
                    loc_name = area.findtext("areaDesc", default="Unknown") if area is not None else "Unknown"
                    loc_id = self.lookups.resolve_location_id(loc_name)

                    start_time = parse_iso_datetime(info.findtext("onset") or alert_elem.findtext("sent"))
                    end_time = parse_iso_datetime(info.findtext("expires"))
                    action = info.findtext("instruction", default="")

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
                        source_format=SourceFormat.CAP_XML,
                        parse_warnings=warnings
                    ))
        except Exception as e:
            logger.error(f"Error parsing CAP XML: {e}")
        return alerts