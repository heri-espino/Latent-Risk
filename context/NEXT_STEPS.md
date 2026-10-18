# Next steps

- [x] User ran the **real derivative pilot diagnostic** on local `20261018T003625232736Z`: 31,383 country-date rows; 4,293 five-country equity dates; 23,785 benchmark rows. Country FX present/missing: MEX 5,720/944, GBR 5,743/963, JPN 6,466/32, EA 4,814/25; US FX N/A. CISS same-date overlaps EA 4,838, US 6,675, UK 6,705; FRED weekly references 1,338 each.
- [x] Implement exploratory ECB CISS **observation-index** matched-origin benchmark EXP-0002 with persistence, AR1 and h-specific nested-CV causal EWMA, offline tests and provenance. **Not yet run on actual VM CISS history.**
- [ ] **Next VM action:** `git pull --ff-only origin main` then `python scripts/run_ciss_baselines.py --start 2008-01-01 --horizons 1,5,21 --stride 21`; report score counts and RMSE/MAE. Treat as engineering/retrospective evidence only.
- [ ] The main scientific EXP-0001 still needs a source-release-time-aware index and forecast-origin protocol, second-difference penalized smoother and additional credit/bank/funding domains before confirmatory prediction claims.


- [x] **REAL USER VM PREPARATION** `python scripts/build_market_pilot.py` succeeded: **31,383** long five-country market rows (2000-03-30 to 2026-10-16), **4,293** exact common equity sessions (2007-07-05 to 2026-10-16), **23,785** external references (2000-01-03 to 2026-10-15).
- [x] Implemented read-only saved-derivative diagnostic `scripts/audit_market_pilot.py`, verifying hashes, FX missingness by country, common panel identities, same-date reference overlap and tests. **Not yet run against actual VM outputs**.
- [x] Actual market-pilot diagnostic completed on VM and country/FX/benchmark coverage reported; see `data/audits/2026-10-17-market-diagnostics-complete.md`.
- [ ] Decide forecast-origin clock and CISS reporting vintages; define an exploratory observed-target protocol without claiming actual past release-time predictive signals. Only then fit reference forecasting baselines / smoothing.


- [x] User reran corrected file audit: **34 PASS / 0 FAIL / 1 warning**. CL=F had exactly one nonpositive close, 2020-04-20, −37.630001068115234 (~−37.63); matches historical WTI futures settlement date.
- [x] Implemented end-of-day, past-only market-feature preparation: five country equities, four FX quotes, exact dates, 21/63 observation trailing statistics, explicitly separate ECB/FRED benchmarks, source-hash provenance and tests.
- [x] User ran `scripts/build_market_pilot.py` and reported all three derived output row counts/spans. No models were fitted.
- [ ] Inspect date-matched common panel, market/FX missingness, source adjustments, and cross-timezone close rules before model fitting.
- [ ] Freeze first descriptive observed CISS target versus original inferred latent-factor estimand; do not label this dataset a valid pseudo-real-time panel.


- [x] User VM quality run inspected 34 source series: **33 PASS, `CL=F` FAIL** exclusively for market positivity rule. Do not treat WTI futures negative closes as automatically corrupt (CFTC confirms 2020-04-20 negative settlement).
- [x] Correct WTI `CL=F` to signed price domain, retaining hard finite/hash/calendar checks, nonpositive observations in data, warning/count/minimum/date, and positivity of unmarked equity/FX; test legacy source manifests.
- [x] Completed corrected VM physical source QA: all 34 PASS, one signed WTI warning with date/minimum verified by local script.
- [ ] Define admissible oil futures features as past-only signed differences or economically justified transforms; audit front-contract rolls and never log-transform through zero.


- [x] User completed the official FRED API second request: **8/8 OK**. Cumulative catalog (six manifests) **34 OK / 0 FAILED / 6 NEVER_REQUESTED**; eight new monthly histories recorded in `data/audits/2026-10-17-fred-catalog-complete.md`.
- [x] Added read-only CSV SHA256, row/date/value integrity gate: `python scripts/audit_source_quality.py`, with seven offline tests. **Not yet run on real downloaded files.**
- [x] First VM read-only quality check executed: 33/34 passed; WTI signed-price domain corrected, rerun pending. Do not upload vendor data to Git.
- [x] Implemented initial strict five-equity-market date intersection and past-only equity/FX feature preparation. Real matched source dates and exact quote close times still require VM-derived output audit.
- [ ] Keep CISS/STLFSI4/NFCI as external comparison references and choose first exploratory forecast target/chronological evaluation protocol.
- [ ] Missing banking/credit/funding dimensions remain a limitation for full systemic-risk claims.


- [x] User retried all 12 FRED graph CSV series on 2026-10-17: **0/12**, all `RemoteDisconnected` or `ReadTimeoutError`. Four manifests total: **22 OK, 12 FAILED, 6 NEVER_REQUESTED**; no loss of earlier market/Banxico/ECB snapshots.
- [x] Implement an **opt-in official FRED API v1 backend** at `api.stlouisfed.org` using `FRED_API_KEY`, `--fred-backend api`, optional `--only` for short probes, safe exception redaction and synthetic offline tests.
- [x] User verified `api.stlouisfed.org` reachability and downloaded **4/4** FRED series (`DGS2`, `DGS10`, `STLFSI4`, `NFCI`) with key via official API. Five-manifest status now **26 OK, 8 FAILED, 6 NEVER_REQUESTED**, per user CLI (not inspected raw CSVs).
- [x] The other eight FRED money/reserves series have been acquired via official API and saved; not mandated inputs to the equity/FX/CISS methodological pilot.
- [ ] Distinguish FRED's now-working official API from the failed website Graph CSV endpoint in any diagnosis.

- [x] User-reported first full download audit: 3 VM manifests, 40 catalog sources = **22 OK (market 14, Banxico 3, ECB 5), 10 FAILED (FRED), 8 NEVER_REQUESTED**. Transcribed non-sensitive statuses in `data/audits/2026-10-17-user-vm-coverage.md`; raw files still on user's VM, not independently checked.
- [x] ECB daily CISS for EA/US/GBR successfully downloaded (6,997 rows each since Jan 2000); no need to rerun ECB.
- [ ] Start *descriptive/technical*, not confirmatory, pilot with published CISS and local market inputs; distinguish observed CISS target from factor construction and original-latent-index research.
- [ ] Build and test proper dated market panel and trailing equity/FX return/volatility/drawdown features with genuine past-only alignment, noting five-country `^STOXX50E` starts March 30, 2007.
- [ ] Source multi-domain credit/bank/funding market variables and stable histories before making a cross-country systemic financial-stress measurement claim.

- [x] Review OFR FSI, ECB CISS, Banxico IEMF and BIS vulnerability literature; propose direct stress-factor domains separate from money stocks and external benchmark series (`data/indicator_priorities.md`, `ADR-0005`).
- [x] Register ECB CISS keys for US/UK/EA, FRED STLFSI4/NFCI for external validation; support daily ECB CSV and date-scoped API requests, with offline tests.
- [ ] Confirm which market-based indicators can actually be fetched across all five geographies; the user has not uploaded complete download manifests.
- [ ] Design a 2008-compatible credit/funding proxy without ICE FRED corporate credit spreads (restricted to 3 years since Apr 2026).
- [ ] Examine original historical Banxico IEMF tables for external evaluation and find a credible Japan reference index or explicitly report its absence.

- [x] Audit the repository bootstrap: 12 tests, Ruff, structural validator and Sphinx passed on commit `075f9027` (https://github.com/heri-espino/Latent-Risk/actions/runs/38994859776); PR-only change checker and LaTeX compilation were not run.
- [x] Implement an initial candidate source catalog and downloader with 19 offline tests passing, Ruff, structure and Sphinx pass (https://github.com/heri-espino/Latent-Risk/actions/runs/38998827014); **no live data have been retrieved yet**.
- [x] Add ECB M1/M2, BoE M4/SONIA, BOJ M1/M2 and Banxico modern M1/M2 to the audited catalog; add independent source parsers and local multi-snapshot auditor (all new live-provider fetches `UNVERIFIED`).
- [ ] Run expanded downloader (`--sources ecb,boe,boj` and again `--sources banxico` for the new M1/M2), inspect all manifests with `scripts/audit_downloads.py`, preserve SHA256 provenance and report missing or short series.
- [x] FRED Graph CSV website `ConnectionError` bypassed with **official** FRED API: all 12 requested series acquired. Original graph failure remains in historic manifests.
- [x] Identify Banxico current money aggregates as M1 `SF311408`, M2 `SF311418` (modern methodology). Independently confirm API metadata and observed coverage on VM.
- [ ] Identify comparable money aggregates and rates for all five study geographies; UK M4, BoJ M2, ECB M2 have different definitions. Audit historical release dates and revisions.
- [ ] Establish a source/availability-date catalog for Mexico, USA, UK, Japan and euro area. Prefer a small comparable core indicator panel.
- [ ] Decide point-in-time index identification, sign convention, standardization and missing-data rules.
- [ ] Implement constrained Gaussian d=2 local-linear trend with marginalized likelihood; derive and verify equivalent PLS optimization.
- [ ] Implement a country-panel experimental loader with strict observation_date / available_date semantics.
- [ ] Benchmark signed average, PCA and Gaussian DFM on the same vintage information set.
- [ ] Specify a common external outcome for cross-index predictive validity; never compare raw factor RMSEs as if factors were identical.
- [ ] Freeze the pilot test years, crisis windows, quiet controls, horizons and primary evaluation metrics before running confirmation.
- [ ] Complete bibliography/Docling annotations only after verifying source availability and rights.
- [ ] Discuss authorship and prior-work citation with the earlier U.S. latent-risk collaborators.
