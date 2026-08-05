import hashlib
from typing import List
from src.models import NormalizedAlert

class AlertDeduplicator:
    def __init__(self):
        self.seen_fingerprints = set()

    def mark_duplicates(self, alerts: List[NormalizedAlert]) -> List[NormalizedAlert]:
        for alert in alerts:
            # Generate key fingerprint based on ID or hazard + location + action
            if alert.alert_id and not alert.alert_id.startswith("MALFORMED"):
                fingerprint = f"id:{alert.alert_id.strip().lower()}"
            else:
                fingerprint = f"content:{alert.hazard_type.value}|{alert.location_name.lower()}|{alert.start_time}"
            
            fingerprint_hash = hashlib.md5(fingerprint.encode("utf-8")).hexdigest()
            
            if fingerprint_hash in self.seen_fingerprints:
                alert.is_duplicate = True
            else:
                self.seen_fingerprints.add(fingerprint_hash)
                alert.is_duplicate = False
                
        return alerts