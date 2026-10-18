"""Past-only equity and foreign-exchange features for a *descriptive* market pilot.

Every value is derived from the current or earlier observation for that
instrument. This does NOT establish the exact intraday publication time,
original historical provider vintage or cross-exchange close synchronization.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

EQUITY_BY_COUNTRY = {
    "MEX": "^MXX",
    "USA": "^GSPC",
    "GBR": "^FTSE",
    "JPN": "^N225",
    "EA": "^STOXX50E",
}
# Direction +1 if the quote is local units per USD, -1 if USD per local unit.
# Positive fx_depreciation_log_return denotes local-currency depreciation.
FX_BY_COUNTRY = {
    "MEX": ("MXN=X", +1),
    "GBR": ("GBPUSD=X", -1),
    "JPN": ("JPY=X", +1),
    "EA": ("EURUSD=X", -1),
}
STRESS_REFERENCES = {
    ("ecb", "CISS.D.U2.Z0Z.4F.EC.SS_CIN.IDX"): "EA",
    ("ecb", "CISS.D.US.Z0Z.4F.EC.SS_CIN.IDX"): "USA",
    ("ecb", "CISS.D.GB.Z0Z.4F.EC.SS_CIN.IDX"): "GBR",
    ("fred", "STLFSI4"): "USA",
    ("fred", "NFCI"): "USA",
}


def _checked_close(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate positive dated Close prices without reordering observations.

    Parameters
    ----------
    frame : pandas.DataFrame
        Saved Yahoo daily frame with ISO observation_date and Close fields.

    Returns
    -------
    pandas.DataFrame
        A copy containing only observation_date and close.

    Raises
    ------
    ValueError
        On invalid dates, duplicate/nonmonotone observations, prices <= 0,
        nonfinite prices, or fewer than 64 observations.
    """
    if not {"observation_date", "Close"} <= set(frame.columns):
        raise ValueError("market frame must include observation_date and Close")
    dt = pd.to_datetime(frame["observation_date"], format="%Y-%m-%d", errors="raise")
    price = pd.to_numeric(frame["Close"], errors="raise")
    if (len(frame) < 64 or dt.isna().any() or dt.duplicated().any()
            or not dt.is_monotonic_increasing):
        raise ValueError("market frame requires >=64 unique sorted dates")
    if (not np.isfinite(price.to_numpy(dtype=float)).all()
            or (price <= 0).any()):
        raise ValueError("market equity/FX Close must be finite and positive")
    return pd.DataFrame({
        "observation_date": dt.to_numpy(),
        "close": price.to_numpy(dtype=float),
    })


def equity_trailing_features(
    frame: pd.DataFrame, *, vol_window: int = 21, drawdown_window: int = 63,
) -> pd.DataFrame:
    """Compute one-day log return, trailing volatility and peak-to-date drawdown.

    The 21-session standard deviation uses returns ending *at* the dated close.
    The 63-observation running peak includes the current session. No future
    observations, full-sample normalizations, or extrapolations are used.

    Parameters
    ----------
    frame : pandas.DataFrame
        Strictly positive market Close prices.
    vol_window : int
        Trailing count of log returns for sample standard deviation (ddof=1).
    drawdown_window : int
        Trailing count of actual equity observations for rolling maximum.

    Returns
    -------
    pandas.DataFrame
        observation_date, equity_log_return_1d, equity_vol_21,
        equity_drawdown_63; rows before the full warmup are removed.
    """
    if vol_window < 2 or drawdown_window < 2:
        raise ValueError("windows must be >=2 observations")
    x = _checked_close(frame)
    r = np.log(x["close"]).diff()
    peak = x["close"].rolling(drawdown_window, min_periods=drawdown_window).max()
    result = pd.DataFrame({
        "observation_date": x["observation_date"],
        "equity_log_return_1d": r,
        "equity_vol_21": r.rolling(vol_window, min_periods=vol_window).std(ddof=1),
        "equity_drawdown_63": 1 - x["close"] / peak,
    })
    return result.dropna().reset_index(drop=True)


def fx_trailing_features(
    frame: pd.DataFrame, *, direction: int, vol_window: int = 21,
) -> pd.DataFrame:
    """Compute signed local depreciation and trailing FX volatility.

    Parameters
    ----------
    frame : pandas.DataFrame
        Positive FX quotes with observation_date and Close.
    direction : int
        +1 for USD/local (USD strength is local depreciation);
        -1 for local/USD (USD strength is negative log return).
    vol_window : int
        Rolling count of daily FX log returns.

    Returns
    -------
    pandas.DataFrame
        observation_date, fx_depreciation_log_return_1d, fx_vol_21.
        Values are computed from present/past close observations only.
    """
    if direction not in {-1, +1} or vol_window < 2:
        raise ValueError("direction must be +/-1 and window >= 2")
    x = _checked_close(frame)
    ret = np.log(x["close"]).diff()
    result = pd.DataFrame({
        "observation_date": x["observation_date"],
        "fx_depreciation_log_return_1d": direction * ret,
        "fx_vol_21": ret.rolling(vol_window, min_periods=vol_window).std(ddof=1),
    })
    return result.dropna().reset_index(drop=True)


def build_country_market_panel(
    frames: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Construct unscaled country features and exact-calendar equity intersection.

    Parameters
    ----------
    frames : dict of pandas.DataFrame
        Vendor-symbol-keyed, previously integrity-audited source frames.

    Returns
    -------
    tuple of pandas.DataFrame
        First: long country-specific equity and optional FX features.
        Second: all-five-country exact matching equity observation dates
        with explicit country-prefixed feature columns.

    Raises
    ------
    ValueError
        If any required equity or FX source is missing or date uniqueness fails.

    Notes
    -----
    This is an END-OF-DAY retrospective panel, not point-in-time market close
    timestamp verification. US FX columns remain missing by design.
    """
    requested = set(EQUITY_BY_COUNTRY.values())
    requested.update(item[0] for item in FX_BY_COUNTRY.values())
    missing = requested - set(frames)
    if missing:
        raise ValueError(f"missing required daily market source(s): {sorted(missing)}")

    long_parts: list[pd.DataFrame] = []
    equity_parts: list[pd.DataFrame] = []
    for country, symbol in EQUITY_BY_COUNTRY.items():
        eq = equity_trailing_features(frames[symbol])
        eq["country"] = country
        eq["equity_symbol"] = symbol
        # Intersection means the cross-country result is not forward-filled.
        equity_parts.append(eq[[
            "observation_date", "equity_log_return_1d",
            "equity_vol_21", "equity_drawdown_63",
        ]].rename(columns={
            col: f"{country}_{col}"
            for col in ("equity_log_return_1d", "equity_vol_21", "equity_drawdown_63")
        }))
        if country in FX_BY_COUNTRY:
            fx_symbol, direction = FX_BY_COUNTRY[country]
            fx = fx_trailing_features(frames[fx_symbol], direction=direction)
            eq = eq.merge(fx, on="observation_date", how="left", validate="one_to_one")
            eq["fx_symbol"] = fx_symbol
        else:
            eq["fx_depreciation_log_return_1d"] = float("nan")
            eq["fx_vol_21"] = float("nan")
            eq["fx_symbol"] = ""
        long_parts.append(eq)
    long = pd.concat(long_parts, ignore_index=True).sort_values(
        ["country", "observation_date"],
    ).reset_index(drop=True)
    common = equity_parts[0]
    for other in equity_parts[1:]:
        common = common.merge(
            other, on="observation_date", how="inner", validate="one_to_one",
        )
    common = common.sort_values("observation_date").reset_index(drop=True)
    if common.empty:
        raise ValueError("no common five-country equity observations after warmup")
    return long, common
