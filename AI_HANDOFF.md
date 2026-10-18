# AI handoff — Latent Risk

**Last updated:** 2026-10-17  
**Latest dated journal entry:** [2026-10-17-wti-signed-prices.md](journal/2026-10/2026-10-17-wti-signed-prices.md)  
**Current research stage:** user CLI now confirms 14 market + 5 ECB + 3 Banxico + **12 FRED** success via official FRED API. Six-manifest catalog audit **34 OK, 0 FAILED, 6 NEVER_REQUESTED**. Initial read-only file integrity audit user-reported: **33 PASS, 1 FAIL (WTI `CL=F` only)**. Positivity rule corrected for signed WTI futures; VM re-audit pending. No forecasting experiment executed.

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

## Proposed but unimplemented algorithms
- `PROPOSED`: country-specific Gaussian DFM, robust factors, Markov-switching index variants.
- `PROPOSED`: constrained local-linear-trend **marginal** MLE/REML with Kalman filtering.
- `PROPOSED`: rolling-origin pseudo-real-time cross-country evaluation and calibrated forecast exceedance analysis.

## Observed VM integrity results (user-reported 2026-10-17)
- User's `python scripts/audit_source_quality.py`: **33 PASS, 1 FAIL `market CL=F` (6,566 rows)**. Sole reported reason: closes not strictly positive. Institutional evidence supports possible negative WTI futures prices on 2020-04-20, but no actual user WTI observations have been inspected. Updated integrity validator is source-aware and allows signed WTI as **PASS with warnings, pending rerun**, while other market series remain strictly positive. See [audit note](data/audits/2026-10-17-source-quality-wti.md).

## Observed VM download status (user-reported 2026-10-17)
- **Latest SIXTH manifest**: eight more FRED API monthly series downloaded (8/8). Six-manifest audit now **34 OK, 0 FAILED, 6 NEVER_REQUESTED** out of 40. Older Mexican FRED M2 `MYAGM2MXM189N` ends 2017-05 (209 rows), older M1 `MANMM101MXM189S` ends 2018-12 (228 rows). Six not requested are Banxico money 2, Bank of England 2, Bank of Japan 2. See [completion note](data/audits/2026-10-17-fred-catalog-complete.md). Older per-run status descriptions below remain historical evidence, not current state.
- **Latest fifth manifest (20261017T235600038504Z)**: official FRED API with personal key: **4/4 successful**. DGS2/DGS10 each 6,700 rows (2000-01-03 to 2026-10-15); STLFSI4/NFCI each 1,397 rows (2000-01-07 to 2026-10-09). Combined 40 catalog codes: **26 OK / 8 FAILED / 6 NEVER_REQUESTED**. Eight FRED failures are older website Graph CSV attempts and were not tested using new API. Reference: [record](data/audits/2026-10-17-fred-api-live-success.md).
- New fourth manifest: all **12** FRED Graph CSV requests failed, with `RemoteDisconnected` or `ReadTimeoutError` errors; 40 expected series now **22 OK, 12 FAILED, 6 NEVER_REQUESTED**. Previously successful market/Banxico/ECB snapshots unchanged. Official FRED API alternative newly implemented, but NOT live-tested. Earlier three-manifest transcription remains historically accurate for its run.
- Three local manifests, 40 expected: **22 OK, 10 failed (FRED), 8 never requested**. ECB all 5 OK; new three CISS series each 6,997 dates Jan 2000–Oct 15 2026, and M1/M2 each 320 monthly dates. Banxico FIX/CETES/reserves 3 OK, newer M1/M2 not requested. All 14 Yahoo tickers OK (Euro Stoxx 50 starts 2007-03-30; several FX tickers start 2003-12-01). BoE/BoJ not requested. Complete statuses/dates: [transcription](data/audits/2026-10-17-user-vm-coverage.md).
- **Do not claim data validated, point-in-time, or a completed index model.** Raw bytes/hashes not available to assistant; no independently confirmed provider vintages.

## Experimental results and limitations
- `UNKNOWN`: no run of the international research design yet. Catalog now includes 14 Yahoo, 12 FRED (including STLFSI4/NFCI), 5 Banxico, 5 ECB (including 3 CISS), 2 BoE and 2 BoJ. Source status is independently detailed in user-reported coverage record. Mexico's historical FRED M2 ends in 2017.
- `PROPOSED`: point-in-time macro revisions/release-date audit, additional sovereign yields, financial-stress outcomes, and a complete balanced panel. UK M4 is NOT directly equivalent to US/EA/JP/MEX M2.
- The original 2008 exercise reported very different validation and test RMSEs but used factor parameters/standardization estimated through 2026 and a smoothing choice inconsistent with a better refined candidate. See `context/STATE.md`; **do not treat this as an independent early-warning result**.

## Decisions
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
1. Do **NOT** redownload ECB/FRED sources. **Next user VM action: `git pull --ff-only origin main`; `python scripts/audit_source_quality.py` again after WTI domain correction**; inspect warnings and `results/runs/source_quality/report.json`. Then prototype a labeled exploratory market-based / CISS study on validated saved local data; bank/credit/funding domains needed for systemic stress index. Banxico/BoE/BoJ six never-requested records optional. Keep user raw data and tokens private.
2. The alternate official FRED API succeeded; leave website graph failures recorded but do not block. Build a point-in-time country indicator catalog; start with Mexico, USA.
3. Implement and test likelihood-based trend smoothing, then index candidates, without reading future observations.
4. Freeze event windows and a common external target before confirming outcomes.

## Important files to inspect next
`AGENTS.md`, journal (in prescribed order), `experiments/EXP-0001.md`, `notes/definitions.md`, `paper/main.tex`, `src/latent_risk/`.
