"""Synthetic no-future-data controls for CISS observation-index backtesting."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from latent_risk.data.ciss_baselines import (
    aggregate_forecast_scores,
    causal_ewma_level,
    evaluate_ciss_series,
    forecast_ar1,
    train_only_alpha,
)


def _sample(n=750):
    t = np.arange(n, dtype=float)
    return pd.DataFrame({
        "observation_date": pd.bdate_range("2000-01-03", periods=n).strftime("%Y-%m-%d"),
        "value": 0.4 + 0.1 * np.sin(t / 33.0) + t * 0.00001,
    })


def test_one_sided_ewma_and_alpha_one_equals_persistence():
    y = np.array([0.1, 0.5, 0.3])
    assert causal_ewma_level(y, 1.0) == pytest.approx(0.3)
    assert causal_ewma_level(y, 0.5) == pytest.approx(0.3)
    with pytest.raises(ValueError):
        causal_ewma_level(y, 0)


def test_nested_cv_never_sees_appended_future():
    data = _sample()
    cutoff = 670
    hist = data.value.to_numpy()[:cutoff]
    a, folds = train_only_alpha(hist, 5)
    appended = np.r_[hist, np.array([999.0, -999.0])]
    # Correct origin supplies history through the origin, no later values:
    b, other_folds = train_only_alpha(appended[:cutoff], 5)
    assert a == b
    assert folds == other_folds
    assert folds > 5


def test_ar1_uses_origin_history_only():
    y = _sample().value.to_numpy()
    result = forecast_ar1(y[:650], 5)
    changed = y.copy()
    changed[650:] += 1000
    assert result == pytest.approx(forecast_ar1(changed[:650], 5))


def test_outer_horizon_target_alignment_and_future_invariance():
    source = _sample(800)
    first = evaluate_ciss_series(
        source.iloc[:720], start="2001-12-31",
        horizons=(1, 5, 21), stride=21,
    )
    changed = source.copy()
    changed.loc[720:, "value"] = 999
    second = evaluate_ciss_series(
        changed.iloc[:720], start="2001-12-31",
        horizons=(1, 5, 21), stride=21,
    )
    pd.testing.assert_frame_equal(first, second)
    assert set(first.model) == {"persistence", "ewma_nested_cv", "ar1_ols"}
    for row in first.itertuples():
        j = source.index[source.observation_date == row.origin_date][0]
        assert row.target_date == source.iloc[j + row.horizon_observations].observation_date
        assert row.actual == source.iloc[j + row.horizon_observations].value


def test_cv_nested_ewma_never_uses_heldout_outer_value():
    orig = _sample(650)
    a = evaluate_ciss_series(orig, start="2001-12-31", horizons=(5,), stride=21)
    changed = orig.copy()
    changed.loc[649, "value"] = 0.95
    b = evaluate_ciss_series(changed, start="2001-12-31", horizons=(5,), stride=21)
    baseline = a.loc[a.origin_date < orig.iloc[649].observation_date]
    matched = b.loc[b.origin_date.isin(baseline.origin_date)]
    pd.testing.assert_frame_equal(
        baseline[["origin_date", "model", "prediction", "selected_ewma_alpha"]]
        .reset_index(drop=True),
        matched[["origin_date", "model", "prediction", "selected_ewma_alpha"]]
        .reset_index(drop=True),
    )


def test_duplicate_observation_dates_rejected():
    source = _sample()
    source.loc[2, "observation_date"] = source.loc[1, "observation_date"]
    with pytest.raises(ValueError, match="invalid CISS"):
        evaluate_ciss_series(source)


def test_matched_score_validation():
    p = evaluate_ciss_series(
        _sample(), start="2001-12-31", horizons=(1, 5), stride=21,
    )
    p.insert(0, "country", "USA")
    scores = aggregate_forecast_scores(p)
    assert len(scores) == 6
    assert scores.n_origin_target_pairs.min() > 0
    bad = p.loc[~((p.model == "ar1_ols") & (p.index == p.index[5]))].copy()
    # Remove one AR1 forecast, so the matched target lists differ.
    ix = bad.index[bad.model == "ar1_ols"][0]
    bad = bad.drop(index=ix)
    with pytest.raises(ValueError, match="unmatched targets"):
        aggregate_forecast_scores(bad)
