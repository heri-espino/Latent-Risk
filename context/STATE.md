# Research state (2026-10-18)

**Status:** `IMPLEMENTED` baseline source-package infrastructure; CI `VERIFIED COMPUTATIONALLY` on commit `075f9027` (12 tests, Ruff, validator, Sphinx pass: https://github.com/heri-espino/Latent-Risk/actions/runs/38994859776). The international empirical evaluation remains `PROPOSED`, not completed.

## Latest BIS download verified and versioned feature implementation (2026-10-18)

**USER CLI VERIFICATION:** All five BIS daily broad NEER codes passed the official download in snapshot `20261018T145643915821Z`: 6,987 valid index levels each for 2000-01-03–2026-10-13, 2,796 explicit missing source observations each excluded. All **39/39** source CSVs pass the integrity audit, 0 failures, 1 historic signed-WTI warning. Across 8 raw manifests, 45 catalog series: **39 OK, 0 FAILED, 6 NEVER_REQUESTED**. The first BIS 0/5 failed parse is preserved in older manifest/journal; do not confuse it with present status. Evidence: `data/audits/2026-10-18-bis-five-series-live-success.md`.

**IMPLEMENTED / SYNTHETIC CI VERIFIED, USER VM RUN PENDING:** `scripts/build_bis_market_pilot.py` creates a completely **new** ignored `data/processed/market_pilot_bis` version with equity and BIS NEER feature columns for all five economies (including US): depreciation-oriented `-Δlog NEER`, 21-observation volatility, exact-date five-equity-only and five-full-feature intersections, independent benchmarks, SHA256 source and output manifest. Legacy bilateral USD/DXY data/pilot remain unmodified. Code CI 95 tests green. BIS observation_date != public available_date; no model estimated.

## Initial data collection (2026-10-16)
`IMPLEMENTED` source acquisition module: 14 daily Yahoo market tickers, 10 FRED macro/financial series and three optional Banxico token-based series in `data/source_catalog.json`. Local isolated UTC snapshots under `data/raw/downloads/` include CSVs, hashes, historical-coverage ranges and failures. `VERIFIED COMPUTATIONALLY`: 19 offline tests, Ruff, structure and Sphinx pass on `8fb85d0` (https://github.com/heri-espino/Latent-Risk/actions/runs/38998827014). **No live download has been run**, so coverage and actual provider success are `UNKNOWN`.

FRED is current revised history, **not** available-date vintage history. No release dates have been fabricated. The old Mexico M2 FRED code `MYAGM2MXM189N` ends in 2017. Current Mexican M1/M2 and other country monetary aggregates require audited official identifiers. Neither the point-in-time balanced panel nor EXP-0001 exists as completed empirical results.

## Official-source expansion (2026-10-17)
`IMPLEMENTED` additional candidate source series: ECB M1/M2, BoE sterling M4/SONIA, BOJ M1/M2, modern Banxico M1/M2 (codes `SF311408`/`SF311418`). Retrieval uses source-specific CSV/JSON parsers and independently stored raw snapshots; `scripts/audit_downloads.py` combines status evidence across snapshots. New-provider HTTP requests have not been executed by assistant, and the user reports Banxico ran before these two codes were added. Full manifests have not yet been provided. All FRED downloads previously failed from the VM with HTTPS `ConnectionError`; no claim of complete US macro coverage is justified. ECB euro area changes composition; BoE M4 != US/ECB M2. Historical availability and real-time data vintages remain `UNKNOWN`.

## Indicator domain reprioritization (2026-10-17)
The user clarified that M1/M2 were examples, not preferred core predictors. Per `data/indicator_priorities.md` and `ADR-0005` (proposed), prioritize directly market-based stress observables and distinguish slower credit/balance-sheet vulnerability indicators. Exact validated published external references: Banxico IEMF (36 variables, six financial-market domains), ECB daily new CISS for UK/US/EA; STLFSI4 and NFCI are US reference candidates. They are **not** model input data for a concordance experiment. ECB CISS source keys now in downloader. Source coverage in Japan remains a gap. US ICE corporate spreads FRED limit to three-year history since Apr 2026; cannot reconstruct 2008 with FRED now.

## User-reported VM coverage — 2026-10-17

**USER-REPORTED, not independently inspected files:** latest source-audit showed **40 expected series, 22 OK, 10 FAILED (all FRED), 8 NEVER_REQUESTED** across three local manifests. Market 14/14; ECB 5/5 (EA, USA and UK CISS: 6,997 rows each, Jan 2000–Oct 15 2026, plus EA M1/M2: 320 rows each); Banxico 3/5 (FIX, CETES, reserves). Unrequested two Banxico modern M1/M2, two BoE, two BoJ and two FRED indices. Note `^STOXX50E` starts **2007-03-30**, some Yahoo FX 2003-12-01; first available five-equity intersection comes after 2007-03-30. All dates refer to observations, not verified release vintages.

Transcribed provenance in `data/audits/2026-10-17-user-vm-coverage.md` and CSV; actual raw snapshots remain on the user's VM and were not reviewed or uploaded. This enables an exploratory market/equity and separately CISS trend-forecast pilot (NOT a completed multi-domain financial-stress model). Credit/funding series and official real-time vintage availability are still essential for confirmatory claims.

## FRED retry and separate-host solution (2026-10-17)
**USER-REPORTED:** The VM retried all twelve FRED website Graph CSV series and received 0/12 successes, with `RemoteDisconnected` and `ReadTimeoutError`. Fourth manifest changes 40 catalog status to **22 OK, 12 FAILED, 6 NEVER_REQUESTED**. Prior successful Yahoo, Banxico and ECB snapshots are unaffected. Source failure does not diagnose whether a firewall, server, network policy, IP filtering or proxy is at fault.

**IMPLEMENTED**, but **not yet verified live**: official API v1 alternative hosted at `api.stlouisfed.org`, activated with `--fred-backend api` and a private `FRED_API_KEY`, plus short-probe `--only` filtering and secret-redacted logs/manifests. The key and API responses remain private; both FRED hostnames could be inaccessible. See `data/README.md` and latest journal.

## Official FRED API live VM success — 2026-10-17

**USER-REPORTED LIVE DOWNLOAD VERIFIED:** `api.stlouisfed.org` TCP port 443 was reachable and FRED `--fred-backend api --only DGS2,DGS10,STLFSI4,NFCI` completed 4/4. Each yield series DGS2/DGS10 has 6,700 rows through 2026-10-15; each weekly benchmark STLFSI4/NFCI has 1,397 rows through 2026-10-09. Five-manifest combined audit: **26 OK, 8 FAILED, 6 NEVER_REQUESTED**. Eight remaining FRED failures refer to earlier `fred.stlouisfed.org` Graph CSV requests; no alternative API attempt made for those eight. See `data/audits/2026-10-17-fred-api-live-success.md`.

**Scientific interpretation:** live transport success does not establish point-in-time financial conditions/stress vintages. The source snapshot includes currently available FRED revisions; NFCI is financial conditions, not identical to STLFSI4/CISS stress. User raw CSV/hash content not independently audited. First method pilot can proceed without the eight monetary/reserve histories; true five-country systemic factor still lacks banking, corporate credit and funding components.

## Completion of initial FRED catalog and file integrity phase (2026-10-17)

**USER REPORTED:** An additional FRED official API request for the remaining eight monetary/reserve/legacy records returned **8/8 OK**, snapshot `20261018T000222516029Z` (UTC), and `audit_downloads.py` now reports six local manifests, **34/40 OK, 0 FAILED, 6 NEVER_REQUESTED**. The unrequested six are two Banxico M1/M2, two BoE and two BoJ. The older Mexico FRED M2 stops May 2017, older M1 December 2018. These source counts are not scientific evidence of stress predictability. See `data/audits/2026-10-17-fred-catalog-complete.md`.

**IMPLEMENTED / TESTED OFFLINE:** `scripts/audit_source_quality.py` selects the latest success per series, checks local immutable CSV hash/row/date/numeric integrity and market close positivity. It writes only an ignored local report. **Not yet run on user's actual raw series.** Do not assert data quality until result is supplied. The remaining scientific hurdles are revisions and availability dates, market calendar matching, transformations, banking/credit/funding domains, external validation and held-out chronological forecasting.

## Initial quality audit WTI exception (2026-10-17)

**USER-REPORTED:** `scripts/audit_source_quality.py` inspected 34 successful source files; **33 PASS and only `CL=F` FAIL (6,566 records)** on the overly universal rule `market close prices must be strictly positive`. CFTC and EIA confirm negative WTI futures settlements are possible (notably −$37.63/b on 2020-04-20), but the user's negative CL=F dates and values have not yet been examined. Signed WTI metadata and an old-immutable-manifest fallback now permit nonpositive CL=F closes **with mandatory warning and exact dates/count/minimum**, and retain positivity for unmarked equity/FX. All other SHA256/date/finite checks remain strict.

**IMPLEMENTED, offline-tested; rerun still needed on VM.** This is an instrument-domain correction, not empirical evidence for the stress forecasting hypothesis. Ordinarily logged returns on CL=F are invalid if negative/zero price ratios; raw data must not be modified to hide the episode. See `data/audits/2026-10-17-source-quality-wti.md` and ADR-0006.

## VM complete source integrity and start of market-feature preparation (2026-10-17)

**USER-REPORTED VERIFIED BY LOCAL AUDIT:** **34/34 PASS**, zero fail, one signed WTI `CL=F` warning. Exact one nonpositive WTI close on 2020-04-20; minimum reported `-37.630001068115234`, i.e. −37.63/barrel. Agrees with CFTC/EIA historical event. All other source files pass physical manifest integrity. Original futures roll contract chain still requires independent review.

**IMPLEMENTED, OFFLINE TESTS:** `src/latent_risk/data/market_features.py` computes five-country local equity daily returns, trailing 21-observation volatility and 63-observation drawdown; optional country FX depreciation and volatility for non-US markets, direction-aware, on present/past observations. `scripts/build_market_pilot.py` checks original source integrity, saves local descriptive market features and an exact matching equity-date panel, but keeps ECB CISS and FRED stress indices in a separate reference CSV. CLI has **not yet run on user's actual VM files**. No retrospective full-sample standardization, fitted stress index or forecast outcomes are claimed. Daily labels and international close times remain unaudited. See `data/audits/2026-10-17-integrity-complete.md` and proposed ADR-0007.

## Derived market panel actually prepared on user VM (2026-10-17)

**USER-REPORTED:** `scripts/build_market_pilot.py` finished: **31,383** country/observation-date features from 2000-03-30 to 2026-10-16, **4,293** exact common five-equity dates 2007-07-05 to 2026-10-16, and **23,785** separately held-out CISS/STLFSI4/NFCI observation rows. Output says **NO MODELS FITTED**. The user pasted a truncated local path; raw generated files remain only in their ignored local `data/processed/market_pilot` hierarchy. Counts/date spans only, not direct assistant-read CSV verification. See `data/audits/2026-10-17-market-pilot-built.md`.

**IMPLEMENTED/OFFLINE VERIFIED:** new `scripts/audit_market_pilot.py` reports exact country and FX missingness, reference same-day overlap, source/output hashes and five-market data consistency; uses no fitted models, provides no claim of historical release dates. Synthetic checks passed in CI; waiting for VM run.

## Real descriptive market diagnosis and exploratory CISS benchmark code (2026-10-17)

**USER VM RUN:** `scripts/audit_market_pilot.py` completed on the existing derived pilot (`20261018T003625232736Z`). Market 31,383 rows; five-way exact equity intersection 4,293 dates (2007-07-05–2026-10-16); external ECB/FRED benchmark 23,785 observations. MEX FX 5,720/6,664 present; GBR 5,743/6,706; JPN 6,466/6,498; EA 4,814/4,839. US FX N/A by design. Same-date CISS overlaps EA 4,838, US 6,675, UK 6,705; weekly FRED 1,338 each. See `data/audits/2026-10-17-market-diagnostics-complete.md`. Historical release vintages and common intraday clocks remain unverified.

**IMPLEMENTED, OFFLINE CI VERIFIED; NOT EXECUTED ON REAL CISS**: preliminary EXP-0002 uses ECB CISS histories as *observed targets* only, models persistence, AR(1) and one-sided EWMA with past-only horizon-specific nested CV gains. Fixes observation-index horizons 1,5,21, evaluation start 2008-01-01 and 21-observation strides. No factor index, PLS smoother, crisis early-warning or pseudo-real-time inference is produced. See `experiments/EXP-0002.md`.

## BIS five-country nominal effective FX acquisition implemented (2026-10-17)

`IMPLEMENTED / SYNTHETICALLY TESTED`: Official BIS SDMX v2 API daily broad nominal effective FX indices `D.N.B.MX`, `D.N.B.US`, `D.N.B.GB`, `D.N.B.JP`, `D.N.B.XM` (Euro area). All are 2020=100 indices with appreciation-positive direction. `scripts/download_data.py --sources bis` writes per-series immutable source CSVs/SHA256 manifests and integrates existing audits. BIS index historic observation dates are not release times; weight vintages/revisions unknown. Candidate future comparable FX feature: negative log difference of NEER, but **not yet added to the existing derived market pilot**. No live user VM download performed yet; offline GitHub CI 79 tests passed on `dd5e4909`. See ADR-0008 and latest journal. Five catalog additions raise expected total from 40 to **45**; existing 34 successful live downloads do not change until new requests are performed.

## First BIS live download failed; numeric/missing data parser correction (2026-10-17)

**USER-REPORTED:** first `--sources bis` on VM returned **0/5** with `BIS SDMX has missing or nonfinite index values`, snapshot `20261018T021112030837Z`; seven manifests **34 OK / 5 BIS FAILED / 6 NEVER_REQUESTED** of 45. Old raw source integrity remains **34/34 PASS, 1 WTI warning**. The failed BIS source responses never became successful archived CSVs. **Root cause hypothesis:** old strict BIS parser rejected explicitly blank/missing SDMX observation values, common in daily index histories. Actual BIS payload not supplied.

**IMPLEMENTED and CI VERIFIED:** new BIS parser distinguishes explicit missing OBS_VALUE rows from malformed/nonfinite numeric tokens, drops missing rows without imputation and records source missing count/first dates/fraction in new successful manifest; rejects wrong SDMX dimensions, duplicate dates, all missing rows and bad numeric values. CI 88 tests/Ruff/structural validator/Sphinx pass on `7e700297`. **Live BIS retry remains pending**; do not claim actual five-source success or new latent index. See `data/audits/2026-10-17-bis-first-live-failure.md`.

## Research question
When and why do forecasts based on smoothed country financial-risk indices fail during financial disturbances? Are unusually large forecast errors informative beyond volatility changes and conventional benchmarks?

## What counts as risk?
There is no observed universal scalar risk series. The index is a model-based measurement: (a) signed standardized composites, (b) PCA, (c) dynamic factors, and later robust or regime-specific versions. Factor signs and scale conventions must be frozen from training vintages. A smaller forecast RMSE for one index does not establish that it is the better index because targets differ.

## Role of smoothing
The baseline proposed smoother is the Gaussian integrated random walk with a second-difference trend penalty and ratio `lambda = measurement_noise_variance / trend_second_difference_variance`, estimated by marginal likelihood. It is a method for forecasting a chosen index, not a substitute for the index itself.

## Two distinct experiments
1. **Retrospective** DFM/index built with full historical sample: description only.
2. **Pseudo-real-time** factor fitting, normalization, drift/tuning, and calibration restricted to publication-date information available by forecast origin: primary forecasting evidence.

## Pilot scope
Mexico, USA, UK, Japan, euro area; monthly data where market and monetary data can be matched with release dates. Proposed horizons 1, 3, 6 months; source availability and feasible start dates unconfirmed. Mexican 1994–95 crisis requires separate older-source data. Include quiet controls and the 2008–09, 2011–12, 2020, 2022 and 2023 event candidates when feasible.

## Legacy project findings (not replicated here)
The old U.S. DFM input series were logged VIX, WTI, GLD and DXY. The run used 2004–2026 full-sample DFM fitting before performing a 2008 train/validation/test analysis: this is **ex-post factor definition**, not pseudo-real-time measurement. Saved Gaussian DFM diagnostics did not pass. Its best refined validation candidate differed from the selected grid minimum. Historical 2008 validation RMSE ~1.92 and June–Dec test RMSE ~30.10 are motivation, not conclusive crisis prediction.

## Constraints
- Do not copy the earlier project's risk manuscript and label it as new original results.
- Preserve citation and joint-author contribution issues from original U.S. poster.
- No country-indicator dataset has been validated for real-time historical availability.
- Do not declare an event detector operational until false-alarm rates, calibration and matched controls exist.

## Linked prior resources
- Legacy risk project: https://github.com/heri-espino/Estimation-of-latent-risk-in-the-U.S.-market-using-representative-variables
- Smoothing-methods theory: https://github.com/heri-espino/Trend-Estimation


## 2026-10-18 — trend likelihood documentation integration
A concurrent agent implemented `src/latent_risk/trends/gaussian.py`, exports and `tests/test_trends_gaussian.py` on `agent/trend-likelihood`. The separate `agent/trend-likelihood-docs-20261018` branch inherits these commits without editing the other agent's owned files, and adds `notes/results/trend_likelihood.md` plus a dated journal. **PROVEN analytically under stated iid Gaussian and diffuse conditions:** affine two-dimensional nullspace, SPD normal equations, r/q ratio, valid Gaussian restricted likelihood and causal filter forecasts. **UNKNOWN pending remote CI:** numerical validity and test outcomes of the inherited remote agent code; a different local alternative implementation independently passed 81 synthetic tests. No financial-stress forecast study or historical first-release index has been completed by this modeling branch. Preserve separate later BIS acquisition findings.
