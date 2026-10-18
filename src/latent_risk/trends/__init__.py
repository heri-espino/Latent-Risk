"""Gaussian second-difference smoothing, diffuse REML and causal trend forecasts."""

from .gaussian import (
    REMLFit,
    TrendFilter,
    TrendForecast,
    effective_degrees_of_freedom,
    filter_local_linear,
    fit_reml,
    forecast_at_origin,
    forecast_with_reml,
    penalized_trend,
    second_difference,
    smooth_local_linear,
)

__all__ = [
    "REMLFit",
    "TrendFilter",
    "TrendForecast",
    "effective_degrees_of_freedom",
    "filter_local_linear",
    "fit_reml",
    "forecast_at_origin",
    "forecast_with_reml",
    "penalized_trend",
    "second_difference",
    "smooth_local_linear",
]
