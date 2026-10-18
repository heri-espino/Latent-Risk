"""Offline coverage and integrity checks for derived market-pilot diagnostics."""
from __future__ import annotations

import json
from hashlib import sha256

import numpy as np
import pandas as pd
import pytest

from latent_risk.data.market_diagnostics import audit_market_pilot
from latent_risk.data.market_features import (
    EQUITY_BY_COUNTRY,
    FX_BY_COUNTRY,
    STRESS_REFERENCES,
    build_country_market_panel,
)


def _pilot(tmp_path):
    """Write a synthetic 5-country pilot with the real manifest schema."""
    n = 127
    prices = {
        sym: pd.DataFrame({
            "observation_date": pd.bdate_range("2020-01-01", periods=n).strftime(
                "%Y-%m-%d"
            ),
            "Close": 100.0 + np.arange(n) * 0.1,
        })
        for sym in {
            *EQUITY_BY_COUNTRY.values(),
            *(x[0] for x in FX_BY_COUNTRY.values()),
        }
    }
    long, common = build_country_market_panel(prices)
    refs = []
    dates = pd.bdate_range("2020-02-01", periods=15).strftime("%Y-%m-%d")
    for (provider, code), country in STRESS_REFERENCES.items():
        refs.append(pd.DataFrame({
            "country": country,
            "provider": provider,
            "series_id": code,
            "observation_date": dates,
            "value": np.linspace(0.1, 0.9, len(dates)),
        }))
    outputs = {
        "country_market_features.csv": long,
        "five_country_common_equity_dates.csv": common,
        "external_stress_references.csv": pd.concat(refs, ignore_index=True),
    }
    folder = tmp_path / "20261017T000000000000Z"
    folder.mkdir()
    manifest = {
        "status": "DESCRIPTIVE_MARKET_FEATURES_NO_FORECAST",
        "git_commit": "synthetic-sha",
        "input_sources": [
            {"source": provider, "id": code, "role": (
                "external_stress_benchmark" if provider == "ecb"
                or code == "STLFSI4" else "external_conditions_benchmark"
            )}
            for provider, code in STRESS_REFERENCES
        ],
        "outputs": {},
    }
    for name, frame in outputs.items():
        path = folder / name
        frame.to_csv(path, index=False, date_format="%Y-%m-%d")
        manifest["outputs"][name] = {
            "sha256": sha256(path.read_bytes()).hexdigest(),
            "rows": len(frame),
        }
    (folder / "manifest.json").write_text(json.dumps(manifest))
    return folder


def test_diagnostics_check_pilot_and_separate_stress_targets(tmp_path):
    pilot = _pilot(tmp_path)
    outcome = audit_market_pilot(pilot)
    assert outcome["common_five_equity_dates"]["count"] == 127 - 62
    assert outcome["country_market_rows"] == 5 * (127 - 62)
    assert outcome["reference_rows"] == 15 * 5
    assert outcome["country"]["USA"]["fx_coverage"] is None
    assert outcome["country"]["USA"]["fx_missing_rows"] is None
    assert set(outcome["external_reference_overlap"]) == {
        identifier for _, identifier in STRESS_REFERENCES
    }


def test_missing_fx_not_silently_imputed(tmp_path):
    pilot = _pilot(tmp_path)
    name = "country_market_features.csv"
    path = pilot / name
    frame = pd.read_csv(path)
    mask = (frame.country == "MEX") & (frame.index == frame[frame.country == "MEX"].index[0])
    frame.loc[mask, "fx_vol_21"] = np.nan
    frame.to_csv(path, index=False)
    manifest = json.loads((pilot / "manifest.json").read_text())
    manifest["outputs"][name]["sha256"] = sha256(path.read_bytes()).hexdigest()
    (pilot / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="missingness is inconsistent"):
        audit_market_pilot(pilot)


def test_tampered_derived_csv_rejected_even_if_readable(tmp_path):
    pilot = _pilot(tmp_path)
    path = pilot / "external_stress_references.csv"
    with path.open("a") as output:
        output.write("USA,fred,STLFSI4,2020-02-10,0.99\n")
    with pytest.raises(ValueError, match="hash mismatch"):
        audit_market_pilot(pilot)


def test_common_calendar_inconsistency_detected(tmp_path):
    pilot = _pilot(tmp_path)
    name = "five_country_common_equity_dates.csv"
    path = pilot / name
    data = pd.read_csv(path)
    data = data.iloc[1:].copy()
    data.to_csv(path, index=False)
    manifest = json.loads((pilot / "manifest.json").read_text())
    manifest["outputs"][name]["sha256"] = sha256(path.read_bytes()).hexdigest()
    manifest["outputs"][name]["rows"] = len(data)
    (pilot / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="not the exact equity intersection"):
        audit_market_pilot(pilot)


def test_reference_identity_validation_catches_label_changes(tmp_path):
    pilot = _pilot(tmp_path)
    name = "external_stress_references.csv"
    path = pilot / name
    data = pd.read_csv(path)
    data.loc[data.series_id == "NFCI", "series_id"] = "FUTURE_STRESS_INDEX"
    data.to_csv(path, index=False)
    manifest = json.loads((pilot / "manifest.json").read_text())
    manifest["outputs"][name]["sha256"] = sha256(path.read_bytes()).hexdigest()
    (pilot / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="unexpected or missing benchmark"):
        audit_market_pilot(pilot)
