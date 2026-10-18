#!/usr/bin/env python3
"""Build descriptive market features from audited saved data; never fetch anew.

This is a retrospective END-OF-DAY feature preparation step, not a
pseudo-real-time forecast experiment and not a completed latent-risk factor.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

import pandas as pd

from latent_risk.data.market_features import (
    EQUITY_BY_COUNTRY,
    FX_BY_COUNTRY,
    STRESS_REFERENCES,
    build_country_market_panel,
)
from latent_risk.data.quality import inspect_source_file, latest_successful_records


def _git_sha(root: Path) -> str | None:
    """Retrieve current code commit without requiring Git availability."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, check=True,
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def prepare_market_pilot(snapshots: Path, output: Path, root: Path) -> dict:
    """Create source-verified derivative features in a new immutable local directory.

    Parameters
    ----------
    snapshots : pathlib.Path
        Directory containing existing timestamped raw-download snapshots.
    output : pathlib.Path
        New path under ignored data/processed, which must not exist yet.
    root : pathlib.Path
        Repository root for code commit identification.

    Returns
    -------
    dict
        Derived-file checksums, source hashes, coverage and research limitations.

    Raises
    ------
    ValueError
        For missing sources, failed CSV integrity checks, invalid close prices,
        or no common country dates.
    FileExistsError
        If output already exists; old derived runs are never overwritten.
    """
    names = set(EQUITY_BY_COUNTRY.values())
    names.update(item[0] for item in FX_BY_COUNTRY.values())
    required = {("market", symbol) for symbol in names} | set(STRESS_REFERENCES)
    sources = {
        (str(record["source"]), str(record["id"])): (folder, record)
        for folder, record in latest_successful_records(snapshots)
    }
    missing = required - set(sources)
    if missing:
        raise ValueError(f"missing downloaded series: {sorted(missing)}")

    frames = {}
    ref_frames = []
    evidence = []
    for source, identifier in sorted(required):
        folder, record = sources[(source, identifier)]
        quality = inspect_source_file(folder, record)
        if quality["status"] != "PASS":
            raise ValueError(
                f"integrity check failed for {source}/{identifier}: {quality['errors']}"
            )
        path = folder / str(record["path"])
        frame = pd.read_csv(path, low_memory=False)
        if source == "market":
            frames[identifier] = frame
        else:
            dt = pd.to_datetime(
                frame["observation_date"], format="%Y-%m-%d", errors="raise",
            )
            if (dt.duplicated().any() or not dt.is_monotonic_increasing
                    or frame.empty):
                raise ValueError(f"external reference has invalid dates: {identifier}")
            country = STRESS_REFERENCES[(source, identifier)]
            out = frame[["observation_date", "value"]].copy()
            out.insert(0, "country", country)
            out.insert(1, "provider", source)
            out.insert(2, "series_id", identifier)
            ref_frames.append(out)
        evidence.append({
            "source": source,
            "id": identifier,
            "role": record.get("role"),
            "snapshot": folder.name,
            "source_sha256": record["sha256"],
            "rows": record["n_rows"],
        })

    country, common = build_country_market_panel(frames)
    refs = pd.concat(ref_frames, ignore_index=True).sort_values(
        ["country", "series_id", "observation_date"],
    ).reset_index(drop=True)

    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing derived directory: {output}")
    output.mkdir(parents=True)
    files = {
        "country_market_features.csv": country,
        "five_country_common_equity_dates.csv": common,
        "external_stress_references.csv": refs,
    }
    products = {}
    for name, frame in files.items():
        path = output / name
        frame.to_csv(path, index=False, date_format="%Y-%m-%d")
        products[name] = {
            "rows": len(frame),
            "sha256": sha256(path.read_bytes()).hexdigest(),
            "first_observation": str(frame["observation_date"].min())[:10],
            "last_observation": str(frame["observation_date"].max())[:10],
        }
    manifest = {
        "schema_version": 1,
        "status": "DESCRIPTIVE_MARKET_FEATURES_NO_FORECAST",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_sha(root),
        "feature_rules": {
            "equity_vol_window": 21,
            "equity_drawdown_window": 63,
            "fx_vol_window": 21,
            "equity_vol_units": "sample std of daily log returns, NOT annualized",
            "country_fx_direction": {
                country: direction for country, (_, direction) in FX_BY_COUNTRY.items()
            },
            "calendar": "exact observation dates, no cross-source forward filling",
            "us_fx": "not defined: no fictitious USD/USD series",
            "oil": "CL=F excluded; signed price and contract-roll audit outstanding",
        },
        "input_sources": evidence,
        "outputs": products,
        "limitations": [
            "Current revised vendor snapshots, not point-in-time published vintages.",
            "Dates are market sessions; cross-timezone market-close availability not proven.",
            "Contemporaneous feature values require each market close to have occurred.",
            "No fit, factor estimation, standardization, forecast or event test performed.",
            "External published stress indices are NOT used as factor inputs.",
            "Cross-country equity intersection may omit national market holidays.",
            "Daily market sampling and rolling windows are counts of source observations.",
        ],
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    return manifest


def main() -> int:
    """Build a new source-checked local panel and print its true observation spans."""
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--snapshots", type=Path, default=root / "data/raw/downloads",
    )
    parser.add_argument(
        "--output-root", type=Path, default=root / "data/processed/market_pilot",
    )
    args = parser.parse_args()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output = args.output_root / timestamp
    try:
        manifest = prepare_market_pilot(args.snapshots, output, root)
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")

    for name, meta in manifest["outputs"].items():
        print(
            f"[OK] {name}: {meta['rows']} rows, "
            f"{meta['first_observation']} to {meta['last_observation']}"
        )
    print("RESULT MARKET_FEATURES_PREPARED_ONLY; no models fitted")
    print(f"Manifest: {(output / 'manifest.json').resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
