"""Parsers and request descriptors for official European and Japanese sources.

All dates are observation labels, NOT historical publication/availability dates.
Macro monthly time-period labels are represented as the first of each month
for convenience; do not use them as available_date in model backtests.
"""
from __future__ import annotations

from datetime import date
from io import BytesIO

import pandas as pd


def parse_ecb_csv(body: bytes, start: str, end: str, key: str) -> pd.DataFrame:
    """Parse a single ECB SDMX csvdata series, preserving period-label semantics.

    Parameters
    ----------
    body : bytes
        The ECB data API `format=csvdata` response.
    start, end : str
        ISO boundaries, end exclusive.
    key : str
        Expected full ECB SDMX series key, including the dataflow prefix.

    Returns
    -------
    pandas.DataFrame
        Monthly first-of-month `observation_date` labels and `value`.

    Raises
    ------
    ValueError
        On a malformed response, mismatched key, or empty result.
    """
    try:
        frame = pd.read_csv(BytesIO(body), low_memory=False)
    except (UnicodeError, ValueError, pd.errors.ParserError) as exc:
        raise ValueError("ECB did not return valid CSV") from exc
    if not {"TIME_PERIOD", "OBS_VALUE"}.issubset(frame.columns):
        raise ValueError("ECB CSV missing TIME_PERIOD or OBS_VALUE; possibly error HTML")
    if "KEY" in frame.columns and frame["KEY"].dropna().ne(key).any():
        raise ValueError("ECB returned a different series key")
    raw_periods = frame["TIME_PERIOD"].astype(str)
    if not raw_periods.str.fullmatch(r"\d{4}-\d{2}").all():
        raise ValueError("expected ECB monthly YYYY-MM periods")
    values = pd.to_numeric(frame["OBS_VALUE"], errors="coerce")
    dates = pd.to_datetime(raw_periods + "-01", format="%Y-%m-%d", errors="raise")
    result = pd.DataFrame({"observation_date": dates, "value": values})
    return _filter_observations(result, start, end, "ECB")


def parse_boe_csv(body: bytes, start: str, end: str, series: str) -> pd.DataFrame:
    """Parse a Bank of England IADB TN single-series date/value CSV.

    Parameters
    ----------
    body : bytes
        One-series IADB CSV with `DATE,<series>` header.
    start, end : str
        ISO boundaries with exclusive end.
    series : str
        Expected Bank of England series code.

    Returns
    -------
    pandas.DataFrame
        Observation dates and values.

    Raises
    ------
    ValueError
        On mismatched headers, invalid dates or empty data.
    """
    try:
        frame = pd.read_csv(BytesIO(body), dtype=str)
    except (UnicodeError, ValueError, pd.errors.ParserError) as exc:
        raise ValueError("Bank of England did not return valid CSV") from exc
    if list(frame.columns) != ["DATE", series]:
        raise ValueError("Bank of England CSV missing expected date or series header")
    dates = pd.to_datetime(frame["DATE"], format="%d %b %Y", errors="raise")
    values = pd.to_numeric(frame[series], errors="coerce")
    result = pd.DataFrame({"observation_date": dates, "value": values})
    return _filter_observations(result, start, end, "Bank of England")


def parse_boj_json(response: dict, start: str, end: str, code: str) -> pd.DataFrame:
    """Parse one BOJ getDataCode JSON time series with status and length checks.

    Parameters
    ----------
    response : dict
        BOJ JSON response, including STATUS and RESULTSET.
    start, end : str
        ISO observation boundaries with exclusive end.
    code : str
        Series code *without* DB prefix (the code query parameter).

    Returns
    -------
    pandas.DataFrame
        Monthly observation labels and values.

    Raises
    ------
    ValueError
        On BOJ logical API errors, unexpected series, malformed values or gaps
        leaving the requested period empty.
    """
    if response.get("STATUS") != 200:
        raise ValueError(f"BOJ API returned STATUS {response.get('STATUS')}")
    results = response.get("RESULTSET")
    if not isinstance(results, list):
        raise ValueError("BOJ result set missing")
    match = [item for item in results if item.get("SERIES_CODE") == code]
    if len(match) != 1:
        raise ValueError("BOJ expected exactly one matching series code")
    item = match[0]
    if item.get("FREQUENCY") != "MONTHLY":
        raise ValueError("BOJ parser expects MONTHLY series")
    obj = item.get("VALUES", {})
    periods = obj.get("SURVEY_DATES", [])
    values = obj.get("VALUES", [])
    if not isinstance(periods, list) or len(periods) != len(values):
        raise ValueError("BOJ period and value lists differ in length")
    if not all(len(str(period)) == 6 and str(period).isdigit() for period in periods):
        raise ValueError("BOJ expected YYYYMM observation periods")
    dates = pd.to_datetime(
        [f"{str(period)[:4]}-{str(period)[4:]}-01" for period in periods],
        format="%Y-%m-%d",
        errors="raise",
    )
    value_column = pd.to_numeric(pd.Series(values), errors="coerce")
    result = pd.DataFrame({"observation_date": dates, "value": value_column})
    return _filter_observations(result, start, end, "Bank of Japan")


def _filter_observations(
    frame: pd.DataFrame, start: str, end: str, provider: str
) -> pd.DataFrame:
    """Filter finite values and strictly reject duplicate observation dates."""
    start_date, end_date = date.fromisoformat(start), date.fromisoformat(end)
    frame = frame.loc[
        (frame["observation_date"] >= pd.Timestamp(start_date))
        & (frame["observation_date"] < pd.Timestamp(end_date))
    ].copy()
    frame = frame.dropna(subset=["value"])
    frame = frame.loc[frame["value"].map(lambda value: abs(value) < float("inf"))]
    if frame.empty:
        raise ValueError(f"{provider} returned no finite observations for requested window")
    if frame["observation_date"].duplicated().any():
        raise ValueError(f"{provider} returned duplicate observation dates")
    return frame.sort_values("observation_date").reset_index(drop=True)


def boe_date(iso_date: str) -> str:
    """Convert ISO date to documented IADB DD/Mon/YYYY query date."""
    return date.fromisoformat(iso_date).strftime("%d/%b/%Y")
