"""Synthetic-only primitives for matured forecast errors and event lead times.

These functions do not establish historical available dates, risk-index
identification, event outcomes, exchange calendars or statistical power.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import ceil, inf, isfinite
from typing import Iterable


@dataclass(frozen=True)
class MaturedForecast:
    """A forecast whose target has been observed and released.

    Parameters
    ----------
    issued_at : date
        Forecast origin (before the target's measurement date).
    target_date : date
        Date of the observation being forecast.
    available_at : date
        Earliest VERIFIED date that this target value was available.
    actual : float
        Observed value at the declared (external) release vintage.
    predicted : float
        Forecast value fixed at issued_at.
    error_scale : float
        Positive forecast-error scale estimated using data available to
        the model at the forecast origin.

    Raises
    ------
    ValueError
        If the date order, finite-value or positive-scale contract fails.

    Notes
    -----
    Checking the supplied dates cannot verify their real-world provenance.
    In particular, current-vintage backfilled targets are not point-in-time.
    """

    issued_at: date
    target_date: date
    available_at: date
    actual: float
    predicted: float
    error_scale: float

    def __post_init__(self) -> None:
        if not self.issued_at < self.target_date <= self.available_at:
            raise ValueError("Require issued_at < target_date <= available_at")
        if not all(isfinite(v) for v in (self.actual, self.predicted, self.error_scale)):
            raise ValueError("Values and error_scale must be finite")
        if self.error_scale <= 0:
            raise ValueError("error_scale must be positive")

    @property
    def surprise(self) -> float:
        """Unsigned standardized surprise, observable only at available_at."""
        return abs(self.actual - self.predicted) / self.error_scale


def calibration_cutoff(
    matured: Iterable[MaturedForecast], *, decision_at: date, alpha: float = 0.05
) -> float:
    """Calibrate a strict alert cutoff exclusively from prior matured errors.

    Parameters
    ----------
    matured : Iterable[MaturedForecast]
        Calibration observations, all released strictly before decision_at.
        No look-ahead rows are discarded silently; an invalid row raises.
    decision_at : date
        Date on which the already calibrated threshold can be used.
    alpha : float
        Desired nominal exceedance budget. Valid only for 0 < alpha < 1.

    Returns
    -------
    float
        Rank-ceiling empirical threshold; +infinity if a finite-sample
        (n+1)-rank requires an unavailable calibration order statistic.

    Raises
    ------
    ValueError
        Empty calibration, invalid alpha, or future information.

    Notes
    -----
    This is the order-statistic cutoff, not a guarantee of finite-sample
    false-positive coverage under serially correlated market errors.
    """
    if not 0 < alpha < 1 or not isfinite(alpha):
        raise ValueError("alpha must be finite and strictly between 0 and 1")
    rows = list(matured)
    if not rows:
        raise ValueError("calibration must not be empty")
    if any(row.available_at >= decision_at for row in rows):
        raise ValueError("calibration includes a target unavailable before decision_at")
    scores = sorted(row.surprise for row in rows)
    rank = ceil((len(scores) + 1) * (1 - alpha))
    return scores[rank - 1] if rank <= len(scores) else inf


def first_event_lead_days(
    available_alert_dates: Iterable[date], *,
    event_onset: date,
    lookback_days: int = 30,
) -> int | None:
    """Return longest strictly positive lead among pre-onset alerts.

    Parameters
    ----------
    available_alert_dates : Iterable[date]
        Date each alert was actually observable, NOT forecast issue dates.
    event_onset : date
        Independently documented event-anchor date.
    lookback_days : int
        Positive calendar-day lookback; for publication metrics use
        exchange-specific eligible sessions instead.

    Returns
    -------
    int or None
        Calendar-day lead from earliest eligible alert to event_onset,
        or None if no valid pre-onset alert exists.

    Raises
    ------
    ValueError
        If lookback_days is not a positive integer.

    Notes
    -----
    This helper cannot determine prior ongoing-stress contamination,
    censoring, session calendars, episode independence or source times.
    """
    if type(lookback_days) is not int or lookback_days <= 0:
        raise ValueError("lookback_days must be a positive integer")
    leads = [
        (event_onset - alert_date).days
        for alert_date in available_alert_dates
        if 1 <= (event_onset - alert_date).days <= lookback_days
    ]
    return max(leads) if leads else None
