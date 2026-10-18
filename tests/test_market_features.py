"""Synthetic chronological, source-separation, and market calendar tests."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from latent_risk.data.market_features import (
    EQUITY_BY_COUNTRY,
    FX_BY_COUNTRY,
    build_country_market_panel,
    equity_trailing_features,
    fx_trailing_features,
)
from latent_risk.data.quality import latest_successful_records


def _data(n=125, *, ratio=1.001, offset=0):
    dates = pd.date_range("2020-01-01", periods=n + offset, freq="B")[offset:]
    return pd.DataFrame({
        "observation_date": dates.strftime("%Y-%m-%d"),
        "Close": 100 * ratio ** np.arange(len(dates)),
    })


def test_equity_windows_are_past_only_and_reject_extra_future_data():
    prices = _data()
    first = equity_trailing_features(prices)
    altered = pd.concat([
        prices, pd.DataFrame({"observation_date": ["2030-01-01"], "Close": [1.0]})
    ], ignore_index=True)
    future = equity_trailing_features(altered)
    pd.testing.assert_frame_equal(first, future.iloc[:len(first)].reset_index(drop=True))
    assert first.iloc[0]["observation_date"] == pd.Timestamp(prices.iloc[62]["observation_date"])
    assert (first["equity_drawdown_63"] >= 0).all()


def test_fx_quote_direction_and_no_leak():
    prices = _data(ratio=1.02)
    a = fx_trailing_features(prices, direction=1)
    b = fx_trailing_features(prices, direction=-1)
    assert np.allclose(a["fx_depreciation_log_return_1d"], -b["fx_depreciation_log_return_1d"])
    assert np.allclose(a["fx_vol_21"], b["fx_vol_21"])
    assert (a["fx_depreciation_log_return_1d"] > 0).all()


def test_common_dates_are_strict_intersection_no_forward_filling():
    frames = {code: _data() for code in EQUITY_BY_COUNTRY.values()}
    for code, _ in FX_BY_COUNTRY.values():
        frames[code] = _data()
    frames["^FTSE"] = frames["^FTSE"].drop(index=100).reset_index(drop=True)
    frames["GBPUSD=X"] = frames["GBPUSD=X"].drop(index=105).reset_index(drop=True)
    long, common = build_country_market_panel(frames)
    assert len(common) == 125 - 62 - 1
    assert not common["observation_date"].isin([
        pd.Timestamp(_data().iloc[100]["observation_date"]),
    ]).any()
    assert len(long[long.country == "USA"]) == 125 - 62
    assert long[long.country == "USA"]["fx_symbol"].eq("").all()
    assert long[long.country == "USA"]["fx_vol_21"].isna().all()
    assert (long[long.country == "GBR"]["fx_vol_21"].isna().sum() >= 1)


def test_missing_series_and_signed_wti_not_accidentally_used():
    frames = {code: _data() for code in EQUITY_BY_COUNTRY.values()}
    with pytest.raises(ValueError, match="missing required"):
        build_country_market_panel(frames)
    assert "CL=F" not in EQUITY_BY_COUNTRY.values()
    assert "CL=F" not in (item[0] for item in FX_BY_COUNTRY.values())


def test_unordered_or_nonpositive_market_prices_are_rejected():
    prices = _data()
    prices.loc[5, "Close"] = -37.63
    with pytest.raises(ValueError, match="positive"):
        equity_trailing_features(prices)
    prices = _data()
    prices.loc[5, "observation_date"] = prices.loc[4, "observation_date"]
    with pytest.raises(ValueError, match="unique"):
        equity_trailing_features(prices)


def test_manifest_selection_prefers_newest_success(tmp_path):
    folder = tmp_path / "20261017"
    folder.mkdir()
    (folder / "manifest.json").write_text(json.dumps({"records": [
        {"status": "OK", "source": "market", "id": "^MXX"}
    ]}))
    chosen = latest_successful_records(tmp_path)
    assert len(chosen) == 1
    assert chosen[0][0] == Path(folder)
