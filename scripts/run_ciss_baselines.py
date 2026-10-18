#!/usr/bin/env python3
"""Run EXP-0002: retrospective, observation-index ECB CISS baselines.

Uses the external reference CSV already prepared in a market_pilot snapshot.
No original historical CISS vintages are available. This evaluates numerical
forecast mechanics only; it is NOT a real-time financial-crisis warning test.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

import pandas as pd

from latent_risk.data.ciss_baselines import (
    CISS_COUNTRIES,
    aggregate_forecast_scores,
    evaluate_ciss_series,
)


def _code_revision(repo: Path) -> str | None:
    """Return current source SHA if the Git executable is available."""
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, check=True,
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def run_ciss_baseline(
    pilot: Path,
    destination: Path,
    *,
    start: str,
    horizons: tuple[int, ...] = (1, 5, 21),
    stride: int = 21,
    root: Path,
) -> dict:
    """Fit three matched CISS forecast baselines using an immutable pilot.

    Parameters
    ----------
    pilot : pathlib.Path
        Previously generated market-pilot folder, containing separated
        external references and a SHA256-derived output manifest.
    destination : pathlib.Path
        New run destination which must not already exist.
    start : str
        First outer evaluation origin date.
    horizons : tuple of int
        CISS observation-step horizons.
    stride : int
        Outer evaluation origin spacing in source observations.
    root : pathlib.Path
        Repository path to annotate code provenance.

    Returns
    -------
    dict
        Run provenance and derived output checksums with scientific limits.

    Raises
    ------
    ValueError
        If a source checksum, identity or training history is invalid.
    FileExistsError
        If the destination already exists.
    """
    meta = json.loads((pilot / "manifest.json").read_text(encoding="utf-8"))
    if meta.get("status") != "DESCRIPTIVE_MARKET_FEATURES_NO_FORECAST":
        raise ValueError("source pilot has wrong manifest status")
    filename = "external_stress_references.csv"
    original = pilot / filename
    if sha256(original.read_bytes()).hexdigest() != meta["outputs"][filename]["sha256"]:
        raise ValueError("external reference source checksum mismatch")
    refs = pd.read_csv(original)
    if not {"series_id", "country", "provider", "observation_date", "value"} <= set(refs):
        raise ValueError("source reference table missing required columns")
    series = set(refs["series_id"])
    if not set(CISS_COUNTRIES) <= series:
        raise ValueError("one or more ECB CISS series missing")
    frames = []
    for code, country in CISS_COUNTRIES.items():
        segment = refs.loc[refs.series_id == code].copy()
        if (not segment["provider"].eq("ecb").all()
                or not segment["country"].eq(country).all()):
            raise ValueError(f"unexpected CISS series identity for {code}")
        predictions = evaluate_ciss_series(
            segment, start=start, horizons=horizons, stride=stride,
        )
        predictions.insert(0, "country", country)
        predictions.insert(1, "series_id", code)
        frames.append(predictions)
    output = pd.concat(frames, ignore_index=True)
    scores = aggregate_forecast_scores(output)
    if destination.exists():
        raise FileExistsError(f"run directory already exists: {destination}")
    destination.mkdir(parents=True)
    products = {}
    for name, data in (
        ("origin_predictions.csv", output),
        ("matched_model_scores.csv", scores),
    ):
        path = destination / name
        data.to_csv(path, index=False)
        products[name] = {
            "rows": len(data),
            "sha256": sha256(path.read_bytes()).hexdigest(),
        }
    result = {
        "id": "EXP-0002",
        "status": "EXPLORATORY_RETROSPECTIVE_CISS_BASELINES",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "code_commit": _code_revision(root),
        "source_pilot": str(pilot.resolve()),
        "source_reference_sha256": meta["outputs"][filename]["sha256"],
        "config": {
            "start_origin_date": start,
            "horizons_CISS_observations": list(horizons),
            "outer_stride_observations": stride,
            "min_train_observations": 504,
            "ewma_candidates": [0.05, 0.1, 0.25, 0.5, 0.85, 1.0],
            "inner_cv_max_training_window": 504,
            "inner_cv_min_train": 252,
            "inner_stride": 21,
            "ewma_prediction_last_window": 252,
            "ar1_ols_fit_window": 504,
            "models": ["persistence", "ewma_nested_cv", "ar1_ols"],
            "seed": None,
        },
        "outputs": products,
        "limitations": [
            "Observation-step chronological backtest on current-vintage CISS values.",
            "Historical CISS release dates, revisions and publication times NOT checked.",
            "Horizon 21 means 21 reported CISS observations, not 21 calendar days.",
            "No estimation of our own latent index or penalized-least-squares smoothing model.",
            "Nested CV tunes EWMA gains within each outer origin; event windows not held out.",
            "No standard error, crisis classification, false-alarm comparison or inference.",
            "CISS is benchmark as the forecasted target here; no market inputs used.",
        ],
    }
    (destination / "manifest.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    return result


def main() -> int:
    """Dispatch the first exploratory, reproducible CISS forecasting study."""
    repo = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pilot-root", type=Path, default=repo / "data/processed/market_pilot",
    )
    parser.add_argument("--pilot-dir", type=Path, default=None)
    parser.add_argument(
        "--output-root", type=Path, default=repo / "results/runs/EXP-0002",
    )
    parser.add_argument("--start", default="2008-01-01")
    parser.add_argument("--horizons", default="1,5,21")
    parser.add_argument("--stride", type=int, default=21)
    args = parser.parse_args()
    try:
        choices = sorted(args.pilot_root.glob("*/manifest.json"))
        if args.pilot_dir is None and not choices:
            raise FileNotFoundError("No market pilot folder exists")
        source = args.pilot_dir or choices[-1].parent
        h = tuple(int(x) for x in args.horizons.split(","))
        run = args.output_root / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        result = run_ciss_baseline(
            source, run, start=args.start, horizons=h, stride=args.stride, root=repo,
        )
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    print("RESULT EXPLORATORY_CISS_BASELINES; NOT A REAL-TIME CRISIS TEST")
    print(f"Forecast rows: {result['outputs']['origin_predictions.csv']['rows']}")
    print(f"Score rows: {result['outputs']['matched_model_scores.csv']['rows']}")
    print(f"Manifest: {(run / 'manifest.json').resolve()}")
    print("Use matched_model_scores.csv for RMSE/MAE; no claim of predictive significance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
