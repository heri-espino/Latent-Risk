"""Offline tests for the local source coverage and provenance contract."""
from __future__ import annotations

import json
from hashlib import sha256

import pandas as pd
import pytest

from latent_risk.data.coverage import source_coverage


def _fixture_snapshot(root, *, corrupt: bool = False):
    """Create one synthetic successful source snapshot with valid CSV hash."""
    snap = root / "20261018T000000000000Z"
    (snap / "bis").mkdir(parents=True)
    data = pd.DataFrame({
        "observation_date": ["2020-01-02", "2020-01-03"],
        "value": [99.8, 100.3],
    })
    path = snap / "bis/D_N_B_MX.csv"
    data.to_csv(path, index=False)
    digest = sha256(path.read_bytes()).hexdigest()
    if corrupt:
        path.write_text("observation_date,value\n2020-01-02,99.9\n", encoding="utf-8")
    record = {
        "source": "bis", "country": "MEX", "id": "D.N.B.MX",
        "status": "OK", "role": "fx_effective_nominal_broad",
        "path": "bis/D_N_B_MX.csv", "n_rows": 2,
        "first_date": "2020-01-02", "last_date": "2020-01-03",
        "sha256": digest, "bis_response_sha256": "sourcebyteshash",
        "bis_missing_observation_count": 1,
    }
    (snap / "manifest.json").write_text(
        json.dumps({"records": [record]}), encoding="utf-8"
    )
    return snap


CATALOG = {
    "bis": [
        {"country": "MEX", "key": "D.N.B.MX", "role": "fx_effective_nominal_broad",
         "frequency": "daily", "unit": "Index (2020=100)", "dataset": "BIS WS_EER 1.0"},
        {"country": "USA", "key": "D.N.B.US", "role": "fx_effective_nominal_broad",
         "frequency": "daily", "unit": "Index (2020=100)"},
    ],
}


def test_coverage_requires_real_saved_bytes_and_reports_exact_span(tmp_path):
    """A verified synthetic source has dates, counts, hashes, and no release dates."""
    _fixture_snapshot(tmp_path)
    rows = source_coverage(CATALOG, tmp_path)
    assert len(rows) == 2
    mx, us = rows
    assert mx["status"] == "OK_FILE_VERIFIED"
    assert mx["first_observation_date"] == "2020-01-02"
    assert mx["last_observation_date"] == "2020-01-03"
    assert (mx["first_observation_year"], mx["last_observation_year"]) == (2020, 2020)
    assert mx["n_observations"] == 2
    assert mx["bis_missing_source_rows"] == 1
    assert mx["frequency_catalog"] == "daily"
    assert mx["dataset_version_catalog"] == "BIS WS_EER 1.0"
    assert mx["historical_first_release_available_date"] is None
    assert mx["units_live_metadata_verified"] is False
    assert us["status"] == "NEVER_REQUESTED"
    assert us["first_observation_date"] is None


def test_corrupt_csv_never_claimed_covered(tmp_path):
    """An intact-looking manifest with changed bytes must fail verification."""
    _fixture_snapshot(tmp_path, corrupt=True)
    row = source_coverage(CATALOG, tmp_path)[0]
    assert row["status"] == "FAILED_FILE_INTEGRITY"
    assert row["first_observation_date"] is None
    assert row["csv_sha256"] is None
    assert row["integrity_errors"]


def test_later_provider_failure_does_not_erase_older_success(tmp_path):
    """Latest attempt and latest valid historical snapshot are different states."""
    _fixture_snapshot(tmp_path)
    retry = tmp_path / "20261018T001000000000Z"
    retry.mkdir()
    (retry / "manifest.json").write_text(json.dumps({"records": [{
        "source": "bis", "id": "D.N.B.MX", "status": "FAILED",
        "error": "offline synthetic HTTP failure",
    }]}), encoding="utf-8")
    row = source_coverage(CATALOG, tmp_path)[0]
    assert row["status"] == "OK_FILE_VERIFIED"
    assert row["last_attempt_status"] == "FAILED"
    assert row["last_success_snapshot"] == "20261018T000000000000Z"


def test_failed_without_success_is_not_covered(tmp_path):
    retry = tmp_path / "20261018T001000000000Z"
    retry.mkdir()
    (retry / "manifest.json").write_text(json.dumps({"records": [{
        "source": "bis", "id": "D.N.B.MX", "status": "FAILED"
    }]}), encoding="utf-8")
    row = source_coverage(CATALOG, tmp_path)[0]
    assert row["status"] == "FAILED_PROVIDER"
    assert row["first_observation_date"] is None


@pytest.mark.parametrize("records", [
    [{"source": "bis", "id": "D.N.B.MX", "status": "BROKEN"}],
    [{"source": "bis", "id": "D.N.B.MX", "status": "OK"}] * 2,
])
def test_malformed_manifests_fail_closed(tmp_path, records):
    snap = tmp_path / "20261018T000000000000Z"
    snap.mkdir()
    (snap / "manifest.json").write_text(
        json.dumps({"records": records}), encoding="utf-8"
    )
    with pytest.raises(ValueError):
        source_coverage(CATALOG, tmp_path)
