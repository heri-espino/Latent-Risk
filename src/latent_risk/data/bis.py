"""Strict BIS SDMX CSV parser for daily broad nominal effective exchange rates.

The SDMX observation time is NOT historical data-publication availability.
Values can be revised after updates to international trade weights.
"""
from __future__ import annotations

from io import BytesIO

import numpy as np
import pandas as pd


def parse_bis_eer_csv(body: bytes, series_id: str, start: str, end: str) -> pd.DataFrame:
    """Validate one BIS daily nominal broad NEER index, with exclusive end.

    Parameters
    ----------
    body : bytes
        Official BIS SDMX CSV response in format=csv with labels=id.
    series_id : str
        Expected BIS WS_EER identifier D.N.B.{MX,US,GB,JP,XM}.
    start, end : str
        Inclusive lower and exclusive upper ISO observation dates.

    Returns
    -------
    pandas.DataFrame
        Chronologically sorted observation_date, value pairs.

    Raises
    ------
    ValueError
        On wrong series identity or dimension, malformed/truncated API data,
        repeated dates, malformed nonmissing/nonfinite values or no finite data in the period.

    Notes
    -----
    Empty/missing OBS_VALUE cells are not fabricated, zero-filled or forwarded:
    exclude them from the numeric CSV and record their dates/counts in
    DataFrame.attrs for the immutable acquisition manifest. Reject malformed
    nonmissing values, infinities, duplicate dates and wrong SDMX series.
    Daily BIS NEER rises on appreciation, unlike USD/local bilateral quotes.
    The data can be revised; TIME_PERIOD is not a release timestamp.
    """
    codes = {"D.N.B.MX", "D.N.B.US", "D.N.B.GB", "D.N.B.JP", "D.N.B.XM"}
    if series_id not in codes:
        raise ValueError("unsupported BIS broad daily nominal index")
    try:
        # Preserve missing-value markers literally. pandas' default NA parser
        # otherwise conflates blank cells with malformed nonmissing numbers.
        raw = pd.read_csv(BytesIO(body), low_memory=False, keep_default_na=False)
    except (UnicodeError, ValueError, pd.errors.ParserError) as exc:
        raise ValueError("BIS SDMX returned unparseable CSV") from exc

    dims = {
        "FREQ": "D",
        "EER_TYPE": "N",
        "EER_BASKET": "B",
        "REF_AREA": series_id.split(".")[-1],
    }
    required = {*dims, "TIME_PERIOD", "OBS_VALUE"}
    if not required <= set(raw.columns):
        raise ValueError(
            "BIS SDMX CSV missing required dimensions, TIME_PERIOD or OBS_VALUE"
        )
    if raw.empty:
        raise ValueError("BIS SDMX CSV returned no observations")
    if any(not raw[col].astype(str).eq(expected).all()
           for col, expected in dims.items()):
        raise ValueError(f"BIS SDMX response has incorrect series dimensions: {series_id}")

    dates_text = raw["TIME_PERIOD"].astype(str)
    if not dates_text.str.fullmatch(r"\d{4}-\d{2}-\d{2}").all():
        raise ValueError("BIS daily index requires ISO YYYY-MM-DD dates")
    dates = pd.to_datetime(dates_text, format="%Y-%m-%d", errors="raise")
    if dates.duplicated().any():
        raise ValueError("BIS SDMX has duplicate observation dates")
    within = (dates >= pd.Timestamp(start)) & (dates < pd.Timestamp(end))
    if not within.any():
        raise ValueError("BIS SDMX returned no rows in requested dates")
    date_scope = dates[within]
    tokens = raw.loc[within, "OBS_VALUE"].astype(str).str.strip()
    # BIS can supply a calendar row for which no index level is published.
    # Such a row is not a zero-valued index observation.
    missing = tokens.str.lower().isin({"", ".", "..", "-", "na", "n/a", "nan", "null"})
    values = pd.to_numeric(tokens, errors="coerce")
    malformed = ~missing & (~np.isfinite(values.to_numpy(dtype=float)))
    if malformed.any():
        example_dates = date_scope.loc[malformed].dt.strftime("%Y-%m-%d").head(5)
        raise ValueError(
            "BIS SDMX has malformed or nonfinite nonmissing index values at "
            + ", ".join(example_dates.tolist())
        )
    valid = ~missing
    if not valid.any():
        raise ValueError("BIS SDMX has no finite observations in requested dates")
    if (values.loc[valid] <= 0).any():
        raise ValueError("BIS NEER index must be strictly positive")

    subset = pd.DataFrame({
        "observation_date": date_scope.loc[valid].to_numpy(),
        "value": values.loc[valid].to_numpy(dtype=float),
    }).sort_values("observation_date").reset_index(drop=True)
    missing_dates = date_scope.loc[missing].dt.strftime("%Y-%m-%d")
    subset.attrs["bis_source_rows_in_window"] = int(within.sum())
    subset.attrs["bis_missing_observation_count"] = int(missing.sum())
    subset.attrs["bis_missing_first_dates"] = missing_dates.head(10).tolist()
    subset.attrs["bis_missing_fraction"] = float(missing.mean())
    return subset
