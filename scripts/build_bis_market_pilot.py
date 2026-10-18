#!/usr/bin/env python3
"""Produce a NEW retrospective BIS-NEER equity+FX market pilot from saved sources.

No downloads, raw edits, model fitting, forward filling or vintage fabrication.
The legacy bilateral-FX market_pilot/ output is not modified.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

import pandas as pd

from latent_risk.data.bis_market_features import (
    BIS_NEER_BY_COUNTRY,
    build_bis_market_panel,
)
from latent_risk.data.market_features import EQUITY_BY_COUNTRY, STRESS_REFERENCES
from latent_risk.data.quality import inspect_source_file, latest_successful_records


def _revision(root: Path) -> str | None:
    """Report Git HEAD if a local git client is installed."""
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, check=True, timeout=5,
            capture_output=True, text=True,
        ).stdout.strip()
    except (OSError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return None


def prepare_bis_market_pilot(
    snapshots: Path, destination: Path, *, root: Path,
) -> dict:
    """Prepare a provenance-stamped, append-only alternative FX pilot.

    Parameters
    ----------
    snapshots : pathlib.Path
        Local raw/downloads containing immutable source manifests.
    destination : pathlib.Path
        A new output folder under ignored data/processed/market_pilot_bis/.
        Refuses to overwrite any earlier version.
    root : pathlib.Path
        Repository root for code provenance.

    Returns
    -------
    dict
        SHA256 input/output provenance, exact feature rules, coverage and
        explicit limitations preventing real-time inference.

    Raises
    ------
    ValueError
        On unavailable source series, source corruption or missing dates.
    FileExistsError
        If the target directory already exists.
    """
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite existing version: {destination}")
    expected = (
        {("market", code) for code in EQUITY_BY_COUNTRY.values()}
        | {("bis", code) for code in BIS_NEER_BY_COUNTRY.values()}
        | set(STRESS_REFERENCES)
    )
    selected = {
        (row["source"], row["id"]): (folder, row)
        for folder, row in latest_successful_records(snapshots)
    }
    absent = expected - selected.keys()
    if absent:
        raise ValueError(f"missing validated source records: {sorted(absent)}")

    equities: dict[str, pd.DataFrame] = {}
    neer: dict[str, pd.DataFrame] = {}
    references: list[pd.DataFrame] = []
    input_provenance: list[dict] = []
    for source, identifier in sorted(expected):
        folder, record = selected[(source, identifier)]
        report = inspect_source_file(folder, record)
        if report["status"] != "PASS":
            raise ValueError(
                f"source {source}/{identifier} failed integrity audit: {report['errors']}"
            )
        data = pd.read_csv(folder / str(record["path"]), low_memory=False)
        if source == "market":
            equities[identifier] = data
        elif source == "bis":
            neer[identifier] = data
        else:
            country = STRESS_REFERENCES[(source, identifier)]
            out = data[["observation_date", "value"]].copy()
            out.insert(0, "series_id", identifier)
            out.insert(0, "provider", source)
            out.insert(0, "country", country)
            references.append(out)
        provenance = {
            "source": source,
            "id": identifier,
            "role": record.get("role"),
            "source_snapshot": folder.name,
            "source_sha256": record["sha256"],
            "rows": record["n_rows"],
        }
        if source == "bis":
            for key in (
                "bis_response_sha256", "bis_source_rows_in_window",
                "bis_missing_observation_count", "bis_missing_fraction",
            ):
                provenance[key] = record.get(key)
        input_provenance.append(provenance)
    country_panel, common_equity, common_full = build_bis_market_panel(
        equities, neer,
    )
    external = pd.concat(references, ignore_index=True).sort_values(
        ["country", "series_id", "observation_date"],
    ).reset_index(drop=True)
    destination.mkdir(parents=True, exist_ok=False)
    outputs = {}
    tables = {
        "country_bis_market_features.csv": country_panel,
        "five_country_common_equity_dates.csv": common_equity,
        "five_country_complete_neer_equity_dates.csv": common_full,
        "external_stress_references.csv": external,
    }
    for name, table in tables.items():
        path = destination / name
        table.to_csv(path, index=False, date_format="%Y-%m-%d")
        outputs[name] = {
            "rows": int(len(table)),
            "sha256": sha256(path.read_bytes()).hexdigest(),
            "first_observation": str(table["observation_date"].min())[:10],
            "last_observation": str(table["observation_date"].max())[:10],
        }
    coverage = {}
    for country, key in BIS_NEER_BY_COUNTRY.items():
        sub = country_panel.loc[country_panel.country == country]
        good = sub["neer_vol_21"].notna()
        coverage[country] = {
            "neer_series_id": key,
            "equity_rows": int(len(sub)),
            "neer_complete_rows": int(good.sum()),
            "neer_missing_rows": int((~good).sum()),
            "neer_coverage_fraction": round(float(good.mean()), 6),
        }
    manifest = {
        "schema_version": 2,
        "status": "DESCRIPTIVE_BIS_NEER_PILOT_NO_FORECAST",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "code_commit": _revision(root),
        "source_snapshots": str(snapshots.resolve()),
        "input_sources": input_provenance,
        "outputs": outputs,
        "coverage_by_country": coverage,
        "feature_rules": {
            "equity_vol_window": 21,
            "equity_drawdown_window": 63,
            "neer_vol_window": 21,
            "neer_depreciation_sign": "-Delta log(NEER): positive is depreciation",
            "neer_index_base": "2020=100",
            "neer_partner_weights": "BIS broad, trade-weighted, differs by country",
            "neer_vol_units": "std of source-observation log changes, not annualized",
            "date_alignment": "exact observed date only; no fill or interpolation",
            "common_equity_panel": "all-five equity dates only",
            "complete_panel": "all-five equity plus all-five NEER features",
            "supersedes_legacy": False,
        },
        "limitations": [
            "Retrospective, current revised BIS series not original daily public vintages.",
            "BIS daily observations released with periodic delays; not available at same-day origins.",
            "A single calendar date does not prove five exchange closes were contemporaneous.",
            "No data after an individual source observation enters rolling calculations.",
            "BIS return is since previous reported observation, possibly separated by holidays.",
            "Effective exchange-rate partner weights vary by country and may be revised.",
            "Separate external benchmarks are NOT predictors in the feature panel.",
            "No inferred latent financial stress factor, smoother, forecast or event test.",
            "Legacy USD-bilateral and DXY market pilot remains independent and unchanged.",
        ],
    }
    (destination / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    return manifest


def main() -> int:
    """Read validated raw source snapshots and create versioned BIS derivatives."""
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--snapshots", type=Path, default=root / "data/raw/downloads",
    )
    parser.add_argument(
        "--output-root", type=Path,
        default=root / "data/processed/market_pilot_bis",
    )
    args = parser.parse_args()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    destination = args.output_root / timestamp
    try:
        result = prepare_bis_market_pilot(args.snapshots, destination, root=root)
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    for name, meta in result["outputs"].items():
        print(
            f"[OK] {name}: {meta['rows']} rows, "
            f"{meta['first_observation']} to {meta['last_observation']}"
        )
    print("COUNTRY EQUITY_ROWS NEER_COMPLETE NEER_MISSING")
    for country, info in result["coverage_by_country"].items():
        print(
            f"{country:7} {info['equity_rows']:11} "
            f"{info['neer_complete_rows']:13} {info['neer_missing_rows']:12}"
        )
    print("RESULT BIS_NEER_PILOT_PREPARED_ONLY; no model fitted")
    print(f"Manifest: {(destination / 'manifest.json').resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
