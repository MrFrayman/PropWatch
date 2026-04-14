# File Timeline Explained

This document expands `FILE_TIMELINE.txt` into a developer reference.
It follows the same chronological file order and explains:
- What each file does.
- Every variable/field/method/function in code files.
- How each file connects to the rest of the repository.

## Cross-File Flow (High-Level)

1. `AGENTS.md`, `docs/MASTER-PLAN.md`, and `README.md` define the intended product behavior and architecture.
2. `src/propwatch/core/*` provides shared constants, environment config, and unit conversion.
3. `src/propwatch/models/*` defines Pydantic models for buildings, listings, units, transactions, raw records, and source metadata.
4. `src/propwatch/services/*` implements core behaviors: adapters, normalization, fingerprinting, and matching.
5. `db/schema.sql` and `docs/schema-notes.md` describe relational storage expectations.
6. `tests/*` validates constants, config, models, normalization, fingerprinting, and matching behavior.

## File-By-File (Timeline Order)

### 1) `AGENTS.md`
- Purpose: Repository guardrails for AI contributors.
- Logic content: No executable code. Defines hard rules around integrity gates, location verification, SqFt canonical unit, deterministic PDF order, and conservative failure behavior.
- Key “variables” (policy-level):
  - Integrity threshold: `FinalIntegrity < 0.7` blocks valuation.
  - Canonical unit: `SqFt`.
  - Verdict ladder and section order are fixed.
- Connections:
  - Constrains how `src/propwatch/core/*`, `services/*`, `models/*`, and reporting behavior should evolve.
  - Aligns directly with `docs/MASTER-PLAN.md`.

### 2) `docs/MASTER-PLAN.md`
- Purpose: Full technical specification and phase plan.
- Logic content: No executable code. Defines architecture, tables, state graph, valuation and integrity formulas, matching ladder, and rollout phases.
- Key “variables” (spec-level):
  - Integrity formula.
  - Fingerprint baseline hash strategy.
  - Confidence tiers and verdict hierarchy.
- Connections:
  - Source-of-truth design reference for all runtime code and schema work.
  - `README.md` is a shorter product-facing summary of this plan.

### 3) `README.md`
- Purpose: Practical project overview and operator guide.
- Logic content: No executable code.
- Key entries:
  - Pipeline stages (`ScoutNode`, `SkepticNode`, `AnalystNode`, `ReporterNode`).
  - Run commands and prerequisites.
  - High-level architecture and conservative policy.
- Connections:
  - Bridges spec docs (`AGENTS.md`, `docs/MASTER-PLAN.md`) to implementation expectations.
  - Referenced by `src/propwatch.egg-info/SOURCES.txt` and packaging metadata.

### 4) `.dockerignore`
- Purpose: Docker ignore rules.
- Current content: Empty file.
- Connections:
  - No active impact yet on Docker build context because no rules are defined.

### 5) `.gitignore`
- Purpose: Excludes local/env/build artifacts from git tracking.
- Entries and logic:
  - `.env` for secrets.
  - Python cache/compiled artifacts: `__pycache__/`, `*.py[cod]`, `*$py.class`.
  - Build/distribution folders: `build/`, `dist/`, `sdist/`, etc.
  - Binary/build extras: `*.so`, PyInstaller artifacts.
- Connections:
  - Supports clean git state for all source and test files.

### 6) `requirements.txt`
- Purpose: Python runtime/test dependency list.
- Packages:
  - `pandas`
  - `pydantic`
  - `python-dotenv`
  - `pytest`
  - `rapidfuzz`
  - `reportlab`
  - `requests`
  - `sqlalchemy`
  - `psycopg2-binary`
- Connections:
  - Powers imports in `packages-test.py` and multiple modules/tests in `src/` and `tests/`.

### 7) `src/propwatch/__init__.py`
- Purpose: Package marker for `propwatch`.
- Logic: Empty.
- Connections:
  - Enables package import paths used across tests and services.

### 8) `src/propwatch/core/__init__.py`
- Purpose: Package marker for `propwatch.core`.
- Logic: Empty.
- Connections:
  - Supports `from propwatch.core import constants/config`.

### 9) `src/propwatch/models/__init__.py`
- Purpose: Package marker for `propwatch.models`.
- Logic: Empty.
- Connections:
  - Supports imports in tests and runtime modules.

### 10) `src/propwatch/services/__init__.py`
- Purpose: Package marker for `propwatch.services`.
- Logic: Empty.
- Connections:
  - Enables service module imports (`fingerprint`, `matching`, `normalization`, adapters).

### 11) `src/propwatch/services/adapters/__init__.py`
- Purpose: Package marker for adapter subpackage.
- Logic: Empty.
- Connections:
  - Enables adapter imports from `propwatch.services.adapters`.

### 12) `src/propwatch/utils/__init__.py`
- Purpose: Package marker for utility subpackage.
- Logic: Empty.
- Connections:
  - Reserved namespace for shared utility functions.

### 13) `packages-test.py`
- Purpose: Environment sanity-check script that imports key packages.
- Imports/variables:
  - Aliases and objects imported from `pandas`, `pydantic`, `requests`, `dotenv`, `sqlalchemy`, `psycopg2`, `rapidfuzz`, `reportlab`, `pytest`.
- Methods/functions:
  - No function definitions; module-level `print(...)` statements output versions/objects.
- Connections:
  - Validates dependencies declared in `requirements.txt`.

### 14) `pyproject.toml`
- Purpose: Build and package metadata.
- Keys/variables:
  - `[build-system]` uses `setuptools.build_meta`.
  - Project metadata: `name="propwatch"`, `version="0.1.0"`.
  - Package discovery location: `where = ["src"]`.
- Connections:
  - Drives generated files in `src/propwatch.egg-info/*`.

### 15) `src/propwatch.egg-info/PKG-INFO`
- Purpose: Generated package metadata snapshot.
- Variables:
  - `Metadata-Version: 2.4`
  - `Name: propwatch`
  - `Version: 0.1.0`
- Connections:
  - Derived from `pyproject.toml`.

### 16) `src/propwatch.egg-info/SOURCES.txt`
- Purpose: Generated manifest of packaged source files.
- Content logic:
  - Flat list of included source and test files at generation time.
- Connections:
  - Reflects package-discovery behavior from `pyproject.toml`.

### 17) `src/propwatch.egg-info/dependency_links.txt`
- Purpose: Generated setuptools dependency links file.
- Content: Empty.
- Connections:
  - Standard packaging artifact.

### 18) `src/propwatch.egg-info/top_level.txt`
- Purpose: Generated top-level package name list.
- Variable:
  - `propwatch`
- Connections:
  - Used by tooling to identify import root package.

### 19) `src/propwatch/core/constants.py`
- Purpose: Shared constants for normalization and integrity behavior.
- Variables:
  - `AREA_UNIT = "SQFT"`: Canonical area unit label.
  - `INTEGRITY_FIRST_VERDICT = "integrity_first"`: Strategy key.
  - `DEFAULT_CONFIDENCE_THRESHOLDS`: Dict with keys `"integrity_first"` and `"default"`.
  - `SOURCE_LABELS`: Maps `"dubai"` and `"sharjah"` to human-readable source names.
  - `INTEGRITY_CEILING = 0.95`: Numeric cap used by policy logic.
- Methods/functions: None.
- Connections:
  - Validated by `tests/test_constants.py`.
  - Intended shared values for services and reporting logic.

### 20) `src/propwatch/models/building.py`
- Purpose: Pydantic model for a building entity.
- Class:
  - `Building(BaseModel)`
- Fields:
  - `name: str`
  - `location: str`
  - `emirate: str`
  - `coordinates: Optional[Dict[str, float]] = None`
  - `metadata: Optional[Dict[str, str]] = None`
- Methods:
  - No custom methods; validation/serialization inherited from Pydantic.
- Connections:
  - Used by `tests/test_models.py`.
  - Conceptually paired with building matching in `services/matching.py`.

### 21) `src/propwatch/models/listing.py`
- Purpose: Pydantic model for inbound listing claims.
- Class:
  - `Listing(BaseModel)`
- Fields:
  - `portal_source: str`
  - `asking_price: float`
  - `area_raw: str`
  - `area_normalized: Optional[float] = None`
  - `building_match: Optional[str] = None`
  - `integrity_fields: Optional[dict] = None`
- Methods:
  - No custom methods; uses Pydantic field validation.
- Connections:
  - Used by `tests/test_models.py`.
  - `area_raw` + `area_normalized` mirrors normalization behavior from `services/normalization.py`.

### 22) `src/propwatch/models/transaction.py`
- Purpose: Pydantic transaction record model.
- Class:
  - `Transaction(BaseModel)`
- Fields:
  - `building_id: int`
  - `raw_area_value: float`
  - `raw_unit: str`
  - `normalized_sqft_value: float`
  - `price: float`
  - `transaction_date: date`
- Methods:
  - No custom methods.
- Connections:
  - Used by `tests/test_models.py`.
  - Structurally aligned with unit conversion and audit-trail conventions.

### 23) `src/propwatch/models/unit.py`
- Purpose: Unit-level model used for per-unit identity.
- Class:
  - `Unit(BaseModel)`
- Fields:
  - `building_reference: str`
  - `floor: int`
  - `unit_type: str`
  - `area: float`
  - `fingerprint: str`
- Methods:
  - No custom methods.
- Connections:
  - Tested in `tests/test_models.py`.
  - `fingerprint` is conceptually produced by `services/fingerprint.py`.

### 24) `.env.example`
- Purpose: Template environment variables for local setup.
- Variables:
  - `DATABASE_URL`
  - `OPENAI_API_KEY`
  - `ANOTHER_API_KEY`
  - `LOG_FILE_PATH`
  - `DATA_FILE_PATH`
  - `DEBUG_MODE`
  - `MAX_CONNECTIONS`
- Connections:
  - `src/propwatch/core/config.py` reads overlapping vars, especially `DATABASE_URL`, `OPENAI_API_KEY`, `DEBUG_MODE`.

### 25) `db/schema.sql`
- Purpose: SQL schema defining relational entities.
- Tables and core columns:
  - `buildings`: `id`, `name`, `address`, `city`, `state`, `zip_code`, timestamps.
  - `units`: `id`, `building_id` FK, `unit_number`, `floor`, `bedrooms`, `bathrooms`, `square_feet`, timestamps.
  - `transactions`: `id`, `unit_id` FK, `transaction_type`, `price`, `transaction_date`, timestamps.
  - `listings`: `id`, `unit_id` FK, `listing_type`, `price`, `listed_date`, timestamps.
  - `inference_results`: `id`, `unit_id` FK, `inferred_price`, `confidence_score`, `inference_date`, timestamps.
- Methods/functions: None (DDL only).
- Connections:
  - Data-model counterpart to `src/propwatch/models/*`.
  - Explained further by `docs/schema-notes.md`.

### 26) `docs/schema-notes.md`
- Purpose: Policy notes and follow-up guidance for schema/model direction.
- Logic content:
  - No executable code; defines enforcement expectations.
- Key guidance points:
  - Separate truth from claims.
  - Canonicalize to SqFt.
  - Keep integrity gates and ghost signals explicit.
  - Keep fingerprint coarse and stable.
  - Enforce official verdict set and report structure.
- Connections:
  - Interprets spec and repository rules for schema/model evolution.
  - References current Pydantic models and expected gaps.

### 27) `src/propwatch/core/config.py`
- Purpose: Environment-backed runtime config container.
- Imports/variables:
  - `os`
  - Optional `load_dotenv` from `dotenv`; fallback `lambda: None` if missing.
  - `load_dotenv()` called at import time.
- Class:
  - `Config`
- Class attributes:
  - `DATABASE_URL = os.getenv("DATABASE_URL")`
  - `OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")`
  - `PDF_STORAGE_PATH = os.getenv("PDF_STORAGE_PATH", "./pdfs")`
  - `REPORT_OUTPUT_PATH = os.getenv("REPORT_OUTPUT_PATH", "./reports")`
  - `DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "t")`
- Methods:
  - `@staticmethod validate()`
  - Logic: accumulates missing required vars in `missing_vars` list and raises `ValueError` if required entries are absent.
- Connections:
  - Tested in `tests/test_config.py`.
  - Depends on `.env` / `.env.example` conventions.

### 28) `src/propwatch/models/schemas.py`
- Purpose: Alternative grouped schema definitions in one module.
- Imports/variables:
  - `BaseModel`, `Field`, typing helpers, `date`.
- Classes and fields:
  - `Building`: same field shape as `models/building.py`.
  - `Unit`: `building_reference`, `floor`, `unit_type`, `area`, `fingerprint`.
  - `Transaction`: `unit_fingerprint`, `transaction_date`, `price`, `source`, optional `normalized_area`.
  - `Verdict`: `transaction_fingerprint`, `valuation`, optional `confidence_score`, optional `rationale`.
- Methods:
  - No custom class methods.
  - Module-level `print("Schemas for Building, Unit, Transaction, and Verdict have been defined.")`.
- Connections:
  - Conceptually overlaps with individual files in `src/propwatch/models/`.
  - Intended as compact schema hub for downstream services/reporting.

### 29) `tests/test_config.py`
- Purpose: Unit tests for config loading and validation behavior.
- Functions/methods:
  - `reload_config_module(monkeypatch)`: reloads config module so class attributes reflect patched env vars.
  - `test_config_validate_missing_env(monkeypatch)`: asserts `Config.validate()` raises when required vars missing.
  - `test_config_reads_env_and_validates(monkeypatch)`: sets env vars, reloads module, validates and asserts values.
- Variables/classes:
  - Uses `monkeypatch`, `pytest`, imported `config`.
- Connections:
  - Tests `src/propwatch/core/config.py`.

### 30) `tests/test_constants.py`
- Purpose: Minimal sanity tests for constants module.
- Functions:
  - `test_imports()`: verifies constants module imports.
  - `test_sqft_constant()`: verifies `AREA_UNIT.lower() == "sqft"`.
- Connections:
  - Tests `src/propwatch/core/constants.py`.

### 31) `tests/test_models.py`
- Purpose: Validation tests for core Pydantic models.
- Variables/constants:
  - `ROOT` computed from file path; inserted into `sys.path`.
- Functions:
  - `test_package_imports()`: imports model modules by name.
  - `test_core_models_validate_sample_payload()`: constructs sample payloads for `Building`, `Unit`, `Transaction`, `Listing` and asserts key fields.
  - `test_listing_area_fields_coexist()`: verifies raw and normalized area can coexist.
- Connections:
  - Tests `src/propwatch/models/building.py`, `unit.py`, `transaction.py`, `listing.py`.
  - Reinforces raw + normalized area rule used by normalization layer.

### 32) `src/propwatch/core/units.py`
- Purpose: Area unit conversion helper.
- Function:
  - `convert_area_to_sqft(value, unit)`
- Internal logic:
  - Normalizes input unit via `unit.lower()`.
  - Conversion cases:
    - `"sqm"` -> `value * 10.7639`
    - `"sqft"` -> `value`
    - `"acres"` -> `value * 43560`
  - Raises `ValueError` for unsupported units.
- Connections:
  - Used by `src/propwatch/services/normalization.py`.
  - Behavior validated indirectly by `tests/test_normalization.py`.

### 33) `src/propwatch/models/raw_record.py`
- Purpose: Raw-source audit models to preserve untouched ingestion values.
- Imports/variables:
  - `BaseModel`, `Field`, `datetime`, `Optional`.
- Classes and fields:
  - `RawRecord(BaseModel)`:
    - `source_url: str`
    - `original_text: str`
    - `original_units: Optional[str]`
    - `parse_timestamp: datetime = Field(default_factory=datetime.utcnow)`
    - `confidence_score: Optional[float]`
  - `RawListing(RawRecord)`: no additional fields.
  - `RawTransaction(RawRecord)`: no additional fields.
- Methods:
  - No custom methods.
  - Module has `if __name__ == "__main__":` sample instantiation and prints.
- Connections:
  - Paired conceptually with `src/propwatch/models/source_metadata.py`.
  - Supports the audit-trail policy in docs/spec.

### 34) `src/propwatch/models/source_metadata.py`
- Purpose: Metadata model describing data-source provenance.
- Imports/variables:
  - `Optional`, `BaseModel`, `Field`, `datetime`, `timezone`.
- Class and fields:
  - `SourceMetadata(BaseModel)`:
    - `source_name: str`
    - `source_type: str`
    - `last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))`
    - `notes: Optional[str]`
- Methods:
  - No custom methods.
  - Module has `if __name__ == "__main__":` sample object creation and print.
- Connections:
  - Complements `raw_record.py` by recording source-level metadata.

### 35) `src/propwatch/services/adapters/base.py`
- Purpose: Adapter contract for source-specific ingestion implementations.
- Class:
  - `BaseAdapter(ABC)`
- Abstract methods:
  - `fetch(self)`: should return raw source data.
  - `parse(self, raw_data)`: should convert raw data to structured intermediate shape.
  - `normalize(self, parsed_data)`: should map parsed data to app-consistent format.
- Connections:
  - Expected base for `dubai.py` and `sharjah.py`.
  - Defines uniform ingestion interface for future orchestration.

### 36) `src/propwatch/services/adapters/dubai.py`
- Purpose: Dubai-specific placeholder adapter implementation.
- Class:
  - `DubaiAdapter(BaseAdapter)`
- Attributes:
  - `source_name = "Dubai"`
  - `data_path = "data/dubai/"`
- Methods:
  - `__init__(self)`: sets source metadata/path.
  - `transform_data(self, raw_data)`: maps each item into normalized dict with keys `id`, `title`, `price`, `location`, `bedrooms`, `bathrooms`, `area`.
  - `load_data(self, transformed_data)`: placeholder print-based sink.
  - `extract_data(self)`: returns hardcoded mock raw listing list.
  - `process_data(self)`: orchestration wrapper (`extract_data` -> `transform_data` -> `load_data`).
- Module-level side effect:
  - `print("Dubai Adapter initialized and ready to process data.")`.
- Connections:
  - Extends `BaseAdapter`.
  - Pattern-matched by `sharjah.py` for adapter-layer consistency.

### 37) `src/propwatch/services/adapters/sharjah.py`
- Purpose: Sharjah-specific placeholder adapter for OCR/PDF-like extraction.
- Class:
  - `SharjahAdapter(BaseAdapter)`
- Methods:
  - `__init__(self, source)`: calls `super().__init__(source)`.
  - `extract_data(self)`: assembles dict with `price`, `location`, `size` from OCR helper methods.
  - `extract_price_from_ocr(self)`: placeholder string return.
  - `extract_location_from_ocr(self)`: placeholder string return.
  - `extract_size_from_ocr(self)`: placeholder string return.
  - `transform_data(self, data)`: standardizes keys to `price`, `location`, `size`.
  - `load_data(self, transformed_data)`: placeholder print sink.
- Module-level side effect:
  - `print("SharjahAdapter initialized and ready to extract, transform, and load data.")`.
- Connections:
  - Extends `BaseAdapter`.
  - Intended low-confidence ingestion path complementing `dubai.py`.

### 38) `src/propwatch/services/fingerprint.py`
- Purpose: Coarse fingerprint generation for unit clustering/matching.
- Function:
  - `generate_fingerprint(building, size_band, unit_type, floor_range)`
- Internal helper:
  - `normalize(text)`: uppercases and strips non-alphanumeric chars.
- Output format:
  - `"{building_segment}-{size_band}-{unit_segment}-{floor_range}"`
  - `building_segment` is first 5 normalized building chars.
  - `unit_segment` is first 3 normalized unit chars.
- Connections:
  - Tested by `tests/test_fingerprints.py`.
  - Conceptually aligns with unit identity model (`models/unit.py`).

### 39) `src/propwatch/services/matching.py`
- Purpose: Building-to-property matching ladder with confidence output.
- Imports/variables:
  - `@dataclass`, `Optional`, `rapidfuzz.fuzz`.
- Data class:
  - `MatchResult`
  - Fields: `building_id: Optional[int]`, `confidence: float`, `match_type: str`.
- Function:
  - `match_building_to_property(building, property, fuzzy_threshold=80) -> MatchResult`
- Internal helpers:
  - `normalize(name)`: lowercases and strips non-alphanumeric chars.
  - `clean(name)`: removes common words (`the`, `and`, `of`, `in`, `at`) for lenient comparison.
- Matching ladder:
  - Exact normalized match -> confidence `1.0`, type `exact_normalized`.
  - Cleaned-text match -> confidence `0.9`, type `cleaned`.
  - Fuzzy ratio above threshold -> confidence score/100, type `fuzzy`.
  - Else -> no match (`None`, `0.0`, `none`).
- Connections:
  - Tested by `tests/test_matching.py`.
  - Consumes building/property objects with `.name`; returns building id for downstream linkage.

### 40) `src/propwatch/services/normalization.py`
- Purpose: Preserve raw area values while generating canonical SqFt.
- Function:
  - `normalize_area(raw_area_value, raw_area_unit)`
- Logic:
  - Calls `convert_area_to_sqft` from `propwatch.core.units`.
  - Returns dict with:
    - `raw_area_value`
    - `raw_area_unit`
    - `normalized_area_sqft`
- Connections:
  - Depends on `src/propwatch/core/units.py`.
  - Tested by `tests/test_normalization.py`.
  - Complements listing/transaction model raw + normalized fields.

### 41) `tests/test_fingerprints.py`
- Purpose: Unit tests for coarse fingerprint stability and differentiation.
- Function:
  - `test_generate_fingerprint()`
- Test logic:
  - Same inputs produce same fingerprint.
  - Differences in building, size band, unit type, or floor range change fingerprint.
- Connections:
  - Tests `src/propwatch/services/fingerprint.py`.

### 42) `tests/test_matching.py`
- Purpose: Unit tests for matching ladder behavior and confidence outputs.
- Local helper classes:
  - `Building` dataclass: `id`, `name`.
  - `Property` dataclass: `name`.
- Test functions:
  - `test_exact_normalized_match()`
  - `test_cleaned_match()`
  - `test_fuzzy_match()`
  - `test_no_match()`
  - `test_ambiguous_match()`
- Connections:
  - Tests `src/propwatch/services/matching.py`.
  - Uses `rapidfuzz.fuzz` to compute expected fuzzy confidence.

### 43) `tests/test_normalization.py`
- Purpose: Unit tests for area normalization behavior.
- Test functions:
  - `test_normalize_area_sqm()`: asserts sqm conversion and raw-value retention.
  - `test_normalize_area_acres()`: asserts acre conversion and raw-value retention.
  - `test_normalize_area_unknown_unit()`: asserts `ValueError` on unsupported unit.
- Connections:
  - Tests `src/propwatch/services/normalization.py` and indirectly `core/units.py`.

## Connection Matrix (Quick)

- `core/constants.py` <-> `tests/test_constants.py`
- `core/config.py` <-> `.env.example`, `tests/test_config.py`
- `core/units.py` <-> `services/normalization.py` <-> `tests/test_normalization.py`
- `services/fingerprint.py` <-> `models/unit.py` (conceptual output target) <-> `tests/test_fingerprints.py`
- `services/matching.py` <-> `models/building.py` (conceptual identity source) <-> `tests/test_matching.py`
- `models/building.py`, `models/unit.py`, `models/transaction.py`, `models/listing.py` <-> `tests/test_models.py`
- `models/raw_record.py` + `models/source_metadata.py` <-> audit/provenance rules in `AGENTS.md`, `docs/MASTER-PLAN.md`, `docs/schema-notes.md`
- `db/schema.sql` <-> `docs/schema-notes.md` <-> model/service evolution plans
- `requirements.txt`, `pyproject.toml`, `src/propwatch.egg-info/*` <-> packaging and dependency health (`packages-test.py`)

## How To Update This File Later

When repository files change, update this document in three passes:
1. Sync the timeline order against `FILE_TIMELINE.txt`.
2. For each changed code file, refresh fields/functions/methods and return shapes.
3. Update the “Connection Matrix” so import/test/flow relationships stay accurate.
