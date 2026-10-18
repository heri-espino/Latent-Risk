"""Offline BIS official daily NEER parser and source acquisition checks."""
from __future__ import annotations

import json

import pytest

from latent_risk.data.acquisition import acquire
from latent_risk.data.bis import parse_bis_eer_csv, summarize_bis_payload


def bis_csv(code: str = "MX", *, date: str = "2020-01-02", value: str = "101.3") -> bytes:
    """Return a minimal source-consistent BIS v2 SDMX CSV response."""
    return (
        "STRUCTURE,STRUCTURE_ID,ACTION,FREQ,EER_TYPE,EER_BASKET,"
        "REF_AREA,TIME_PERIOD,OBS_VALUE\n"
        f"dataflow,BIS:WS_EER(1.0),I,D,N,B,{code},{date},{value}\n"
    ).encode("utf-8")


@pytest.mark.parametrize("country,code", [
    ("MEX", "D.N.B.MX"), ("USA", "D.N.B.US"),
    ("GBR", "D.N.B.GB"), ("JPN", "D.N.B.JP"),
    ("EA", "D.N.B.XM"),
])
def test_all_five_bis_daily_nominal_broad_codes(country, code):
    """Each provider country code must produce one positive index observation."""
    value = parse_bis_eer_csv(bis_csv(code.split(".")[-1]), code,
                              "2020-01-01", "2020-02-01")
    assert country
    assert len(value) == 1
    assert float(value.iloc[0]["value"]) == 101.3


def test_bis_exclusive_end_and_date_sorting():
    raw = bis_csv() + b"dataflow,BIS:WS_EER(1.0),I,D,N,B,MX,2020-02-01,102.3\n"
    frame = parse_bis_eer_csv(raw, "D.N.B.MX", "2020-01-01", "2020-02-01")
    assert len(frame) == 1
    assert frame.iloc[0]["observation_date"].strftime("%Y-%m-%d") == "2020-01-02"


@pytest.mark.parametrize("raw", [
    bis_csv("US"),
    bis_csv("MX", value="0"),
    bis_csv("MX", value="-12"),
    bis_csv("MX", value="not-a-number"),
    bis_csv("MX", date="bad-date"),
    b"<html>error</html>",
])
def test_bis_rejects_wrong_series_bad_values_dates_html(raw):
    with pytest.raises(ValueError):
        parse_bis_eer_csv(raw, "D.N.B.MX", "2020-01-01", "2020-02-01")


def test_bis_missing_calendar_values_are_dropped_with_audit_provenance():
    """Legitimate blank or missing index cells must not erase good BIS history."""
    raw = (
        bis_csv()
        + b"dataflow,BIS:WS_EER(1.0),I,D,N,B,MX,2020-01-03,\n"
        + b"dataflow,BIS:WS_EER(1.0),I,D,N,B,MX,2020-01-04,.\n"
        + b"dataflow,BIS:WS_EER(1.0),I,D,N,B,MX,2020-01-05,NA\n"
        + b"dataflow,BIS:WS_EER(1.0),I,D,N,B,MX,2020-01-06,100.5\n"
    )
    frame = parse_bis_eer_csv(raw, "D.N.B.MX", "2020-01-01", "2020-02-01")
    assert frame["value"].tolist() == [101.3, 100.5]
    assert frame["observation_date"].dt.strftime("%Y-%m-%d").tolist() == [
        "2020-01-02", "2020-01-06",
    ]
    assert frame.attrs["bis_source_rows_in_window"] == 5
    assert frame.attrs["bis_missing_observation_count"] == 3
    assert frame.attrs["bis_missing_first_dates"] == [
        "2020-01-03", "2020-01-04", "2020-01-05",
    ]
    assert frame.attrs["bis_missing_fraction"] == pytest.approx(0.6)


def test_bis_all_missing_rejected():
    with pytest.raises(ValueError, match="no finite observations"):
        parse_bis_eer_csv(bis_csv(value=""), "D.N.B.MX",
                          "2020-01-01", "2020-02-01")


@pytest.mark.parametrize("value", ["inf", "-inf", "1e309", "abc"])
def test_bis_nonmissing_malformed_values_rejected(value):
    with pytest.raises(ValueError, match="malformed or nonfinite"):
        parse_bis_eer_csv(bis_csv(value=value), "D.N.B.MX",
                          "2020-01-01", "2020-02-01")


def test_bis_malformed_extra_csv_field_rejected():
    """A comma in an unquoted value breaks the SDMX row dimensions."""
    with pytest.raises(ValueError, match="incorrect series dimensions"):
        parse_bis_eer_csv(bis_csv(value="101,2"), "D.N.B.MX",
                          "2020-01-01", "2020-02-01")


def test_bis_duplicate_missing_dates_still_rejected():
    raw = bis_csv(value="") + bis_csv(value="99.4").split(b"\n", 1)[1]
    with pytest.raises(ValueError, match="duplicate"):
        parse_bis_eer_csv(raw, "D.N.B.MX", "2020-01-01", "2020-02-01")


def test_bis_duplicate_dates_rejected():
    raw = bis_csv() + b"dataflow,BIS:WS_EER(1.0),I,D,N,B,MX,2020-01-02,102.3\n"
    with pytest.raises(ValueError, match="duplicate"):
        parse_bis_eer_csv(raw, "D.N.B.MX", "2020-01-01", "2020-02-01")


def test_bis_offline_acquisition_manifest(monkeypatch, tmp_path):
    """BIS source must use official key, exclusive period and immutable hashes."""
    class FakeResponse:
        url = "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_EER/1.0/D.N.B.MX?format=csv"
        content = bis_csv()
        def raise_for_status(self):
            pass

    class FakeSession:
        def get(self, url, *, params, headers, timeout):
            assert url.endswith("/BIS/WS_EER/1.0/D.N.B.MX")
            assert params["startPeriod"] == "2020-01-01"
            assert params["endPeriod"] == "2020-01-31"
            assert params["format"] == "csv"
            assert timeout == 90
            assert headers["Accept"] == "text/csv"
            return FakeResponse()
        def close(self):
            pass

    monkeypatch.setattr("latent_risk.data.acquisition._session", FakeSession)
    cat = {"bis": [{"country": "MEX", "key": "D.N.B.MX",
                    "role": "fx_effective_nominal_broad"}]}
    output = acquire(cat, start="2020-01-01", end="2020-02-01",
                     snapshot=tmp_path / "source", sources={"bis"},
                     only_ids={"D.N.B.MX"})
    assert output["status"] == "COMPLETE_SOURCE_DOWNLOAD"
    assert output["counts"]["success"] == 1
    item = output["records"][0]
    assert item["source"] == "bis"
    assert item["id"] == "D.N.B.MX"
    assert item["n_rows"] == 1
    assert item["vintage_status"] == "LATEST_REVISED_SNAPSHOT_NOT_HISTORICAL_VINTAGE"
    assert (tmp_path / "source/bis/D_N_B_MX.csv").is_file()
    assert json.loads((tmp_path / "source/manifest.json").read_text())["status"] == (
        "COMPLETE_SOURCE_DOWNLOAD"
    )


def test_bis_acquisition_saves_missing_counts_and_only_finite_data(
    monkeypatch, tmp_path,
):
    """A missing holiday must be reported, not retained as a zero or a NaN."""
    class FakeResponse:
        url = "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_EER/1.0/D.N.B.MX"
        content = bis_csv() + b"dataflow,BIS:WS_EER(1.0),I,D,N,B,MX,2020-01-03,\n"
        def raise_for_status(self):
            pass

    class FakeSession:
        def get(self, url, *, params, headers, timeout):
            assert params["format"] == "csv"
            return FakeResponse()
        def close(self):
            pass

    monkeypatch.setattr("latent_risk.data.acquisition._session", FakeSession)
    catalog = {"bis": [{"country": "MEX", "key": "D.N.B.MX",
                        "role": "fx_effective_nominal_broad"}]}
    result = acquire(catalog, start="2020-01-01", end="2020-02-01",
                     snapshot=tmp_path / "source", sources={"bis"})
    assert result["status"] == "COMPLETE_SOURCE_DOWNLOAD"
    row = result["records"][0]
    assert row["bis_source_rows_in_window"] == 2
    assert row["bis_missing_observation_count"] == 1
    assert row["bis_missing_first_dates"] == ["2020-01-03"]
    assert row["bis_missing_fraction"] == pytest.approx(0.5)
    assert len((tmp_path / "source/bis/D_N_B_MX.csv").read_text().splitlines()) == 2


def test_bis_unknown_id_fails_before_network_or_snapshot(tmp_path):
    with pytest.raises(ValueError, match="unknown series"):
        acquire({"bis": [{"key": "D.N.B.MX"}]},
                start="2020-01-01", end="2021-01-01",
                snapshot=tmp_path / "no", sources={"bis"},
                only_ids={"D.N.B.FR"})
    assert not (tmp_path / "no").exists()


def test_bis_failure_diagnostics_separate_missing_and_malformed_without_raw_values():
    raw = (
        bis_csv()
        + b"dataflow,BIS:WS_EER(1.0),I,D,N,B,MX,2020-01-03,\n"
        + b"dataflow,BIS:WS_EER(1.0),I,D,N,B,MX,2020-01-06,oops-secret-payload\n"
        + b"dataflow,BIS:WS_EER(1.0),I,D,N,B,MX,2020-01-07,-12\n"
    )
    diag = summarize_bis_payload(raw, "D.N.B.MX", "2020-01-01", "2020-02-01")
    assert diag["rows_total"] == 4
    assert diag["rows_in_window"] == 4
    assert diag["explicit_missing_rows"] == 1
    assert diag["malformed_nonmissing_rows"] == 1
    assert diag["nonpositive_rows"] == 1
    assert diag["first_missing_dates"] == ["2020-01-03"]
    assert diag["first_malformed_dates"] == ["2020-01-06"]
    assert "oops-secret-payload" not in json.dumps(diag)


def test_bis_failure_manifest_keeps_response_hash_and_bounded_diagnostics(
    monkeypatch, tmp_path,
):
    """A rejected live-format payload must not be saved as a successful CSV."""
    from hashlib import sha256

    raw = bis_csv(value="not-a-number")
    class FakeResponse:
        url = "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_EER/1.0/D.N.B.MX"
        content = raw
        def raise_for_status(self):
            pass

    class FakeSession:
        def get(self, url, *, params, headers, timeout):
            return FakeResponse()
        def close(self):
            pass

    monkeypatch.setattr("latent_risk.data.acquisition._session", FakeSession)
    catalog = {"bis": [{"country": "MEX", "key": "D.N.B.MX",
                        "role": "fx_effective_nominal_broad"}]}
    result = acquire(catalog, start="2020-01-01", end="2020-02-01",
                     snapshot=tmp_path / "source", sources={"bis"})
    record = result["records"][0]
    assert result["counts"]["failure"] == 1
    assert record["bis_response_sha256"] == sha256(raw).hexdigest()
    assert record["bis_failure_diagnostics"]["malformed_nonmissing_rows"] == 1
    assert record["status"] == "FAILED"
    assert not (tmp_path / "source/bis/D_N_B_MX.csv").exists()
