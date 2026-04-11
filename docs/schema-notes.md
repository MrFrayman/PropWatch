## What the schema must enforce
- **Separate truth from claims.** Portal data goes in one shape, normalized outcomes in another. The current split (`Building`, `Unit`, `Transaction`, `Verdict`) is on the right track; make sure future DTOs/services keep the boundary crisp instead of blending ingest-time claims with inference outputs.
- **Canonicalize to SqFt.** Every area number must eventually convert to SqFt (MASTER-PLAN §4.1). `Transaction.normalized_area` already exists for downstream comparisons; if other models carry raw units (e.g., listing payloads), pair them with explicit SqFt fields so valuation math never guesses the unit.
- **Honor the integrity gate.** Valuation only happens once `FinalIntegrity >= 0.7` (AGENTS §1, MASTER-PLAN §5). Even though the schema today doesn’t store the integrity fields, anything that creates a `Verdict` must consult the integrity calculation first and embed those signals nearby.
- **Keep fingerprints coarse and stable.** Follow the hash `SHA256(building_id + "-" + bedroom_count + "-" + ROUND(canonical_area_sqft / 50) * 50)` (AGENTS “Unit Fingerprinting”, MASTER-PLAN §4.2). `Unit.fingerprint` and `Transaction.unit_fingerprint` should come from that hash, falling back to an area-agnostic version if the listing lacks area.
- **Use the official verdict list.** ReporterNode needs mutually exclusive verdicts (`NON-COMPLIANT / SUSPICIOUS`, `UNVERIFIED LOCATION`, `DISTRESSED ASSET`, etc.), so the schema or enums must limit values to that ladder; nothing else should sneak in.
- **Respect the PDF order.** The renderer is hardcoded to Header → Identity Block → Verdict Card → Transaction Ledger → Integrity & Ghost Signals → Disclaimer. Schema-driven contracts should flow naturally into that order so the UI never has to reshuffle data.
- **Sharjah gets special handling.** Sharjah output is capped at MEDIUM confidence and decorated with a “Limited Data Source” watermark (README §Sharjah support, MASTER-PLAN §9.3). Any model carrying region metadata should allow downstream logic to trigger those visual cues and cap overrides.
- **Ghost signals stay separate.** Keep ghost metadata in its own structure (JSONB or typed flags). Don’t jam those fields into the canonical truth tables; they belong alongside integrity outputs (AGENTS “Integrity and Ghost Signals”).

## Where the current Pydantic models land
- `Building` stores the identity anchor (name, location, emirate, optional coordinates/metadata) that underpins the Identity Block. It should mirror the PostgreSQL `buildings` table and carry the same constraints.
- `Unit` references a building, floor, unit type, raw area, and fingerprint. It captures the spirit of the fingerprint rules, so future extensions should retain both raw and normalized context before feeding the hash.
- `Transaction` ties to the fingerprint and records the date, price, source, and optional normalized SqFt. It already honors the “store raw and normalized values together” rule and supplies the medians the Analyst node relies on.
- `Verdict` binds to the fingerprint, valuation, optional confidence score, and rationale. If future reporting needs integrity or ghost details, keep them in separate models and just expose references here rather than stuffing all signals into one blob.

## Follow-up items
- Add explicit `Listing` and `Inference` models/DTOs that mirror the PostgreSQL schema described in MASTER-PLAN/AGENTS so raw claims and computed reasoning never intermingle.
- Capture `integrity_score`, `ghost_signals`, `valuation_confidence`, and `final_verdict` in their own models so reporters and sane services can consume them without recomputing decisions.
- Introduce Sharjah-specific flags/enums so the reporting layer can consistently apply the “Limited Data Source” watermark and honor the MEDIUM confidence cap whenever the region is Sharjah.
