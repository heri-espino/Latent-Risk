#!/usr/bin/env python3
"""Export exact observed coverage for catalogued sources on the user's VM.

This read-only command does not download any data, publish CSV observations,
or establish any real-time historical data availability.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from latent_risk.data.coverage import source_coverage

FIELDS = (
    "source", "country", "id", "role", "frequency_catalog", "units_catalog",
    "dataset_version_catalog", "status", "first_observation_date",
    "last_observation_date", "first_observation_year", "last_observation_year",
    "n_observations", "last_success_snapshot", "last_attempt_status",
    "csv_sha256", "response_sha256", "bis_missing_source_rows",
)


def main() -> int:
    """Run local integrity-gated coverage export with a nonzero failure status."""
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=root / "data/source_catalog.json")
    parser.add_argument("--snapshots", type=Path, default=root / "data/raw/downloads")
    parser.add_argument("--output", type=Path, default=root / "results/source_coverage.json")
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    rows = source_coverage(catalog, args.snapshots)
    counts = {
        status: sum(row["status"] == status for row in rows)
        for status in (
            "OK_FILE_VERIFIED", "FAILED_FILE_INTEGRITY",
            "FAILED_PROVIDER", "NEVER_REQUESTED"
        )
    }
    payload = {
        "schema_version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_kind": "LIVE_VM_LOCAL_MANIFEST_AUDIT_NOT_OFFLINE_TEST",
        "counts": counts,
        "limitations": [
            "Observed dates are not release dates or historical first-release vintages.",
            "Catalog units and frequencies are not confirmed from live metadata.",
            "Provider license/redistribution and dataset revisions require separate review.",
            "Source quality and SHA256 do not establish financial-stress inference.",
        ],
        "series": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    csv_path = args.output.with_suffix(".csv")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        print(
            f"{row['source']:7} {row['country']:6} {row['id'][:37]:37} "
            f"{row['status']:21} "
            f"{row['first_observation_date'] or '-':10} "
            f"{row['last_observation_date'] or '-':10} "
            f"{row['n_observations'] if row['n_observations'] is not None else '-'}"
        )
    print(f"SUMMARY {counts}")
    print(f"JSON: {args.output}; CSV: {csv_path}")
    return 1 if counts["FAILED_FILE_INTEGRITY"] or counts["FAILED_PROVIDER"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
