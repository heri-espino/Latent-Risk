"""Read-only per-series coverage from user-held immutable source snapshots.

Reported dates describe observed data in saved files, not release-time vintages.
No source is downloaded and no historical availability date is inferred.
"""
from __future__ import annotations

import json
from pathlib import Path

from latent_risk.data.quality import inspect_source_file

SOURCES = ("market", "fred", "banxico", "ecb", "boe", "boj", "bis")


def source_coverage(catalog: dict, snapshots: Path) -> list[dict]:
    """Audit each catalog series against local manifests and saved CSV hashes.

    Parameters
    ----------
    catalog : dict
        Existing source catalog, with per-provider arrays.
    snapshots : pathlib.Path
        Root containing immutable timestamped acquisition directories.

    Returns
    -------
    list of dict
        Machine-readable statuses, observed date spans, units and frequencies.
        A successful source is reported OK_FILE_VERIFIED only if local source
        integrity checks pass.

    Raises
    ------
    ValueError
        If a manifest is malformed, including repeated series entries.
    OSError
        If a manifest cannot be read.
    """
    history: dict[tuple[str, str], list[tuple[Path, dict]]] = {}
    for path in sorted(snapshots.glob("*/manifest.json")):
        manifest = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or not isinstance(manifest.get("records"), list):
            raise ValueError(f"invalid acquisition manifest: {path}")
        seen: set[tuple[str, str]] = set()
        for record in manifest["records"]:
            if not isinstance(record, dict):
                raise ValueError(f"invalid acquisition record: {path}")
            key = (record.get("source"), record.get("id"))
            if not all(isinstance(part, str) and part for part in key):
                raise ValueError(f"invalid source identifier in: {path}")
            if key in seen:
                raise ValueError(f"duplicate source record in: {path}: {key}")
            seen.add(key)
            if record.get("status") not in {"OK", "FAILED"}:
                raise ValueError(f"invalid source status in: {path}: {key}")
            history.setdefault(key, []).append((path.parent, record))

    output = []
    for provider in SOURCES:
        for entry in catalog.get(provider, []):
            identifier = entry.get("symbol", entry.get("key", entry.get("series")))
            if not isinstance(identifier, str) or not identifier:
                raise ValueError(f"catalog has missing identifier: {provider}")
            attempts = history.get((provider, identifier), [])
            successful = [attempt for attempt in attempts if attempt[1]["status"] == "OK"]
            latest = attempts[-1] if attempts else None
            stored = successful[-1] if successful else None
            qa = inspect_source_file(*stored) if stored else None
            if qa:
                status = (
                    "OK_FILE_VERIFIED" if qa["status"] == "PASS"
                    else "FAILED_FILE_INTEGRITY"
                )
            elif latest:
                status = "FAILED_PROVIDER"
            else:
                status = "NEVER_REQUESTED"
            first = qa.get("first_date") if qa and qa["status"] == "PASS" else None
            last = qa.get("last_date") if qa and qa["status"] == "PASS" else None
            output.append({
                "source": provider,
                "country": entry.get("country", "UNKNOWN"),
                "id": identifier,
                "role": entry.get("role", "UNKNOWN"),
                "frequency_catalog": entry.get(
                    "frequency", "daily" if provider == "market" else "UNKNOWN"
                ),
                "units_catalog": entry.get("units", entry.get("unit", "UNKNOWN")),
                "units_live_metadata_verified": False,
                "dataset_version_catalog": entry.get("dataset", "UNKNOWN"),
                "status": status,
                "last_attempt_status": latest[1]["status"] if latest else "NONE",
                "last_attempt_snapshot": latest[0].name if latest else None,
                "last_success_snapshot": stored[0].name if stored else None,
                "first_observation_date": first,
                "last_observation_date": last,
                "first_observation_year": int(first[:4]) if first else None,
                "last_observation_year": int(last[:4]) if last else None,
                "n_observations": qa.get("rows") if first else None,
                "csv_sha256": stored[1].get("sha256") if first else None,
                "response_sha256": (
                    stored[1].get("bis_response_sha256") if provider == "bis" and first
                    else None
                ),
                "bis_missing_source_rows": (
                    stored[1].get("bis_missing_observation_count")
                    if provider == "bis" and first else None
                ),
                "integrity_errors": qa["errors"] if qa else [],
                "evidence": (
                    "LOCAL_SNAPSHOT_MANIFEST_AND_CSV_SHA256"
                    if first else "NO_VERIFIED_LOCAL_CSV"
                ),
                "historical_first_release_available_date": None,
                "vintage_status": "CURRENT_REVISED_HISTORY_NOT_FIRST_RELEASE",
            })
    return output
