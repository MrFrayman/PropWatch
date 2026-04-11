# PropWatch UAE

A property intelligence engine for Dubai and Sharjah that tells you whether a listing is real, compliant, and fairly priced — or whether you should walk away. The output is a PDF due-diligence report you can actually act on.

---

## Quick Intro

This is not a property search app. It does not help you browse listings. What it does is take a single listing URL, run it through a pipeline of verification and valuation logic, and spit out a structured PDF that answers three questions:

1. Is this listing real and compliant?
2. Is the price defensible against actual transaction history?
3. If either of those fails, why?

The system is intentionally pessimistic. A cheap listing does not get a free pass. If permits are missing or the building can't be matched confidently, valuation stops and the report says so clearly.

---

## What It Actually Does

### The pipeline

A listing URL goes through four sequential nodes, orchestrated by a LangGraph state graph:

**ScoutNode** scrapes the listing with Playwright, extracts DOM data, captures media URLs, pulls permit numbers, and normalizes the listed area from m² to SqFt (the canonical unit for everything downstream).

**SkepticNode** is where trust gets earned or denied. It computes perceptual hashes of listing images and checks them against Redis for collision with other listings, verifies the Madmoun QR code, checks Trakheesi and Media Council permit validity, and runs the integrity formula:

```
FinalIntegrity = min(1.0, BaseIntegrity + MadmounBoost) × GateMultiplier
```

If `FinalIntegrity < 0.7`, the listing is locked as `NON-COMPLIANT / SUSPICIOUS` and nothing else runs. That's a hard stop, not a soft warning.

**AnalystNode** only runs if integrity passed. It matches the listing to a verified building record (exact DLD ID first, then fuzzy name match above 85% similarity, then coordinate proximity), queries six months of actual DLD transaction history for comparable units using a coarse fingerprint, and produces a valuation verdict from this ladder:

- `NON-COMPLIANT / SUSPICIOUS`
- `UNVERIFIED LOCATION`
- `DISTRESSED ASSET`
- `UNDERVALUED`
- `FAIR MARKET VALUE`
- `OVERPRICED`
- `DATA INSUFFICIENT`

**ReporterNode** compiles the approved state into a PDF using a fixed section order: Header → Identity Block → Verdict Card → Transaction Ledger → Integrity & Ghost Signals → Disclaimer. The section order is not configurable and never gets reshuffled.

### The unit fingerprint

This part was tricky. Linking a live portal listing to historical DLD transaction records is hard because the data comes from completely different sources with inconsistent naming. The solution is a coarse fingerprint:

```
SHA256(building_id + "-" + bedroom_count + "-" + ROUND(canonical_area_sqft / 50) * 50)
```

The 50 SqFt bucketing is intentional — it groups similar units together rather than fragmenting the transaction pool into single-record slices that produce useless medians. View, floor level, and premium narration are deliberately excluded.

### Sharjah support

Dubai has proper API access through Dubai Pulse. Sharjah data comes from OCR and PDF parsing, which is noisier. All Sharjah output is capped at `MEDIUM` confidence, and the PDF gets a visible "Limited Data Source" watermark. This is not a temporary workaround — it's the policy until the data quality situation improves.

---

## How to Run It

### Prerequisites

- Docker and Docker Compose
- Node.js (for local dev outside Docker)

### Start the infrastructure

```bash
docker-compose up -d
```

This starts four containers: `propwatch-api` (NestJS), `propwatch-worker` (BullMQ consumer), `propwatch-db` (PostgreSQL 16), and `propwatch-redis` (Redis 7).

### Ingest transaction history

Before you can value anything, you need the DLD transaction data loaded. Download the Dubai Pulse CSV and run:

```bash
npm run ingest:transactions -- --file="path/to/dld-export.csv"
```

This normalizes all areas to SqFt and loads the building and transaction records. Don't skip this — the valuation logic has nothing to query against without it.

### Generate a report

```bash
npm run generate:report -- --url="https://bayut.com/.../1234"
```

The PDF lands in the `reports/` output directory. That's it.

### Environment variables

Copy `.env.example` to `.env` and fill in:

```
DATABASE_URL=
REDIS_URL=
MADMOUN_API_KEY=        # if applicable
```

No secrets in source code, no manual browser steps required.

---

## Why I Built This

The UAE property market, especially Dubai, has a real ghost listing problem. Portals are full of listings with recycled photos, expired permits, inflated prices, and no verifiable connection to an actual available unit. As someone looking at the market from an investor perspective, I got tired of not being able to quickly tell a genuine listing from a fabricated one.

There are tools that show you transaction data, and there are tools that aggregate listings. Nothing I found combined both in a way that explicitly blocked valuation when compliance signals were weak. The default assumption everywhere else seems to be "show the listing, maybe caveat it lightly." I wanted the opposite: assume the listing is suspicious until it proves otherwise.

I also wanted a paper trail. The PDF output is not decorative — it's the thing you can actually refer back to when making or defending a decision.

---

## Tech Stack Summary

| Layer | Technology |
|---|---|
| Backend | NestJS v10+ (TypeScript, strict mode) |
| Orchestration | LangGraph via `@langchain/langgraph` |
| Database | PostgreSQL 16+ |
| Queue / Cache | Redis 7+ with BullMQ |
| Scraping | Playwright or Puppeteer |
| PDF rendering | Puppeteer + HTML/CSS templates |
| Typography | Inter (all weights, all output) |

---

## License

MIT. Use it, fork it, adapt it. If you find a ghost listing with it, that's the point.