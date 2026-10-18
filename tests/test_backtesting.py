"""Adversarial, deterministic tests of chronological and nested forecast evaluation."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from latent_risk.evaluation.backtesting import (
    BacktestConfig,
    Candidate,
    ForecastFamily,
    run_backtest,
)
from latent_risk.evaluation.baselines import (
    AR1OLS,
    Persistence,
    VolatilityAdjustedPersistence,
    baseline_families,
)
from latent_risk.evaluation.scoring import hac_loss_differentials, score_matched


def fixture(n: int = 240) -> pd.DataFrame:
    """Deterministic synthetic stress-style series; no market data or results."""
    rng = np.random.default_rng(812)
    values = 0.5 + np.cumsum(rng.normal(0, 0.015, size=n))
    dates = pd.bdate_range("2010-01-04", periods=n).strftime("%Y-%m-%d")
    return pd.DataFrame({"observation_date": dates, "value": values})


def config(**changes) -> BacktestConfig:
    defaults = dict(
        horizons=(1, 5), first_origin="2010-01-04", min_train=100,
        inner_min_train=80, stride=11, inner_stride=13,
        vintage_policy="current_vintage",
    )
    defaults.update(changes)
    return BacktestConfig(**defaults)


def run(frame=None, *, families=None, settings=None):
    return run_backtest(
        fixture() if frame is None else frame,
        country="USA", target_id="synthetic_CISS_proxy",
        target_scale="synthetic_index_level_v1",
        families=baseline_families() if families is None else families,
        config=config() if settings is None else settings,
    )


def test_synthetic_fixture_and_all_baselines_are_matched():
    result = run()
    assert set(result.model) == {
        "persistence", "ar1_ols", "ewma_nested", "volatility_adjusted_persistence",
    }
    assert set(result.horizon) == {1, 5}
    assert (result.fit_cutoff_date <= result.origin_date).all()
    assert (result.train_start_date <= result.fit_cutoff_date).all()
    assert (result.inner_folds >= 2).all()
    counts = result.groupby(["horizon", "model"]).size()
    assert counts.nunique() == 1
    scores = score_matched(result, n_boot=70, seed=99)
    assert len(scores) == 8
    assert (scores.mse >= 0).all() and (scores.mae >= 0).all()
    assert np.isfinite(scores[["rmse_ci_low", "rmse_ci_high"]]).all().all()


def test_arbitrary_future_values_never_change_any_earlier_forecast_or_selection():
    original = fixture()
    changed = original.copy()
    cutoff = 173
    changed.loc[cutoff:, "value"] = np.linspace(1e9, -1e9, len(changed) - cutoff)
    a = run(original)
    b = run(changed)
    earlier = original.iloc[cutoff].observation_date
    columns = ["origin_date", "target_date", "horizon", "model",
               "candidate", "prediction", "fit_cutoff_date", "inner_folds"]
    # Keep all forecasts issued strictly before the future injection, even
    # those whose eventual targets lie inside the modified interval.
    left = a.loc[a.origin_date < earlier, columns].reset_index(drop=True)
    right = b.loc[b.origin_date < earlier, columns].reset_index(drop=True)
    pd.testing.assert_frame_equal(left, right, check_exact=True)


def test_no_released_future_target_enters_nested_selection():
    original = fixture(230)
    # The modified observation is only available 12 days after its recorded date.
    dates = pd.to_datetime(original.observation_date)
    original["available_date"] = (dates + pd.Timedelta(days=12)).dt.strftime("%Y-%m-%d")
    setting = config(vintage_policy="provided_release_dates", min_train=80,
                     inner_min_train=50, stride=1, inner_stride=8)
    model = (ForecastFamily("persist", (Candidate("last", Persistence),)),)
    altered = original.copy()
    altered.loc[130, "value"] += 999999.0
    first = run(original, families=model, settings=setting)
    second = run(altered, families=model, settings=setting)
    at = original.loc[130, "observation_date"]
    left = first[first.origin_date == at]
    right = second[second.origin_date == at]
    assert not left.empty
    np.testing.assert_allclose(left.prediction, right.prediction, rtol=0, atol=0)
    assert (left.fit_cutoff_date < at).all()


def test_rolling_and_expanding_train_lengths_and_horizon_units():
    expanding = run(settings=config(horizons=(1,), stride=17))
    rolling = run(settings=config(horizons=(1,), stride=17, train_window=100))
    assert expanding.train_n.max() > 100
    assert set(rolling.train_n) == {100}
    assert set(rolling.horizon_unit) == {"observed_CISS_points"}
    origin = pd.Timestamp(expanding.origin_date.iloc[0])
    target = pd.Timestamp(expanding.target_date.iloc[0])
    assert target > origin


def test_bad_vintage_schema_duplicate_or_unsorted_dates_rejected():
    raw = fixture()
    families = (ForecastFamily("persist", (Candidate("last", Persistence),)),)
    with pytest.raises(ValueError, match="requires available_date"):
        run(raw, families=families, settings=config(
            vintage_policy="provided_release_dates"
        ))
    bad = raw.copy()
    bad.loc[5, "observation_date"] = bad.loc[4, "observation_date"]
    with pytest.raises(ValueError, match="unique"):
        run(bad, families=families)
    bad = raw.copy().iloc[::-1]
    with pytest.raises(ValueError, match="increasing"):
        run(bad, families=families)


def test_missing_future_folds_fail_closed_instead_of_dropping_a_model():
    raw = fixture(140)
    raw["available_date"] = (
        pd.to_datetime(raw.observation_date) + pd.Timedelta(days=800)
    ).dt.strftime("%Y-%m-%d")
    families = (ForecastFamily("persist", (Candidate("last", Persistence),)),)
    with pytest.raises(ValueError, match="no eligible outer"):
        run(raw, families=families, settings=config(
            min_train=35, inner_min_train=10, vintage_policy="provided_release_dates"
        ))


def test_unfit_ar_and_volatility_are_rejected():
    with pytest.raises(ValueError, match="unfitted"):
        AR1OLS().predict(1)
    with pytest.raises(ValueError, match="unfitted"):
        VolatilityAdjustedPersistence().predict(1)
    with pytest.raises(ValueError, match="positive"):
        Persistence().predict(0)


def test_scoring_rejects_cherry_picked_unmatched_targets_and_scales():
    result = run(families=(
        ForecastFamily("persist", (Candidate("last", Persistence),)),
        ForecastFamily("ar", (Candidate("ar", AR1OLS),)),
    ))
    ix = result.index[result.model == "ar"][0]
    with pytest.raises(ValueError, match="unmatched"):
        score_matched(result.drop(ix), n_boot=5)
    bad = result.copy()
    ix = bad.index[bad.model == "ar"][0]
    bad.loc[ix, "actual"] += 100
    with pytest.raises(ValueError, match="unmatched"):
        score_matched(bad, n_boot=5)
    # A different latent scale is a distinct target group, never pooled.
    rescaled = result.copy()
    rescaled["target_scale"] = "another_factor_with_different_units"
    both = pd.concat([result, rescaled])
    scored = score_matched(both, n_boot=5)
    assert scored.target_scale.nunique() == 2


def test_hac_paired_loss_difference_has_reported_lag_and_finite_normal_p():
    result = run(families=(
        ForecastFamily("persistence", (Candidate("last", Persistence),)),
        ForecastFamily("ar1", (Candidate("ar1", AR1OLS),)),
    ), settings=config(horizons=(1,), stride=7))
    dm = hac_loss_differentials(result, benchmark="persistence", lag=2)
    assert len(dm) == 1
    assert dm.hac_lag.iloc[0] == 2
    assert 0 <= dm.p_two_sided_normal.iloc[0] <= 1
    assert dm.inference.iloc[0] == "EXPLORATORY_DM_STYLE_NEWEY_WEST_NORMAL"
