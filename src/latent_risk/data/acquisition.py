"""Download an auditable *initial raw-source snapshot* for the country stress study.

This script downloads source observations, not a point-in-time backtest panel:
monthly macro series returned by FRED graph CSV lack original release dates
and historical vintage values. All outputs are stored locally under ignored
data/raw/downloads/, with a machine-readable per-source manifest.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from latent_risk.data.official import boe_date, parse_boe_csv, parse_boj_json, parse_ecb_csv


def _slug(identifier: str) -> str:
    """Make a safe readable filename segment for a vendor identifier."""
    result = re.sub(r"[^A-Za-z0-9]+", "_", identifier).strip("_")
    if not result:
        raise ValueError(f"invalid series identifier: {identifier!r}")
    return result


def parse_fred_csv(body: bytes, start: str, end: str) -> pd.DataFrame:
    """Validate and date-filter a FRED graph CSV without inventing release dates.

    Parameters
    ----------
    body : bytes
        Response bytes from FRED graph CSV endpoint.
    start, end : str
        ISO date boundaries. End date is exclusive.

    Returns
    -------
    pandas.DataFrame
        Columns `observation_date` and `value` with finite observations.

    Raises
    ------
    ValueError
        On unexpected CSV format, missing data or invalid numeric values.
    """
    try:
        frame = pd.read_csv(BytesIO(body))
    except (UnicodeError, ValueError, pd.errors.ParserError) as exc:
        raise ValueError("FRED response is not parseable CSV") from exc
    if frame.shape[1] != 2:
        raise ValueError("expected FRED CSV with a date and a single series column")
    frame.columns = ["observation_date", "value"]
    try:
        frame["observation_date"] = pd.to_datetime(
            frame["observation_date"], format="%Y-%m-%d", errors="raise"
        )
    except (ValueError, TypeError) as exc:
        raise ValueError("FRED observations must contain ISO dates") from exc
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame = frame.loc[
        (frame["observation_date"] >= pd.Timestamp(start))
        & (frame["observation_date"] < pd.Timestamp(end))
        & frame["value"].notna()
    ].copy()
    if frame.empty or not frame["value"].map(lambda value: bool(pd.notna(value))).all():
        raise ValueError("FRED returned no observations in requested window")
    if not frame["value"].map(lambda value: bool(abs(value) < float("inf"))).all():
        raise ValueError("FRED returned nonfinite values")
    return frame.sort_values("observation_date").reset_index(drop=True)


def parse_fred_api(response: dict, start: str, end: str) -> pd.DataFrame:
    """Validate FRED official observations API JSON; retain current-vintage values only.

    Parameters
    ----------
    response : dict
        Official FRED `fred/series/observations?file_type=json` payload.
        No historical release dates are inferred.
    start, end : str
        ISO date boundaries, with end exclusive.

    Returns
    -------
    pandas.DataFrame
        Sorted observation_date and finite value columns.

    Raises
    ------
    ValueError
        For unexpected payload, pagination/truncation, duplicates or no
        finite observations.
    """
    observations = response.get("observations")
    if not isinstance(observations, list):
        raise ValueError("FRED API response lacks observations")
    try:
        count = int(response["count"])
        offset = int(response.get("offset", 0))
    except (ValueError, TypeError, KeyError) as exc:
        raise ValueError("FRED API response lacks valid count/offset") from exc
    if offset != 0 or count != len(observations):
        raise ValueError("FRED API response is truncated or paginated")
    rows = []
    for item in observations:
        if not isinstance(item, dict) or not isinstance(item.get("date"), str):
            raise ValueError("FRED API response has a malformed observation")
        raw = item.get("value")
        if not isinstance(raw, str):
            raise ValueError("FRED API observation has a malformed value")
        rows.append({"observation_date": item["date"], "value": raw})
    frame = pd.DataFrame(rows, columns=["observation_date", "value"])
    try:
        frame["observation_date"] = pd.to_datetime(
            frame["observation_date"], format="%Y-%m-%d", errors="raise"
        )
    except (ValueError, TypeError) as exc:
        raise ValueError("FRED API observations must use ISO dates") from exc
    frame["value"] = pd.to_numeric(frame["value"].replace(".", float("nan")), errors="coerce")
    frame = frame.loc[
        (frame["observation_date"] >= pd.Timestamp(start))
        & (frame["observation_date"] < pd.Timestamp(end))
        & frame["value"].notna()
    ].copy()
    if frame.empty:
        raise ValueError("FRED API returned no finite observations in requested window")
    if frame["observation_date"].duplicated().any():
        raise ValueError("FRED API returned duplicate observation dates")
    if not frame["value"].map(lambda x: abs(x) < float("inf")).all():
        raise ValueError("FRED API returned nonfinite observations")
    return frame.sort_values("observation_date").reset_index(drop=True)


def normalize_market_frame(frame: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """Keep dated Yahoo OHLCV data with its original market-close dates.

    Parameters
    ----------
    frame : pandas.DataFrame
        Single-symbol yfinance daily output.
    start, end : str
        ISO date boundaries; end is exclusive.

    Returns
    -------
    pandas.DataFrame
        Chronologically sorted source fields and `observation_date`.

    Raises
    ------
    ValueError
        On empty vendor data, missing close prices, or invalid dates.

    Notes
    -----
    The trade date is not the exact intraday timestamp when prices were known.
    Evaluation at intraday forecasting origins requires separate intraday data.
    """
    if frame is None or frame.empty:
        raise ValueError("empty market series returned by Yahoo Finance")
    result = frame.copy()
    if isinstance(result.columns, pd.MultiIndex):
        result.columns = result.columns.get_level_values(0)
    if "Close" not in result.columns:
        raise ValueError("market series missing Close prices")
    times = pd.to_datetime(result.index)
    if times.tz is not None:
        times = times.tz_localize(None)
    result.index = times.normalize()
    result = result.loc[
        (result.index >= pd.Timestamp(start)) & (result.index < pd.Timestamp(end))
    ].dropna(subset=["Close"]).sort_index()
    if result.empty:
        raise ValueError("market series has no close prices in requested window")
    if result.index.has_duplicates:
        raise ValueError("duplicate market observation dates")
    result.index.name = "observation_date"
    return result.reset_index()


def parse_banxico_series(response: dict, series_id: str, start: str, end: str) -> pd.DataFrame:
    """Parse one Banco de Mexico API series without fabricating release dates.

    Parameters
    ----------
    response : dict
        JSON payload returned by SIE API.
    series_id : str
        Expected SIE series code.
    start, end : str
        ISO date interval with exclusive end date.

    Returns
    -------
    pandas.DataFrame
        Observation dates and numeric values.

    Raises
    ------
    ValueError
        For an API error, missing dates, or empty numeric output.
    """
    try:
        series = response["bmx"]["series"]
        match = next(s for s in series if s.get("idSerie") == series_id)
        observations = match["datos"]
    except (KeyError, TypeError, StopIteration) as exc:
        raise ValueError("unexpected Banxico response or series identifier") from exc
    rows = []
    for item in observations:
        raw_value = str(item.get("dato", "")).replace(",", "")
        if raw_value in ("", "N/E", "N/D", "-", "nan"):
            continue
        try:
            observation = datetime.strptime(item["fecha"], "%d/%m/%Y").date()
            value = float(raw_value)
        except (ValueError, TypeError, KeyError) as exc:
            raise ValueError("invalid Banxico date or numeric value") from exc
        if date.fromisoformat(start) <= observation < date.fromisoformat(end):
            rows.append({"observation_date": observation.isoformat(), "value": value})
    result = pd.DataFrame(rows, columns=["observation_date", "value"])
    if result.empty or not result["value"].map(lambda x: abs(x) < float("inf")).all():
        raise ValueError("Banxico returned no finite observations in the requested period")
    if result["observation_date"].duplicated().any():
        raise ValueError("Banxico returned duplicate observation dates")
    return result.sort_values("observation_date").reset_index(drop=True)


def _session() -> requests.Session:
    """Create an HTTP session with bounded retries for transient server errors."""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(("GET",)),
        respect_retry_after_header=True,
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers["User-Agent"] = "LatentRisk-Research/0.1 (+public academic data retrieval)"
    return session


def _git_sha(root: Path) -> str | None:
    """Return the local repository commit, if Git is available."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, check=True, text=True,
            capture_output=True, timeout=5,
        )
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def _save_frame(frame: pd.DataFrame, path: Path) -> str:
    """Write dated observations and return the SHA256 of exact saved bytes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, date_format="%Y-%m-%d")
    return sha256(path.read_bytes()).hexdigest()


def _parse_dates(start: str, end: str) -> None:
    """Reject invalid time windows before making any download request."""
    try:
        low, high = date.fromisoformat(start), date.fromisoformat(end)
    except ValueError as exc:
        raise ValueError("start/end must be ISO YYYY-MM-DD") from exc
    if low >= high:
        raise ValueError("start must be earlier than exclusive end")


def acquire(
    catalog: dict,
    *,
    start: str,
    end: str,
    snapshot: Path,
    sources: set[str],
    banxico_token: str | None = None,
    fred_api_key: str | None = None,
    fred_backend: str = "graph",
    only_ids: set[str] | None = None,
) -> dict:
    """Acquire and audit individual vendor series from an explicit source catalog.

    Parameters
    ----------
    catalog : dict
        Source catalog with market, fred, banxico, ecb, boe and boj arrays.
    start, end : str
        Beginning and exclusive end of requested observations (ISO dates).
    snapshot : pathlib.Path
        A new snapshot directory; must not already exist.
    sources : set of str
        Subset of `market`, `fred`, `banxico`, `ecb`, `boe`, and `boj`.
    banxico_token : str, optional
        Private token for Banxico via HTTP header; never written to metadata.
    fred_api_key : str, optional
        User's FRED official API v1 key; required when backend is `api`.
        Never written to metadata, stdout or exception messages.
    fred_backend : str, default "graph"
        `graph` for legacy website CSV, or `api` for separately hosted official
        key-authenticated observations API.
    only_ids : set of str, optional
        Download only these explicit series IDs from the selected providers;
        rejects unrecognized identifiers.

    Returns
    -------
    dict
        Run manifest listing successes, failures, exact file hashes and
        the limitations of retrospectively downloaded revisions.

    Raises
    ------
    ValueError
        For bad dates, invalid sources or token mismatch.
    FileExistsError
        If the snapshot already exists.
    """
    _parse_dates(start, end)
    allowed = {"market", "fred", "banxico", "ecb", "boe", "boj"}
    if not sources or not sources <= allowed:
        raise ValueError("sources must be a nonempty subset of market,fred,banxico,ecb,boe,boj")
    if "banxico" in sources and not banxico_token:
        raise ValueError("Banxico requires BANXICO_TOKEN in the environment")
    if fred_backend not in {"graph", "api"}:
        raise ValueError("FRED backend must be graph or api")
    if "fred" in sources and fred_backend == "api" and not fred_api_key:
        raise ValueError("FRED API backend requires FRED_API_KEY in the environment")
    if only_ids is not None:
        if not only_ids:
            raise ValueError("only_ids may not be empty")
        available = {
            (row["symbol"] if source == "market"
             else row["key"] if source == "ecb"
             else row["series"])
            for source in sources
            for row in catalog[source]
        }
        missing = only_ids - available
        if missing:
            raise ValueError(f"unknown series identifiers: {sorted(missing)}")
    snapshot.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parents[3]
    started = datetime.now(timezone.utc).isoformat()
    manifest: dict = {
        "schema_version": 1,
        "status": "IN_PROGRESS",
        "download_utc": started,
        "git_commit": _git_sha(root),
        "period": {"start_inclusive": start, "end_exclusive": end},
        "sources_requested": sorted(sources),
        "fred_backend": fred_backend if "fred" in sources else None,
        "only_ids_requested": sorted(only_ids) if only_ids is not None else None,
        "records": [],
        "limitations": [
            "FRED Graph CSV and official observations API are current-vintage histories,"
            " not original publication vintages.",
            "No historical available_date column is fabricated for any macro source.",
            "ECB, BoE and BOJ monthly observation labels are NOT public release dates.",
            "Market timestamps are daily trade dates; intraday availability is not established.",
            "All series are vendor-provided and licensing/republication is not automatically granted.",
            "A successful download does not imply cross-country comparability or completeness.",
        ],
    }
    client = _session()
    try:
        for source in ("market", "fred", "banxico", "ecb", "boe", "boj"):
            if source not in sources:
                continue
            for entry in catalog[source]:
                identifier = (
                    entry["symbol"] if source == "market"
                    else entry["key"] if source == "ecb"
                    else entry["series"]
                )
                if only_ids is not None and identifier not in only_ids:
                    continue
                metadata = dict(entry)
                metadata.update({"source": source, "id": identifier, "status": "FAILED"})
                if source == "fred":
                    metadata["fred_backend"] = fred_backend
                try:
                    if source == "market":
                        import yfinance as yf

                        url = f"https://finance.yahoo.com/quote/{identifier}"
                        downloaded = yf.download(
                            tickers=identifier, start=start, end=end, interval="1d",
                            auto_adjust=False, actions=False, progress=False,
                            threads=False, multi_level_index=False, timeout=30,
                        )
                        data = normalize_market_frame(downloaded, start, end)
                    elif source == "fred":
                        if fred_backend == "api":
                            # Store only the fixed endpoint URL, never the requested
                            # URL including secret API key query parameters.
                            url = "https://api.stlouisfed.org/fred/series/observations"
                            inclusive_end = (date.fromisoformat(end) - timedelta(days=1))
                            response = client.get(
                                url,
                                params={
                                    "series_id": identifier,
                                    "api_key": fred_api_key,
                                    "file_type": "json",
                                    "observation_start": start,
                                    "observation_end": inclusive_end.isoformat(),
                                    "limit": 100000,
                                },
                                timeout=45,
                            )
                            if response.status_code >= 400:
                                raise ValueError(
                                    f"FRED official API returned HTTP {response.status_code}"
                                    f" for {identifier}"
                                )
                            data = parse_fred_api(response.json(), start, end)
                        else:
                            url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={identifier}"
                            response = client.get(
                                url, params={"cosd": start, "coed": end}, timeout=45,
                            )
                            response.raise_for_status()
                            data = parse_fred_csv(response.content, start, end)
                    elif source == "banxico":
                        url = (
                            "https://www.banxico.org.mx/SieAPIRest/service/v1/series/"
                            f"{identifier}/datos/{start}/{end}"
                        )
                        response = client.get(
                            url, headers={"Bmx-Token": banxico_token or ""}, timeout=45,
                        )
                        response.raise_for_status()
                        data = parse_banxico_series(
                            response.json(), identifier, start, end,
                        )
                    elif source == "ecb":
                        url = f"https://data-api.ecb.europa.eu/service/data/{identifier.replace('.', '/', 1)}"
                        last_day = date.fromisoformat(end) - timedelta(days=1)
                        frequency = identifier.split(".")[1]
                        if frequency not in {"D", "M"}:
                            raise ValueError("ECB source must be daily or monthly")
                        first_period = start if frequency == "D" else start[:7]
                        last_period = (
                            last_day.isoformat() if frequency == "D"
                            else last_day.strftime("%Y-%m")
                        )
                        response = client.get(
                            url,
                            params={
                                "startPeriod": first_period,
                                "endPeriod": last_period,
                                "format": "csvdata",
                            },
                            headers={"Accept": "text/csv"},
                            timeout=60,
                        )
                        response.raise_for_status()
                        url = response.url
                        data = parse_ecb_csv(response.content, start, end, identifier)
                    elif source == "boe":
                        url = (
                            "https://www.bankofengland.co.uk/boeapps/database/"
                            "_iadb-fromshowcolumns.asp"
                        )
                        response = client.get(
                            url,
                            params={
                                "csv.x": "yes",
                                "Datefrom": boe_date(start),
                                "Dateto": boe_date((date.fromisoformat(end) - timedelta(days=1)).isoformat()),
                                "SeriesCodes": identifier,
                                "CSVF": "TN",
                                "UsingCodes": "Y",
                                "VPD": "Y",
                                "VFD": "N",
                            },
                            headers={"User-Agent": "Mozilla/5.0 (compatible; LatentRiskAcademic/0.1)"},
                            timeout=60,
                        )
                        response.raise_for_status()
                        url = response.url
                        data = parse_boe_csv(response.content, start, end, identifier)
                    else:  # boj
                        url = "https://www.stat-search.boj.or.jp/api/v1/getDataCode"
                        last_day = date.fromisoformat(end) - timedelta(days=1)
                        response = client.get(
                            url,
                            params={
                                "db": entry["database"],
                                "code": identifier,
                                "lang": "en",
                                "format": "json",
                                "startDate": start[:7].replace("-", ""),
                                "endDate": last_day.strftime("%Y%m"),
                            },
                            timeout=60,
                        )
                        response.raise_for_status()
                        url = response.url
                        payload = response.json()
                        if payload.get("NEXTPOSITION") is not None:
                            raise ValueError("BOJ paginated response; no partial series is accepted")
                        data = parse_boj_json(payload, start, end, identifier)
                    path = snapshot / source / f"{_slug(identifier)}.csv"
                    digest = _save_frame(data, path)
                    metadata.update({
                        "status": "OK",
                        "n_rows": len(data),
                        "first_date": str(data["observation_date"].iloc[0])[:10],
                        "last_date": str(data["observation_date"].iloc[-1])[:10],
                        "path": path.relative_to(snapshot).as_posix(),
                        "sha256": digest,
                        "url": url,
                        "vintage_status": "LATEST_REVISED_SNAPSHOT_NOT_HISTORICAL_VINTAGE",
                    })
                    print(f"[OK] {source:7} {identifier:18} rows={len(data)}")
                except Exception as exc:
                    # requests' nested errors can contain the full URL, including
                    # query-authenticated FRED_API_KEY; never persist or print it.
                    detail = str(exc)
                    for secret in (fred_api_key, banxico_token):
                        if secret:
                            detail = detail.replace(secret, "[REDACTED]")
                    metadata["error"] = f"{type(exc).__name__}: {detail}"
                    print(f"[FAIL] {source:7} {identifier:18} {metadata['error']}", file=sys.stderr)
                manifest["records"].append(metadata)
    finally:
        client.close()
        manifest["completed_utc"] = datetime.now(timezone.utc).isoformat()
        success = sum(record["status"] == "OK" for record in manifest["records"])
        manifest["counts"] = {
            "success": success,
            "failure": len(manifest["records"]) - success,
            "requested": len(manifest["records"]),
        }
        manifest["status"] = (
            "COMPLETE_SOURCE_DOWNLOAD" if success == len(manifest["records"])
            else "PARTIAL_SOURCE_DOWNLOAD"
        )
        (snapshot / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
        )
    return manifest


def main() -> int:
    """Run a local immutable download snapshot from the repository root."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="2000-01-01")
    parser.add_argument(
        "--fred-backend", choices=("graph", "api"), default="graph",
        help="Choose FRED graph CSV (legacy) or official FRED API (needs FRED_API_KEY)",
    )
    parser.add_argument(
        "--only", default=None,
        help="Comma-separated series IDs to download, e.g. DGS2,DGS10,STLFSI4,NFCI",
    )
    parser.add_argument("--end", required=True, help="Exclusive ISO end date, e.g. 2026-10-17")
    parser.add_argument(
        "--sources", default="market,fred",
        help="Comma-separated subset: market,fred,banxico,ecb,boe,boj",
    )
    parser.add_argument("--catalog", type=Path, default=Path(__file__).resolve().parents[3] / "data/source_catalog.json")
    parser.add_argument("--output", type=Path, default=Path("data/raw/downloads"))
    args = parser.parse_args()
    selected = {item.strip() for item in args.sources.split(",")}
    try:
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        snapshot = args.output / stamp
        manifest = acquire(
            catalog, start=args.start, end=args.end, snapshot=snapshot,
            sources=selected, banxico_token=os.getenv("BANXICO_TOKEN"),
            fred_backend=args.fred_backend, fred_api_key=os.getenv("FRED_API_KEY"),
            only_ids=set(args.only.split(",")) if args.only is not None else None,
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    print(f"\nManifest: {(snapshot / 'manifest.json').resolve()}")
    print(
        f"RESULT {manifest['status']}: "
        f"{manifest['counts']['success']}/{manifest['counts']['requested']} downloaded"
    )
    return 0 if manifest["counts"]["failure"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
