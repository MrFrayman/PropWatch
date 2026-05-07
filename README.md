# PropWatch UAE

PropWatch is a work in progress.

It started as a simple idea: if property listings can be checked against real evidence, then it should be easier to spot suspicious listings, normalize messy data, and get a clearer picture of what is actually being offered in Dubai and Sharjah.

That is the direction of the project. It is still being built.

## What this project is

PropWatch is an investor-oriented property intelligence system.

The core idea is to bring together:
- raw listing data,
- transaction evidence,
- building-level context,
- and verification signals,

then organize all of that into something easier to inspect than a normal listing page.

The project is being designed conservatively. If the data is weak, incomplete, or inconsistent, the system should reflect that instead of smoothing it over.

## Why I am building it

This project is mainly about building something useful and learning while doing it.

Real estate data tends to be messy in ways that are easy to underestimate:
- area values are not always consistent,
- listings can drift from the actual building or unit,
- verification signals may be missing,
- and pricing can look reasonable until it is checked against the right baseline.

PropWatch is my attempt to build a system that takes those problems seriously.

## Current state

The project is still under active development.

Right now, the focus is on the backend foundation:
- source adapters,
- ingestion,
- normalization,
- matching,
- fingerprinting,
- integrity checks,
- and verdict logic.

The frontend exists only as a working surface for now. It is intentionally plain. I am not trying to make it look finished before the system underneath is actually solid.

## What it is supposed to do

Eventually, PropWatch should be able to:
- pull in listing data from the relevant sources,
- normalize area and price fields,
- compare listings with building-level and transaction-level evidence,
- flag suspicious or low-trust listings,
- and generate a report that makes the result easier to review.

Nothing about that is meant to be flashy. The point is to be useful and reliable.

## Project shape

The current architecture is built around a pipeline:

1. Ingest raw data.
2. Normalize it.
3. Match it to buildings and units.
4. Check trust and integrity signals.
5. Compare pricing against evidence.
6. Compose a final verdict.
7. Present the result in a report.

That is the shape of the system I am building right now.

## Tech stack

This is the stack I am using for the project right now:

- **Backend:** Python, FastAPI.
- **Database:** PostgreSQL.
- **Frontend:** React-based frontend in progress.
- **Validation / data modeling:** Pydantic-style models and typed Python code.
- **Reporting:** PDF generation for final inspection reports.
- **Development style:** modular services, clear separation between ingestion, normalization, matching, and reporting.

The stack may evolve as the project matures, but this is the current direction.

## Design rules

A few things matter a lot in this project:

- Prefer correctness over cleverness.
- Prefer explicit code over hidden behavior.
- Prefer conservative judgments over optimistic guesses.
- If something is uncertain, say it is uncertain.

Those rules are the reason PropWatch exists in the first place.

## Status note

This repository is not a polished product. It is a build in progress.

Some parts may be incomplete, some may be rough, and some may change as I learn more and refine the design. That is expected.

## If you are looking around the repo

The best place to start is usually the data model and the ingestion pipeline. That is where the project becomes real.

The rest of the system makes more sense once those pieces are in place.
