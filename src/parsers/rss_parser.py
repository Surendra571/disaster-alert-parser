import feedparser
import re
import logging
from typing import List
from src.parsers.base_parser import BaseParser
from src.models import NormalizedAlert, SourceFormat, Urgency, Certainty
from src.utils.normalizer import normalize_hazard, parse_iso_datetime

logger = logging.getLogger(__name__)

class RSSParser(BaseParser):
    def parse(self, raw_content: str) -> List[NormalizedAlert]:
        alerts = []
        try:
            feed = feedparser.parse(raw_content)
            source = feed.feed.get("title", "RSS Feed")

            for entry in feed.entries:
                warnings = []
                alert_id = entry.get("guid") or entry.get("id") or "RSS-UNKNOWN"
                title = entry.get("title", "")
                desc = entry.get("description", "")

                # Severity Extraction from Title
                raw_sev = title.split(":")[0] if ":" in title else title
                sev, s_warn = self.lookups.resolve_severity(raw_sev)
                if s_warn: warnings.append(s_warn)

                # Hazard Extraction
                hazard, h_warn = normalize_hazard(title + " " + desc)
                if h_warn: warnings.append(h_warn)

                # Location & Recommended Action from Description
                loc_match = re.search(r"for ([A-Za-z0-9\s]+)", title)
                loc_name = loc_match.group(1).strip() if loc_match else "Unknown"
                loc_id = self.lookups.resolve_location_id(loc_name)

                action_match = re.search(r"Action:\s*(.*?)(?=\.\s*Valid|$)", desc)
                action = action_match.group(1).strip() if action_match else desc

                start_time = parse_iso_datetime(entry.get("published"))

                alerts.append(NormalizedAlert(
                    alert_id=alert_id,
                    source=source,
                    hazard_type=hazard,
                    severity=sev,
                    urgency=Urgency.UNKNOWN,
                    certainty=Certainty.UNKNOWN,
                    location_name=loc_name,
                    location_id=loc_id,
                    start_time=start_time,
                    end_time=None,
                    recommended_action=action,
                    source_format=SourceFormat.RSS,
                    parse_warnings=warnings
                ))
        except Exception as e:
            logger.error(f"Error parsing RSS feed: {e}")
        return alerts