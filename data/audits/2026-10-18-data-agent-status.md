# 2026-10-18 — acquisition-agent status, source coverage and licensing

**Branch:** `agent/data-bis-and-coverage`. **Scope:** acquisition, quality, source provenance, source audits, provider tests; no statistical modeling, no changes to previously saved vendor data.

## Evidence provenance

| Claim | Evidence | Status |
| --- | --- | --- |
| 34 prior sources passed integrity checks; WTI signed close 2020-04-20 was negative | Earlier user-VM output transcribed in `2026-10-17-integrity-complete.md` | **USER-REPORTED LIVE VM**; not rerun here |
| 31,383 country-market rows, 4,293 synchronized five-country equity sessions, 23,785 held-out reference rows | Earlier user-VM output transcribed in `2026-10-17-market-diagnostics-complete.md` | **USER-REPORTED LIVE VM**; unchanged |
| First BIS attempt was 0/5, same missing/nonfinite error | Historical immutable failed manifest summary `2026-10-17-bis-first-live-failure.md` | **USER-REPORTED LIVE VM**; no BIS CSV saved |
| Initial BIS parser fix accepts explicit blanks and rejects malformed values | `src/latent_risk/data/bis.py`, prior CI 88 tests: https://github.com/heri-espino/Latent-Risk/actions/runs/39089446309 | **IMPLEMENTED / PRIOR CI VERIFIED**, live retry UNKNOWN |
| BIS source provider pages and licensing | BIS public portal and terms URLs below, checked 2026-10-18 | **VERIFIED PUBLIC METADATA**, not downloader or VM evidence |
| New coverage/diagnostic code | Current branch code and synthetic tests | **IMPLEMENTED**, actual VM execution UNKNOWN |

This agent has GitHub repository access but **no direct access to the user's VM or its ignored `data/raw/downloads/` directories**. No new network source CSV acquisition, manifest audit or provider-data download has been carried out here. Any populated coverage report must be produced by the read-only CLI on the VM. Do not describe preexisting main-branch synthetic tests as new live verification.

## Exact observed coverage (known evidence versus unknown)

**BIS, planned series, all daily, nominal, broad basket, index 2020=100.** The table below separates *provider-published coverage* from the *downloaded file* coverage. The only page date span recovered in this session was Mexico's published range; its URL reported **1996-04-11 to 2026-10-06**, observed **on the BIS series portal**, not on this project's VM. Other series dates require live manifest verification. Generic BIS documentation says daily broad nominal indices began in 1996; it does **not** establish an identical exact start for every economy.

| Economy | BIS series ID | Units | Frequency | Provider page coverage evidenced | VM saved coverage |
| --- | --- | --- | --- | --- | --- |
| Mexico | `D.N.B.MX` | 2020=100 index | Daily | 1996-04-11–2026-10-06 (public portal; access metadata dated October 2026) | UNKNOWN, first attempt failed |
| USA | `D.N.B.US` | 2020=100 index | Daily | Exact dates UNKNOWN | UNKNOWN, first attempt failed |
| UK | `D.N.B.GB` | 2020=100 index | Daily | Exact dates UNKNOWN | UNKNOWN, first attempt failed |
| Japan | `D.N.B.JP` | 2020=100 index | Daily | Exact dates UNKNOWN | UNKNOWN, first attempt failed |
| Euro area | `D.N.B.XM` | 2020=100 index | Daily | Exact dates UNKNOWN | UNKNOWN, first attempt failed |

The **full existing 45-series catalog** (all source IDs, frequency, declared unit, local observed start/end/years, file count/hash/status) is exported by:

```powershell
python scripts/audit_source_coverage.py
```

Its JSON/CSV outputs are ignored and must be run against **actual VM snapshots** to provide a defensible per-economy date table. Source catalog monetary/market units not explicitly declared are displayed as UNKNOWN rather than guessed. A request window (2000–2026) does not prove continuous observations throughout that window. An observed calendar date does not prove same-day publication.

## BIS parser diagnosis

**Known:** The first response passed far enough into the previous parser to trigger a numeric/missing value error. **UNKNOWN:** Whether all five actual BIS responses contain explicitly blank `OBS_VALUE` rows, how many, which exact dates, or whether a different data formatting issue occurred. The latest main-branch parser drops only recognized missing markers and retains strict positivity and identity checks. This branch adds a bounded response summary on future parsing failures and SHA256 for failed responses, without keeping licensed response bytes in Git. Re-running the same source query on the user's VM writes a *new* immutable snapshot.

## Source license and vintage audit

- **BIS:** The [terms of permitted use](https://data.bis.org/help/legal) allow statistical use subject to attribution and other conditions; the BIS API has additional terms (service as-is, possible access limits, API terms can change). The portal says nominal broad effective indices are trade-weighted, periodically recalculated and daily data updated around mid-week. Neither the observations nor their dates constitute historical real-time release vintages.
- **FRED:** The official API succeeded earlier on the user's VM for 12 catalog entries. FRED series can carry **third-party copyrights**, and access via API is not redistribution permission. The existing downloadable historical data are not first-release vintages. Especially scrutinize any Moody's corporate bond feed.
- **Banxico/ECB/BoE/BoJ:** Existing source catalog links and metadata are not license approval. Data rights, original release timestamps, changes in definition, regional composition and revisions remain unverified at the per-series/vintage level.
- **Yahoo:** Daily local close prices require adjustment/roll/calendar inspection and redistributability review; the signed WTI exception is not data corruption by itself.

## Short, evidence-backed additional-data candidates (not downloaded)

| Candidate | Reason | Availability/licensing concern | Decision |
| --- | --- | --- | --- |
| FRED `BAA10YM`, USA monthly Baa–10Y spread | Explicit credit-risk spread, long observation history; public FRED table reports **1953-04-01 to 2026-09-01** | Moody's intellectual-property terms forbid unapproved republication; live API retrieval and publication lags not checked | **PROPOSED**, license check first |
| FRED `SOFR`, USA overnight secured funding rate | Funding benchmark; official FRED table reports start **2018-04-03** | Cannot cover 2008; rate *level* alone is not a credit/funding stress spread; compare only against defensible benchmark | **PROPOSED** post-2018 sensitivity |
| FRED `TEDRATE`, USA historical TED spread | Funding tension for 2008 retrospective pilot; public table reports **1986-01-02 to 2022-01-21** | **DISCONTINUED**; cannot serve a complete 2026 live input without a documented replacement/regime break | **NOT CORE**, optional pre-2022 sensitivity |
| BIS total credit / credit-to-GDP gap, multiple countries | Slow-moving leverage/vulnerability control, not redundant with equity/FX | Quarterly releases, revisions, country definitions and observed spans unverified | **DEFER** until design explicitly needs slow risk controls |

Exact provider links: [BIS MX](https://data.bis.org/topics/EER/BIS%2CWS_EER%2C1.0/D.N.B.MX), [BIS overview](https://data.bis.org/topics/EER), [BIS terms](https://data.bis.org/help/legal), [FRED BAA10YM](https://fred.stlouisfed.org/data/BAA10YM), [FRED SOFR](https://fred.stlouisfed.org/data/SOFR), [FRED TEDRATE](https://fred.stlouisfed.org/data/TEDRATE). No candidates added to `source_catalog.json`; coordinator approval precedes shared design or new downloads.

## Contract, limits, next action

`data/provider_metadata_contract.proposed.json` sets out a **PROPOSED** machine-readable schema separating observation date, unit, raw-response hash, saved-file hash, provider version, and documented release-time availability. It does **not** change current manifest fields. Missing historical availability stays null; no negative, zero or guessed lag is introduced.

Next action: on the user's VM use the already activated environment, acquire *only BIS* once using the corrected branch, then run `scripts/audit_source_coverage.py` and `scripts/audit_source_quality.py`. Report the new BIS per-source count, missing count, raw-response digest, first/latest observed dates, and any bounded failure diagnostics. Preserve all older snapshots. Submit any interface contract change separately for coordinator approval.

**No stress-index construction, forecasting experiment, financial disturbance inference or true first-release vintage validation is claimed.**
