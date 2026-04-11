# PropWatch UAE: Master Technical Specification & Project Plan  
**Document Version:** 1.0 Final Locked Spec  
**Target Market:** Dubai (Primary API) and Sharjah (Secondary OCR/PDF)  
**Core Design Principle:** Pessimistic Verification and Investor-First Due Diligence

This document is the authoritative source of truth for the architecture, data model, business logic, and implementation phases of the PropWatch engine. Every operational boundary, fallback, and edge case has been hardened into this blueprint so the system can produce deterministic, conservative, and investor-safe outputs.

## 1. Product Purpose

PropWatch UAE is an autonomous property intelligence and due-diligence system that detects ghost listings, normalizes pricing, and exposes value asymmetry in Dubai and Sharjah. The product exists to help an investor determine whether a listing is real, compliant, underpriced, fairly priced, overvalued, or too unreliable to trust. The system prioritizes evidence quality over marketing polish, and it should fail safely whenever location, permit, or transaction confidence is insufficient.

The product is intentionally conservative. A suspicious or unverified listing must never be “rescued” by attractive pricing, and Sharjah support must be treated as best-effort lower-confidence ingestion rather than equivalent to Dubai’s primary data path.

## 2. System Architecture

The system uses a modular monolith design, with clear internal boundaries that allow future microservice extraction without adding unnecessary complexity to the first build. The architecture is optimized for speed of execution, deterministic domain logic, and strong separation between ingestion, verification, valuation, and reporting.

### 2.1 Core Stack

- **Backend Framework:** NestJS v10+.
- **Orchestration Engine:** LangGraph via `@langchain/langgraph`.
- **Database Engine:** PostgreSQL 16+.
- **Vector Extension:** `pgvector` reserved for future semantic search, not required for v1 decisioning.
- **Queue and Cache:** Redis 7+ with BullMQ.
- **Scraping and Reporting Engine:** Playwright or Puppeteer.
- **Reporting Presentation:** Next.js 15 with Server Components, or pure HTML/CSS templates rendered with Puppeteer.
- **Typography Standard:** Inter family only, for consistent professional output.

NestJS is selected for its TypeScript discipline, dependency injection model, and clean compatibility with BullMQ-based workers. LangGraph is used to manage the cyclical, stateful workflow between scouting, skepticism, valuation, and reporting.

### 2.2 Dockerized Infrastructure

The complete local and production environment is standardized using Docker Compose.

- `propwatch-api`: NestJS core process.
- `propwatch-worker`: Separate NestJS worker consuming BullMQ queues for scraping and LangGraph tasks.
- `propwatch-db`: PostgreSQL database instance.
- `propwatch-redis`: Redis instance.

The API process should never perform long-running crawling or PDF generation synchronously. Those tasks belong in the worker tier to preserve responsiveness, isolate failures, and support horizontal scaling later.

## 3. Domain Model

The database is designed around the “Two-Column Audit” rule and a strict separation between historical truth and volatile marketing data. Historical transaction facts are canonical; portal listings are ephemeral and must always be treated as external claims awaiting verification.

### 3.1 Geographic and Truth Anchors

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE buildings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dld_building_id VARCHAR(100) UNIQUE,
    name_en VARCHAR(255) NOT NULL,
    area_name_en VARCHAR(150) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    total_floors INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (name_en, area_name_en)
);

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    building_id UUID REFERENCES buildings(id) ON DELETE CASCADE,
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    procedure_name_en VARCHAR(100) NOT NULL,
    reg_type_id VARCHAR(50) NOT NULL,

    source_area DECIMAL(10, 2) NOT NULL,
    source_unit VARCHAR(10) DEFAULT 'sqm',
    canonical_area_sqft DECIMAL(10, 2) NOT NULL,

    actual_worth DECIMAL(15, 2) NOT NULL,
    price_per_sqft DECIMAL(15, 2) GENERATED ALWAYS AS (actual_worth / canonical_area_sqft) STORED,

    property_type_en VARCHAR(50),
    rooms INT,
    instance_date DATE NOT NULL,
    is_off_plan BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_transactions_building_date ON transactions(building_id, instance_date);
```

`buildings` is the structural anchor for location and identity. `transactions` is the truth layer for valuation and must retain both the raw imported area and the normalized canonical area, so future re-normalization is always possible.

### 3.2 Volatile Market Layer

```sql
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    building_id UUID REFERENCES buildings(id),
    external_portal_id VARCHAR(100) UNIQUE NOT NULL,
    portal_source VARCHAR(50) NOT NULL,
    url TEXT NOT NULL,

    asking_price DECIMAL(15, 2) NOT NULL,
    listed_area_sqft DECIMAL(10, 2) NOT NULL,
    bedroom_count INT,

    agent_name VARCHAR(255),
    agency_name VARCHAR(255),
    madmoun_qr_url TEXT,
    trakheesi_permit VARCHAR(100),
    media_council_permit VARCHAR(100),

    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE inferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    listing_id UUID REFERENCES listings(id) ON DELETE CASCADE,
    unit_fingerprint VARCHAR(255) NOT NULL,

    base_integrity_score DECIMAL(3, 2),
    madmoun_coefficient DECIMAL(3, 2),
    final_integrity_score DECIMAL(3, 2) NOT NULL,
    ghost_signals JSONB,

    building_median_psf DECIMAL(15, 2),
    price_deviation_pct DECIMAL(5, 2),
    valuation_confidence VARCHAR(20),

    final_verdict VARCHAR(50) NOT NULL,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

`listings` stores raw portal claims and may remain unlinked until matching succeeds. `inferences` stores the outcome of the engine’s reasoning, including integrity and valuation outputs, and must never overwrite the source listing record.

### 3.3 Schema Policy Notes

The schema must support these rules:

- Store raw source values and canonical normalized values together.
- Preserve origin metadata for every imported transaction and listing.
- Keep valuation outputs separate from listing claims.
- Keep `ghost_signals` flexible via JSONB, but expose the highest-value flags clearly in application logic.
- Track match confidence and match method explicitly in the application layer, even if not fully materialized in the first table draft.

These rules preserve auditability and make the system safe for later forensic review.

## 4. Unit Normalization and Fingerprinting

### 4.1 Canonical Conversion

The canonical pricing unit is SqFt. The conversion constant is:

\[
1 \text{ m}^2 = 10.7639 \text{ SqFt}
\]

All imported transaction areas from DLD or related sources must be normalized to SqFt before any valuation logic is executed. The raw source area must still be retained for audit purposes.

### 4.2 Unit Fingerprint

The unit fingerprint is a coarse identity bridge between live marketing data and historical transaction truth. The baseline fingerprint hash is:

`SHA256(building_id + "-" + bedroom_count + "-" + ROUND(canonical_area_sqft / 50) * 50)`

This fingerprint intentionally groups units into practical bands rather than over-fragmenting the data into false uniqueness. Height, view, and premium positioning may be recorded as soft narrative modifiers, but they do not change the fingerprint in v1.

### 4.3 Missing Area Rule

If area is missing from the listing, the fingerprint must degrade to an area-agnostic hash. That condition immediately drops valuation confidence to LOW and may halt valuation if no reliable building match exists.

## 5. Integrity Gate

The Skeptic Agent evaluates whether a listing is eligible for valuation at all. Integrity is not a soft signal; it is a hard gate, and the system must fail closed when compliance evidence is weak or missing.

### 5.1 Integrity Formula

The integrity calculation is defined as:

\[
\text{FinalIntegrity} = \min(1.0, \text{BaseIntegrity} + \text{MadmounBoost}) \times \text{GateMultiplier}
\]

### 5.2 Scoring Rules

- **Base Integrity:** Ranges from 0.0 to 0.7 and is derived from agency history, image uniqueness, and listing freshness.
- **Gate Multiplier:** If `madmoun_qr_url` is missing or invalid, `GateMultiplier = 0.4`.
- **Madmoun Boost:** If `madmoun_qr_url` resolves to valid Trakheesi and Media Council permits, `MadmounBoost = 0.3`.
- **Final Cap:** Integrity is capped at 1.0 after boosts are applied.

### 5.3 Hard Failure State

If `FinalIntegrity < 0.7`, the listing is immediately locked to `NON-COMPLIANT / SUSPICIOUS`. Valuation logic is bypassed entirely. This rule prevents a cheap but non-compliant listing from being mislabeled as a good deal.

### 5.4 Ghost Signals

Ghost signals are indicators of low trust or probable fraud. Examples include:

- Duplicate image collisions.
- Stale or stagnant listing age.
- Reused portal content.
- Agency history issues.
- Invalid or missing permit evidence.

Ghost signals must be reported clearly in the output PDF and should influence the integrity score, but they must not be disguised as valuation variables.

## 6. Valuation Logic

Valuation only occurs after integrity passes. The Analyst Agent queries the transactions table using a six-month rolling window and evaluates the listing against relevant transaction medians.

### 6.1 Confidence Ladder

- **HIGH Confidence:** `N >= 8` transactions in the same `building_id` and variance below 10%. Use the building median.
- **MEDIUM Confidence:** `3 <= N < 8` transactions in the same building, or `N >= 15` in the wider project/complex. Use building or project median.
- **LOW Confidence:** `N < 3` transactions. Fall back to area median.
- **Sharjah Limitation:** All Sharjah SRERD parsed data is artificially capped at MEDIUM confidence due to OCR/PDF ingestion limitations.

### 6.2 Valuation Outputs

Valuation should calculate:

- Building median PSF.
- Asking price deviation percentage.
- Confidence label.
- Final valuation verdict.

A valuation may only be presented if integrity has already passed the hard gate. If the location is unverified, valuation must be halted and the output must reflect that explicitly.

### 6.3 Verdict Ladder

The verdict system must be mutually exclusive and hierarchically ordered.

- `NON-COMPLIANT / SUSPICIOUS` if integrity fails.
- `UNVERIFIED LOCATION` if fuzzy matching cannot confirm the building.
- `DISTRESSED ASSET` if price is more than 15% below building median and integrity passes.
- `UNDERVALUED` if price is 5% to 15% below building median and integrity passes.
- `FAIR MARKET VALUE` if price is within ±5% of median and integrity passes.
- `OVERPRICED` if price is above median beyond the accepted band.
- `DATA INSUFFICIENT` if the system cannot safely determine valuation.

Integrity verdicts always override valuation verdicts.

## 7. Entity Resolution

Building matching must follow a conservative, stepwise disambiguation process. The engine should prefer certainty over coverage, and it must stop rather than guess when confidence is insufficient.

### 7.1 Matching Stages

1. **Exact Match:** Match on `dld_building_id` if exposed in the portal DOM.
2. **Fuzzy Name Match:** Apply Levenshtein similarity above 85% on `building_name_en` scoped to the same `area_name_en`.
3. **Coordinate Disambiguation:** If multiple candidates remain, compare GPS coordinates and choose the shortest Euclidean distance.
4. **Unresolved Tie:** If no GPS is available to break the tie, mark the state as `UNVERIFIED LOCATION` and halt valuation.

### 7.2 Collision Examples

High-rise towers with similar names, such as “Marina Tower 1” and “Marina Tower 2,” must be resolved using the strictest available evidence. The engine should never infer a building match solely from marketing copy if identity evidence remains ambiguous.

## 8. LangGraph Orchestration

The workflow operates as a strict cyclical graph with clear state transitions. The graph is designed to keep responsibility boundaries explicit and to prevent any single node from performing unrelated duties.

### 8.1 State Definition

```typescript
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

### 8.2 Node Responsibilities

#### ScoutNode
- Uses Playwright to extract DOM elements.
- Extracts image URLs.
- Extracts Trakheesi numbers.
- Converts listed area from m² to SqFt.
- Produces normalized structured listing data only.

#### SkepticNode
- Downloads listing images.
- Computes perceptual hashes.
- Checks Redis for image collisions.
- Verifies the Madmoun URL.
- Applies the integrity gate math.
- Emits integrity verdicts and ghost signals.

#### AnalystNode
- Executes the valuation query.
- Runs fuzzy matching logic.
- Calculates median PSF and price deviation.
- Produces valuation confidence and valuation verdicts only if integrity passed.

#### ReporterNode
- Compiles the final state into the PDF data contract.
- Never re-evaluates integrity or valuation logic.
- Serializes the approved result into the reporting layer.

### 8.3 Routing Rules

- If integrity score is below 0.7, route directly to ReporterNode with a suspicious verdict.
- If location matching fails, halt valuation and mark the state as unverified.
- If integrity passes, route to AnalystNode, then ReporterNode.

The graph must remain deterministic, with no hidden fallback branches that could override the hard safety gates.

## 9. Reporting Output

The minimum viable product is a command-line operation that generates a professional PDF due-diligence report. The PDF is not a decorative artifact; it is the tangible business output of the engine.

### 9.1 Execution Command

```bash
npm run generate:report -- --url="https://bayut.com/.../1234"
```

### 9.2 Presentation Standard

- **Font Family:** Inter only.
- **Headings:** Inter SemiBold 600.
- **Body:** Inter Regular 400.
- **Data Tables:** Inter Mono.
- **Tone:** Professional, strict, and evidence-driven.

### 9.3 PDF Structure

The report must follow this exact order:

1. **Header**
   - PropWatch logo.
   - Generation timestamp.
   - Target URL.

2. **Identity Block**
   - Exact matched building name.
   - DLD ID.
   - Unit fingerprint.
   - Unit descriptor such as `2BR-1200SQFT`.

3. **Verdict Card**
   - Full-width high-contrast summary box.
   - Final label such as `DISTRESSED ASSET` or `NON-COMPLIANT`.

4. **Transaction Ledger**
   - Last 3 actual DLD sales for the exact unit fingerprint.
   - Date.
   - Procedure.
   - SqFt price.

5. **Integrity and Ghost Signals**
   - Madmoun status.
   - Trakheesi status.
   - Media Council permit status.
   - Image collision warnings.
   - Other ghost signals.

6. **Disclaimer**
   - Methodology footprint.
   - Explicit note of the six-month valuation window.
   - “Limited Data Source” watermark if the property is in Sharjah.

### 9.4 Report Contract Rules

- Identity comes first so the user immediately knows what is being analyzed.
- Verdict comes early so the decision is visible immediately.
- Transaction evidence must be tabular and concise.
- Ghost and compliance evidence must be explicit, not buried.
- Sharjah output must visibly communicate reduced confidence.

## 10. Phase Plan

The roadmap is designed so that data integrity is proven before the UI and reporting layer are finalized.

### Phase 1: Data Bedrock, Week 1

**Goal:** Establish ground truth.

**Tasks:**
- Initialize the NestJS monolith and PostgreSQL container.
- Implement `TransactionIngestionService`.
- Download historical Dubai Pulse CSV data.
- Write the ingestion script with enforced m² to SqFt conversion.
- Write raw SQL queries to calculate building medians.
- Validate that canonical prices and transaction medians are correct before any portal scraping begins.

### Phase 2: Ingestion and Verification, Week 2

**Goal:** Automate market reading and integrity checking.

**Tasks:**
- Set up BullMQ and Redis.
- Implement ScoutNode to scrape a single Bayut or Dubizzle URL.
- Implement SkepticNode.
- Add Madmoun QR parsing.
- Implement the capped coefficient integrity logic.
- Test image hashing and collision detection.

### Phase 3: Agentic Orchestration and Valuation, Week 3

**Goal:** Connect the logic gates.

**Tasks:**
- Implement the LangGraph StateGraph.
- Build AnalystNode.
- Implement fuzzy matching and building resolution.
- Query the Phase 1 database for the six-month median.
- Enforce the conflict-resolution policy where integrity overrides valuation.

### Phase 4: Output Layer, Week 4

**Goal:** Generate the final report artifact.

**Tasks:**
- Design the HTML template using Inter fonts.
- Implement ReporterNode with Puppeteer PDF generation.
- Finalize CLI scaffolding.
- Run test sweeps against known ghost listings.
- Confirm that suspicious listings are correctly blocked and that report layout remains stable.

## 11. Operational Guardrails

The following rules are mandatory across the entire system:

- The system must fail safely when evidence is missing.
- Integrity must always precede valuation.
- Sharjah must be explicitly labeled as lower-confidence unless future data quality improves.
- Canonical valuation math must use SqFt only.
- Raw source values must always be retained.
- Building matching must be conservative.
- No hidden AI reasoning output should be stored as database truth.
- ReporterNode must never alter underlying decisions.
- Any unresolved location or compliance issue must block valuation.

## 12. Final Acceptance Criteria

The system is acceptable only if it can do all of the following:

- Normalize Dubai transaction data into canonical SqFt values correctly.
- Match listings to buildings with conservative confidence rules.
- Detect suspicious listings through integrity signals.
- Block valuation when compliance or location evidence is insufficient.
- Produce a deterministic, professional PDF report with the exact required hierarchy.
- Support Sharjah OCR/PDF ingestion as best-effort with explicit lower-confidence handling.
- Preserve the full audit trail from raw source to final verdict.