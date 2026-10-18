#!/usr/bin/env python3
"""Audit immutable downloaded CSVs before constructing research features.

This command reads all local manifests and successfully downloaded files. It
never modifies raw data, and writes a report only under ignored results/runs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from latent_risk.data.quality import audit_source_integrity


def main() -> int:
    """Run integrity checks and summarize failures to the PowerShell console."""
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshots", type=Path, default=root / "data/raw/downloads")
    parser.add_argument(
        "--output", type=Path, default=root / "results/runs/source_quality/report.json",
    )
    args = parser.parse_args()
    try:
        result = audit_source_integrity(args.snapshots)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")

    print(f"{'SOURCE':8} {'IDENTIFIER':37} {'STATUS':7} {'ROWS':8} WARNINGS")
    for row in result["series"]:
        issues = "; ".join(row["errors"] or row["warnings"])
        print(
            f"{row['source']:8} {row['id'][:37]:37} {row['status']:7} "
            f"{row.get('rows', 0):8} {issues}"
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"\nQuality audit: {result['passes']}/{result['series_audited']} passed, "
        f"{result['failures']} failed, {result['warnings']} with warnings."
    )
    print(f"Report: {args.output.resolve()}")
    return 1 if result["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
