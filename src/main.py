import os
import json
import logging
from typing import List
from src.models import NormalizedAlert
from src.utils.lookups import ReferenceLookups
from src.utils.deduplicator import AlertDeduplicator
from src.parsers.json_parser import JSONParser
from src.parsers.cap_parser import CAPParser
from src.parsers.rss_parser import RSSParser
from src.parsers.text_parser import PlaintextParser

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def find_file_fuzzy(target_keyword: str, search_path: str = ".") -> str | None:
    target_keyword = target_keyword.lower()
    for root, dirs, files in os.walk(search_path):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("venv", "env", "outputs", "__pycache__")]
        for f in files:
            if target_keyword in f.lower():
                return os.path.join(root, f)
    return None

class DisasterAlertPipeline:
    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir

        loc_csv = find_file_fuzzy("location_reference", root_dir) or ""
        sev_csv = find_file_fuzzy("severity_mapping_reference", root_dir) or ""
        
        logger.info(f"Location CSV: {loc_csv}")
        logger.info(f"Severity CSV: {sev_csv}")

        self.lookups = ReferenceLookups(loc_csv, sev_csv)
        self.deduplicator = AlertDeduplicator()

        self.json_parser = JSONParser(self.lookups)
        self.cap_parser = CAPParser(self.lookups)
        self.rss_parser = RSSParser(self.lookups)
        self.txt_parser = PlaintextParser(self.lookups)

    def run(self) -> List[NormalizedAlert]:
        all_alerts: List[NormalizedAlert] = []

        # Find all directories named 'data' or 'raw'
        target_dirs = set()
        for root, dirs, _ in os.walk(self.root_dir):
            if any(k in root.lower() for k in ["data", "raw"]):
                target_dirs.add(root)

        if not target_dirs:
            target_dirs.add(self.root_dir)

        processed_files = set()

        for search_dir in target_dirs:
            for file in os.listdir(search_dir):
                file_path = os.path.join(search_dir, file)

                if os.path.isdir(file_path) or file_path in processed_files:
                    continue

                file_lower = file.lower()

                # Skip reference CSVs, output directory files, and python scripts
                if file_lower.endswith((".csv", ".py", ".ini", ".md")) or "requirements" in file_lower or "normalized" in file_lower:
                    continue

                logger.info(f"Processing candidate file: {file_path}")
                processed_files.add(file_path)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")
                    continue

                # Auto-route to correct parser based on file name or content structure
                if file_lower.endswith(".json") or "json" in file_lower:
                    logger.info(f"Parsing {file} with JSONParser...")
                    all_alerts.extend(self.json_parser.parse(content))
                elif "cap" in file_lower or ("<alert" in content.lower() and "<rss" not in content.lower()):
                    logger.info(f"Parsing {file} with CAPParser...")
                    all_alerts.extend(self.cap_parser.parse(content))
                elif "rss" in file_lower or "<rss" in content.lower():
                    logger.info(f"Parsing {file} with RSSParser...")
                    all_alerts.extend(self.rss_parser.parse(content))
                elif file_lower.endswith(".txt") or "text" in file_lower or "plain" in file_lower:
                    logger.info(f"Parsing {file} with PlaintextParser...")
                    all_alerts.extend(self.txt_parser.parse(content))

        # Deduplicate records
        all_alerts = self.deduplicator.mark_duplicates(all_alerts)
        
        output_dir = os.path.join(self.root_dir, "data", "outputs")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "normalized_alerts.json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([alert.model_dump(mode="json") for alert in all_alerts], f, indent=2)

        logger.info(f"Pipeline complete. Exported {len(all_alerts)} alerts to {output_path}")
        return all_alerts

if __name__ == "__main__":
    pipeline = DisasterAlertPipeline()
    pipeline.run()