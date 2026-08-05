# Disaster Alert Parser: Architectural Overview & Project Summary

## 1. Core Approach & Architecture

To ingest heterogeneous disaster alert formats and transform them into a unified output, we designed a modular, object-oriented pipeline anchored by Pydantic models.

* **Abstract Base Class Pattern**: We created an abstract `BaseParser` class defining a common `.parse(content: str) -> List[NormalizedAlert]` contract. Format-specific classes (`JSONParser`, `CAPParser`, `RSSParser`, `PlaintextParser`) implement this interface, isolating format quirks from the main execution workflow.
* **Strict Schema & Enums**: Data normalization relies on standard enumerations (`HazardType`, `Severity`, `SourceFormat`) and Pydantic models (`NormalizedAlert`), guaranteeing strict output schema adherence.
* **Lookup & Normalization Engine**: A dedicated `ReferenceLookups` utility ingests location and severity mapping CSVs, enabling clean term resolution and fuzzy entity mapping.
* **Deduplication Engine**: An `AlertDeduplicator` computes MD5 content hashes across core payload attributes (`hazard_type`, `location_id`, `valid_from`, and `severity`) to identify duplicate alerts across multi-format inputs.

## 2. Key Technical Decisions

* **Graceful Degradation over Hard Failures**: When parsing malformed text or partial inputs, the system logs parse warnings directly into the `parse_warnings` field on the alert model rather than throwing unhandled exceptions.
* **Robust ISO-8601 Timestamp Parsing**: Custom datetime utilities handle varied date formats across RSS, CAP, and custom JSON payloads, normalizing all timestamps to standard ISO-8601 strings.
* **Fuzzy Directory & Reference Discovery**: To keep the CLI seamless, dynamic directory walking (`find_file_fuzzy`) locates input datasets and reference lookup files regardless of minor path nesting variations (e.g., `data/` vs `data/raw/`).

## 3. Challenges & Resolutions

* **Handling Malformed Plaintext and XML**: Free-form plaintext and invalid CAP XML (such as malformed XML attributes) caused execution crashes in initial iterations.
* *Resolution*: Standardized fallback handling within `PlaintextParser` to catch non-standard line delimiters and added explicit XML syntax error handling inside `CAPParser` to isolate unparseable payloads.


* **Directory Ambiguity in Search Paths**: Variations between test environments and command-line execution led to reference lookups missing CSV files or skipping raw data inputs.
* *Resolution*: Updated file discovery in `src/main.py` to recursively evaluate candidate files across directory boundaries while filtering out non-data files (`.py`, `.ini`, `.md`).


* **Lookup Term Case Sensitivity**: Unmapped severity labels were defaulting to `Severity.UNKNOWN` when exact term casing failed to match lookup dictionaries.
* *Resolution*: Added fallback casing normalization (`.strip().capitalize()`) directly into the severity resolution logic.



## 4. Results

* **100% Test Pass Rate**: The suite (`tests/test_golden_samples.py`) passes all extraction, parsing, and warning validation checks under `pytest`.
* **Multi-Format Processing**: Verified end-to-end processing across JSON (`alerts.json`), CAP XML (`alerts.xml`), and Plaintext (`alerts.txt`) sources.
* **Output Standardization**: Successfully exported clean, deduplicated, and normalized records to `data/outputs/normalized_alerts.json`.