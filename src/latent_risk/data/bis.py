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


def summarize_bis_payload(body: bytes, series_id: str, start: str, end: str) -> dict:
    """Summarize a BIS CSV response without retaining its licensed observations.

    Parameters
    ----------
    body : bytes
        BIS response bytes (kept only in memory).
    series_id : str
        Expected nominal broad daily EER key.
    start, end : str
        Inclusive start and exclusive end as ISO dates.

    Returns
    -------
    dict
        Bounded counts and up to five ISO dates per error class. Never raw
        market values, HTTP credentials, complete rows, or payload contents.

    Notes
    -----
    This is a diagnostic, not a substitute for strict series validation.
    It cannot prove that a missing marker represents an officially justified
    holiday without observing the vendor documentation and payload.
    """
    import csv
    import math
    from io import StringIO

    report: dict = {
        "diagnostic_kind": "BOUNDED_BIS_CSV_METADATA_NOT_RAW_PAYLOAD",
        "response_bytes": len(body),
        "rows_total": 0,
        "rows_in_window": 0,
        "explicit_missing_rows": 0,
        "malformed_nonmissing_rows": 0,
        "nonpositive_rows": 0,
        "wrong_dimensions_or_row_width": 0,
        "bad_date_rows": 0,
        "first_missing_dates": [],
        "first_malformed_dates": [],
        "format_issue": None,
    }
    try:
        content = body.decode("utf-8-sig")
        reader = csv.DictReader(StringIO(content), strict=True)
        required = {
            "FREQ", "EER_TYPE", "EER_BASKET", "REF_AREA",
            "TIME_PERIOD", "OBS_VALUE",
        }
        if not required.issubset(set(reader.fieldnames or [])):
            report["format_issue"] = "missing_required_columns"
            return report
        for row in reader:
            report["rows_total"] += 1
            if None in row or any(value is None for value in row.values()):
                report["wrong_dimensions_or_row_width"] += 1
                continue
            if (
                row["FREQ"] != "D" or row["EER_TYPE"] != "N"
                or row["EER_BASKET"] != "B"
                or row["REF_AREA"] != series_id.rsplit(".", 1)[-1]
            ):
                report["wrong_dimensions_or_row_width"] += 1
                continue
            day = row["TIME_PERIOD"]
            try:
                parsed = pd.to_datetime(day, format="%Y-%m-%d", errors="raise")
                if parsed.strftime("%Y-%m-%d") != day:
                    raise ValueError("non-ISO date")
            except (ValueError, TypeError):
                report["bad_date_rows"] += 1
                continue
            if not start <= day < end:
                continue
            report["rows_in_window"] += 1
            token = row["OBS_VALUE"].strip()
            if token.lower() in {"", ".", "..", "-", "na", "n/a", "nan", "null"}:
                report["explicit_missing_rows"] += 1
                if len(report["first_missing_dates"]) < 5:
                    report["first_missing_dates"].append(day)
                continue
            try:
                value = float(token)
                if not math.isfinite(value):
                    raise ValueError("nonfinite")
            except ValueError:
                report["malformed_nonmissing_rows"] += 1
                if len(report["first_malformed_dates"]) < 5:
                    report["first_malformed_dates"].append(day)
                continue
            if value <= 0:
                report["nonpositive_rows"] += 1
    except (UnicodeError, csv.Error):
        report["format_issue"] = "unparseable_csv"
    return report
