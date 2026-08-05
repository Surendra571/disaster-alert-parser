# Disaster Alert Parser

A modular, extensible Python pipeline designed to ingest heterogeneous disaster alert formats (JSON, CAP/XML, RSS feeds, and Plaintext), normalize them using standard reference lookups, apply MD5-based deduplication, and export unified JSON outputs.

---

## Features

* **Multi-Format Ingestion**: Supports JSON, Common Alerting Protocol (CAP XML), RSS feeds, and Plaintext alert structures.
* **Reference Normalization**: Maps raw location names and severity levels to canonical schemas using CSV reference datasets.
* **Automated Discovery**: Dynamically scans directory trees to locate input data files and reference lookup datasets.
* **Deduplication**: Calculates MD5 fingerprints across critical payload attributes to flag duplicate records.
* **Robust Parsing & Warnings**: Gracefully handles malformed inputs while logging warnings without crashing the execution pipeline.

---

## Directory Structure

```text
disaster-alert-parser/
│
├── data/
│   ├── raw/
│   │   ├── location_reference.csv
│   │   ├── severity_mapping_reference.csv
│   │   ├── alerts.json
│   │   ├── alerts.xml
│   │   └── alerts.txt
│   └── outputs/
│       └── normalized_alerts.json
│
├── src/
│   ├── models.py
│   ├── main.py
│   ├── parsers/
│   │   ├── base_parser.py
│   │   ├── json_parser.py
│   │   ├── cap_parser.py
│   │   ├── rss_parser.py
│   │   └── text_parser.py
│   └── utils/
│       ├── deduplicator.py
│       ├── lookups.py
│       └── time_utils.py
│
├── tests/
│   └── test_golden_samples.py
│
├── pytest.ini
├── requirements.txt
└── README.md

```

---

## Installation

1. **Clone the repository**:
```bash
git clone <git remote add origin https://github.com/Surendra571/disaster-alert-parser.git>
cd disaster-alert-parser

```


2. **Set up a virtual environment**:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

```


3. **Install dependencies**:
```bash
pip install -r requirements.txt

```



---

## Usage

### Running the Pipeline

Place your raw input files (`.json`, `.xml`, `.txt`, `.rss`) into the `data/raw/` directory and execute the main pipeline runner:

```bash
python -m src.main

```

The parsed and deduplicated alerts will be generated at `data/outputs/normalized_alerts.json`.

---

## Running Tests

Execute the unit test suite using `pytest`:

```bash
python -m pytest tests/

```

---

## Schema Overview

The pipeline normalizes all incoming records into the following structured payload:

| Field | Type | Description |
| --- | --- | --- |
| `alert_id` | `str` | Unique source identifier for the alert |
| `hazard_type` | `HazardType` | Canonical hazard classification |
| `severity` | `Severity` | Standardized severity level (Extreme, Severe, Moderate, Minor, Unknown) |
| `location_name` | `str` | Target location name |
| `location_id` | `str` | Reference lookup code mapped from the location name |
| `valid_from` | `datetime` | ISO-8601 formatted start timestamp |
| `valid_to` | `datetime` | ISO-8601 formatted expiration timestamp |
| `description` | `str` | Alert body or directive instructions |
| `source_format` | `SourceFormat` | Original input format (JSON, CAP, RSS, PLAINTEXT) |
| `is_duplicate` | `bool` | True if identified as a duplicate payload |
| `parse_warnings` | `List[str]` | List of non-fatal execution warnings generated during parsing |
