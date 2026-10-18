"""Forecast diagnostics and chronologically valid, source-free evaluation.

Public API separates raw retrospective observation histories from genuine
point-in-time data availability; neither is inferred from a file's date alone.
"""
from .backtesting import BacktestConfig, Candidate, ForecastFamily, Forecaster, run_backtest
from .baselines import AR1OLS, OneSidedEWMA, Persistence, VolatilityAdjustedPersistence, baseline_families
from .errors import forecast_errors, standardized_errors
from .scoring import hac_loss_differentials, score_matched

__all__ = [
    "AR1OLS",
    "BacktestConfig",
    "Candidate",
    "ForecastFamily",
    "Forecaster",
    "OneSidedEWMA",
    "Persistence",
    "VolatilityAdjustedPersistence",
    "baseline_families",
    "forecast_errors",
    "hac_loss_differentials",
    "run_backtest",
    "score_matched",
    "standardized_errors",
]
