"""Simple matched-target level forecasts for chronological evaluation.

These are source-free engineering baselines, NOT estimated stress factors.
The volatility-adjusted persistence forecast is an upward-stress heuristic,
not a claim that volatility alone is an unbiased conditional-mean forecast.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .backtesting import Candidate, ForecastFamily


def _history(values: np.ndarray, minimum: int) -> np.ndarray:
    z = np.asarray(values, dtype=float)
    if z.ndim != 1 or len(z) < minimum or not np.isfinite(z).all():
        raise ValueError(f"forecaster requires {minimum} finite chronological points")
    return z.copy()


def _horizon(horizon: int) -> None:
    if type(horizon) is not int or horizon < 1:
        raise ValueError("horizon must be a positive observed-point integer")


@dataclass
class Persistence:
    """Forecast the last released/observed value unchanged."""

    last_: float | None = None

    def fit(self, history: np.ndarray) -> "Persistence":
        self.last_ = float(_history(history, 1)[-1])
        return self

    def predict(self, horizon: int) -> float:
        _horizon(horizon)
        if self.last_ is None:
            raise ValueError("unfitted persistence model")
        return self.last_


@dataclass
class AR1OLS:
    """OLS AR(1) on the latest training-only observations, recursively h ahead."""

    window: int = 504
    intercept_: float | None = None
    slope_: float | None = None
    last_: float | None = None

    def fit(self, history: np.ndarray) -> "AR1OLS":
        if self.window < 30:
            raise ValueError("AR(1) window must be >=30")
        z = _history(history, 30)[-self.window:]
        design = np.column_stack((np.ones(len(z) - 1), z[:-1]))
        a, b = np.linalg.lstsq(design, z[1:], rcond=None)[0]
        self.intercept_, self.slope_, self.last_ = float(a), float(b), float(z[-1])
        return self

    def predict(self, horizon: int) -> float:
        _horizon(horizon)
        if self.last_ is None or self.intercept_ is None or self.slope_ is None:
            raise ValueError("unfitted AR(1) model")
        value = self.last_
        for _ in range(horizon):
            value = self.intercept_ + self.slope_ * value
        return float(value)


@dataclass
class OneSidedEWMA:
    """Training-only recursive EWMA with a constant h-step level forecast."""

    alpha: float = 0.25
    level_: float | None = None

    def fit(self, history: np.ndarray) -> "OneSidedEWMA":
        if not 0 < self.alpha <= 1:
            raise ValueError("EWMA alpha must be in (0,1]")
        z = _history(history, 1)
        level = float(z[0])
        for value in z[1:]:
            level += self.alpha * (float(value) - level)
        self.level_ = level
        return self

    def predict(self, horizon: int) -> float:
        _horizon(horizon)
        if self.level_ is None:
            raise ValueError("unfitted EWMA model")
        return self.level_


@dataclass
class VolatilityAdjustedPersistence:
    """Level forecast y_t + loading * std(Δy) * sqrt(h).

    std(Δy) uses the last `window` first differences available at the
    origin. An explicitly asymmetric stress-tail heuristic, not a pure
    conditional-mean volatility model; compare on the SAME level targets.
    """

    window: int = 21
    loading: float = 0.5
    last_: float | None = None
    vol_: float | None = None

    def fit(self, history: np.ndarray) -> "VolatilityAdjustedPersistence":
        if self.window < 2 or not np.isfinite(self.loading):
            raise ValueError("invalid volatility window or loading")
        z = _history(history, self.window + 1)
        self.last_ = float(z[-1])
        self.vol_ = float(np.std(np.diff(z[-self.window - 1:]), ddof=0))
        return self

    def predict(self, horizon: int) -> float:
        _horizon(horizon)
        if self.last_ is None or self.vol_ is None:
            raise ValueError("unfitted volatility baseline")
        return float(self.last_ + self.loading * self.vol_ * np.sqrt(horizon))


def baseline_families() -> tuple[ForecastFamily, ...]:
    """Return predetermined persistence, AR, EWMA, and volatility competitors.

    EWMA gains are selected by inner origin CV, NOT using outer-target values.
    AR(1) and volatility alternatives use the same exact outer origin/target grid.
    Factories create new estimators with no previously learned state.
    """
    alphas = (0.05, 0.1, 0.25, 0.5, 0.85, 1.0)
    return (
        ForecastFamily("persistence", (Candidate("last", Persistence),)),
        ForecastFamily("ar1_ols", (Candidate("ar1_504", AR1OLS),)),
        ForecastFamily(
            "ewma_nested",
            tuple(Candidate(f"alpha_{a:g}", lambda a=a: OneSidedEWMA(a)) for a in alphas),
        ),
        ForecastFamily(
            "volatility_adjusted_persistence",
            (
                Candidate("window_21_loading_0.5",
                          lambda: VolatilityAdjustedPersistence(21, 0.5)),
                Candidate("window_63_loading_0.5",
                          lambda: VolatilityAdjustedPersistence(63, 0.5)),
            ),
        ),
    )
