# 2026-10-17 — First successful official FRED API download on user VM

**Status:** USER-REPORTED SUCCESS — five local manifests summarized by user's CLI; raw bytes and SHA256 hashes have **not** been independently examined by assistant.

## Executed VM command and provenance

The user checked `Test-NetConnection api.stlouisfed.org -Port 443` and received `TcpTestSucceeded : True`. They then supplied a private key via interactive SecureString and executed:

```powershell
python scripts/download_data.py --start 2000-01-01 --end 2026-10-17 --sources fred --fred-backend api --only DGS2,DGS10,STLFSI4,NFCI
```

The key was cleared after execution and was **not provided in the conversation**.

- Source snapshot: `data/raw/downloads/20261017T235600038504Z/manifest.json` (VM-local).
- Response: `RESULT COMPLETE_SOURCE_DOWNLOAD: 4/4 downloaded`.
- Additional source status audit: `Read 5 manifests; expected catalog series: 40`.
- Final audit counts: **26 OK, 8 FAILED, 6 NEVER_REQUESTED**.

| Source | Code | n_rows | First observation | Last observation | Status |
| --- | --- | ---: | --- | --- | --- |
| FRED official API | `DGS2` | 6,700 | 2000-01-03 | 2026-10-15 | OK |
| FRED official API | `DGS10` | 6,700 | 2000-01-03 | 2026-10-15 | OK |
| FRED official API | `STLFSI4` | 1,397 | 2000-01-07 | 2026-10-09 | OK |
| FRED official API | `NFCI` | 1,397 | 2000-01-07 | 2026-10-09 | OK |

## Remaining catalog status

- **14/14 Yahoo**: OK.
- **4/12 FRED**: API method OK for yields DGS2/DGS10 and external indexes STLFSI4/NFCI. The other **8/12 are marked FAILED** because of earlier FRED *website Graph CSV* attempts. **Their status does not represent a failed attempt through the official FRED API**, which has not been requested for those IDs.
- **3/5 Banxico**: OK; M1/M2 unrequested.
- **5/5 ECB**: OK.
- **0/2 BoE**, **0/2 BoJ**: not requested.

The remaining eight FRED IDs are `M1SL`, `M2SL`, `TRESEGUSM052N`, `TRESEGMXM052N`, `TRESEGGBM052N`, `TRESEGJPM052N`, `MYAGM2MXM189N`, `MANMM101MXM189S`. These are monetary/reserve and older historical money-stock series, **not the first-choice direct financial-stress inputs** in ADR-0005.

## Scientific and operational limits

A successful transport test verifies source retrieval, not original historical publication vintages. FRED's default observations API returns today's available/revised history; the current `STLFSI4` design is not necessarily the vintage of the index published in 2008. `NFCI` measures financial conditions, rather than being interchangeable with STLFSI4 or ECB CISS. These are explicitly **external benchmarks**, not eligible latent-index inputs when comparing against the same series.

A first restricted market-derived risk-factor / separate observed-CISS forecasting pilot is technically feasible with current user data. Still missing are adequately comparable credit, bank equity and funding-liquidity inputs for a five-country systemic-stress index. Macro release calendars and historical factor-vintage modeling are still not constructed.

## Recommended next step

Do not require all 40 catalog IDs for a *market-stress* feasibility pilot. Begin a rolling-origin source-quality and feature-transformation audit for local equity/FX measures with CISS and US stress indices held out as external references. If user wants archive completeness, retry the eight remaining FRED codes with `--fred-backend api --only` and their private API key, but keep obsolete series as auxiliary historical context.
