"""Versioned retrospective five-country panel using BIS broad nominal NEER.

No archived publication vintages or cross-market close times are supplied.
Daily BIS observations are release-lagged in practice; this is *not* a
pseudo-real-time forecasting information set.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from latent_risk.data.market_features import (
    EQUITY_BY_COUNTRY,
    equity_trailing_features,
)

BIS_NEER_BY_COUNTRY = {
    "MEX": "D.N.B.MX",
    "USA": "D.N.B.US",
    "GBR": "D.N.B.GB",
    "JPN": "D.N.B.JP",
    "EA": "D.N.B.XM",
}

EQUITY_FEATURES = (
    "equity_log_return_1d",
    "equity_vol_21",
    "equity_drawdown_63",
)
NEER_FEATURES = (
    "neer_depreciation_log_return_1d",
    "neer_vol_21",
)


def neer_trailing_features(
    frame: pd.DataFrame, *, vol_window: int = 21,
) -> pd.DataFrame:
    """Derive causal nominal-effective FX depreciation and volatility.

    Parameters
    ----------
    frame : pandas.DataFrame
        Positive BIS 2020=100 index observations in strict increasing
        ISO observation-date order, with columns observation_date and value.
    vol_window : int, default 21
        Number of *reported BIS observations* (not calendar days) used
        to estimate sample standard deviation of daily log changes.

    Returns
    -------
    pandas.DataFrame
        Exact original BIS observation dates after rolling warm-up, index
        level, negative daily log change and trailing 21-return volatility.

    Raises
    ------
    ValueError
        On duplicated/unordered/invalid dates, nonpositive/nonfinite
        values or insufficient history.

    Notes
    -----
    A rise in BIS nominal effective exchange rate means appreciation, hence
    depreciation = -log(E_t/E_{t-1}). Missing dates are NEVER filled, even
    when corresponding equity markets traded on the same calendar day.
    """
    if vol_window < 2 or not {"observation_date", "value"} <= set(frame):
        raise ValueError("BIS NEER requires valid window, observation_date and value")
    dates_text = frame["observation_date"].astype(str)
    if not dates_text.str.fullmatch(r"\d{4}-\d{2}-\d{2}").all():
        raise ValueError("BIS NEER requires ISO observation dates")
    dates = pd.to_datetime(dates_text, format="%Y-%m-%d", errors="raise")
    level = pd.to_numeric(frame["value"], errors="coerce").to_numpy(dtype=float)
    if (len(level) < vol_window + 1 or dates.isna().any()
            or dates.duplicated().any() or not dates.is_monotonic_increasing
            or not np.isfinite(level).all() or np.any(level <= 0)):
        raise ValueError("BIS NEER requires increasing unique dates and finite positive levels")
    log_change = pd.Series(np.log(level)).diff()
    output = pd.DataFrame({
        "observation_date": dates.to_numpy(),
        "neer_level_2020_100": level,
        "neer_depreciation_log_return_1d": -log_change,
        "neer_vol_21": log_change.rolling(
            vol_window, min_periods=vol_window,
        ).std(ddof=1),
    })
    return output.dropna().reset_index(drop=True)


def build_bis_market_panel(
    equity_frames: dict[str, pd.DataFrame],
    bis_frames: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build independent end-of-day country features and two matched calendars.

    Parameters
    ----------
    equity_frames : dict of pandas.DataFrame
        Yahoo equity data keyed by index symbols.
    bis_frames : dict of pandas.DataFrame
        BIS daily NEER data keyed by complete SDMX series IDs.

    Returns
    -------
    tuple of pandas.DataFrame
        (country-level equity and NEER feature observations,
        five-country equity-only exact-date panel,
        five-country *complete equity plus NEER* exact-date panel).
        All joined values refer to identically labeled observation days.

    Raises
    ------
    ValueError
        On missing provider sources, invalid numeric inputs or no shared
        five-country complete observation dates.

    Notes
    -----
    The second panel preserves the historical equity-only comparison even
    where nominal effective FX is unavailable; the third is strictly
    complete-case with no interpolation or forward-fill. Same-date labels
    do NOT prove simultaneous historical availability for forecasting.
    """
    missing_equity = set(EQUITY_BY_COUNTRY.values()) - equity_frames.keys()
    missing_neer = set(BIS_NEER_BY_COUNTRY.values()) - bis_frames.keys()
    if missing_equity or missing_neer:
        raise ValueError(
            f"missing sources: equity={sorted(missing_equity)}, BIS={sorted(missing_neer)}"
        )
    long_parts: list[pd.DataFrame] = []
    common_equity: pd.DataFrame | None = None
    for country, equity_symbol in EQUITY_BY_COUNTRY.items():
        bis_key = BIS_NEER_BY_COUNTRY[country]
        eq = equity_trailing_features(equity_frames[equity_symbol])
        neer = neer_trailing_features(bis_frames[bis_key])
        eq_panel = eq.rename(columns={
            col: f"{country}_{col}" for col in EQUITY_FEATURES
        })
        if common_equity is None:
            common_equity = eq_panel
        else:
            common_equity = common_equity.merge(
                eq_panel, on="observation_date", how="inner", validate="one_to_one",
            )
        merged = eq.merge(
            neer, on="observation_date", how="left", validate="one_to_one",
        )
        merged["country"] = country
        merged["equity_symbol"] = equity_symbol
        merged["neer_series_id"] = bis_key
        long_parts.append(merged)
    long = pd.concat(long_parts, ignore_index=True).sort_values(
        ["country", "observation_date"],
    ).reset_index(drop=True)
    if common_equity is None or common_equity.empty:
        raise ValueError("no common five-country equity observation dates")
    common_equity = common_equity.sort_values(
        "observation_date",
    ).reset_index(drop=True)
    complete = common_equity.copy()
    for country in EQUITY_BY_COUNTRY:
        sub = long.loc[long["country"] == country, [
            "observation_date", *NEER_FEATURES,
        ]]
        complete = complete.merge(
            sub.rename(columns={
                col: f"{country}_{col}" for col in NEER_FEATURES
            }),
            on="observation_date", how="left", validate="one_to_one",
        )
    complete = complete.dropna().reset_index(drop=True)
    if complete.empty:
        raise ValueError("no dates have all five-country equity and BIS NEER features")
    return long, common_equity, complete
