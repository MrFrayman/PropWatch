# PropWatch UAE

A property intelligence engine for Dubai and Sharjah that verifies whether a listing is real, compliant, and fairly priced, then compiles the findings into a PDF due-diligence report.

The project is a work in progress. Most of what's described here is the intended design; implementation is ongoing.

---

## The idea

The UAE property market, Dubai especially, has a ghost listing problem. Portals are full of listings with recycled photos, expired permits, inflated prices, and no verifiable connection to an actual available unit. There are tools that show transaction data, and tools that aggregate listings, but nothing that combines both and explicitly blocks valuation when compliance signals are weak. The default assumption everywhere seems to be: show the listing, maybe caveat it lightly.

PropWatch is built around the opposite assumption: treat the listing as suspicious until it proves otherwise.

---

## What it's designed to do

It takes a single listing URL, runs it through a pipeline of verification and valuation logic, and produces a structured PDF that answers two questions: is this listing real and compliant, and does the price hold up against actual transaction history.

This is not a property search tool. It won't help you browse listings or shortlist neighborhoods; it operates on one URL at a time and produces one report.

---

## Planned pipeline

Four nodes, intended to run in sequence.

**ScoutNode** will handle scraping: Playwright pulls the listing DOM, grabs media URLs, extracts permit numbers, and normalizes the listed area into SqFt. Everything downstream is designed to work in SqFt; that's the canonical unit throughout.

**SkepticNode** is where listings earn trust or don't. The plan is to run perceptual hashes on listing images and check for collisions in Redis, recycled photos being a classic ghost listing tell; verify the Madmoun QR code; and check Trakheesi and Media Council permit validity. All of that would feed into an integrity score:

```
FinalIntegrity = min(1.0, BaseIntegrity + MadmounBoost) × GateMultiplier
```

If the score comes back below 0.7, the listing gets flagged `NON-COMPLIANT / SUSPICIOUS` and the pipeline stops there. Hard stop, not a soft warning.

**AnalystNode** only runs if integrity passed. It's intended to match the listing to a verified DLD building record: exact ID first, then fuzzy name match above 85% similarity, then coordinate proximity as a last resort. Once the building is confirmed, it queries six months of DLD transaction history for comparable units and produces a verdict: `NON-COMPLIANT / SUSPICIOUS`, `UNVERIFIED LOCATION`, `DISTRESSED ASSET`, `UNDERVALUED`, `FAIR MARKET VALUE`, `OVERPRICED`, or `DATA INSUFFICIENT`.

**ReporterNode** compiles the approved state into a PDF with a fixed section order: Header, Identity Block, Verdict Card, Transaction Ledger, Integrity & Ghost Signals, Disclaimer.

---

## The fingerprint approach

Matching a live portal listing to DLD transaction records is hard because the data comes from completely different sources with inconsistent naming and no shared IDs. The intended solution is a coarse fingerprint:

```
SHA256(building_id + "-" + bedroom_count + "-" + ROUND(canonical_area_sqft / 50) * 50)
```

The 50 SqFt bucket is deliberate. Without it, transaction pools fragment into one or two records, and a median from two data points is meaningless. View, floor level, and agent narration are all excluded; those aren't data.

---

## Sharjah

Dubai has proper API access through Dubai Pulse; Sharjah doesn't, so that data would come from OCR and PDF parsing, which is noisier. All Sharjah output is intended to be capped at `MEDIUM` confidence, with a visible "Limited Data Source" watermark on the report. That's a policy decision, not a placeholder, and it stays until the underlying data quality actually improves.

---

## Intended stack

| Layer | Tech |
|---|---|
| Backend | NestJS v10+ (TypeScript, strict mode) |
| Orchestration | LangGraph via `@langchain/langgraph` |
| Database | PostgreSQL 16+ |
| Queue / Cache | Redis 7+ with BullMQ |
| Scraping | Playwright / Puppeteer |
| PDF rendering | Puppeteer + HTML/CSS templates |
| Typography | Inter, everything |

---

## License

MIT. Use it, fork it, adapt it.
