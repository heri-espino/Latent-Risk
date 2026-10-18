# Research data — acquisition and provenance

No research data are committed to this public repository. The downloader records **initial source snapshots**, not backtest-ready historical vintages. Source licensing and API terms apply (Yahoo Finance, FRED and underlying IMF/OECD sources, Banco de Mexico).

## VM setup and download

From PowerShell in a directory where the repository can be cloned:

```powershell
git clone https://github.com/heri-espino/Latent-Risk.git
Set-Location Latent-Risk
conda create --name latent-risk python=3.11 -y
conda run -n latent-risk python -m pip install -e '.[data,dev,docs]'
conda run -n latent-risk python scripts/download_data.py --start 2000-01-01 --end 2026-10-17
```

`--end` is **exclusive**. This downloads Yahoo Finance market sources and FRED macro/financial sources from the initial [catalog](source_catalog.json), each individually, into a unique UTC timestamped `data/raw/downloads/` folder. It prints `[OK]` or `[FAIL]` per series, saves CSV files and a `manifest.json` recording the downloaded row counts, effective date span, source URL, SHA256 and failure reasons. The script returns a **nonzero exit code if any requested series failed**. You may rerun it; prior snapshots are preserved.

The catalog has five equity benchmarks, FX proxies, shared oil/gold/dollar/volatility proxies, U.S. yields and M1/M2, reserve series for MEX/USA/GBR/JPN, and historical Mexico M1/M2 sources. **The old Mexico FRED M2 source ends in 2017** and is not a current Mexican M2 history. Some tickers and sources may fail or have shorter coverage; the manifest determines what was actually obtained.

### Optional: official Banxico SIE sources

Create a personal API token using [Banxico SIE](https://www.banxico.org.mx/SieAPIRest/swagger/index.html) and assign it to an environment variable **without committing it**:

```powershell
$env:BANXICO_TOKEN = Read-Host 'Paste your personal Banxico API token'
conda run -n latent-risk python scripts/download_data.py --start 2000-01-01 --end 2026-10-17 --sources banxico
Remove-Item Env:BANXICO_TOKEN
```

Initially configured SIE series are FX FIX `SF43718`, 28-day CETES `SF60633`, and reserves `SF43707`. The updated catalog now also has **Banxico M1 SF311408 and M2 SF311418** (2018 methodology), corroborated against independent SIE API client examples and the official CF807 table. Verify titles, units and observation span using live SIE metadata; no historical release vintages are implied. Running the optional source makes a separate immutable snapshot. Do not store tokens in files or commands checked into Git.

### Inspection

```powershell
Get-ChildItem .\data\raw\downloads -Directory | Sort-Object Name -Descending | Select-Object -First 3
$latest = Get-ChildItem .\data\raw\downloads -Directory | Sort-Object Name -Descending | Select-Object -First 1
Get-Content (Join-Path $latest.FullName 'manifest.json') | ConvertFrom-Json |
  Select-Object status, counts, period
```

## Next VM session: expand the official dataset

Use the already activated `(latent-risk)` shell. All following commands run the Python executable in that environment, without `conda run`:

```powershell
git pull --ff-only origin main
python -m pip install -e '.[data,dev,docs]'
python scripts/audit_downloads.py
python scripts/download_data.py --start 2000-01-01 --end 2026-10-17 --sources ecb,boe,boj
python scripts/audit_downloads.py
```

Six new official-source series are included: ECB monthly euro-area M1 and M2, Bank of England UK monthly M4 and daily SONIA, and Bank of Japan monthly M1 and M2. The existing Banxico source set now includes two additional series, M1 and M2. **Re-run the Banxico source explicitly with your token to get those two**. See the token paragraph above. A series can fail while the rest of its batch is saved; inspect the resulting audit and manifest.

An audit file is generated at `results/acquisition_audit.json` (ignored by Git) combining the latest successes across multiple runs. Its columns distinguish `OK`, `FAILED`, and `NEVER_REQUESTED`. The audit does not infer a historical release date from an observation date and does not establish cross-source comparability.

### Recheck the blocked FRED source

Previously all ten FRED series failed on the user's VM with HTTPS `ConnectionError`. Installing more Python packages or downloading a different provider cannot by itself resolve FRED access. Check it separately before retrying:

```powershell
Test-NetConnection fred.stlouisfed.org -Port 443
try {
    (Invoke-WebRequest -Uri 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10' -UseBasicParsing -TimeoutSec 30).StatusCode
} catch {
    $_.Exception.ToString()
}
```

If both succeed, run `python scripts/download_data.py --start 2000-01-01 --end 2026-10-17 --sources fred`; otherwise save the complete error for diagnosing VM/proxy/TLS access. Don't claim those US rates or money stocks were acquired without a successful manifest.

### Source and measurement differences

The official UK series `LPMAUYN` is seasonally adjusted sterling **M4**, not M2. Bank of Japan monthly M1/M2 are average outstanding amounts (in hundred-million yen); ECB M1/M2 are seasonally adjusted stock levels (in millions of euro). Banco de México M1/M2 are in thousands of MXN. Period labels, scaling, seasonal adjustment, and monetary definitions differ and must remain explicit in the measurement plan.

Japan BOJ API gives a JSON status field even on HTTP 200 responses; the downloader checks it. ECB `format=csvdata` monthly periods are represented as first-of-month labels, NOT data availability dates. Bank of England exports raw observation dates. Official API access can still fail; none of these providers were accessed live in the automated CI tests.

Official references: [Banxico CF807](https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?accion=consultarCuadro&idCuadro=CF807&locale=es), [ECB monetary aggregates](https://data.ecb.europa.eu/data/publications/BSI01_01), [BoE IADB API syntax](https://www.bankofengland.co.uk/boeapps/database/help.asp), [BoJ series table](https://www.stat-search.boj.or.jp/ssi/mtshtml/md02_m_1_en.html).

## Critical scientific constraints

- FRED Graph CSV gives the **currently revised history**; a FRED reference date is **not** a release date. Neither original release dates nor ALFRED vintages are downloaded here.
- Banxico series returned by this simple endpoint are retrospective snapshots. Actual historical availability and methodology changes still require independent validation.
- Yahoo daily timestamps identify market dates; they are not release timestamps for pre-close forecasts. Neither Yahoo nor FRED guarantees complete historical coverage.
- Do **not** equate a monthly monetary aggregate's month label with when it became known. No `available_date` is fabricated. The existing `latent_risk.data.vintages` validator expects this field only after availability auditing.
- Different equity benchmarks, FX conventions, yields and monetary series cannot be combined into PCA or DFM without a defined economic transformation, training-only scaling and common frequency.
- Licenses/copyrights of IMF data and Yahoo market feeds should be reviewed before redistributing files; all raw files remain gitignored.

## Next data-collection gap

Audit the newly included Banxico M1/M2 and official Euro-area M1/M2, Japan M1/M2 and UK M4 observations; acquire UK/Japan/euro area comparable sovereign yields, US failed FRED histories, local volatility measurements, the euro-area reserve definition, official release calendars/vintages, and a common observable validation target. The initial downloader is **stage 0**, not 'all the research data' or a finished international panel.

Possible sources: [Banxico SIE](https://www.banxico.org.mx/SieAPIRest/swagger/index.html), [FRED](https://fred.stlouisfed.org/), [IMF](https://data.imf.org/), [OECD](https://data-explorer.oecd.org/).

## Why M1/M2 are not primary stress-factor inputs

The user clarified that M1/M2 were illustrative, not the desired default factors. The economically motivated primary domains are equity downside/realized volatility, FX volatility, credit and funding spreads and bank stress, with slower BIS credit-gap/DSR and M1/M2 as separately evaluated extensions. See [indicator selection and benchmarks](indicator_priorities.md). Three daily ECB CISS indices (EA, US, UK) are now downloaded along with ECB BSI when running `--sources ecb` and **must remain external references**, not factor inputs. Banxico IEMF is another official external comparator, but historical coverage, reproducible scraping and historical publication dates remain unverified.

FRED benchmark identifiers `STLFSI4` and `NFCI` are cataloged; they do not solve the VM's FRED connectivity failures. ICE US corporate OAS is limited to three years of FRED histories from April 2026, so it is not sufficient for 2008 replay.

## Official FRED API fallback (VM connection failures, 2026-10-17)

**Status:** The user's VM consistently times out or receives connection aborts from
`fred.stlouisfed.org/graph/fredgraph.csv`. Twelve FRED graph CSV series
failed twice. This does **not** imply a bad series identifier or missing
Conda package.

A second, official endpoint is now supported with
`--fred-backend api`: `https://api.stlouisfed.org/fred/series/observations`.
FRED API v1 requires a user's private API key, requested from
https://fred.stlouisfed.org/docs/api/api_key.html . A valid key does **not**
guarantee the VM can reach the separate `api.stlouisfed.org` hostname.

In the **already activated** `(latent-risk)` PowerShell environment:

```powershell
git pull --ff-only origin main
python -m pip install -e '.[data,dev,docs]'

# Before acquiring a key, check basic host reachability:
Test-NetConnection api.stlouisfed.org -Port 443

# After obtaining a personal FRED API key:
$env:FRED_API_KEY = Read-Host 'Enter your personal FRED API key'

# Probe only two core yield curves and two stress benchmarks first:
try {
    python scripts/download_data.py --start 2000-01-01 --end 2026-10-17 --sources fred --fred-backend api --only DGS2,DGS10,STLFSI4,NFCI
} finally {
    Remove-Item Env:FRED_API_KEY -ErrorAction SilentlyContinue
}

python scripts/audit_downloads.py
```

If the 4-series probe succeeds, set `FRED_API_KEY` again and omit
`--only` to request all 12 FRED series. `--only` also applies to other
providers when IDs are known; unrecognized IDs fail before a snapshot is
created. The legacy graph backend stays the default for reproducibility.

The API key is sent only via HTTPS to the official FRED endpoint and is
removed from PowerShell by the example. Because FRED API v1 uses URL-query
authentication, HTTP libraries might temporarily hold the credential
inside an in-process request URL; downloader logs and manifests explicitly
redact it and save only a stable URL without query parameters. Do not copy
HTTP debug traces or publicize the key.

FRED official API returns **current-vintage observation values by default**.
Historical availability and release dates remain unverified; no
`available_date` is fabricated. FRED API vintages/ALFRED remain a later
separate research workflow.

Source: official FRED
[API keys](https://fred.stlouisfed.org/docs/api/api_key.html) and
[observations endpoint](https://fred.stlouisfed.org/docs/api/fred/series_observations.html).

### Live FRED API result reported by user (2026-10-17)

The user ran the four-series `--fred-backend api --only DGS2,DGS10,STLFSI4,NFCI` test on the activated Conda VM. **All four returned OK**; the combined catalog now reports **26 OK, 8 FAILED, 6 NEVER_REQUESTED** across five local snapshots. The eight remaining FRED failures are **older website Graph CSV failures** and have not been retried with the working API hostname. This live result is transcribed in [the 2026-10-17 audit](audits/2026-10-17-fred-api-live-success.md); original manifests and raw CSV files remain on the VM.

For a complete optional source archive, enter the FRED key privately as explained above, then run the **eight remaining, not primary financial-stress series** using `--fred-backend api --only M1SL,M2SL,TRESEGUSM052N,TRESEGMXM052N,TRESEGGBM052N,TRESEGJPM052N,MYAGM2MXM189N,MANMM101MXM189S`. Some older series are discontinued and may have short coverage; do not assume a full 2000–2026 span. The first market/CISS pilot need not await these macro series.


## Initial 34-series acquisition milestone (2026-10-17)

The user's activated VM now reports **six source manifests**, and the
catalog has **34 OK, 0 FAILED, 6 NEVER_REQUESTED** series. All 12 FRED
codes have been retrieved via the official key-authenticated backend.
The six unrequested series are two Banxico monetary aggregates, two
Bank of England indicators and two Bank of Japan monetary aggregates.
These are optional for the initial market-stress pilot.

Do **not** interpret the six as source failures or require another FRED
download. Mexico's legacy FRED money M2 ends 2017-05, M1 ends 2018-12.
The official API downloaded currently revised values, not historical
point-in-time release vintages.

### Next VM command: physical source-file quality

```powershell
git pull --ff-only origin main
python scripts/audit_source_quality.py
```

This is a **read-only source integrity gate**, not a forecast-model run.
It chooses each provider/ID's newest *successful* downloaded source
snapshot, verifies the CSV file SHA256 against the manifest, checks
row count, sorted unique ISO dates, finite numeric values, the recorded
first/last date range and positive market close prices. It counts
large daily equity/FX log-return moves as warnings for manual review.
No prices, keys or raw CSVs are uploaded to Git.

The report is saved to
`results/runs/source_quality/report.json` (ignored by Git);
the program returns nonzero if any integrity check fails. It does
not identify unobserved market holidays, revisions, future data leaks,
source licensing restrictions or compatible factor identification.
Only proceed to rolling-origin feature engineering after checking
the report's exceptions and adjusting an auditable data policy.

Source evidence: [user-reported FRED completion](audits/2026-10-17-fred-catalog-complete.md).
