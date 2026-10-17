# 2026-10-17 — FRED website connection failures and official API alternative

**Date:** 2026-10-17 (America/Mexico_City)  
**Objective:** address reproducible FRED source-download failure with a separate official API backend and preserve auditable provenance.

## Motivation
The user's activated Conda VM retried all 12 FRED graph CSV series with `--sources fred`. All returned HTTP connection exceptions, either `RemoteDisconnected` or `ReadTimeoutError`; not a Python import/package issue. Four local manifests now show 22 OK (previous Yahoo 14, Banxico 3, ECB 5), 12 FAILED (all FRED), 6 NEVER_REQUESTED. Prior successful data remain preserved.

## Questions
Is there an officially supported endpoint at a different hostname? Can we request only four target series to avoid 12 blocked timeout attempts? Can the user's FRED API key be kept out of metadata and console errors?

## Work performed
- Verified official FRED API version 1 documentation: `https://api.stlouisfed.org/fred/series/observations`, JSON per-series observations, API key requirement, and default current-vintage semantics. Key requested via FRED account, not GitHub.
- Added opt-in `--fred-backend api` with `FRED_API_KEY` and `--only` ID filter to `src/latent_risk/data/acquisition.py`. Legacy `graph` remains default; only the selected source data are downloaded.
- Added strict JSON parser for date filtering, missing values, duplicate observation rejection, truncated pagination detection, and data sorting. Convert the exclusive end date to the API's inclusive `observation_end`.
- Record `fred_backend` and requested series IDs in manifest, without storing API key or secret-augmented URL. Scrub secrets even in nested requests exception strings.
- Added offline parsing, selection/credential validation, and exception redaction tests; updated data README, context, and handoff.

## Files changed
`src/latent_risk/data/acquisition.py`, `tests/test_acquisition.py`, `data/README.md`, `AI_HANDOFF.md`, `context/STATE.md`, `context/NEXT_STEPS.md`, `journal/LATEST.md` and this dated journal.

## Reasoning
Transport failures across all 12 series suggest a hostname/network restriction or remote closure, not 12 bad identifiers. The official API hostname is distinct, but the VM may still block it. The purpose of an optional backend is to separate website access from API access, not to circumvent license restrictions or claim successful retrieval without user-provided live evidence.

## Validation and experiments
Software path verified only by synthetic offline CI tests. **No live FRED API request** and no international forecasting model experiment was run by the assistant. Await user's VM download manifest for real observations, endpoint accessibility and source coverage.

## Failures and alternatives
The website graph CSV method failed twice on VM; retain its historical manifests. No DBnomics or third-party mirror implemented, avoiding uncertain vintage and license semantics. The Federal Reserve Board H.15 official CSV provides a separate potential source for U.S. 2- and 10-year yields, but it cannot replace the other twelve series in full.

## Limitations
HTTP 200 or downloaded data are necessary but not sufficient for historical-vintage forecasting. The FRED API default result is current-vintage history; no `available_date` is assigned. Even the official API may encounter VM firewall/DNS/TLS or service blocks, and a FRED API key requires an account.

## Next steps
User: `git pull --ff-only origin main`, `python -m pip install -e '.[data,dev,docs]'`, test `Test-NetConnection api.stlouisfed.org -Port 443`, request personal FRED API key, and run `python scripts/download_data.py --sources fred --fred-backend api --only DGS2,DGS10,STLFSI4,NFCI --start 2000-01-01 --end 2026-10-17`, then audit. If unreachable, prioritize already-downloaded ECB CISS+market pilot and separately investigate VM egress. Keep token out of Git/logs.
