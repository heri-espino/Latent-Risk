"""Read-only integrity validation for local vendor snapshots.

No download happens here. Historical release-date validity and economic
cross-country comparability are NOT established by these integrity checks.
"""
from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

import numpy as np
import pandas as pd


def latest_successful_records(snapshots: Path) -> list[tuple[Path, dict]]:
    """Return each provider/ID's most recent successful manifest record.

    Parameters
    ----------
    snapshots : pathlib.Path
        Root containing immutable timestamped directories with manifest.json.

    Returns
    -------
    list of tuple
        Pairs of snapshot directory and successful metadata, sorted by
        provider and identifier.

    Notes
    -----
    Older failed download attempts do not invalidate a successful snapshot.
    Entries absent from manifests cannot be audited.
    """
    selected: dict[tuple[str, str], tuple[Path, dict]] = {}
    for manifest_path in sorted(snapshots.glob("*/manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for record in manifest.get("records", []):
            if record.get("status") == "OK":
                key = (str(record["source"]), str(record["id"]))
                selected[key] = (manifest_path.parent, record)
    return [selected[key] for key in sorted(selected)]


def inspect_source_file(snapshot: Path, record: dict) -> dict:
    """Validate file, SHA256, dates, values and manifest consistency.

    Parameters
    ----------
    snapshot : pathlib.Path
        Root of the immutable download containing the record's CSV.
    record : dict
        Original successful manifest record.

    Returns
    -------
    dict
        Machine-readable integrity outcome and basic coverage statistics.
        No raw time-series observations are included.

    Notes
    -----
    Hash and row checks test snapshot integrity, NOT whether source values
    were accurate or accessible at a historical forecast origin.
    """
    result = {
        "source": str(record.get("source", "")),
        "country": str(record.get("country", "")),
        "id": str(record.get("id", "")),
        "role": str(record.get("role", "")),
        "snapshot": snapshot.name,
        "status": "FAIL",
        "errors": [],
        "warnings": [],
    }
    errors = result["errors"]
    warnings = result["warnings"]
    relative = Path(str(record.get("path", "")))
    root = snapshot.resolve()
    path = (root / relative).resolve()
    if (not record.get("path") or not path.is_relative_to(root)
            or path.suffix.lower() != ".csv"):
        errors.append("unsafe or missing CSV path")
        return result
    if not path.is_file():
        errors.append("CSV file missing")
        return result
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != record.get("sha256"):
        errors.append("CSV SHA256 does not match download manifest")
    try:
        data = pd.read_csv(path, low_memory=False)
    except (OSError, ValueError, UnicodeError, pd.errors.ParserError):
        errors.append("CSV could not be parsed")
        return result

    if "observation_date" not in data.columns:
        errors.append("CSV lacks observation_date")
        return result

    dates_text = data["observation_date"].astype(str)
    if not dates_text.str.fullmatch(r"\d{4}-\d{2}-\d{2}").all():
        errors.append("observation dates are not ISO YYYY-MM-DD")
    dates = pd.to_datetime(dates_text, format="%Y-%m-%d", errors="coerce")
    if dates.isna().any():
        errors.append("invalid observation date")
    if dates.duplicated().any():
        errors.append("duplicate observation dates")
    if not dates.is_monotonic_increasing:
        errors.append("observation dates out of order")

    value_col = "Close" if record.get("source") == "market" else "value"
    if value_col not in data.columns:
        errors.append(f"CSV lacks {value_col} column")
        return result
    values = pd.to_numeric(data[value_col], errors="coerce")
    bad_values = ~np.isfinite(values.to_numpy(dtype=float))
    result["missing_or_nonfinite_values"] = int(bad_values.sum())
    if bad_values.any():
        errors.append(f"missing or nonfinite {value_col} observations")

    result["rows"] = int(len(data))
    if len(data) != record.get("n_rows"):
        errors.append("CSV row count differs from manifest")
    if len(data) == 0:
        errors.append("empty CSV")
    if len(data) and not dates.isna().any():
        first = dates.iloc[0].strftime("%Y-%m-%d")
        last = dates.iloc[-1].strftime("%Y-%m-%d")
        result["first_date"] = first
        result["last_date"] = last
        if first != record.get("first_date") or last != record.get("last_date"):
            errors.append("CSV first/last dates differ from manifest")
        if len(dates) > 1:
            result["largest_calendar_gap_days"] = int(dates.diff().dt.days.max())

    is_price = record.get("source") == "market"
    if is_price and not bad_values.any():
        # Old immutable download manifests predate the explicit catalog field.
        # Their metadata must remain untouched, so apply a narrowly scoped
        # historical instrument policy for the known signed WTI futures series.
        domain = record.get("price_domain")
        if domain is None:
            domain = (
                "signed"
                if result["id"] == "CL=F" and result["role"] == "global_oil"
                else "strictly_positive"
            )
        result["price_domain"] = domain
        if domain not in {"strictly_positive", "signed"}:
            errors.append(f"unknown market close price_domain: {domain}")
        nonpositive = values <= 0
        result["nonpositive_close_count"] = int(nonpositive.sum())
        if nonpositive.any():
            positions = np.flatnonzero(nonpositive.to_numpy())
            result["nonpositive_close_first_dates"] = [
                dates.iloc[int(i)].strftime("%Y-%m-%d") if not pd.isna(dates.iloc[int(i)])
                else str(data.iloc[int(i)]["observation_date"])
                for i in positions[:10]
            ]
            minimum_index = values.idxmin()
            result["minimum_close"] = float(values.loc[minimum_index])
            result["minimum_close_date"] = str(data.loc[minimum_index, "observation_date"])
            if domain == "signed":
                warnings.append(
                    f"{result['nonpositive_close_count']} nonpositive signed futures "
                    f"closes; first dates {', '.join(result['nonpositive_close_first_dates'])}; "
                    "verify contract rolls/vendor adjustments; never apply ordinary log returns"
                )
            else:
                errors.append("market close prices must be strictly positive")
        role = result["role"]
        if role in {"local_equity", "regional_equity"} or role.startswith("fx_"):
            if (values > 0).all():
                jumps = np.log(values).diff().abs() > 0.4
                result["daily_log_moves_over_40pct"] = int(jumps.sum())
                if jumps.any():
                    warnings.append("extreme market moves: review ticker adjustments")
    if len(data) and len(data) < 50:
        warnings.append("short observed series: less than 50 observations")

    result["status"] = "PASS" if not errors else "FAIL"
    return result


def audit_source_integrity(snapshots: Path) -> dict:
    """Validate every successfully downloaded vendor file from local manifests.

    Parameters
    ----------
    snapshots : pathlib.Path
        Location of the user-held immutable download snapshots.

    Returns
    -------
    dict
        Per-series outcomes, counts and explicit scientific limitations.

    Raises
    ------
    FileNotFoundError
        If no successful source series has been downloaded.
    """
    selected = latest_successful_records(snapshots)
    if not selected:
        raise FileNotFoundError("no successful download records found")
    records = [inspect_source_file(path, record) for path, record in selected]
    passes = sum(row["status"] == "PASS" for row in records)
    return {
        "schema_version": 1,
        "series_audited": len(records),
        "passes": passes,
        "failures": len(records) - passes,
        "warnings": sum(bool(row["warnings"]) for row in records),
        "limitations": [
            "Integrity verification does not establish historical availability dates.",
            "Nonpositive signed futures prices can be genuine; they require contract-roll review and forbid ordinary log returns.",
            "Missing trading sessions, revisions and corporate adjustments need separate audits.",
            "Different country source definitions are not necessarily comparable.",
            "Published CISS and STLFSI4/NFCI remain external reference indices.",
        ],
        "series": records,
    }
