"""Network-free tests for official-source parsers and acquisition catalog."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from latent_risk.data.official import (
    boe_date,
    parse_boe_csv,
    parse_boj_json,
    parse_ecb_csv,
)


def test_ecb_csv_period_and_key():
    key = "BSI.M.U2.Y.V.M10.X.1.U2.2300.Z01.E"
    source = (
        f"KEY,TIME_PERIOD,OBS_VALUE\n{key},2020-01,123\n"
        f"{key},2020-02,125\n"
    ).encode()
    out = parse_ecb_csv(source, "2020-01-01", "2020-02-01", key)
    assert out["value"].tolist() == [123]
    assert out.iloc[0]["observation_date"].strftime("%Y-%m-%d") == "2020-01-01"


def test_ecb_rejects_unexpected_series():
    body = b"KEY,TIME_PERIOD,OBS_VALUE\nBSI.other,2020-01,5\n"
    with pytest.raises(ValueError, match="different"):
        parse_ecb_csv(body, "2020-01-01", "2021-01-01", "BSI.expected")


def test_boe_csv_dates_and_missing():
    body = b"DATE,LPMAUYN\n31 Jan 2020,128\n29 Feb 2020,..\n31 Mar 2020,135\n"
    out = parse_boe_csv(body, "2020-01-01", "2020-03-01", "LPMAUYN")
    assert out["value"].tolist() == [128]
    assert boe_date("2020-01-01") == "01/Jan/2020"


def test_boe_rejects_html():
    with pytest.raises(ValueError, match="missing expected"):
        parse_boe_csv(b"<html>error</html>", "2020-01-01", "2021-01-01", "LPMAUYN")


def test_boj_json_months_and_missing_values():
    payload = {
        "STATUS": 200,
        "NEXTPOSITION": None,
        "RESULTSET": [{
            "SERIES_CODE": "MAM1NAM2M2MO",
            "FREQUENCY": "MONTHLY",
            "VALUES": {
                "SURVEY_DATES": [202001, 202002, 202003],
                "VALUES": [100.0, None, 110.0],
            },
        }],
    }
    out = parse_boj_json(payload, "2020-01-01", "2020-03-01", "MAM1NAM2M2MO")
    assert out["value"].tolist() == [100.0]
    assert out.iloc[0]["observation_date"].strftime("%Y-%m-%d") == "2020-01-01"


def test_boj_non_200_error():
    with pytest.raises(ValueError, match="STATUS"):
        parse_boj_json({"STATUS": 400}, "2020-01-01", "2021-01-01", "ABC")


def test_official_catalog_contains_unique_ids():
    catalog_path = Path(__file__).resolve().parents[1] / "data/source_catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    assert len(catalog["ecb"]) == 2
    assert len(catalog["boe"]) == 2
    assert len(catalog["boj"]) == 2
    for source in ("ecb", "boe", "boj"):
        ids = [item.get("key", item.get("series")) for item in catalog[source]]
        assert len(set(ids)) == len(ids)
