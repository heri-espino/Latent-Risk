"""Diagnostics for one immutable, retrospective market-feature pilot.

This module validates generated files, observation-date intersections, source
separation, and empirical missingness. It does NOT establish availability at
historical intraday forecast origins, nor estimate/forecast a risk factor.
"""
from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

import numpy as np
import pandas as pd

from latent_risk.data.market_features import EQUITY_BY_COUNTRY, FX_BY_COUNTRY, STRESS_REFERENCES

EQUITY_COLUMNS = (
    "equity_log_return_1d", "equity_vol_21", "equity_drawdown_63",
)
FX_COLUMNS = ("fx_depreciation_log_return_1d", "fx_vol_21")


def _dated(frame: pd.DataFrame, label: str) -> pd.DataFrame:
    """Parse strict unique ISO dates without filling or relabeling them.

    Parameters
    ----------
    frame : pandas.DataFrame
        CSV records containing observation_date.
    label : str
        Identifier for descriptive error messages.

    Returns
    -------
    pandas.DataFrame
        Copy with datetime64 observation_date.

    Raises
    ------
    ValueError
        When dates are invalid.
    """
    if "observation_date" not in frame:
        raise ValueError(f"{label} missing observation_date")
    dates = frame["observation_date"].astype(str)
    if not dates.str.fullmatch(r"\d{4}-\d{2}-\d{2}").all():
        raise ValueError(f"{label} has non-ISO observation dates")
    copy = frame.copy()
    copy["observation_date"] = pd.to_datetime(
        dates, format="%Y-%m-%d", errors="raise",
    )
    return copy


def audit_market_pilot(directory: Path) -> dict:
    """Inspect existing market pilot CSVs against their immutable manifest.

    Parameters
    ----------
    directory : pathlib.Path
        Timestamped output produced by scripts/build_market_pilot.py.

    Returns
    -------
    dict
        Counts, source consistency, FX missingness, exact calendar coverage,
        same-date reference overlaps, and explicit methodological limitations.

    Raises
    ------
    ValueError
        On unexpected schema, hashes, duplicate days, invalid numbers,
        mismatched country/date intersection, or reference source leakage.
    """
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("status") != "DESCRIPTIVE_MARKET_FEATURES_NO_FORECAST":
        raise ValueError("unexpected data-preparation manifest status")
    expected_files = {
        "country_market_features.csv",
        "five_country_common_equity_dates.csv",
        "external_stress_references.csv",
    }
    if set(manifest.get("outputs", {})) != expected_files:
        raise ValueError("pilot manifest output list does not match expected schema")
    frames = {}
    for name in sorted(expected_files):
        path = directory / name
        if sha256(path.read_bytes()).hexdigest() != manifest["outputs"][name]["sha256"]:
            raise ValueError(f"generated CSV hash mismatch: {name}")
        frame = pd.read_csv(path, low_memory=False)
        if len(frame) != manifest["outputs"][name]["rows"]:
            raise ValueError(f"generated CSV row count mismatch: {name}")
        frames[name] = _dated(frame, name)

    market = frames["country_market_features.csv"]
    common = frames["five_country_common_equity_dates.csv"]
    refs = frames["external_stress_references.csv"]

    required_market = {"country", "equity_symbol", "fx_symbol", *EQUITY_COLUMNS, *FX_COLUMNS}
    if not required_market <= set(market):
        raise ValueError("country-market schema lacks required features")
    required_refs = {"country", "provider", "series_id", "value"}
    if not required_refs <= set(refs):
        raise ValueError("reference schema lacks required identifier or value")
    if set(market["country"]) != set(EQUITY_BY_COUNTRY):
        raise ValueError("market panel has unexpected country set")
    if market.duplicated(["country", "observation_date"]).any():
        raise ValueError("country-market panel duplicates country/date")
    if common["observation_date"].duplicated().any():
        raise ValueError("common equity dates are duplicated")
    if refs.duplicated(["provider", "series_id", "observation_date"]).any():
        raise ValueError("published reference has duplicate series dates")
    if len(common) == 0 or len(market) == 0 or len(refs) == 0:
        raise ValueError("empty market or reference dataset")
    for name, frame in (
        ("country market", market), ("common equity", common), ("external reference", refs),
    ):
        numeric = list(EQUITY_COLUMNS) if name == "country market" else (
            ["value"] if name == "external reference" else [
                col for col in common.columns if col != "observation_date"
            ]
        )
        for col in numeric:
            if col not in frame:
                raise ValueError(f"{name} missing numeric column {col}")
            values = pd.to_numeric(frame[col], errors="coerce")
            if not np.isfinite(values.to_numpy(dtype=float)).all():
                raise ValueError(f"{name}/{col} contains nonfinite values")

    observed_refs = set(zip(refs["provider"], refs["series_id"], strict=True))
    if observed_refs != set(STRESS_REFERENCES):
        raise ValueError("reference dataset has unexpected or missing benchmark series")
    for reference in manifest["input_sources"]:
        key = (reference["source"], reference["id"])
        if key in STRESS_REFERENCES and reference.get("role") not in {
            "external_stress_benchmark", "external_conditions_benchmark",
        }:
            raise ValueError("reference source is not marked as a benchmark")
    country_details = {}
    all_dates: set[pd.Timestamp] | None = None
    for country, symbol in EQUITY_BY_COUNTRY.items():
        data = market.loc[market.country == country].sort_values("observation_date")
        if len(data) == 0 or not data["equity_symbol"].eq(symbol).all():
            raise ValueError(f"{country} has incorrect equity mapping")
        if not data["observation_date"].is_monotonic_increasing:
            raise ValueError(f"{country} equity dates not sorted")
        dates = set(data["observation_date"])
        all_dates = dates if all_dates is None else all_dates & dates
        fx_na = data[list(FX_COLUMNS)].isna()
        if country == "USA":
            if not data["fx_symbol"].fillna("").eq("").all() or not fx_na.all().all():
                raise ValueError("USA must have no fictitious FX quote")
            fx_symbol = None
            complete = 0
            missing = None
        else:
            fx_symbol = FX_BY_COUNTRY[country][0]
            if not data["fx_symbol"].eq(fx_symbol).all():
                raise ValueError(f"{country} has incorrect FX mapping")
            if not fx_na.iloc[:, 0].equals(fx_na.iloc[:, 1]):
                raise ValueError(f"{country} FX pair missingness is inconsistent")
            available = data["fx_vol_21"].notna()
            for col in FX_COLUMNS:
                values = pd.to_numeric(data.loc[available, col], errors="coerce")
                if not np.isfinite(values.to_numpy(dtype=float)).all():
                    raise ValueError(f"{country} contains nonfinite FX feature values")
            complete = int(available.sum())
            missing = int((~available).sum())
        country_details[country] = {
            "equity_symbol": symbol,
            "rows": int(len(data)),
            "start": data["observation_date"].iloc[0].strftime("%Y-%m-%d"),
            "end": data["observation_date"].iloc[-1].strftime("%Y-%m-%d"),
            "fx_symbol": fx_symbol,
            "fx_complete_rows": complete,
            "fx_missing_rows": missing,
            "fx_coverage": (
                round(complete / len(data), 6) if country != "USA" else None
            ),
        }

    intersection = all_dates if all_dates is not None else set()
    if set(common["observation_date"]) != intersection:
        raise ValueError("five-country common dates are not the exact equity intersection")
    # Validate feature values too, not just dates: the common panel must be
    # precisely the matching equity values from each country-specific series.
    for country in EQUITY_BY_COUNTRY:
        by_date = market.loc[market.country == country].set_index("observation_date")
        for column in EQUITY_COLUMNS:
            expected = by_date.loc[common["observation_date"], column].to_numpy(dtype=float)
            actual_col = f"{country}_{column}"
            if actual_col not in common:
                raise ValueError(f"common panel lacks {actual_col}")
            actual = pd.to_numeric(common[actual_col], errors="coerce").to_numpy(dtype=float)
            if not np.allclose(actual, expected, rtol=1e-12, atol=1e-12):
                raise ValueError(f"common panel disagrees with country data: {actual_col}")

    ref_details = {}
    for (provider, code), country in STRESS_REFERENCES.items():
        data = refs.loc[(refs.provider == provider) & (refs.series_id == code)]
        if not data["country"].eq(country).all():
            raise ValueError(f"benchmark {code} has incorrect country")
        dates = set(data["observation_date"])
        country_market_dates = set(market.loc[
            market.country == country, "observation_date",
        ])
        ref_details[code] = {
            "country": country,
            "provider": provider,
            "observations": int(len(data)),
            "market_same_date_overlap": int(len(dates & country_market_dates)),
            "earliest_date": data["observation_date"].min().strftime("%Y-%m-%d"),
            "latest_date": data["observation_date"].max().strftime("%Y-%m-%d"),
        }

    return {
        "status": "DESCRIPTIVE_PILOT_DIAGNOSTIC_ONLY",
        "source_snapshot": directory.name,
        "source_git_commit": manifest.get("git_commit"),
        "raw_input_count": len(manifest.get("input_sources", [])),
        "country_market_rows": int(len(market)),
        "common_five_equity_dates": {
            "count": int(len(common)),
            "start": common["observation_date"].min().strftime("%Y-%m-%d"),
            "end": common["observation_date"].max().strftime("%Y-%m-%d"),
            "fraction_of_equity_sessions_by_country": {
                country: round(len(common) / x["rows"], 6)
                for country, x in country_details.items()
            },
        },
        "reference_rows": int(len(refs)),
        "country": country_details,
        "external_reference_overlap": ref_details,
        "limitations": [
            "End-of-day retrospective observations, not point-in-time release vintages.",
            "Same calendar day does NOT imply all international closes were available simultaneously.",
            "Weekly FRED benchmark values may be released after their observation-date label.",
            "Matching benchmarks by observed date measures sample overlap, NOT valid forecast timing.",
            "US FX missingness is structural; it must never be imputed as zero.",
            "Index construction, model fitting and out-of-sample forecasting have NOT occurred.",
            "Credit, bank and funding domains are still missing from a systemic-risk measurement.",
        ],
    }
