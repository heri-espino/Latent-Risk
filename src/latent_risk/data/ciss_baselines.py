"""Exploratory rolling-origin benchmarks on revised ECB CISS observations.

Observation-index backtest ONLY. This is not historical real-time forecasting:
the retrieved CISS history is current-vintage and has no publication timestamps.
The causal EWMA baseline is not the Gaussian penalized-least-squares smoother.
"""
from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

CISS_COUNTRIES = {
    "CISS.D.U2.Z0Z.4F.EC.SS_CIN.IDX": "EA",
    "CISS.D.US.Z0Z.4F.EC.SS_CIN.IDX": "USA",
    "CISS.D.GB.Z0Z.4F.EC.SS_CIN.IDX": "GBR",
}
ALPHAS = (0.05, 0.10, 0.25, 0.50, 0.85, 1.0)


def causal_ewma_level(y: np.ndarray, alpha: float) -> float:
    """Return the endpoint of a one-sided exponentially weighted mean.

    Parameters
    ----------
    y : numpy.ndarray
        Finite 1-D observations, chronological ascending.
    alpha : float
        Constant smoothing gain in (0, 1].

    Returns
    -------
    float
        Last filtered level based only on values supplied in y.

    Raises
    ------
    ValueError
        Empty, nonfinite, non-1-D data or invalid smoothing gain.
    """
    z = np.asarray(y, dtype=float)
    if (z.ndim != 1 or not len(z) or not np.isfinite(z).all()
            or not 0 < alpha <= 1):
        raise ValueError("EWMA expects nonempty finite 1-D data and 0<alpha<=1")
    result = float(z[0])
    for value in z[1:]:
        result += alpha * (float(value) - result)
    return result


def train_only_alpha(
    history: np.ndarray,
    horizon: int,
    *,
    alphas: Sequence[float] = ALPHAS,
    cv_window: int = 504,
    inner_min_train: int = 252,
    inner_stride: int = 21,
) -> tuple[float, int]:
    """Choose EWMA gain with nested historical h-step time-series CV.

    Inner targets and all inner fitted levels are strictly before or at the
    outer forecast origin. The most recent cv_window values provide the
    internal validation sample. Never evaluate a candidate using the outer
    target or any observation after the outer origin.

    Parameters
    ----------
    history : numpy.ndarray
        Only observations available in sequence up to the outer origin.
    horizon : int
        Forecast horizon measured in CISS observation steps.
    alphas : sequence of float
        Prefixed candidate gains, including 1 (last-value persistence).
    cv_window : int
        Maximum observations supplied to internal scoring.
    inner_min_train : int
        Minimum observations for the earliest inner origin.
    inner_stride : int
        Spacing between internal evaluation origins.

    Returns
    -------
    tuple of float, int
        Minimizing alpha (stable preference for smaller alpha in a tie)
        and count of internal forecast origins.

    Raises
    ------
    ValueError
        Invalid length, horizon or candidate gains.
    """
    z = np.asarray(history, dtype=float)
    if (z.ndim != 1 or not np.isfinite(z).all() or horizon < 1
            or not alphas or not all(0 < a <= 1 for a in alphas)
            or cv_window < inner_min_train + horizon
            or inner_min_train < 2 or inner_stride < 1):
        raise ValueError("invalid nested CV configuration or finite training history")
    recent = z[-cv_window:]
    indices = list(range(inner_min_train - 1, len(recent) - horizon, inner_stride))
    if len(indices) < 2:
        raise ValueError("too few inner time-series CV origins")
    scores = []
    for alpha in alphas:
        errors = [
            (causal_ewma_level(recent[: origin + 1], float(alpha))
             - float(recent[origin + horizon])) ** 2
            for origin in indices
        ]
        scores.append(float(np.mean(errors)))
    winner = int(np.argmin(scores))
    return float(alphas[winner]), len(indices)


def forecast_ar1(history: np.ndarray, horizon: int, *, fit_window: int = 504) -> float:
    """Fit a causal AR(1) by OLS and recursively forecast h observation steps.

    Parameters
    ----------
    history : numpy.ndarray
        History through the outer forecast origin, not including its future.
    horizon : int
        Positive CISS observation-step horizon.
    fit_window : int
        Maximum latest training observations for AR(1) OLS.

    Returns
    -------
    float
        Out-of-sample iterative h-step AR(1) prediction.

    Raises
    ------
    ValueError
        On insufficient training, nonfinite input or invalid horizons.
    """
    z = np.asarray(history, dtype=float)
    if (z.ndim != 1 or len(z) < 30 or not np.isfinite(z).all()
            or horizon < 1 or fit_window < 30):
        raise ValueError("AR1 requires >=30 finite observations and valid horizon")
    recent = z[-fit_window:]
    design = np.column_stack((np.ones(len(recent) - 1), recent[:-1]))
    intercept, slope = np.linalg.lstsq(design, recent[1:], rcond=None)[0]
    pred = float(recent[-1])
    for _ in range(horizon):
        pred = float(intercept + slope * pred)
    return pred


def evaluate_ciss_series(
    frame: pd.DataFrame,
    *,
    start: str = "2008-01-01",
    horizons: Sequence[int] = (1, 5, 21),
    stride: int = 21,
    min_train: int = 504,
) -> pd.DataFrame:
    """Evaluate persistence, nested-CV EWMA and AR1 on matched CISS origins.

    Parameters
    ----------
    frame : pandas.DataFrame
        One CISS history with unique sorted observation_date and value.
    start : str
        Earliest outer origin date, fixed prior to evaluating outcomes.
    horizons : sequence of int
        Positive CISS *observation-step* horizons.
    stride : int
        Spacing between outer forecast origins (21 observations by default).
    min_train : int
        Minimum previous+current CISS observations at first origin.

    Returns
    -------
    pandas.DataFrame
        Per-origin forecast errors, including target observation date and
        provenance of internal alpha selection.

    Notes
    -----
    Candidate EWMA gains are optimized on earlier observations only,
    conditional on the retrospective observation series and its current
    revised values. No future observations enter the numerical forecasts.
    """
    required = {"observation_date", "value"}
    if not required <= set(frame):
        raise ValueError("missing CISS value or observation_date")
    dates = pd.to_datetime(frame["observation_date"], format="%Y-%m-%d", errors="raise")
    y = pd.to_numeric(frame["value"], errors="raise").to_numpy(dtype=float)
    if (len(y) < min_train + max(horizons) + 1 or not np.isfinite(y).all()
            or dates.isna().any() or dates.duplicated().any()
            or not dates.is_monotonic_increasing or stride < 1
            or min_train < 504 or not horizons or min(horizons) < 1
            or len(set(horizons)) != len(horizons)):
        raise ValueError("invalid CISS series, horizon or rolling-origin parameters")
    first = max(min_train - 1, int(dates.searchsorted(pd.Timestamp(start))))
    last_h = max(horizons)
    rows = []
    for origin in range(first, len(y) - last_h, stride):
        hist = y[: origin + 1]
        for h in horizons:
            actual = float(y[origin + h])
            best_alpha, folds = train_only_alpha(hist, h)
            predictions = (
                ("persistence", float(hist[-1]), None),
                ("ewma_nested_cv", causal_ewma_level(hist[-252:], best_alpha), best_alpha),
                ("ar1_ols", forecast_ar1(hist, h), None),
            )
            for method, predicted, alpha in predictions:
                rows.append({
                    "origin_date": dates.iloc[origin].strftime("%Y-%m-%d"),
                    "target_date": dates.iloc[origin + h].strftime("%Y-%m-%d"),
                    "horizon_observations": h,
                    "model": method,
                    "prediction": predicted,
                    "actual": actual,
                    "error": actual - predicted,
                    "selected_ewma_alpha": alpha,
                    "ewma_inner_cv_origins": folds if method == "ewma_nested_cv" else None,
                })
    if not rows:
        raise ValueError("no outer forecast origins available")
    return pd.DataFrame(rows)


def aggregate_forecast_scores(predictions: pd.DataFrame) -> pd.DataFrame:
    """Summarize RMSE/MAE without cross-index factor-score comparisons.

    Parameters
    ----------
    predictions : pandas.DataFrame
        Row-wise model forecasts produced by evaluate_ciss_series with
        country and series_id added to each row.

    Returns
    -------
    pandas.DataFrame
        Per-country, per-horizon, per-model matched forecast metrics.

    Raises
    ------
    ValueError
        Empty table or unequal model target grids within a country/horizon.
    """
    if predictions.empty:
        raise ValueError("no forecast predictions")
    rows = []
    for (country, h), subset in predictions.groupby(
        ["country", "horizon_observations"], sort=True,
    ):
        baseline = subset.loc[
            subset["model"] == "persistence", ["origin_date", "target_date"]
        ].sort_values(["origin_date", "target_date"]).reset_index(drop=True)
        if baseline.empty:
            raise ValueError("persistence baseline missing")
        for model, data in subset.groupby("model", sort=True):
            origins = data[["origin_date", "target_date"]].sort_values(
                ["origin_date", "target_date"],
            ).reset_index(drop=True)
            if not baseline.equals(origins):
                raise ValueError(f"unmatched targets for {country}, h={h}, {model}")
            errs = data["error"].to_numpy(dtype=float)
            rows.append({
                "country": country,
                "horizon_observations": int(h),
                "model": model,
                "n_origin_target_pairs": len(errs),
                "rmse": float(np.sqrt(np.mean(errs ** 2))),
                "mae": float(np.mean(np.abs(errs))),
            })
    return pd.DataFrame(rows)
