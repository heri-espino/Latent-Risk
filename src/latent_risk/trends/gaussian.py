"""Exact d=2 PLS and Gaussian local-linear-trend methods for one fixed index.

The first two latent coordinates have a flat/diffuse prior. Consequently
filter_local_linear evaluates the n-2 dimensional restricted (diffuse)
Gaussian likelihood, not an ordinary n-observation marginal ML likelihood.
Observations must be equally spaced, finite, and ordered, without gaps.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.linalg import cholesky_banded
from scipy.optimize import minimize, minimize_scalar
from scipy.sparse import diags, eye
from scipy.sparse.linalg import spsolve

_F = np.array([[2.0, -1.0], [1.0, 0.0]])


def _observations(y: object, minimum: int = 3) -> np.ndarray:
    values = np.asarray(y, dtype=float)
    if values.ndim != 1 or values.size < minimum or not np.all(np.isfinite(values)):
        raise ValueError(f"y must be a finite 1-D array with at least {minimum} observations")
    return values


def second_difference(n: int):
    """Return the (n-2) by n sparse forward second-difference matrix.

    Its rows contain (1, -2, 1); no periodic or clamped end rows.
    """
    if isinstance(n, (bool, np.bool_)) or not isinstance(n, (int, np.integer)) or n < 3:
        raise ValueError("n must be an integer >= 3")
    return diags(
        (np.ones(n - 2), -2 * np.ones(n - 2), np.ones(n - 2)),
        offsets=(0, 1, 2),
        shape=(n - 2, n),
        format="csr",
    )


def _penalty_system(n: int, lam: float):
    d = second_difference(n)
    return eye(n, format="csc") + lam * (d.T @ d).tocsc()


def penalized_trend(y: object, lam: float) -> np.ndarray:
    """Minimize ||y-tau||^2 + lam ||D2 tau||^2 without dense inversion.

    lam=0 interpolates; lam=inf is the least-squares affine fit.
    Large finite ratios can be poorly conditioned; compare a scale sweep.
    """
    y = _observations(y)
    if np.isnan(lam) or lam < 0:
        raise ValueError("lam must be nonnegative")
    if np.isposinf(lam):
        t = np.arange(y.size, dtype=float)
        x = np.column_stack((np.ones(y.size), t))
        return x @ np.linalg.lstsq(x, y, rcond=None)[0]
    if not np.isfinite(lam):
        raise ValueError("lam must be finite or +infinity")
    if lam == 0:
        return y.copy()
    return np.asarray(spsolve(_penalty_system(y.size, lam), y), dtype=float)


def effective_degrees_of_freedom(n: int, lam: float) -> float:
    """Compute trace((I+lam D2.T D2)^-1) with O(n) banded selected inversion.

    The exactly unpenalized two-dimensional affine nullspace contributes 2.
    """
    if np.isnan(lam) or lam < 0:
        raise ValueError("lam must be nonnegative")
    d = second_difference(n)
    if lam == 0:
        return float(n)
    if np.isposinf(lam):
        return 2.0
    if not np.isfinite(lam):
        raise ValueError("lam must be finite or +infinity")
    a = eye(n, format="csc") + lam * (d.T @ d).tocsc()
    ab = np.zeros((3, n))
    ab[0] = a.diagonal()
    ab[1, : n - 1] = a.diagonal(-1)
    ab[2, : n - 2] = a.diagonal(-2)
    c = cholesky_banded(ab, lower=True, check_finite=False)
    l1 = c[1, : n - 1] / c[0, : n - 1]
    l2 = c[2, : n - 2] / c[0, : n - 2]
    z0 = np.zeros(n)
    z1 = np.zeros(n - 1)
    z2 = np.zeros(n - 2)
    for i in range(n - 1, -1, -1):
        if i + 2 < n:
            z2[i] = -l1[i] * z1[i + 1] - l2[i] * z0[i + 2]
        if i + 1 < n:
            z1[i] = -l1[i] * z0[i + 1]
            if i + 2 < n:
                z1[i] -= l2[i] * z1[i + 1]
        z0[i] = 1 / c[0, i] ** 2
        if i + 1 < n:
            z0[i] -= l1[i] * z1[i]
        if i + 2 < n:
            z0[i] -= l2[i] * z2[i]
    return float(np.sum(z0))


@dataclass(frozen=True)
class TrendFilter:
    """Exact diffuse-filter result; states span observations 2,...,n (1-based)."""

    states: np.ndarray
    covariances: np.ndarray
    predicted_states: np.ndarray
    predicted_covariances: np.ndarray
    innovations: np.ndarray
    innovation_variances: np.ndarray
    reml_nll: float
    measurement_variance: float
    curvature_variance: float

    @property
    def filtered_trend(self) -> np.ndarray:
        """One-sided E[tau_t | y_1,...,y_t] for t=1,...,n."""
        return np.r_[self.states[0, 1], self.states[:, 0]]


def filter_local_linear(y: object, measurement_variance: float, curvature_variance: float):
    """Kalman innovations filter with exactly diffuse tau_1,tau_2.

    Let alpha_t=(tau_t,tau_(t-1)), F=[[2,-1],[1,0]], Q=diag(q,0),
    H=(1,0) and R=r. The flat prior yields, after y1,y2,
    alpha_2 | y1,y2 ~ N((y2,y1), diag(r,r)). The n-2 subsequent
    innovations define REML for the two-dimensional affine nullspace.
    The filter is causal. r and q may be zero individually.
    """
    y = _observations(y)
    r, q = float(measurement_variance), float(curvature_variance)
    if not np.isfinite(r) or not np.isfinite(q) or min(r, q) < 0 or r + q <= 0:
        raise ValueError("finite nonnegative r,q with r+q>0 required")
    n = len(y)
    means = np.empty((n - 1, 2))
    cov = np.empty((n - 1, 2, 2))
    predicted = np.empty_like(means)
    pred_cov = np.empty_like(cov)
    innovations = np.empty(n - 2)
    variances = np.empty(n - 2)
    means[0] = (y[1], y[0])
    cov[0] = np.diag([r, r])
    predicted[0] = means[0]
    pred_cov[0] = cov[0]
    q_matrix = np.array([[q, 0.0], [0.0, 0.0]])
    nll = 0.0
    for i in range(1, n - 1):
        m = _F @ means[i - 1]
        p = _F @ cov[i - 1] @ _F.T + q_matrix
        v = y[i + 1] - m[0]
        s = p[0, 0] + r
        if s <= 0 or not np.isfinite(s):
            raise ArithmeticError("non-positive/invalid innovation variance")
        k = p[:, 0] / s
        means[i] = m + k * v
        updated = p - np.outer(k, p[0])
        cov[i] = 0.5 * (updated + updated.T)
        predicted[i] = m
        pred_cov[i] = p
        innovations[i - 1], variances[i - 1] = v, s
        nll += 0.5 * (np.log(2 * np.pi * s) + v * v / s)
    return TrendFilter(means, cov, predicted, pred_cov, innovations, variances, nll, r, q)


def smooth_local_linear(y: object, measurement_variance: float, curvature_variance: float):
    """Full-sample RTS posterior mean; retrospective only, not a forecast.

    For positive r and q this equals penalized_trend(y, r/q) up to numerical
    error. Does not use the smoother in any forecasting function.
    """
    if measurement_variance <= 0 or curvature_variance <= 0:
        raise ValueError("RTS equivalence implementation requires r>0,q>0")
    result = filter_local_linear(y, measurement_variance, curvature_variance)
    m, p = result.states.copy(), result.covariances.copy()
    for i in range(len(m) - 2, -1, -1):
        xp, pp = result.predicted_states[i + 1], result.predicted_covariances[i + 1]
        j = np.linalg.solve(pp, _F @ result.covariances[i]).T
        m[i] += j @ (m[i + 1] - xp)
        p[i] += j @ (p[i + 1] - pp) @ j.T
    return np.r_[m[0, 1], m[:, 0]]


@dataclass(frozen=True)
class REMLFit:
    """Variance-component restricted likelihood fit and boundary diagnosis."""

    measurement_variance: float
    curvature_variance: float
    lambda_ratio: float
    negative_log_likelihood: float
    boundary: str
    success: bool
    message: str


def fit_reml(y: object) -> REMLFit:
    """Estimate r and q by exact diffuse Gaussian REML, including zero boundaries.

    Two diffuse nullspace dimensions yield n-2 innovations. To avoid
    floating-point scaling problems, subtract an affine fit and normalize by
    the second-difference root mean square. Optimize in log variances, compare
    the two exact zero-variance boundaries, and diagnose search-limit fits.
    For very short or nearly affine samples variance ratios may be weakly
    identified; no finite REML optimum exists for perfectly affine data.
    """
    y = _observations(y, minimum=5)
    d2 = np.diff(y, n=2)
    scale = float(np.sqrt(np.mean(d2**2)))
    if scale == 0:
        raise ValueError("perfect affine data yield an unbounded variance likelihood")
    times = np.arange(y.size, dtype=float)
    x = np.column_stack((np.ones(y.size), times))
    standardized = (y - x @ np.linalg.lstsq(x, y, rcond=None)[0]) / scale
    # Truncation limits in normalized variance units; keep this diagnostic visible.
    bound = (-18.0, 18.0)

    def objective(z):
        return filter_local_linear(standardized, np.exp(z[0]), np.exp(z[1])).reml_nll

    candidates = []
    for start in ((-2, -2), (0, -7), (-7, 0)):
        fitted = minimize(objective, start, method="L-BFGS-B", bounds=[bound, bound])
        if fitted.success and np.isfinite(fitted.fun):
            candidates.append((float(fitted.fun), *np.exp(fitted.x), fitted.x, "interior"))
    for name in ("q_zero", "r_zero"):
        def boundary_objective(logv, *, which=name):
            v = float(np.exp(logv))
            r, q = (v, 0.0) if which == "q_zero" else (0.0, v)
            return filter_local_linear(standardized, r, q).reml_nll

        fitted = minimize_scalar(boundary_objective, method="bounded", bounds=bound)
        if fitted.success and np.isfinite(fitted.fun):
            v = np.exp(fitted.x)
            r, q = (v, 0.0) if name == "q_zero" else (0.0, v)
            candidates.append((float(fitted.fun), r, q, [fitted.x], name))
    if not candidates:
        raise ArithmeticError("REML numerical optimization failed")
    nll, r, q, logs, boundary = min(candidates, key=lambda a: a[0])
    if boundary == "interior" and np.min(np.abs(np.asarray(logs) - bound[0])) < 1e-3:
        boundary = "search_limit"
    if boundary == "interior" and np.min(np.abs(np.asarray(logs) - bound[1])) < 1e-3:
        boundary = "search_limit"
    r, q = float(r * scale**2), float(q * scale**2)
    nll += (y.size - 2) * np.log(scale)
    lam = np.inf if q == 0 else r / q
    msg = "Exact diffuse REML; do not interpret as proper finite-prior marginal ML"
    if boundary == "search_limit":
        msg += "; optimizer reached variance search limits"
    return REMLFit(r, q, float(lam), float(nll), boundary, True, msg)


@dataclass(frozen=True)
class TrendForecast:
    """Causal conditional means and variances at a fixed observation origin."""

    origin: int
    horizon: int
    mean: float
    latent_variance: float
    observation_variance: float


def forecast_at_origin(
    y: object,
    origin: int,
    horizon: int,
    measurement_variance: float,
    curvature_variance: float,
) -> TrendForecast:
    """Forecast y_(origin+h) from y[:origin+1] only; 0-based origin.

    The forecast is alpha_t[0]+h(alpha_t[0]-alpha_t[1]), based on the
    filtered state. The trend variance adds q sum_{j=1}^h j^2; observed
    variance additionally adds measurement noise r.
    """
    y = _observations(y)
    if not isinstance(origin, (int, np.integer)) or not 2 <= origin < y.size:
        raise ValueError("origin must be an observed 0-based index >=2")
    if not isinstance(horizon, (int, np.integer)) or horizon < 1:
        raise ValueError("horizon must be a positive integer")
    filt = filter_local_linear(y[: origin + 1], measurement_variance, curvature_variance)
    a = filt.states[-1]
    p = filt.covariances[-1]
    h = int(horizon)
    w = np.array([h + 1.0, -float(h)])
    mean = float(w @ a)
    latent_var = float(w @ p @ w + curvature_variance * h * (h + 1) * (2 * h + 1) / 6)
    return TrendForecast(int(origin), h, mean, latent_var, latent_var + measurement_variance)


def forecast_with_reml(y: object, origin: int, horizon: int) -> tuple[TrendForecast, REMLFit]:
    """Reestimate variances using only the origin prefix, then forecast causally."""
    y = _observations(y, minimum=5)
    if not isinstance(origin, (int, np.integer)) or not 4 <= origin < y.size:
        raise ValueError("REML forecast origin must be >=4 and within observed y")
    fit = fit_reml(y[: origin + 1])
    return forecast_at_origin(y, origin, horizon, fit.measurement_variance, fit.curvature_variance), fit
