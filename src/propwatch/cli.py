# Expose a simple CLI command so you can manually run ingestion while developing.
# Keep this orchestration thin; the real logic should stay in the adapter, normalization, matching, and validation modules.

import argparse
import sys

from propwatch.services.ingestion import IngestionService


def main():
    parser = argparse.ArgumentParser(description="PropWatch Developer CLI")
    subparsers = parser.add_subparsers(dest="command")

    ingest_parser = subparsers.add_parser("ingest", help="Run data ingestion")
    ingest_parser.add_argument(
        "source", choices=["dubai", "sharjah"], help="Source of the data to ingest"
    )

    args = parser.parse_args()

    if args.command == "ingest":
        service = IngestionService()
        try:
            results = service.run(args.source)
            print("--- Ingestion Complete ---")
            print(f"Processed {len(results)} records from {args.source}.")
            for r in results[:3]:
                print(
                    f"    [Record] Price: {r.asking_price} | Area: {r.area_normalized} SqFt"
                )
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
