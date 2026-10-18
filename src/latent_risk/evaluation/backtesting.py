"""Chronological, source-free forecast evaluation with nested selection.

The only numerical input to a forecaster is a training prefix assembled as of
its forecast origin. Implement complete preprocessing *inside* fit(), including
scaling, factor extraction, cross-country weights, trend fitting and thresholds.

This protects against future numerical values, not against revised historical
vintages, data snooping in target definitions, or unknown publication times.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal, Protocol

import numpy as np
import pandas as pd

VintagePolicy = Literal["current_vintage", "provided_release_dates"]


class Forecaster(Protocol):
    """Fit a fresh, unfitted estimator at an explicit cutoff and predict a positive-step horizon.

    Every fit receives only a finite chronological one-dimensional history ending
    at or before its explicit cutoff. Factories must not retain global training
    state or access full-sample arrays. Exogenous and multi-country pipelines
    require a separately reviewed, origin-filtered adapter.
    """

    def fit(self, history: np.ndarray, *, cutoff: str) -> "Forecaster":
        """Refit all estimator parameters and transformations on history alone."""
        ...

    def predict(self, horizon: int) -> float:
        """Predict the level h *observed target points* after the origin."""
        ...


@dataclass(frozen=True)
class Candidate:
    """One immutable hyperparameter setting; factory returns an unfitted model."""

    key: str
    factory: Callable[[], Forecaster]


@dataclass(frozen=True)
class ForecastFamily:
    """Named competitor with choices selected on *inner* historical origins."""

    name: str
    candidates: tuple[Candidate, ...]


@dataclass(frozen=True)
class BacktestConfig:
    """Immutable chronology specification and explicit data-vintage policy.

    Parameters
    ----------
    horizons : tuple of int
        Forecast horizons in *observed target points*, not calendar days.
    first_origin : str
        Minimum outer origin date (inclusive).
    min_train : int
        Minimum as-of available target observations in each outer fit.
    stride : int
        Outer origin step count in the original observed target index.
    train_window : int or None
        Most recent observations to retain per fit; None is expanding.
    inner_min_train : int
        Minimum training observations per inner fit.
    inner_stride : int
        Inner origin spacing in observed points.
    inner_window : int or None
        Optional bound for each inner training history; None uses train_window.
    vintage_policy : {"current_vintage", "provided_release_dates"}
        Current-vintage observations are explicitly NOT genuine historical
        release vintages. Supplied release dates are not independently verified.
    horizon_unit : str
        Dataset-specific observation-unit label.
    """

    horizons: tuple[int, ...] = (1, 5, 21)
    first_origin: str = "2008-01-01"
    min_train: int = 504
    stride: int = 21
    train_window: int | None = None
    inner_min_train: int = 252
    inner_stride: int = 21
    inner_window: int | None = None
    vintage_policy: VintagePolicy = "current_vintage"
    horizon_unit: str = "observed_CISS_points"


def _dates(column: pd.Series, name: str) -> pd.Series:
    if column.isna().any():
        raise ValueError(f"{name} has missing dates")
    try:
        result = pd.to_datetime(column, format="%Y-%m-%d", errors="raise")
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid {name}") from exc
    if result.isna().any() or result.dt.tz is not None:
        raise ValueError(f"invalid or timezone-aware {name}")
    return result.reset_index(drop=True)


def _observations(frame: pd.DataFrame, policy: VintagePolicy) -> pd.DataFrame:
    required = {"observation_date", "value"}
    if not required.issubset(frame.columns) or frame.empty:
        raise ValueError("nonempty observation_date and value required")
    if policy not in ("current_vintage", "provided_release_dates"):
        raise ValueError("unknown vintage_policy")
    dates = _dates(frame["observation_date"], "observation_date")
    if dates.duplicated().any() or not dates.is_monotonic_increasing:
        raise ValueError("observation dates must be unique and increasing")
    try:
        values = pd.to_numeric(frame["value"], errors="raise").to_numpy(dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid target values") from exc
    if not np.isfinite(values).all():
        raise ValueError("target must be finite")
    if policy == "provided_release_dates":
        if "available_date" not in frame:
            raise ValueError("release-aware mode requires available_date")
        available = _dates(frame["available_date"], "available_date")
        if (available < dates).any():
            raise ValueError("available_date precedes observation_date")
    else:
        # Deliberately discard any supplied timestamps in retrospective mode:
        # they must not confer a spurious point-in-time claim.
        available = dates.copy()
    return pd.DataFrame({"date": dates, "available": available, "value": values})


def _check(config: BacktestConfig, families: tuple[ForecastFamily, ...]) -> None:
    if (
        not config.horizons or any(type(h) is not int or h < 1 for h in config.horizons)
        or len(set(config.horizons)) != len(config.horizons)
        or config.min_train < 3 or config.inner_min_train < 3
        or config.inner_min_train >= config.min_train
        or config.stride < 1 or config.inner_stride < 1
        or (config.train_window is not None and config.train_window < config.min_train)
        or (config.inner_window is not None
            and config.inner_window < config.inner_min_train)
        or not config.horizon_unit.strip()
        or not families or len({f.name for f in families}) != len(families)
    ):
        raise ValueError("invalid backtesting configuration or model names")
    if any(
        not family.name.strip() or not family.candidates
        or len({c.key for c in family.candidates}) != len(family.candidates)
        or any(not c.key.strip() for c in family.candidates)
        for family in families
    ):
        raise ValueError("invalid model family or hyperparameter keys")
    try:
        pd.Timestamp(config.first_origin)
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid first_origin") from exc


def _as_of(data: pd.DataFrame, date: pd.Timestamp, window: int | None) -> np.ndarray:
    past = data.loc[
        (data["date"] <= date) & (data["available"] <= date), "value"
    ].to_numpy(dtype=float)
    return past if window is None else past[-window:]


def _fresh_forecast(candidate: Candidate, history: np.ndarray, h: int, cutoff: str) -> float:
    model = candidate.factory()
    # Defensive private copy: avoid a mutating estimator changing shared data.
    fitted = model.fit(history.copy(), cutoff=cutoff)
    result = float(fitted.predict(h))
    if not np.isfinite(result):
        raise ValueError(f"nonfinite forecast from candidate {candidate.key}")
    return result


def _select(
    data: pd.DataFrame,
    outer_index: int,
    outer_date: pd.Timestamp,
    horizon: int,
    family: ForecastFamily,
    config: BacktestConfig,
) -> tuple[Candidate, int]:
    """Score inner candidates only on targets released by the outer origin."""
    inner_window = config.train_window if config.inner_window is None else config.inner_window
    folds: list[tuple[np.ndarray, float, str]] = []
    for j in range(config.inner_min_train - 1, outer_index - horizon + 1,
                   config.inner_stride):
        as_of = data["date"].iloc[j]
        target = data.iloc[j + horizon]
        if target["date"] > outer_date or target["available"] > outer_date:
            continue
        history = _as_of(data, as_of, inner_window)
        if len(history) >= config.inner_min_train:
            folds.append((history, float(target["value"]), as_of.strftime("%Y-%m-%d")))
    if len(folds) < 2:
        raise ValueError(
            f"insufficient *released* inner targets for {family.name} "
            f"at {outer_date.date()}, horizon {horizon}"
        )
    scored: list[tuple[float, str, Candidate]] = []
    for candidate in family.candidates:
        errors = [
            (_fresh_forecast(candidate, past, horizon, cutoff) - actual) ** 2
            for past, actual, cutoff in folds
        ]
        scored.append((float(np.mean(errors)), candidate.key, candidate))
    winner = min(scored, key=lambda entry: (entry[0], entry[1]))
    return winner[2], len(folds)


def run_backtest(
    observations: pd.DataFrame,
    *,
    country: str,
    target_id: str,
    target_scale: str,
    families: tuple[ForecastFamily, ...],
    config: BacktestConfig = BacktestConfig(),
) -> pd.DataFrame:
    """Generate fully nested expanding- or rolling-origin level forecasts.

    Parameters
    ----------
    observations : pandas.DataFrame
        Sorted unique observation_date/value; in provided_release_dates mode,
        also available_date. Dates use ISO YYYY-MM-DD at end-of-day.
    country, target_id, target_scale : str
        Nonempty target identity; factor scale and vintage MUST remain explicit.
    families : tuple of ForecastFamily
        Every candidate is a *new* estimator at every fit. No full-sample
        normalizations or externally prefitted factor/smoother parameters.
    config : BacktestConfig
        Prespecified outer and inner origin rules and availability policy.

    Returns
    -------
    pandas.DataFrame
        One row per country/target/horizon/origin/family on a matched grid.
        Forecast errors are actual minus prediction.

    Raises
    ------
    ValueError
        Invalid chronology, unavailable inner targets, insufficient training,
        nonfinite predictions or inconsistent configurations.

    Notes
    -----
    Target horizon h counts rows in the observation-index calendar, not elapsed
    calendar days. An as-of date filter prevents direct future observations.
    Data with historical revisions remain *current-vintage* unless real first-
    release snapshots are separately established and supplied.
    """
    families = tuple(families)
    _check(config, families)
    if any(not x or not x.strip() for x in (country, target_id, target_scale)):
        raise ValueError("country, target_id and target_scale must be explicit")
    data = _observations(observations, config.vintage_policy)
    first_date = pd.Timestamp(config.first_origin)
    last_h = max(config.horizons)
    if len(data) < config.min_train + last_h:
        raise ValueError("insufficient series length")
    first = max(config.min_train - 1, int(data["date"].searchsorted(first_date)))
    rows: list[dict] = []
    for i in range(first, len(data) - last_h, config.stride):
        as_of = data["date"].iloc[i]
        past = _as_of(data, as_of, config.train_window)
        if len(past) < config.min_train:
            continue
        fit_dates = data.loc[
            (data["date"] <= as_of) & (data["available"] <= as_of), "date"
        ]
        fit_last = fit_dates.iloc[-1].strftime("%Y-%m-%d")
        fit_first = fit_dates.iloc[-len(past)].strftime("%Y-%m-%d")
        for h in config.horizons:
            target = data.iloc[i + h]
            for family in families:
                selected, n_inner = _select(data, i, as_of, h, family, config)
                predicted = _fresh_forecast(selected, past, h, as_of.strftime("%Y-%m-%d"))
                actual = float(target["value"])
                rows.append({
                    "country": country,
                    "target_id": target_id,
                    "target_scale": target_scale,
                    "vintage_mode": config.vintage_policy,
                    "origin_date": as_of.strftime("%Y-%m-%d"),
                    "target_date": target["date"].strftime("%Y-%m-%d"),
                    "horizon": h,
                    "horizon_unit": config.horizon_unit,
                    "model": family.name,
                    "candidate": selected.key,
                    "inner_folds": n_inner,
                    "train_n": len(past),
                    "train_start_date": fit_first,
                    "fit_cutoff_date": fit_last,
                    "as_of_date": as_of.strftime("%Y-%m-%d"),
                    "actual": actual,
                    "prediction": predicted,
                    "error": actual - predicted,
                })
    if not rows:
        raise ValueError("no eligible outer forecast origins")
    return pd.DataFrame(rows)
