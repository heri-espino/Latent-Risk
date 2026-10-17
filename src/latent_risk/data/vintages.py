"""Long-form indicator data with separate observation and availability dates."""
from __future__ import annotations

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = (
    "country", "observation_date", "available_date", "variable", "value", "source"
)


def validate_long_panel(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate point-in-time indicator-table schema and chronological ordering.

    Parameters
    ----------
    frame : pandas.DataFrame
        One row per country/observation_date/variable. Required columns:
        country, observation_date, available_date, variable, value, source.

    Returns
    -------
    pandas.DataFrame
        Copy with parsed datetime values and finite numeric measurement.

    Raises
    ------
    ValueError
        For missing fields, invalid or empty values, duplicates, nonfinite
        observations, or availability preceding observation.

    Notes
    -----
    This routine checks *user supplied* publication dates. It does not verify
    external data-vintage provenance, historical revisions or licensed sources.
    """
    missing = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError("missing required columns: " + ", ".join(missing))
    data = frame.copy()
    for name in ("country", "variable", "source"):
        if data[name].isna().any() or (data[name].astype(str).str.strip() == "").any():
            raise ValueError(f"{name} must be non-empty")
        data[name] = data[name].astype(str).str.strip()
    for name in ("observation_date", "available_date"):
        try:
            data[name] = pd.to_datetime(data[name], errors="raise")
        except (ValueError, TypeError) as exc:
            raise ValueError(f"invalid {name}") from exc
        if data[name].isna().any():
            raise ValueError(f"{name} has missing dates")
        if getattr(data[name].dt, "tz", None) is not None:
            raise ValueError("date fields must be timezone-naive; document release timezone")
    if (data["available_date"] < data["observation_date"]).any():
        raise ValueError("available_date cannot precede observation_date")
    try:
        data["value"] = pd.to_numeric(data["value"], errors="raise")
    except (TypeError, ValueError) as exc:
        raise ValueError("value must be numeric") from exc
    if not np.isfinite(data["value"].to_numpy(dtype=float)).all():
        raise ValueError("value must be finite")
    if data.duplicated(["country", "observation_date", "variable"]).any():
        raise ValueError("duplicate country/observation_date/variable key")
    return data


def available_as_of(frame: pd.DataFrame, origin: str | pd.Timestamp) -> pd.DataFrame:
    """Select measurements actually published by the specified forecast origin.

    Parameters
    ----------
    frame : pandas.DataFrame
        Valid long-form panel or unvalidated copy in the same schema.
    origin : str or pandas.Timestamp
        Forecast date in ISO `YYYY-MM-DD` or timestamp form.

    Returns
    -------
    pandas.DataFrame
        Rows published on or before the origin, in canonical chronological
        order. This function does not estimate a model.

    Raises
    ------
    ValueError
        On malformed panel or invalid origin.

    Examples
    --------
    >>> import pandas as pd
    >>> from latent_risk.data import available_as_of
    >>> panel = pd.DataFrame([dict(country="MEX", observation_date="2020-01-31",
    ...     available_date="2020-02-07", variable="m2", value=1.0, source="Banxico")])
    >>> len(available_as_of(panel, "2020-01-31"))
    0
    """
    data = validate_long_panel(frame)
    try:
        as_of = pd.Timestamp(origin)
    except (ValueError, TypeError) as exc:
        raise ValueError("invalid origin") from exc
    if as_of.tzinfo is not None:
        raise ValueError("origin must be timezone-naive")
    if pd.isna(as_of):
        raise ValueError("origin must not be NaT")
    filtered = data.loc[data["available_date"] <= as_of].copy()
    return filtered.sort_values(["country", "observation_date", "variable"]).reset_index(drop=True)
