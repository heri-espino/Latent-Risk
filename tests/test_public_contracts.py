"""Offline QA contracts for public Latent-Risk APIs and proposed pipeline boundaries.

No provider calls, user VM downloads, secrets, or real market observations.
The one-sided state/forecast functions below are test-local reference stubs,
NOT production trend, forecasting, or financial-event detection algorithms.
"""
from __future__ import annotations

import hashlib
import importlib
import socket

import numpy as np
import pandas as pd
import pytest

from latent_risk.data import available_as_of, validate_long_panel
from latent_risk.data.market_features import (
    EQUITY_BY_COUNTRY,
    FX_BY_COUNTRY,
    STRESS_REFERENCES,
    build_country_market_panel,
)
from latent_risk.data.quality import inspect_source_file
from latent_risk.evaluation import forecast_errors, standardized_errors
from latent_risk.indices import fit_pca, fit_signed_composite


def _synthetic_market_frames(periods: int = 128) -> dict[str, pd.DataFrame]:
    """Make invented, strictly positive, aligned market-close observations."""
    days = pd.date_range("2020-01-01", periods=periods, freq="B")
    t = np.arange(periods, dtype=float)
    close = 100.0 * np.exp(0.002 * t + 0.01 * np.sin(t / 7.0))
    frame = pd.DataFrame({
        "observation_date": days.strftime("%Y-%m-%d"),
        "Close": close,
    })
    tickers = set(EQUITY_BY_COUNTRY.values())
    tickers.update(ticker for ticker, _ in FX_BY_COUNTRY.values())
    return {ticker: frame.copy() for ticker in tickers}


def _synthetic_vintage_panel() -> pd.DataFrame:
    """Create two independent invented stress-oriented features."""
    rows = []
    for i, obs in enumerate(pd.date_range("2020-01-01", periods=10, freq="B")):
        available = obs + pd.Timedelta(days=1)  # synthetic, NOT provider metadata
        for variable, value in (
            ("equity_vol_21", 0.3 + 0.04 * i + 0.02 * np.sin(i)),
            ("fx_vol_21", 0.6 + 0.03 * i + 0.08 * np.cos(i)),
        ):
            rows.append({
                "country": "MEX",
                "observation_date": obs.strftime("%Y-%m-%d"),
                "available_date": available.strftime("%Y-%m-%d"),
                "variable": variable,
                "value": value,
                "source": "invented-offline-fixture",
            })
    return pd.DataFrame(rows)


def _matrix_as_of(panel: pd.DataFrame, origin: str) -> np.ndarray:
    """Reference adapter: select only dated releases and freeze feature order."""
    allowed = available_as_of(panel, origin)
    return (
        allowed.pivot(
            index="observation_date", columns="variable", values="value"
        )[["equity_vol_21", "fx_vol_21"]]
        .to_numpy(dtype=float)
    )


def _reference_one_sided_state(factor_history: np.ndarray) -> float:
    """Test-only causal EWMA: never a claim of fitted PLS or Kalman filtering."""
    if factor_history.ndim != 1 or not len(factor_history):
        raise ValueError("factor history must be a nonempty vector")
    state = float(factor_history[0])
    for value in factor_history[1:]:
        state = 0.25 * float(value) + 0.75 * state
    return state


def test_installed_public_imports_and_exports():
    """The existing API imports without imaginary pipeline exports."""
    package = importlib.import_module("latent_risk")
    indices = importlib.import_module("latent_risk.indices")
    vintage = importlib.import_module("latent_risk.data")
    evaluation = importlib.import_module("latent_risk.evaluation")
    assert isinstance(package.__version__, str)
    assert callable(package.fit_pca)
    assert callable(package.fit_signed_composite)
    assert callable(indices.fit_pca)
    assert callable(vintage.available_as_of)
    assert callable(evaluation.standardized_errors)


def test_external_benchmark_sentinels_never_change_market_feature_outputs():
    """Reference indices cannot accidentally enter the current market pilot."""
    clean = _synthetic_market_frames()
    expected_long, expected_common = build_country_market_panel(clean)
    with_references = {key: value.copy() for key, value in clean.items()}
    # Extremely large invented reference values would visibly poison a factor.
    for (provider, source_id), country in STRESS_REFERENCES.items():
        assert provider in {"fred", "ecb"}
        assert country in {"EA", "USA", "GBR"}
        with_references[source_id] = pd.DataFrame({
            "observation_date": clean["^GSPC"]["observation_date"],
            "Close": np.full(len(clean["^GSPC"]), 1e18),
        })
    actual_long, actual_common = build_country_market_panel(with_references)
    pd.testing.assert_frame_equal(actual_long, expected_long)
    pd.testing.assert_frame_equal(actual_common, expected_common)
    assert not ({key for _, key in STRESS_REFERENCES} & set(actual_common.columns))
    # This is a market-pilot gate, NOT enforcement inside the generic PCA fit API.


def test_pca_anchor_and_scale_are_frozen_after_training():
    """The PCA loading and standardizer must not be recomputed on future rows."""
    rng = np.random.default_rng(42)
    training = rng.normal(size=(60, 3))
    model = fit_pca(training, stress_anchor=0)
    original_component = model.component.copy()
    original_mean, original_std = model.standardizer.mean.copy(), model.standardizer.std.copy()
    original_scores = model.transform(training)
    future = np.array([[10_000.0, -10_000.0, 2000.0]])
    augmented_scores = model.transform(np.concatenate([training, future]))
    assert model.component[0] > 0
    np.testing.assert_array_equal(original_component, model.component)
    np.testing.assert_array_equal(original_mean, model.standardizer.mean)
    np.testing.assert_array_equal(original_std, model.standardizer.std)
    np.testing.assert_allclose(original_scores, augmented_scores[:-1])


def test_unpublished_values_are_excluded_and_missing_release_is_rejected():
    """Missing release verification must not be treated as an early publication."""
    panel = _synthetic_vintage_panel()
    asof = available_as_of(panel, "2020-01-07")
    assert set(asof["observation_date"]) <= set(
        pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-06"])
    )
    assert (asof["available_date"] <= pd.Timestamp("2020-01-07")).all()
    unverified = panel.copy()
    unverified.loc[0, "available_date"] = None
    with pytest.raises(ValueError, match="missing dates"):
        validate_long_panel(unverified)
    # Note: this existing API rejects unknown dates rather than modeling null
    # availability explicitly. The proposed strict UTC contract must do so.


def test_calendar_intersection_does_not_forward_fill_foreign_holidays():
    """A missing UK session must not fabricate a common five-country date."""
    frames = _synthetic_market_frames()
    removed_date = frames["^FTSE"].iloc[90]["observation_date"]
    frames["^FTSE"] = frames["^FTSE"].drop(index=90).reset_index(drop=True)
    long, common = build_country_market_panel(frames)
    assert pd.Timestamp(removed_date) not in set(common["observation_date"])
    assert pd.Timestamp(removed_date) in set(
        long.loc[long["country"] == "USA", "observation_date"]
    )
    assert common["observation_date"].is_monotonic_increasing


def test_naive_vintage_contract_rejects_timezone_mixing():
    """Current vintage API is date-only; it cannot interpret intraday clocks."""
    panel = _synthetic_vintage_panel()
    with pytest.raises(ValueError, match="timezone-naive"):
        available_as_of(panel, pd.Timestamp("2020-01-07T16:00:00Z"))
    tz_panel = panel.copy()
    tz_panel["available_date"] = pd.to_datetime(tz_panel["available_date"], utc=True)
    with pytest.raises(ValueError, match="timezone-naive"):
        validate_long_panel(tz_panel)


def test_source_csv_sha256_is_conserved_and_tampering_is_detected(tmp_path):
    """Original archived bytes stay unchanged during read-only audit."""
    snapshot = tmp_path / "fixture_snapshot"
    snapshot.mkdir()
    content = (
        b"observation_date,value\n"
        b"2020-01-01,1.1\n2020-01-02,1.2\n2020-01-03,1.3\n"
    )
    file = snapshot / "invented.csv"
    file.write_bytes(content)
    original_sha256 = hashlib.sha256(content).hexdigest()
    record = {
        "status": "OK",
        "source": "fred",
        "country": "USA",
        "id": "SYNTHETIC_TEST_ONLY",
        "role": "synthetic_feature",
        "path": "invented.csv",
        "sha256": original_sha256,
        "n_rows": 3,
        "first_date": "2020-01-01",
        "last_date": "2020-01-03",
    }
    clean = inspect_source_file(snapshot, record)
    assert clean["status"] == "PASS", clean["errors"]
    assert file.read_bytes() == content
    file.write_bytes(content.replace(b"1.2", b"9.2"))
    tampered = inspect_source_file(snapshot, record)
    assert tampered["status"] == "FAIL"
    assert any("SHA256" in error for error in tampered["errors"])
    assert record["sha256"] == original_sha256


def test_forecast_origin_invariant_to_future_rows_and_outliers():
    """Synthetic end-to-end: gate → actual composite → reference state → error."""
    panel = _synthetic_vintage_panel()
    origin = "2020-01-09"
    baseline = _matrix_as_of(panel, origin)
    with_far_future = pd.concat([
        panel, pd.DataFrame([{
            "country": "MEX",
            "observation_date": "2030-02-01",
            "available_date": "2030-02-02",
            "variable": feature,
            "value": 1e20,
            "source": "invented-offline-fixture",
        } for feature in ("equity_vol_21", "fx_vol_21")])
    ], ignore_index=True)
    altered = _matrix_as_of(with_far_future, origin)
    np.testing.assert_array_equal(baseline, altered)

    model_a = fit_signed_composite(baseline, directions=[1, 1])
    model_b = fit_signed_composite(altered, directions=[1, 1])
    history_a, history_b = model_a.transform(baseline), model_b.transform(altered)
    np.testing.assert_array_equal(history_a, history_b)
    prediction_a = _reference_one_sided_state(history_a)
    prediction_b = _reference_one_sided_state(history_b)
    assert prediction_a == prediction_b

    # A synthetic next-observation realization and a strictly training-based SD.
    observed = float(model_a.transform([[0.67, 0.92]])[0])
    sd = max(float(np.std(history_a, ddof=0)), 1e-6)
    errors = forecast_errors([observed], [prediction_a])
    score_a = standardized_errors([observed], [prediction_a], [sd])
    score_b = standardized_errors([observed], [prediction_b], [sd])
    np.testing.assert_allclose(errors / sd, score_a)
    np.testing.assert_array_equal(score_a, score_b)
    # No production one-sided trend/forecaster/event-scoring engine exists yet.


def test_fixed_seed_is_repeatable_and_does_not_require_vendor_input():
    """Both random fixture generation and fitted public PCA are deterministic."""
    left = np.random.default_rng(20261018).normal(size=(40, 3))
    right = np.random.default_rng(20261018).normal(size=(40, 3))
    np.testing.assert_array_equal(left, right)
    lhs = fit_pca(left, stress_anchor=0)
    rhs = fit_pca(right, stress_anchor=0)
    np.testing.assert_array_equal(lhs.component, rhs.component)
    np.testing.assert_array_equal(lhs.transform(left), rhs.transform(right))


def test_end_to_end_reference_path_has_no_network_dependency(monkeypatch):
    """Verify the synthetic path works even with all socket connects disabled."""
    def deny_network(*args, **kwargs):
        raise AssertionError("synthetic contract tests must never contact a vendor")

    monkeypatch.setattr(socket.socket, "connect", deny_network)
    monkeypatch.setattr(socket, "create_connection", deny_network)
    panel = _synthetic_vintage_panel()
    training = _matrix_as_of(panel, "2020-01-09")
    factor = fit_signed_composite(training, directions=[1, 1]).transform(training)
    forecast = _reference_one_sided_state(factor)
    assert np.isfinite(forecast)
    assert np.isfinite(standardized_errors([1.0], [forecast], [1.0])).all()
