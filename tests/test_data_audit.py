"""Tests covering multi-snapshot coverage aggregation."""
from scripts.audit_downloads import audit


def test_audit_records_latest_success_without_losing_failed_attempt():
    catalog = {
        "fred": [{"country": "USA", "role": "rate_10y", "series": "DGS10"}],
        "ecb": [{"country": "EA", "role": "money_m1", "key": "BSI.M.TEST"}],
    }
    manifests = [
        ("20261016", {"records": [
            {"source": "fred", "id": "DGS10", "status": "OK",
             "n_rows": 50, "first_date": "2000-01-01", "last_date": "2004-01-01"}
        ]}),
        ("20261017", {"records": [
            {"source": "fred", "id": "DGS10", "status": "FAILED", "error": "timeout"}
        ]}),
    ]
    rows = audit(catalog, manifests)
    assert len(rows) == 2
    assert rows[0]["result"] == "OK"
    assert rows[0]["last_attempt"] == "FAILED"
    assert rows[0]["last_date"] == "2004-01-01"
    assert rows[1]["result"] == "NEVER_REQUESTED"
