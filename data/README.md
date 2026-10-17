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
