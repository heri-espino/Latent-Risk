# AI handoff — Latent Risk

**Last updated:** 2026-10-18 (QA branch only; acquisition claims below remain dated 2026-10-17)  
**Latest dated journal entry:** [2026-10-18-library-qa-contracts.md](journal/2026-10/2026-10-18-library-qa-contracts.md)  
**Current research stage:** user CLI now confirms 14 market + 5 ECB + 3 Banxico + **12 FRED** success via official FRED API. Six-manifest catalog audit **34 OK, 0 FAILED, 6 NEVER_REQUESTED**. User VM source integrity re-audit: **34/34 PASS, zero failed, one signed WTI warning**. One CL=F nonpositive close on 2020-04-20 at −37.630001068115234 (matches documented −37.63). No models fitted. User successfully prepared the market panel: 31,383 country/date feature rows; 4,293 common five-equity dates (2007-07-05 to 2026-10-16); 23,785 separately held-out ECB/FRED reference rows. Exploratory CISS forecasting benchmark EXP-0002 code implemented and CI tested but **not run on user's actual CISS files**; full latent-risk EXP-0001 remains proposed/unexecuted.

## Project identity and objective
International assessment of when smoothed forecasts of financial-risk indicators fail and whether exceedances add information about financial stress beyond ordinary time-varying volatility. Mexico is a core country. The early U.S.-only repository is antecedent work, not validated evidence transferred here.

## Verified mathematical results
- `PROVEN (standard)`: under Gaussian independent measurement and second-difference shocks, and compatible diffuse boundary treatment, the PLS penalty ratio is `lambda = r/q`. See `notes/definitions.md`; implementation equivalence still requires tests.
- `UNKNOWN`: whether this framework reliably identifies crises beyond conventional risk and volatility indicators.

## Open mathematical questions
How should estimated factor uncertainty enter predictive intervals? What common observable target enables fair cross-index forecasting comparisons? How should the factor be anchored between refits? Can the exact penalized solution be matched by a constrained state-space likelihood implementation?

## Implemented algorithms and features
- `IMPLEMENTED` and **CI VERIFIED**: training-only signed composite and PCA, vintage filtering, and standardized-error utilities, with 12 passing unit tests.
- `IMPLEMENTED` and **CI VERIFIED**: repository structural validator, Ruff linting and Sphinx docs builder.

- `IMPLEMENTED` and **CI VERIFIED**: Yahoo market, FRED graph CSV, and optional token-gated Banxico raw-source downloading with immutable UTC snapshots, per-series SHA256, provenance and failure manifest. End date is exclusive. Unit tests use synthetic/in-memory data; no provider downloaded in CI.

- `IMPLEMENTED`: official ECB BSI (euro area M1/M2), BoE IADB (UK M4 and SONIA), BoJ API (Japan M1/M2) with source-specific CSV/JSON parsers and offline tests. Modern Banxico M1/M2 (`SF311408`, `SF311418`) added to catalog. `scripts/audit_downloads.py` aggregates latest successful local snapshots separately from network failures. All live new-provider statuses remain `UNKNOWN` until VM run.

- `IMPLEMENTED`: ECB daily CISS parser and downloader entries for US/UK/EA; FRED published STLFSI4/NFCI reference identifiers. Source catalog design explicitly tags `external_stress_benchmark` and excludes these from a proposed latent-input panel.

- `IMPLEMENTED`: optional official FRED API v1 backend `--fred-backend api`, requiring `FRED_API_KEY`, with `--only` identifier filtering and secret redaction. **VERIFIED BY USER'S LIVE VM COMMAND OUTPUT** for DGS2, DGS10, STLFSI4 and NFCI: all four fetched via `api.stlouisfed.org`; not independently inspected as raw CSVs. Default Graph CSV remains unchanged.

- `IMPLEMENTED` and **CI VERIFIED**: `python scripts/audit_source_quality.py` checks local saved CSV SHA256, manifest alignment, date ordering, finite numeric values and market close integrity, without modifying raw files. It emits local ignored `results/runs/source_quality/report.json`. **User initial run: 33 PASS, WTI `CL=F` failed only strict positivity.** Corrected signed WTI policy is CI-tested but not yet rerun on user VM.

- `IMPLEMENTED`: WTI `CL=F` is a signed futures price domain, with nonpositive-close warnings and count/date/minimum report, legacy manifest fallback, and retained strict equity/FX positivity. Added `ADR-0006` and tests. Actual WTI nonpositive observation dates/values are still UNKNOWN; re-run audit in VM.

- `IMPLEMENTED` / offline tests: `src/latent_risk/data/market_features.py` and `python scripts/build_market_pilot.py` prepare exact-date, past-only 5-country equity+4-FX descriptive features and separate stress benchmarks (3 ECB CISS and 2 FRED indices); save ignored dated CSVs and SHA256 manifest. **Run successfully by user on VM**, producing the above three CSVs in a dated ignored directory. No fitted model or true point-in-time panel.

- `IMPLEMENTED` and offline CI verified (57 passed): `python scripts/audit_market_pilot.py` checks existing derivatives' hashes, per-country FX/market coverage, strict five-equity calendar/value matching and *separate* ECB/FRED benchmark same-date overlaps; it writes ignored `results/runs/market_diagnostics/summary.json`. **Succeeded on user VM**, with diagnostic results above.

- `IMPLEMENTED / CI VERIFIED`: exploratory `EXP-0002` three-series ECB CISS *direct forecast* baselines, persistence vs AR1 vs nested historical CV-selected one-sided EWMA, horizons 1/5/21 CISS observation steps. Run `python scripts/run_ciss_baselines.py --start 2008-01-01 --horizons 1,5,21 --stride 21` on VM. Neither real-time first-release CISS nor the desired penalized second-difference local-linear trend; not yet run on VM.

- `IMPLEMENTED, OFFLINE CI VERIFIED`: BIS daily broad NEER downloader via `python scripts/download_data.py --start 2000-01-01 --end 2026-10-18 --sources bis`, five canonical codes MX/US/GB/JP/XM; SDMX v2 CSV strict identity/parser; audit included. BIS key-free official API **first LIVE attempt 0/5 (parser rejected missing values); corrected offline, live retry PENDING**. Uses revised current-vintage observations; old USD bilateral and DXY untouched. 79 tests green at https://github.com/heri-espino/Latent-Risk/actions/runs/39088582188. **NOT YET integrated into a new market feature pilot**.

- `IMPLEMENTED` / offline verified, NOT live-retested: revised BIS SDMX `OBS_VALUE` parser accepts narrowly defined missing *rows* with NO zero-fill/imputation and logs source missing counts/dates/rate + response SHA256 in new successful snapshot manifests; rejects unknown malformed/nonfinite values, duplicate dates, wrong dimensions and empty observations. Correction green **88 tests** on `7e700297`: https://github.com/heri-espino/Latent-Risk/actions/runs/39089446309 . See first failed live attempt below.

## Proposed but unimplemented algorithms
- `PROPOSED`: country-specific Gaussian DFM, robust factors, Markov-switching index variants.
- `PROPOSED`: constrained local-linear-trend **marginal** MLE/REML with Kalman filtering.
- `PROPOSED`: rolling-origin pseudo-real-time cross-country evaluation and calibrated forecast exceedance analysis.

## First real BIS download failed on user VM (2026-10-17)
- `python scripts/download_data.py --start 2000-01-01 --end 2026-10-18 --sources bis` first yielded **0/5**, all `BIS SDMX has missing or nonfinite index values`. Failed snapshot `20261018T021112030837Z`. **Seven manifests**: **34 OK, 5 FAILED, 6 NEVER_REQUESTED** of 45. Older raw QA **34/34 PASS / 1 WTI warning**, expected because BIS did not save a success. The original parser rejected all NA cells; revised parser recognizes explicit missing rows while preserving strict nonmissing validation. This is a hypothesized fix to verify with a new VM retry, NOT a confirmed five-series download. Audit: `data/audits/2026-10-17-bis-first-live-failure.md`.

## Completed real VM market-pilot diagnostic (reported 2026-10-17)
- `python scripts/audit_market_pilot.py` finished for timestamp `20261018T003625232736Z`: 31,383 market rows, 4,293 common equity dates (2007-07-05–2026-10-16), 23,785 benchmark values. FX complete/missing: MEX 5,720/944, GBR 5,743/963, JPN 6,466/32, EA 4,814/25. US FX deliberately N/A. Same-date CISS overlap EA 4,838, US 6,675, UK 6,705; weekly STLFSI4 and NFCI 1,338 each. See `data/audits/2026-10-17-market-diagnostics-complete.md`. Descriptive coverage, **no model yet**.

## Actual VM derived dataset (reported 2026-10-17)
- `python scripts/build_market_pilot.py` returned **31,383** country-market rows, **4,293** exact five-country equity dates (2007-07-05 to 2026-10-16) and **23,785** separate reference observations. Preparation-only; no models fitted. Source: `data/audits/2026-10-17-market-pilot-built.md`. `scripts/audit_market_pilot.py` now exists for numerical coverage verification; still pending VM run.

## Observed VM integrity results (user-reported 2026-10-17)
- Corrected **latest** re-audit: 34/34 PASS, 0 fail, 1 WTI warning; one CL=F nonpositive close **2020-04-20, −37.630001068115234**. Matches historically documented −37.63; non-WTI data pass. Prior 33/34 result below is historical, not current. Evidence in `data/audits/2026-10-17-integrity-complete.md`.

- User's `python scripts/audit_source_quality.py`: **33 PASS, 1 FAIL `market CL=F` (6,566 rows)**. Sole reported reason: closes not strictly positive. Institutional evidence supports possible negative WTI futures prices on 2020-04-20, but no actual user WTI observations have been inspected. Updated integrity validator is source-aware and allows signed WTI as **PASS with warnings, pending rerun**, while other market series remain strictly positive. See [audit note](data/audits/2026-10-17-source-quality-wti.md).

## Observed VM download status (user-reported 2026-10-17)
- **Latest SIXTH manifest**: eight more FRED API monthly series downloaded (8/8). Six-manifest audit now **34 OK, 0 FAILED, 6 NEVER_REQUESTED** out of 40. Older Mexican FRED M2 `MYAGM2MXM189N` ends 2017-05 (209 rows), older M1 `MANMM101MXM189S` ends 2018-12 (228 rows). Six not requested are Banxico money 2, Bank of England 2, Bank of Japan 2. See [completion note](data/audits/2026-10-17-fred-catalog-complete.md). Older per-run status descriptions below remain historical evidence, not current state.
- **Latest fifth manifest (20261017T235600038504Z)**: official FRED API with personal key: **4/4 successful**. DGS2/DGS10 each 6,700 rows (2000-01-03 to 2026-10-15); STLFSI4/NFCI each 1,397 rows (2000-01-07 to 2026-10-09). Combined 40 catalog codes: **26 OK / 8 FAILED / 6 NEVER_REQUESTED**. Eight FRED failures are older website Graph CSV attempts and were not tested using new API. Reference: [record](data/audits/2026-10-17-fred-api-live-success.md).
- New fourth manifest: all **12** FRED Graph CSV requests failed, with `RemoteDisconnected` or `ReadTimeoutError` errors; 40 expected series now **22 OK, 12 FAILED, 6 NEVER_REQUESTED**. Previously successful market/Banxico/ECB snapshots unchanged. Official FRED API alternative newly implemented, but NOT live-tested. Earlier three-manifest transcription remains historically accurate for its run.
- Three local manifests, 40 expected: **22 OK, 10 failed (FRED), 8 never requested**. ECB all 5 OK; new three CISS series each 6,997 dates Jan 2000–Oct 15 2026, and M1/M2 each 320 monthly dates. Banxico FIX/CETES/reserves 3 OK, newer M1/M2 not requested. All 14 Yahoo tickers OK (Euro Stoxx 50 starts 2007-03-30; several FX tickers start 2003-12-01). BoE/BoJ not requested. Complete statuses/dates: [transcription](data/audits/2026-10-17-user-vm-coverage.md).
- **Do not claim data validated, point-in-time, or a completed index model.** Raw bytes/hashes not available to assistant; no independently confirmed provider vintages.

## Experimental results and limitations
- `UNKNOWN`: no run of the international research design yet. Catalog now includes 14 Yahoo, 12 FRED (including STLFSI4/NFCI), 5 Banxico, 5 ECB (including 3 CISS), 2 BoE, 2 BoJ and **5 BIS broad daily NEER candidates not yet fetched live**. Source status is independently detailed in user-reported coverage record. Mexico's historical FRED M2 ends in 2017.
- `PROPOSED`: point-in-time macro revisions/release-date audit, additional sovereign yields, financial-stress outcomes, and a complete balanced panel. UK M4 is NOT directly equivalent to US/EA/JP/MEX M2.
- The original 2008 exercise reported very different validation and test RMSEs but used factor parameters/standardization estimated through 2026 and a smoothing choice inconsistent with a better refined candidate. See `context/STATE.md`; **do not treat this as an independent early-warning result**.

## Decisions
- [ADR-0008](journal/decisions/ADR-0008.md): BIS five-country consistent NEER acquisition, preservation of old FX inputs.
- [ADR-0007](journal/decisions/ADR-0007.md) (`PROPOSED`): first retrospective market features, exact-calendar matching and separate external stress references.
- [ADR-0006](journal/decisions/ADR-0006.md): instrument-specific signed WTI futures price audit policy.
- [ADR-0005](journal/decisions/ADR-0005.md) (`PROPOSED`): stress-first index measurements; separate official benchmark indices from raw factor inputs.
- [ADR-0004](journal/decisions/ADR-0004.md): official provider integration and non-equivalence of money-stock definitions.
- [ADR-0003](journal/decisions/ADR-0003.md): acquire raw source snapshots separately from the historically published point-in-time study panel.
- [ADR-0001](journal/decisions/ADR-0001.md): new separate repository, `src/` architecture, journal-first AI workflow.
- [ADR-0002](journal/decisions/ADR-0002.md): measurement, smoothing, and evaluation are independent stages; no retroactive real-time claims.

## Known issues and unresolved status
- The original FRED graph endpoint failed on all 12 series; official FRED API later succeeded 4/4 for four selected IDs. Eight other FRED Graph CSV failures remain historic, not current official API failures. Initial source series are candidates; downloads may fail because of network, vendor changes or incomplete coverage. Any failure gives a nonzero exit status and an auditable manifest. There is **no** complete current Mexican M1/M2 acquisition yet.
- No verified international release-date panel exists; source data must be audited.
- Final manuscript authorship and source reuse should be discussed with original collaborators.
- Automated tests must be executed and their outcomes recorded after committing the initial scaffold.

## Current testing status
- `VERIFIED COMPUTATIONALLY` source acquisition module on `8fb85d0`: **19 passed** (three harmless Python invalid-escape deprecation warnings, corrected in next documentation cleanup), Ruff **pass**, structure **pass**, Sphinx **pass**: https://github.com/heri-espino/Latent-Risk/actions/runs/38998827014. These checks use synthetic data; they do not test live network retrieval.
- `VERIFIED COMPUTATIONALLY` on commit `075f9027`: **12 passed**, Ruff **pass**, research structure validator **pass**, Sphinx documentation **pass**. Evidence: https://github.com/heri-espino/Latent-Risk/actions/runs/38994859776.
- PR-only `check_change_protocol.py` and LaTeX PDF compilation were not executed in the push CI run; original setup bugs and corrections are documented in the latest journal entry.

## Exact next actions
0. Review [proposed indicator priorities](data/indicator_priorities.md); M1/M2/M4 no longer assumed core stress factors. Core candidate feature domains are market/equity downside, FX volatility, funding/credit spread and banking stress; BIS credit gap/DSR is a different longer-horizon vulnerability experiment. ECB CISS for EA/US/UK and Banxico IEMF are reference comparisons, not factor input variables. US ICE credit-spread FRED data limited to ~3 years since April 2026, not suitable for historical 2008 tests without other sources.
1. Do **NOT** redownload ECB/FRED sources. **Next user VM action: `git pull --ff-only origin main`; rerun `python scripts/download_data.py --start 2000-01-01 --end 2026-10-18 --sources bis`; then `python scripts/audit_downloads.py` and `python scripts/audit_source_quality.py`.** First BIS 0/5 attempt is fully recorded, parser corrected offline only. Existing CISS EXP-0002 code remains available to run later. This is an observation-index exploratory method check, **not** real-time CISS or user-made latent-index evidence; then work on strict information-set rules; bank/credit/funding domains needed for systemic stress index. Banxico/BoE/BoJ six never-requested records optional. Keep user raw data and tokens private.
2. The alternate official FRED API succeeded; leave website graph failures recorded but do not block. Build a point-in-time country indicator catalog; start with Mexico, USA.
3. Implement and test likelihood-based trend smoothing, then index candidates, without reading future observations.
4. Freeze event windows and a common external target before confirming outcomes.

## Important files to inspect next
`AGENTS.md`, journal (in prescribed order), `experiments/EXP-0001.md`, `notes/definitions.md`, `paper/main.tex`, `src/latent_risk/`.

## Independent library API QA — 2026-10-18 (branch-only, PROPOSED)

`docs/architecture/interfaces.md` and `integration_checklist.md` propose a versioned source/feature contract (nullable verified UTC availability, explicit benchmark role, immutable source-hash lineage), factor→one-sided state→forecast→event-score Protocol boundaries, and coordinator decisions. New `tests/test_public_contracts.py` uses synthetic offline fixtures to exercise **existing** importable public boundaries and a clearly test-local one-sided forecast stub; no production statistical engine or new exports were added. Strict release-time and multi-vintage enforcement remain **UNIMPLEMENTED**; current `data.available_as_of` checks user-provided timezone-naive **dates only**. See dated journal. PR CI verification is separate from design review; do not imply that EXP-0001 has run.
