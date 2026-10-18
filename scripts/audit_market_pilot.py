#!/usr/bin/env python3
"""Audit latest local derived market pilot and print numerical coverage.

No downloads, model estimation, forecasting or release-date assumptions occur.
The selected source derivatives and their original manifest remain unchanged.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from latent_risk.data.market_diagnostics import audit_market_pilot


def main() -> int:
    """Validate one saved market pilot and write ignored diagnostic summary."""
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pilot-root", type=Path, default=root / "data/processed/market_pilot",
    )
    parser.add_argument(
        "--pilot-dir", type=Path, default=None,
        help="Explicit generated pilot directory; default is latest by name",
    )
    parser.add_argument(
        "--output", type=Path,
        default=root / "results/runs/market_diagnostics/summary.json",
    )
    args = parser.parse_args()
    try:
        if args.pilot_dir is not None:
            selected = args.pilot_dir
        else:
            choices = sorted(args.pilot_root.glob("*/manifest.json"))
            if not choices:
                raise FileNotFoundError("No generated market-pilot manifest found")
            selected = choices[-1].parent
        result = audit_market_pilot(selected)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")

    print(f"Input pilot: {selected.resolve()}")
    print(f"Country feature rows: {result['country_market_rows']}")
    eq = result["common_five_equity_dates"]
    print(f"Common equity dates: {eq['count']} ({eq['start']} to {eq['end']})")
    print(f"External reference observations: {result['reference_rows']}")
    print("COUNTRY EQUITY_ROWS FX_ROWS_PRESENT FX_ROWS_MISSING")
    for country, row in result["country"].items():
        miss = "NOT_APPLICABLE" if row["fx_missing_rows"] is None else str(
            row["fx_missing_rows"]
        )
        print(f"{country:7} {row['rows']:11} {row['fx_complete_rows']:15} {miss}")
    print("EXTERNAL REFERENCES (same-date overlap, not forecast-origin availability)")
    for code, row in result["external_reference_overlap"].items():
        print(f"{code}: {row['market_same_date_overlap']} same-date overlaps")
    print("RESULT DESCRIPTIVE_COVERAGE_DIAGNOSTIC_ONLY; no model fitted")
    print(f"Report: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
