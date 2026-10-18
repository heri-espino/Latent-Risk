"""Regression and numerical tests for second-difference PLS/diffuse REML."""

import numpy as np
import pytest
from numpy.testing import assert_allclose

from latent_risk.trends import (
    effective_degrees_of_freedom,
    filter_local_linear,
    fit_reml,
    forecast_at_origin,
    forecast_with_reml,
    penalized_trend,
    second_difference,
    smooth_local_linear,
)


def test_sparse_matches_dense_and_boundary_conditions():
    rng = np.random.default_rng(10)
    for n in (3, 4, 7, 25):
        y = rng.normal(size=n)
        d = second_difference(n).toarray()
        for lam in (0.0, 0.01, 1.0, 30.0, 1e4):
            a = np.eye(n) + lam * d.T @ d
            assert_allclose(penalized_trend(y, lam), np.linalg.solve(a, y), rtol=1e-9, atol=1e-9)
            assert_allclose(effective_degrees_of_freedom(n, lam), np.trace(np.linalg.inv(a)), rtol=1e-8)


def test_affine_nullspace_moments_and_dof_limits():
    n = 40
    y = 7.0 - 0.31 * np.arange(n)
    d = second_difference(n)
    assert np.linalg.matrix_rank(d.toarray()) == n - 2
    for lam in (0.01, 1.0, 1e5, np.inf):
        assert_allclose(penalized_trend(y, lam), y, atol=2e-7)
    assert_allclose(penalized_trend(y + np.sin(np.arange(n)), np.inf),
                    np.polyval(np.polyfit(np.arange(n), y + np.sin(np.arange(n)), 1), np.arange(n)))
    assert effective_degrees_of_freedom(n, 0) == n
    assert effective_degrees_of_freedom(n, np.inf) == 2
    assert 2 < effective_degrees_of_freedom(n, 2000) < n


def test_rts_matches_pls_for_multiple_ratios():
    y = np.random.default_rng(44).normal(size=42).cumsum()
    for r, q in ((1.0, 1.0), (10.0, 0.1), (0.01, 3.0), (5.0, 0.001)):
        assert_allclose(smooth_local_linear(y, r, q), penalized_trend(y, r / q), rtol=1e-8, atol=1e-7)


def _dense_reml(y, r, q):
    z = second_difference(len(y)) @ y
    d = second_difference(len(y)).toarray()
    c = r * (d @ d.T) + q * np.eye(len(z))
    sign, logdet = np.linalg.slogdet(c)
    assert sign > 0
    return 0.5 * (len(z) * np.log(2 * np.pi) + logdet + z @ np.linalg.solve(c, z))


def test_kalman_innovations_are_exact_reml_not_profiled_residuals():
    y = np.random.default_rng(13).normal(size=12).cumsum()
    for r, q in ((1.5, 0.2), (0.01, 50.0), (20.0, 0.001), (1.0, 0.0), (0.0, 1.0)):
        result = filter_local_linear(y, r, q)
        assert_allclose(result.reml_nll, _dense_reml(y, r, q), rtol=5e-10, atol=5e-8)
        assert len(result.innovations) == len(y) - 2
        assert np.all(result.innovation_variances > 0)


def test_analytic_dense_likelihood_gradient_vs_finite_differences():
    y = np.random.default_rng(81).normal(size=10)
    r, q = 1.2, 0.4
    z = second_difference(len(y)) @ y
    d = second_difference(len(y)).toarray()
    rmat = d @ d.T
    cov = r * rmat + q * np.eye(len(z))
    inv = np.linalg.inv(cov)
    w = inv @ z
    analytic = [0.5 * (np.trace(inv @ a) - w @ a @ w) for a in (rmat, np.eye(len(z)))]
    finite = []
    for j in range(2):
        v1, v2 = [r, q], [r, q]
        v1[j] += 1e-5
        v2[j] -= 1e-5
        finite.append((_dense_reml(y, *v1) - _dense_reml(y, *v2)) / 2e-5)
    assert_allclose(analytic, finite, rtol=1e-6, atol=1e-6)


def test_reml_parameter_recovery_over_simulated_replicates():
    rng = np.random.default_rng(8)
    rs, qs = [], []
    true_r, true_q = 0.7, 0.15
    for _ in range(8):
        n = 180
        second = rng.normal(0.0, np.sqrt(true_q), size=n - 2)
        tau = np.r_[0.0, 0.0, np.zeros(n - 2)]
        for j in range(2, n):
            tau[j] = 2 * tau[j - 1] - tau[j - 2] + second[j - 2]
        y = tau + rng.normal(0.0, np.sqrt(true_r), n)
        result = fit_reml(y)
        rs.append(result.measurement_variance)
        qs.append(result.curvature_variance)
        assert result.success
        assert result.boundary in {"interior", "q_zero", "r_zero", "search_limit"}
    assert abs(np.mean(rs) - true_r) < 0.3
    assert abs(np.mean(qs) - true_q) < 0.10


def test_extreme_ratios_and_finite_forecast_uncertainty():
    y = np.arange(70) * 0.02 + np.random.default_rng(101).normal(size=70)
    for r, q in ((1e-6, 1.0), (1.0, 1e-6), (1.0, 0.0), (0.0, 1.0)):
        filt = filter_local_linear(y, r, q)
        prediction = forecast_at_origin(y, 40, 6, r, q)
        assert np.isfinite(filt.reml_nll)
        assert np.isfinite(prediction.mean)
        assert prediction.latent_variance >= -1e-9
        assert_allclose(prediction.observation_variance - prediction.latent_variance, r)


def test_future_perturbation_cannot_change_origin_forecast():
    y = np.random.default_rng(9).normal(size=80).cumsum()
    future = y.copy()
    future[35:] += 100000.0
    original = forecast_at_origin(y, 34, 7, 1.3, 0.3)
    changed = forecast_at_origin(future, 34, 7, 1.3, 0.3)
    assert original == changed
    forecast1, fit1 = forecast_with_reml(y, 34, 3)
    forecast2, fit2 = forecast_with_reml(future, 34, 3)
    assert forecast1 == forecast2
    assert fit1 == fit2
    unknown_future = y.copy()
    unknown_future[35:] = np.nan
    assert forecast_at_origin(unknown_future, 34, 7, 1.3, 0.3) == original
    assert forecast_with_reml(unknown_future, 34, 3) == (forecast1, fit1)
    assert not np.allclose(smooth_local_linear(y, 1.3, 0.3),
                           smooth_local_linear(future, 1.3, 0.3))


def test_invalid_inputs_and_nonidentifiable_affine_data():
    with pytest.raises(ValueError):
        penalized_trend([1.0, np.nan, 2.0], 1)
    with pytest.raises(ValueError):
        penalized_trend([1, 2, 3], -1)
    with pytest.raises(ValueError):
        filter_local_linear([1, 2, 3], 0, 0)
    with pytest.raises(ValueError, match="affine"):
        fit_reml(np.arange(30.0))
    with pytest.raises(ValueError, match="origin"):
        forecast_at_origin(np.arange(30.0), 1, 2, 1, 1)
