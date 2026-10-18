"""Offline chronological and provenance tests for the versioned BIS market pilot."""
from __future__ import annotations

import json
from hashlib import sha256

import numpy as np
import pandas as pd
import pytest

from latent_risk.data.bis_market_features import (
    BIS_NEER_BY_COUNTRY,
    build_bis_market_panel,
    neer_trailing_features,
)
from latent_risk.data.market_features import EQUITY_BY_COUNTRY, STRESS_REFERENCES
from scripts.build_bis_market_pilot import prepare_bis_market_pilot


def _prices(n=150, *, index=False):
    dates = pd.bdate_range("2020-01-01", periods=n)
    return pd.DataFrame({
        "observation_date": dates.strftime("%Y-%m-%d"),
        "value" if index else "Close": 100.0 + np.arange(n) * 0.1,
    })


def _frames():
    eq = {ticker: _prices() for ticker in EQUITY_BY_COUNTRY.values()}
    ne = {key: _prices(index=True) for key in BIS_NEER_BY_COUNTRY.values()}
    return eq, ne


def test_neer_depreciation_sign_and_trailing_volatility():
    frame = _prices(index=True)
    value = neer_trailing_features(frame)
    assert (value["neer_depreciation_log_return_1d"] < 0).all()
    assert np.isfinite(value["neer_vol_21"]).all()
    assert value.iloc[0]["observation_date"] == pd.Timestamp(frame.iloc[21]["observation_date"])


def test_neer_later_values_do_not_change_earlier_features():
    frame = _prices(index=True)
    earlier = neer_trailing_features(frame)
    modified = pd.concat([
        frame, pd.DataFrame({"observation_date": ["2030-01-01"], "value": [1.0]}),
    ], ignore_index=True)
    later = neer_trailing_features(modified)
    pd.testing.assert_frame_equal(earlier, later.iloc[: len(earlier)].reset_index(drop=True))


def test_empty_holiday_gap_is_not_filled_and_usa_has_real_fx():
    equities, neer = _frames()
    removed = pd.Timestamp(_prices().iloc[70]["observation_date"])
    neer["D.N.B.US"] = neer["D.N.B.US"].loc[
        neer["D.N.B.US"]["observation_date"] != removed.strftime("%Y-%m-%d"),
    ].reset_index(drop=True)
    long, equity_only, complete = build_bis_market_panel(equities, neer)
    usa = long.loc[long.country == "USA"].set_index("observation_date")
    assert pd.isna(usa.loc[removed, "neer_vol_21"])
    assert usa["neer_vol_21"].notna().sum() > 0
    assert removed in set(equity_only["observation_date"])
    assert removed not in set(complete["observation_date"])
    assert complete.notna().all().all()
    assert len(equity_only) == 150 - 62


def test_wrong_or_nonpositive_source_rejected():
    equities, neer = _frames()
    neer["D.N.B.US"].loc[0, "value"] = -1
    with pytest.raises(ValueError, match="finite positive"):
        build_bis_market_panel(equities, neer)
    equities, neer = _frames()
    del neer["D.N.B.GB"]
    with pytest.raises(ValueError, match="missing sources"):
        build_bis_market_panel(equities, neer)


def _source_fixture(tmp_path):
    snapshots = tmp_path / "raw" / "downloads"
    folder = snapshots / "20261018T000000000000Z"
    folder.mkdir(parents=True)
    equity, neer = _frames()
    records = []
    expected = (
        {("market", k) for k in equity}
        | {("bis", k) for k in neer}
        | set(STRESS_REFERENCES)
    )
    for source, code in sorted(expected):
        if source == "market":
            frame = equity[code]
        elif source == "bis":
            frame = neer[code]
        else:
            frame = _prices(index=True)
        # Match production schema of immutable acquisition snapshots.
        output = folder / source / (code.replace(".", "_").replace("^", "") + ".csv")
        output.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(output, index=False)
        records.append({
            "source": source, "id": code, "status": "OK",
            "role": "external_stress_benchmark" if source in {"ecb", "fred"} else (
                "fx_effective_nominal_broad" if source == "bis" else "local_equity"
            ),
            "path": output.relative_to(folder).as_posix(),
            "sha256": sha256(output.read_bytes()).hexdigest(),
            "n_rows": len(frame),
            "first_date": frame.iloc[0]["observation_date"],
            "last_date": frame.iloc[-1]["observation_date"],
        })
    (folder / "manifest.json").write_text(json.dumps({"records": records}))
    return snapshots, folder


def test_versioned_builder_reads_only_audited_sources(tmp_path):
    snapshots, original = _source_fixture(tmp_path)
    destination = tmp_path / "processed" / "new"
    report = prepare_bis_market_pilot(snapshots, destination, root=tmp_path)
    assert report["status"] == "DESCRIPTIVE_BIS_NEER_PILOT_NO_FORECAST"
    assert len(report["input_sources"]) == 15
    assert report["outputs"]["five_country_common_equity_dates.csv"]["rows"] == 88
    assert report["outputs"]["five_country_complete_neer_equity_dates.csv"]["rows"] == 88
    assert report["coverage_by_country"]["USA"]["neer_complete_rows"] == 88
    assert (original / "bis" / "D_N_B_US.csv").exists()
    assert (destination / "external_stress_references.csv").exists()
    assert "external_stress_references.csv" in report["outputs"]
    with pytest.raises(FileExistsError):
        prepare_bis_market_pilot(snapshots, destination, root=tmp_path)


def test_builder_refuses_tampered_immutable_raw_source(tmp_path):
    snapshots, source = _source_fixture(tmp_path)
    stored = source / "bis" / "D_N_B_US.csv"
    with stored.open("a") as out:
        out.write("2030-01-01,999\n")
    with pytest.raises(ValueError, match="source .* failed integrity audit"):
        prepare_bis_market_pilot(snapshots, tmp_path / "processed", root=tmp_path)


def test_bis_country_names_comparable():
    assert set(BIS_NEER_BY_COUNTRY) == set(EQUITY_BY_COUNTRY)
