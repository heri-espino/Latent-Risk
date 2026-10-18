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
        repeated dates, nonfinite values or an empty requested period.

    Notes
    -----
    Daily BIS NEER rises on appreciation, unlike USD/local bilateral quotes.
    The data can be revised; TIME_PERIOD is not a release timestamp.
    """
    codes = {"D.N.B.MX", "D.N.B.US", "D.N.B.GB", "D.N.B.JP", "D.N.B.XM"}
    if series_id not in codes:
        raise ValueError("unsupported BIS broad daily nominal index")
    try:
        raw = pd.read_csv(BytesIO(body), low_memory=False)
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
    values = pd.to_numeric(raw["OBS_VALUE"], errors="coerce")
    if values.isna().any() or not np.isfinite(values.to_numpy(dtype=float)).all():
        raise ValueError("BIS SDMX has missing or nonfinite index values")
    if (values <= 0).any():
        raise ValueError("BIS NEER index must be strictly positive")

    subset = pd.DataFrame({"observation_date": dates, "value": values})
    subset = subset.loc[
        (subset["observation_date"] >= pd.Timestamp(start))
        & (subset["observation_date"] < pd.Timestamp(end))
    ]
    if subset.empty:
        raise ValueError("BIS SDMX has no index values in requested dates")
    return subset.sort_values("observation_date").reset_index(drop=True)
