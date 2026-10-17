"""Offline tests for the raw-source downloader; never contact Yahoo/FRED/Banxico."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from latent_risk.data.acquisition import (
    acquire,
    _parse_dates,
    _slug,
    normalize_market_frame,
    parse_banxico_series,
    parse_fred_csv,
    parse_fred_api,
)


def test_fred_filters_dates_and_missing_values():
    body = b"observation_date,DGS10\n2020-01-01,.\n2020-01-02,1.88\n2020-01-03,1.80\n"
    panel = parse_fred_csv(body, "2020-01-02", "2020-01-03")
    assert len(panel) == 1
    assert panel["value"].tolist() == [1.88]


def test_fred_rejects_empty_and_html():
    with pytest.raises(ValueError, match="no observations"):
        parse_fred_csv(b"DATE,SERIES\n2020-01-01,.\n", "2020-01-01", "2020-02-01")
    with pytest.raises(ValueError):
        parse_fred_csv(b"<html>not CSV</html>", "2020-01-01", "2020-02-01")


def test_yahoo_monthly_historical_dates_are_not_invented():
    dates = pd.to_datetime(["2020-01-30", "2020-01-31", "2020-02-03"])
    frame = pd.DataFrame({"Close": [100, 102, 103], "Volume": [10, 11, 12]}, index=dates)
    cleaned = normalize_market_frame(frame, "2020-01-01", "2020-02-01")
    assert cleaned["observation_date"].dt.strftime("%Y-%m-%d").tolist() == [
        "2020-01-30", "2020-01-31"
    ]
    assert cleaned["Close"].tolist() == [100, 102]


def test_banxico_parses_comma_numbers_and_exclusive_end():
    data = {
        "bmx": {
            "series": [
                {"idSerie": "SF43718", "datos": [
                    {"fecha": "31/01/2020", "dato": "18.72"},
                    {"fecha": "01/02/2020", "dato": "18.73"},
                    {"fecha": "07/02/2020", "dato": "N/E"},
                ]}
            ]
        }
    }
    cleaned = parse_banxico_series(data, "SF43718", "2020-01-01", "2020-02-01")
    assert len(cleaned) == 1
    assert float(cleaned.iloc[0]["value"]) == 18.72


def test_parse_dates_raises_for_reverse_window():
    with pytest.raises(ValueError):
        _parse_dates("2020-02-01", "2020-01-01")


def test_slug_safe():
    assert _slug("^GSPC") == "GSPC"
    assert _slug("CL=F") == "CL_F"
    assert _slug("DX-Y.NYB") == "DX_Y_NYB"


def test_catalog_contains_all_five_country_equities():
    import json

    root = Path(__file__).resolve().parents[1]
    catalog = json.loads((root / "data/source_catalog.json").read_text(encoding="utf-8"))
    equities = {
        entry["country"] for entry in catalog["market"] if entry["role"] == "local_equity"
        or entry["role"] == "regional_equity"
    }
    assert equities == {"MEX", "USA", "GBR", "JPN", "EA"}
    assert catalog["important_gaps"]


def test_fred_official_api_parser_filters_missing_and_exclusive_end():
    response = {
        "count": 4, "offset": 0,
        "observations": [
            {"date": "2019-12-31", "value": "2.3"},
            {"date": "2020-01-01", "value": "."},
            {"date": "2020-01-02", "value": "1.8"},
            {"date": "2020-02-01", "value": "1.9"},
        ],
    }
    frame = parse_fred_api(response, "2020-01-01", "2020-02-01")
    assert frame["value"].tolist() == [1.8]
    assert frame.iloc[0]["observation_date"].strftime("%Y-%m-%d") == "2020-01-02"


def test_fred_api_rejects_truncation_and_duplicates():
    with pytest.raises(ValueError, match="truncated"):
        parse_fred_api(
            {"count": 2, "offset": 0, "observations": [{"date": "2020-01-01", "value": "1"}]},
            "2020-01-01", "2021-01-01",
        )
    with pytest.raises(ValueError, match="duplicate"):
        parse_fred_api(
            {"count": 2, "offset": 0, "observations": [
                {"date": "2020-01-01", "value": "1"},
                {"date": "2020-01-01", "value": "2"},
            ]},
            "2020-01-01", "2021-01-01",
        )


def test_fred_api_requires_key_before_creating_snapshot(tmp_path):
    with pytest.raises(ValueError, match="FRED_API_KEY"):
        acquire(
            {"fred": [{"series": "DGS10"}]}, start="2020-01-01", end="2021-01-01",
            snapshot=tmp_path / "none", sources={"fred"}, fred_backend="api",
        )
    assert not (tmp_path / "none").exists()


def test_fred_api_key_never_persisted_on_request_failure(monkeypatch, tmp_path, capsys):
    import json
    import requests

    secret = "secret-test-key-do-not-store"
    class FakeSession:
        def get(self, url, *, params, timeout):
            assert url == "https://api.stlouisfed.org/fred/series/observations"
            assert params["api_key"] == secret
            assert params["observation_end"] == "2020-01-31"
            assert timeout == 45
            raise requests.exceptions.ConnectionError(f"request failed: ?api_key={secret}")
        def close(self):
            pass

    monkeypatch.setattr("latent_risk.data.acquisition._session", FakeSession)
    snapshot = tmp_path / "snapshot"
    outcome = acquire(
        {"fred": [{"series": "DGS10", "country": "USA"}]},
        start="2020-01-01", end="2020-02-01", snapshot=snapshot,
        sources={"fred"}, fred_backend="api", fred_api_key=secret,
        only_ids={"DGS10"},
    )
    output = capsys.readouterr()
    on_disk = (snapshot / "manifest.json").read_text()
    assert outcome["counts"] == {"success": 0, "failure": 1, "requested": 1}
    assert secret not in on_disk
    assert secret not in output.out
    assert secret not in output.err
    manifest = json.loads(on_disk)
    assert "url" not in manifest["records"][0]
    assert manifest["fred_backend"] == "api"


def test_fred_only_unknown_series_rejected_before_snapshot(tmp_path):
    with pytest.raises(ValueError, match="unknown series"):
        acquire(
            {"fred": [{"series": "DGS10"}]}, start="2020-01-01", end="2021-01-01",
            snapshot=tmp_path / "none", sources={"fred"}, only_ids={"DGS100"},
        )
    assert not (tmp_path / "none").exists()
