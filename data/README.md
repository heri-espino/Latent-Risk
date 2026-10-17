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

Initially configured SIE series are FX FIX `SF43718`, 28-day CETES `SF60633`, and reserves `SF43707`. Current revised-definition monetary aggregate M1/M2 IDs are **not guessed**: they must be individually identified and audited before being added. Running the optional source makes a separate immutable snapshot. Do not store tokens in files or commands checked into Git.

### Inspection

```powershell
Get-ChildItem .\data\raw\downloads -Directory | Sort-Object Name -Descending | Select-Object -First 3
$latest = Get-ChildItem .\data\raw\downloads -Directory | Sort-Object Name -Descending | Select-Object -First 1
Get-Content (Join-Path $latest.FullName 'manifest.json') | ConvertFrom-Json |
  Select-Object status, counts, period
```

## Critical scientific constraints

- FRED Graph CSV gives the **currently revised history**; a FRED reference date is **not** a release date. Neither original release dates nor ALFRED vintages are downloaded here.
- Banxico series returned by this simple endpoint are retrospective snapshots. Actual historical availability and methodology changes still require independent validation.
- Yahoo daily timestamps identify market dates; they are not release timestamps for pre-close forecasts. Neither Yahoo nor FRED guarantees complete historical coverage.
- Do **not** equate a monthly monetary aggregate's month label with when it became known. No `available_date` is fabricated. The existing `latent_risk.data.vintages` validator expects this field only after availability auditing.
- Different equity benchmarks, FX conventions, yields and monetary series cannot be combined into PCA or DFM without a defined economic transformation, training-only scaling and common frequency.
- Licenses/copyrights of IMF data and Yahoo market feeds should be reviewed before redistributing files; all raw files remain gitignored.

## Next data-collection gap

Identify current, historically comparable M1/M2 data for Mexico, UK, Japan and euro area, country sovereign-yield curves, local volatility measurements, the euro-area reserve definition, official release calendars/vintages, and a common observable validation target. The initial downloader is **stage 0**, not 'all the research data' or a finished international panel.

Possible sources: [Banxico SIE](https://www.banxico.org.mx/SieAPIRest/swagger/index.html), [FRED](https://fred.stlouisfed.org/), [IMF](https://data.imf.org/), [OECD](https://data-explorer.oecd.org/).
