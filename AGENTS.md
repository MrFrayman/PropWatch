# PropWatch UAE — AGENTS.md
# Purpose: guidance for future AI assistants contributing to this repository.

## Project Overview

PropWatch UAE is an investor-first property intelligence engine for Dubai and Sharjah. It detects ghost listings, normalizes real estate transactions, verifies compliance signals, and generates conservative due-diligence reports for listings. The system is intentionally pessimistic: integrity checks override valuation, and uncertain data must fail safely rather than produce optimistic guesses.

## Core Product Principles

- Prefer truth over coverage.
- Prefer deterministic logic over heuristic improvisation.
- Prefer safe failure over confident error.
- Integrity always gates valuation.
- Sharjah data is best-effort and lower-confidence unless explicitly upgraded by future data quality.
- SqFt is the canonical pricing unit.
- Preserve raw source values alongside normalized values.
- Never silently infer missing compliance, location, or permit evidence.
- The PDF report is the product output, not a secondary UI.

## Repository Goals

This repository implements:
- A NestJS modular monolith.
- BullMQ/Redis worker-based ingestion and processing.
- LangGraph-driven workflow orchestration.
- PostgreSQL truth storage for buildings, transactions, listings, and inferences.
- Playwright/Puppeteer scraping and report generation.
- A strict CLI-to-PDF reporting flow.

## Tech Stack

- Backend: NestJS v10+.
- Language: TypeScript.
- Workflow engine: LangGraph via `@langchain/langgraph`.
- Database: PostgreSQL 16+.
- Queue/cache: Redis 7+ with BullMQ.
- Scraping: Playwright or Puppeteer.
- Reporting: HTML/CSS templates or Next.js Server Components rendered to PDF with Puppeteer.
- Future optional search: pgvector.

## Non-Negotiable Rules

### 1) Integrity is a hard gate
- Do not produce valuation outputs unless integrity has passed.
- If integrity is below threshold, the listing must be labeled `NON-COMPLIANT / SUSPICIOUS`.
- Never let pricing attractiveness override compliance failures.

### 2) Location must be verified
- If building matching is uncertain, stop valuation.
- If the location cannot be resolved confidently, use `UNVERIFIED LOCATION`.
- Do not “best guess” a building match when GPS or exact identifiers are missing.

### 3) SqFt is canonical
- Convert all imported areas to SqFt.
- Preserve raw source area and source unit for auditability.
- Never use sqm as the final valuation basis.

### 4) Keep raw and normalized data separate
- Store source claims in source tables/fields.
- Store canonical truth and computed outputs separately.
- Never overwrite raw portal data with inferred values.

### 5) Report determinism
- The PDF output must follow the fixed section order.
- Do not reorder the report sections without an explicit design change.
- Do not hide integrity or ghost-signal findings in footnotes.

## Domain Model Conventions

### Buildings
- `buildings` is the anchor for identity and location.
- Building names are unique within an area.
- DLD building IDs, when available, are preferred over fuzzy text matching.
- Latitude and longitude are authoritative when available.

### Transactions
- `transactions` represent truth and historical valuation evidence.
- Every record should preserve the original area value and unit.
- `price_per_sqft` should be derived, not manually entered.
- Use transaction history for medians and confidence tiers.

### Listings
- `listings` are volatile external claims.
- Treat every portal listing as untrusted until verified.
- Store portal source, URL, agent, agency, permits, and scraping timestamp.
- Missing fields are common and should be handled explicitly.

### Inferences
- `inferences` stores the engine’s reasoning outputs.
- Keep integrity score, ghost signals, valuation confidence, and final verdict here.
- Do not mix raw listing claims with inference results.
- Final verdicts must be explainable from the stored signals.

## Unit Fingerprinting Rules

The unit fingerprint is a coarse identity bridge between listings and historical transactions.

Baseline fingerprint:
`SHA256(building_id + "-" + bedroom_count + "-" + ROUND(canonical_area_sqft / 50) * 50)`

Rules:
- Use building ID when available.
- Use bedroom count as a major discriminator.
- Bucket area in 50 SqFt increments.
- Do not over-fragment units with soft attributes like view, floor, or premium narration.
- If area is missing, fall back to an area-agnostic fingerprint and set valuation confidence to LOW.
- Keep the fingerprint stable and coarse enough to preserve transaction statistics.

## Integrity and Ghost Signals

### Integrity formula
`FinalIntegrity = min(1.0, BaseIntegrity + MadmounBoost) * GateMultiplier`

Rules:
- `BaseIntegrity` ranges from 0.0 to 0.7.
- If Madmoun QR is absent or invalid, `GateMultiplier = 0.4`.
- If Madmoun QR resolves to valid Trakheesi and Media Council permits, `MadmounBoost = 0.3`.
- Cap integrity at 1.0.
- If `FinalIntegrity < 0.7`, the listing is suspicious and valuation is bypassed.

### Ghost signals
Track and surface signals such as:
- Duplicate images.
- Reused images across listings.
- Stale or stagnant listings.
- Invalid or missing permits.
- Agent/agency trust issues.
- Content or metadata collisions.

Ghost signals should influence integrity, not replace it.

## Valuation Rules

### Rolling window
- Use a 6-month rolling transaction window.
- Prefer building-level evidence first.
- Expand to project or area medians only when building-level evidence is insufficient.

### Confidence ladder
- `HIGH`: at least 8 building transactions, variance below 10%.
- `MEDIUM`: 3 to 7 building transactions, or at least 15 in the wider project/complex.
- `LOW`: fewer than 3 relevant transactions.
- Sharjah OCR/PDF data is capped at MEDIUM confidence unless a future policy explicitly changes it.

### Verdict ladder
Use mutually exclusive verdicts:
- `NON-COMPLIANT / SUSPICIOUS`
- `UNVERIFIED LOCATION`
- `DISTRESSED ASSET`
- `UNDERVALUED`
- `FAIR MARKET VALUE`
- `OVERPRICED`
- `DATA INSUFFICIENT`

Rules:
- Integrity failures override all valuation outcomes.
- Location uncertainty blocks valuation.
- A suspicious listing can never be “distressed” or “undervalued.”
- Valuation verdicts are only allowed after integrity passes.

## Matching and Disambiguation

When linking a listing to a building:

1. Exact match on `dld_building_id`.
2. Fuzzy name match within the same area using a similarity threshold above 85%.
3. If multiple candidates remain, compare coordinates and choose the closest.
4. If no coordinate evidence breaks the tie, halt with `UNVERIFIED LOCATION`.

Rules:
- Never assume tower suffixes, floor hints, or neighborhood phrasing are sufficient by themselves.
- Never force a match when multiple candidates remain plausible.
- Favor precision over recall.

## Agent Architecture Rules

### ScoutNode
Responsibilities:
- Scrape the listing.
- Extract DOM data.
- Capture media URLs.
- Extract permits and area details.
- Normalize area to SqFt.

Do not:
- Compute final integrity.
- Compute valuation.
- Decide verdicts.

### SkepticNode
Responsibilities:
- Compute image hashes.
- Check for image collisions.
- Verify compliance signals.
- Apply the integrity formula.
- Emit ghost signals.

Do not:
- Perform valuation.
- Override location uncertainty.
- Reclassify suspicious listings as undervalued.

### AnalystNode
Responsibilities:
- Match the listing to a building.
- Query transaction medians.
- Compute valuation metrics.
- Assign valuation confidence.

Do not:
- Ignore integrity results.
- Run valuation when location is unresolved.
- Change source truth records.

### ReporterNode
Responsibilities:
- Assemble the final PDF contract.
- Render the final report.
- Preserve the exact section order.

Do not:
- Recompute core business logic.
- Reorder decision sections.
- Suppress warnings or disclaimers.

## Graph State Conventions

Recommended state shape:

```ts
interface PropWatchState {
  listingUrl: string;
  rawHtml: string;
  listingData: ListingEntity | null;
  integrityScore: number;
  valuationData: ValuationMetrics | null;
  verdict: string;
  errors: string[];
}
```

Additional guidance:
- Keep state serializable.
- Avoid storing large binary objects in state.
- Store references to files or hashes instead of raw media whenever possible.
- Preserve errors as an array of actionable messages.

## Database Conventions

- Prefer UUID primary keys.
- Use explicit foreign keys.
- Index join keys and date fields used for medians.
- Store timestamps in UTC.
- Use generated columns only when the formula is stable and deterministic.
- Use JSONB only for semi-structured signal data that may expand later.
- Do not store chain-of-thought or hidden reasoning text in the database.

## Ingestion Conventions

- Treat each ingestion source as untrusted until normalized.
- Separate source adapters by portal or authority.
- Make parsers idempotent.
- Preserve raw payloads only when needed for audit or debugging.
- Normalize units, naming, and identifiers immediately after extraction.
- Detect and log malformed or partial records rather than silently repairing them.

## Reporting Conventions

The PDF output must use this exact structure:
1. Header.
2. Identity Block.
3. Verdict Card.
4. Transaction Ledger.
5. Integrity and Ghost Signals.
6. Disclaimer.

Presentation rules:
- Use Inter font family only.
- Keep the verdict highly visible.
- Display the last 3 relevant transactions for the exact fingerprint.
- Clearly surface permit and compliance status.
- Include a methodology disclaimer.
- Add a “Limited Data Source” watermark for Sharjah output when applicable.

## Coding Conventions

- Write TypeScript with strict typing.
- Prefer small, testable functions.
- Keep domain logic out of controllers.
- Put reusable business rules in services or pure utilities.
- Avoid implicit coercion.
- Validate inputs at boundaries.
- Use explicit return types for exported functions.
- Prefer descriptive names over clever abbreviations.
- Keep helper functions short and single-purpose.

## Error Handling Conventions

- Fail fast on missing critical inputs.
- Return explicit error states for unresolved location, missing permits, or unreadable source data.
- Never swallow exceptions in background jobs.
- Convert external failures into actionable domain errors.
- Log enough context to reproduce the failure without exposing secrets.

## Testing Conventions

Prioritize tests in this order:
1. Unit conversion and normalization.
2. Integrity gate math.
3. Unit fingerprinting.
4. Fuzzy matching and disambiguation.
5. Transaction median calculations.
6. Report rendering and layout stability.
7. End-to-end ghost listing detection.

Testing rules:
- Add regression tests for every logic gate change.
- Test both success and safe-failure paths.
- Include known bad listings and edge cases.
- Verify that report section order never changes accidentally.

## CLI and Build Conventions

- The MVP should be invocable through a CLI command.
- Keep commands deterministic and scriptable.
- Ensure worker tasks can be run independently from the API.
- Provide clear environment-variable configuration.
- Do not make manual browser steps required for normal usage.

## Security and Compliance Conventions

- Do not embed secrets in source code.
- Use environment variables or secrets management.
- Sanitize scraped inputs before storage or rendering.
- Treat portal content as untrusted.
- Be careful with copyrighted material in generated outputs.
- Preserve a clear audit trail for all computed findings.

## Documentation Conventions

When updating code:
- Update the spec if architecture or behavior changes.
- Keep README and AGENTS-style guidance consistent.
- Note any changes to thresholds, formulas, or verdict rules.
- Document migration steps when schema changes occur.

## When Unsure

If a task is ambiguous:
- Prefer the conservative interpretation.
- Preserve data integrity.
- Ask for clarification only when the ambiguity changes core behavior.
- Do not improvise on compliance, pricing, or location rules.
- Do not expand scope beyond the current phase unless explicitly requested.

## Final Reminder

This project is designed to be deterministic, conservative, and evidence-led. The assistant’s job is to preserve the truth model, protect the integrity gate, and keep the report output stable, professional, and decision-ready.