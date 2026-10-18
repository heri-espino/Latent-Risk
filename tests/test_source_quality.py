"""Offline tests for immutable raw-source integrity verification."""
from __future__ import annotations

import hashlib
import json

import pandas as pd

from latent_risk.data.quality import (
    audit_source_integrity,
    inspect_source_file,
    latest_successful_records,
)


def _make_record(snapshot, *, values=(1.0, 2.0), kind="fred", filename="DGS10"):
    """Write fixture CSV and valid metadata into an isolated fake snapshot."""
    subfolder = snapshot / kind
    subfolder.mkdir(parents=True, exist_ok=True)
    path = subfolder / f"{filename}.csv"
    pd.DataFrame({
        "observation_date": ["2020-01-01", "2020-01-02"],
        "Close" if kind == "market" else "value": values,
    }).to_csv(path, index=False)
    return {
        "source": kind, "country": "USA", "id": filename, "role": "rate_10y",
        "status": "OK", "path": f"{kind}/{filename}.csv",
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "n_rows": 2, "first_date": "2020-01-01", "last_date": "2020-01-02",
    }


def test_valid_snapshot_has_matching_hash_and_dates(tmp_path):
    snapshot = tmp_path / "20261017"
    record = _make_record(snapshot)
    result = inspect_source_file(snapshot, record)
    assert result["status"] == "PASS"
    assert result["rows"] == 2
    assert result["first_date"] == "2020-01-01"


def test_snapshot_detects_modification_and_duplicates(tmp_path):
    snapshot = tmp_path / "20261017"
    record = _make_record(snapshot)
    path = snapshot / "fred/DGS10.csv"
    path.write_text("observation_date,value\n2020-01-01,1\n2020-01-01,2\n")
    result = inspect_source_file(snapshot, record)
    assert result["status"] == "FAIL"
    assert any("SHA256" in issue for issue in result["errors"])
    assert any("duplicate" in issue for issue in result["errors"])


def test_snapshot_prevents_relative_path_escape(tmp_path):
    result = inspect_source_file(
        tmp_path / "folder",
        {"source": "fred", "id": "DGS10", "path": "../outside.csv"},
    )
    assert result["status"] == "FAIL"
    assert "unsafe" in result["errors"][0]


def test_nonpositive_market_close_fails(tmp_path):
    snapshot = tmp_path / "20261017"
    record = _make_record(snapshot, kind="market", values=(100.0, 0.0))
    result = inspect_source_file(snapshot, record)
    assert result["status"] == "FAIL"
    assert any("strictly positive" in issue for issue in result["errors"])


def test_negative_wti_futures_close_is_reviewable_not_corruption(tmp_path):
    snapshot = tmp_path / "20261017"
    record = _make_record(snapshot, kind="market", filename="CL_F",
                          values=(18.27, -37.63))
    record.update({"id": "CL=F", "role": "global_oil", "price_domain": "signed"})
    result = inspect_source_file(snapshot, record)
    assert result["status"] == "PASS"
    assert result["nonpositive_close_count"] == 1
    assert result["minimum_close"] == -37.63
    assert result["minimum_close_date"] == "2020-01-02"
    assert result["nonpositive_close_first_dates"] == ["2020-01-02"]
    assert any("log returns" in warning for warning in result["warnings"])


def test_legacy_wti_manifest_without_price_domain_is_reviewable(tmp_path):
    """Older raw manifests remain immutable but must use WTI price semantics."""
    snapshot = tmp_path / "20261017"
    record = _make_record(snapshot, kind="market", filename="CL_F",
                          values=(18.27, -37.63))
    record.update({"id": "CL=F", "role": "global_oil"})
    assert "price_domain" not in record
    result = inspect_source_file(snapshot, record)
    assert result["status"] == "PASS"
    assert result["price_domain"] == "signed"
    assert result["warnings"]


def test_zero_wti_futures_close_is_allowed_with_warning(tmp_path):
    snapshot = tmp_path / "20261017"
    record = _make_record(snapshot, kind="market", filename="CL_F",
                          values=(18.27, 0.0))
    record.update({"id": "CL=F", "role": "global_oil", "price_domain": "signed"})
    result = inspect_source_file(snapshot, record)
    assert result["status"] == "PASS"
    assert result["nonpositive_close_count"] == 1
    assert result["warnings"]


def test_negative_unmarked_equity_close_remains_failure(tmp_path):
    snapshot = tmp_path / "20261017"
    record = _make_record(snapshot, kind="market", filename="GSPC",
                          values=(100.0, -2.0))
    result = inspect_source_file(snapshot, record)
    assert result["status"] == "FAIL"
    assert "market close prices must be strictly positive" in result["errors"]


def test_invalid_market_price_domain_fails(tmp_path):
    snapshot = tmp_path / "20261017"
    record = _make_record(snapshot, kind="market", filename="CL_F",
                          values=(1.0, 2.0))
    record["price_domain"] = "unrestricted_and_unreviewed"
    result = inspect_source_file(snapshot, record)
    assert result["status"] == "FAIL"
    assert any("price_domain" in error for error in result["errors"])


def test_bad_manifest_count_fails(tmp_path):
    snapshot = tmp_path / "20261017"
    record = _make_record(snapshot)
    record["n_rows"] = 4
    result = inspect_source_file(snapshot, record)
    assert any("row count" in issue for issue in result["errors"])


def test_select_latest_success_and_ignore_later_failed(tmp_path):
    first = tmp_path / "20261017"
    record = _make_record(first)
    (first / "manifest.json").write_text(json.dumps({"records": [record]}))
    second = tmp_path / "20261018"
    second.mkdir()
    (second / "manifest.json").write_text(json.dumps({"records": [
        {"source": "fred", "id": "DGS10", "status": "FAILED", "error": "timeout"}
    ]}))
    selected = latest_successful_records(tmp_path)
    assert len(selected) == 1
    assert selected[0][0] == first
    report = audit_source_integrity(tmp_path)
    assert report["series_audited"] == 1
    assert report["passes"] == 1


def test_malformed_dates_and_missing_values_rejected(tmp_path):
    snapshot = tmp_path / "20261017"
    record = _make_record(snapshot)
    path = snapshot / "fred/DGS10.csv"
    path.write_text("observation_date,value\n2020-01-01,1\nnot-a-date,\n")
    record["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    result = inspect_source_file(snapshot, record)
    assert result["status"] == "FAIL"
    assert any("dates" in issue or "date" in issue for issue in result["errors"])
    assert result["missing_or_nonfinite_values"] == 1
