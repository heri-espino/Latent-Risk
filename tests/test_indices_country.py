"""Source-free, deterministic tests for cutoff-bounded country index estimators."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from latent_risk.indices.country import fit_country_index


def synthetic_panel(n: int = 150, *, stress: bool = True) -> pd.DataFrame:
    """Seeded one-factor market proxy; not a calibrated stress data-generating model."""
    rng = np.random.default_rng(4107)
    t = np.arange(n)
    latent = 0.3 * np.sin(t / 8) + rng.normal(0, 0.15, n)
    if stress:
        latent[65:85] += 2.0
    noise = rng.normal(0, 0.12, (n, 4))
    return pd.DataFrame(
        {
            "equity_vol": 2 * latent + noise[:, 0],
            "equity_drawdown": -1.5 * latent + noise[:, 1],
            "fx_depreciation": 1.2 * latent + noise[:, 2],
            "bond_spread": 0.8 * latent + noise[:, 3],
        },
        index=pd.date_range("2010-01-01", periods=n, freq="D"),
    )


SIGNS = {
    "equity_vol": 1,
    "equity_drawdown": -1,
    "fx_depreciation": 1,
    "bond_spread": 1,
}


@pytest.mark.parametrize("kind", ["composite", "pca", "state_space"])
def test_future_perturbation_does_not_rewrite_frozen_past(kind):
    original = synthetic_panel()
    changed = original.copy()
    changed.iloc[115:] = changed.iloc[115:] * -1000 + 9999
    kwargs = dict(
        training_cutoff=original.index[95],
        origin=original.index[112],
        model=kind,
        directions=SIGNS,
        stress_anchor="equity_vol",
    )
    a = fit_country_index(original, **kwargs)
    b = fit_country_index(changed, **kwargs)
    pd.testing.assert_series_equal(a.factor, b.factor, check_exact=True)
    pd.testing.assert_series_equal(a.loadings, b.loadings, check_exact=True)
    if kind == "state_space":
        pd.testing.assert_series_equal(a.uncertainty, b.uncertainty, check_exact=True)
        assert a.estimate_kind == "filtered"
        assert a.metadata["estimation"].startswith("two_stage")
        assert a.diagnostics["parameter_optimizer"] == "not_applicable_two_stage"
    else:
        assert a.uncertainty is None
        assert a.estimate_kind == "pointwise"
    assert a.factor.index.max() == original.index[112]
    assert a.information_cutoff == original.index[112]


@pytest.mark.parametrize("kind", ["composite", "pca", "state_space"])
def test_frozen_training_fit_means_later_origins_do_not_revise_past(kind):
    panel = synthetic_panel()
    base_kwargs = dict(
        training_cutoff=panel.index[100],
        model=kind,
        directions=SIGNS,
        stress_anchor="equity_vol",
    )
    early = fit_country_index(panel, origin=panel.index[110], **base_kwargs)
    later = fit_country_index(panel, origin=panel.index[130], **base_kwargs)
    np.testing.assert_allclose(
        early.factor.to_numpy(), later.factor.loc[early.factor.index].to_numpy(), atol=1e-14, rtol=0
    )
    if kind == "state_space":
        np.testing.assert_allclose(
            early.uncertainty.to_numpy(),
            later.uncertainty.loc[early.uncertainty.index].to_numpy(),
            atol=0,
            rtol=0,
        )


@pytest.mark.parametrize("kind", ["composite", "pca", "state_space"])
def test_synthetic_stress_response_and_training_metadata(kind):
    panel = synthetic_panel()
    result = fit_country_index(
        panel, panel.index[120], model=kind, directions=SIGNS, stress_anchor="equity_vol"
    )
    assert result.factor.loc[panel.index[68:82]].mean() > (
        result.factor.loc[panel.index[25:45]].mean() + 0.5
    )
    assert result.factor.notna().all()
    assert result.metadata["source_availability_verification"] == "CALLER_RESPONSIBILITY_NOT_VERIFIED"
    assert set(result.diagnostics["residual_lag1_correlation"]) == set(SIGNS)
    assert set(result.diagnostics["residual_pairwise_correlation"]) == set(SIGNS)
    assert "pca_split_loading_cosine" in result.diagnostics if kind != "composite" else True
    assert np.isfinite(result.loadings).all()
    assert result.training_cutoff == panel.index[120]


def test_no_stress_synthetic_is_valid_without_crisis_claim():
    clean = synthetic_panel(stress=False)
    result = fit_country_index(clean, clean.index[100], directions=SIGNS)
    assert np.isfinite(result.factor).all()
    assert result.model == "composite"


def test_missing_values_use_training_moments_and_explicit_policy():
    frame = synthetic_panel()
    frame.iloc[15:18, 0] = np.nan
    frame.iloc[100, :] = np.nan
    frame.iloc[110, 2] = np.nan
    a = fit_country_index(
        frame, frame.index[90], origin=frame.index[120], model="pca",
        directions=SIGNS, stress_anchor="equity_vol",
    )
    assert np.isnan(a.factor.iloc[100])
    assert np.isfinite(a.factor.iloc[110])
    assert a.metadata["training_missing_fraction"]["equity_vol"] > 0
    assert "training-mean" in a.metadata["missing_policy"]
    b = fit_country_index(
        frame, frame.index[90], origin=frame.index[120], model="composite",
        directions=SIGNS,
    )
    assert np.isnan(b.factor.iloc[100])
    assert b.factor.iloc[110] == pytest.approx(
        np.nanmean(
            (frame.iloc[110].to_numpy() - frame.iloc[:91].mean().to_numpy())
            / frame.iloc[:91].std(ddof=0).to_numpy()
            * np.array([1, -1, 1, 1])
        )
    )


def test_state_space_unobserved_date_uses_prior_not_future():
    frame = synthetic_panel()
    frame.iloc[115] = np.nan
    fit = fit_country_index(
        frame, frame.index[100], origin=frame.index[118],
        model="state_space", directions=SIGNS, stress_anchor="equity_vol",
    )
    assert np.isfinite(fit.factor.iloc[115])
    assert fit.uncertainty.iloc[115] > fit.uncertainty.iloc[114]
    assert frame.index[115].strftime("%Y-%m-%d") in fit.diagnostics["all_missing_dates"]


@pytest.mark.parametrize("reference", ["ECB_CISS_EA", "STLFSI4", "us_nfci_reference"])
def test_published_reference_rejected(reference):
    frame = synthetic_panel().rename(columns={"bond_spread": reference})
    with pytest.raises(ValueError, match="external stress benchmark"):
        fit_country_index(frame, frame.index[100], directions=SIGNS)


def test_direction_schema_and_coverage_fail_closed():
    frame = synthetic_panel()
    with pytest.raises(ValueError, match="direction"):
        fit_country_index(frame, frame.index[100], directions={"equity_vol": 1})
    bad = frame.copy()
    bad.iloc[:70, 1] = np.nan
    with pytest.raises(ValueError, match="missingness"):
        fit_country_index(bad, bad.index[100], directions=SIGNS)


def test_invalid_date_order_and_reversed_origin_fail():
    frame = synthetic_panel()
    with pytest.raises(ValueError, match="increasing"):
        fit_country_index(frame.iloc[::-1], frame.index[100], directions=SIGNS)
    with pytest.raises(ValueError, match="on/after"):
        fit_country_index(frame, frame.index[100], origin=frame.index[90], directions=SIGNS)


def test_state_space_rejects_underidentified_two_features_and_short_history():
    short = synthetic_panel(n=30)
    with pytest.raises(ValueError, match=">=40"):
        fit_country_index(
            short, short.index[-1], model="state_space", directions=SIGNS,
            stress_anchor="equity_vol"
        )
    two = synthetic_panel()[["equity_vol", "fx_depreciation"]]
    with pytest.raises(ValueError, match=">=3"):
        fit_country_index(
            two, two.index[110], model="state_space",
            directions={"equity_vol": 1, "fx_depreciation": 1},
            stress_anchor="equity_vol",
        )


def test_metadata_refits_can_change_historical_scores_and_are_not_pit_vintages():
    frame = synthetic_panel()
    early = fit_country_index(frame, frame.index[95], directions=SIGNS)
    later = fit_country_index(frame, frame.index[120], directions=SIGNS)
    # Explicit different training moments are expected to revise previous values:
    assert not np.allclose(early.factor.to_numpy(), later.factor.iloc[:len(early.factor)].to_numpy())
