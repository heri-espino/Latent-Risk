# AI handoff — Latent Risk

**Last updated:** 2026-10-17  
**Latest dated journal entry:** [2026-10-17-vm-coverage.md](journal/2026-10/2026-10-17-vm-coverage.md)  
**Current research stage:** live user VM downloads **reported** for 14 market, 3 Banxico and 5 ECB sources; 40-series catalog coverage has been transcribed from CLI output. Raw files/manifests have not been independently read; no forecasting experiment has been executed.

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

## Proposed but unimplemented algorithms
- `PROPOSED`: country-specific Gaussian DFM, robust factors, Markov-switching index variants.
- `PROPOSED`: constrained local-linear-trend **marginal** MLE/REML with Kalman filtering.
- `PROPOSED`: rolling-origin pseudo-real-time cross-country evaluation and calibrated forecast exceedance analysis.

## Observed VM download status (user-reported 2026-10-17)
- Three local manifests, 40 expected: **22 OK, 10 failed (FRED), 8 never requested**. ECB all 5 OK; new three CISS series each 6,997 dates Jan 2000–Oct 15 2026, and M1/M2 each 320 monthly dates. Banxico FIX/CETES/reserves 3 OK, newer M1/M2 not requested. All 14 Yahoo tickers OK (Euro Stoxx 50 starts 2007-03-30; several FX tickers start 2003-12-01). BoE/BoJ not requested. Complete statuses/dates: [transcription](data/audits/2026-10-17-user-vm-coverage.md).
- **Do not claim data validated, point-in-time, or a completed index model.** Raw bytes/hashes not available to assistant; no independently confirmed provider vintages.

## Experimental results and limitations
- `UNKNOWN`: no run of the international research design yet. Catalog now includes 14 Yahoo, 12 FRED (including STLFSI4/NFCI), 5 Banxico, 5 ECB (including 3 CISS), 2 BoE and 2 BoJ. Source status is independently detailed in user-reported coverage record. Mexico's historical FRED M2 ends in 2017.
- `PROPOSED`: point-in-time macro revisions/release-date audit, additional sovereign yields, financial-stress outcomes, and a complete balanced panel. UK M4 is NOT directly equivalent to US/EA/JP/MEX M2.
- The original 2008 exercise reported very different validation and test RMSEs but used factor parameters/standardization estimated through 2026 and a smoothing choice inconsistent with a better refined candidate. See `context/STATE.md`; **do not treat this as an independent early-warning result**.

## Decisions
- [ADR-0005](journal/decisions/ADR-0005.md) (`PROPOSED`): stress-first index measurements; separate official benchmark indices from raw factor inputs.
- [ADR-0004](journal/decisions/ADR-0004.md): official provider integration and non-equivalence of money-stock definitions.
- [ADR-0003](journal/decisions/ADR-0003.md): acquire raw source snapshots separately from the historically published point-in-time study panel.
- [ADR-0001](journal/decisions/ADR-0001.md): new separate repository, `src/` architecture, journal-first AI workflow.
- [ADR-0002](journal/decisions/ADR-0002.md): measurement, smoothing, and evaluation are independent stages; no retroactive real-time claims.

## Known issues and unresolved status
- All ten FRED series previously failed on user's VM due to ConnectionError; this is unresolved separately from the new official sources. Initial source series are candidates; downloads may fail because of network, vendor changes or incomplete coverage. Any failure gives a nonzero exit status and an auditable manifest. There is **no** complete current Mexican M1/M2 acquisition yet.
- No verified international release-date panel exists; source data must be audited.
- Final manuscript authorship and source reuse should be discussed with original collaborators.
- Automated tests must be executed and their outcomes recorded after committing the initial scaffold.

## Current testing status
- `VERIFIED COMPUTATIONALLY` source acquisition module on `8fb85d0`: **19 passed** (three harmless Python invalid-escape deprecation warnings, corrected in next documentation cleanup), Ruff **pass**, structure **pass**, Sphinx **pass**: https://github.com/heri-espino/Latent-Risk/actions/runs/38998827014. These checks use synthetic data; they do not test live network retrieval.
- `VERIFIED COMPUTATIONALLY` on commit `075f9027`: **12 passed**, Ruff **pass**, research structure validator **pass**, Sphinx documentation **pass**. Evidence: https://github.com/heri-espino/Latent-Risk/actions/runs/38994859776.
- PR-only `check_change_protocol.py` and LaTeX PDF compilation were not executed in the push CI run; original setup bugs and corrections are documented in the latest journal entry.

## Exact next actions
0. Review [proposed indicator priorities](data/indicator_priorities.md); M1/M2/M4 no longer assumed core stress factors. Core candidate feature domains are market/equity downside, FX volatility, funding/credit spread and banking stress; BIS credit gap/DSR is a different longer-horizon vulnerability experiment. ECB CISS for EA/US/UK and Banxico IEMF are reference comparisons, not factor input variables. US ICE credit-spread FRED data limited to ~3 years since April 2026, not suitable for historical 2008 tests without other sources.
1. ECB collection already succeeded on VM; do **not** insist on redownloading it. Prototype a clearly labeled exploratory market-based / CISS methodological study using saved local data; separately source credit/bank/funding domains before a full systemic latent-index claim. Optionally collect new Banxico monetary and BoE/BoJ macro data only if motivated by a separate macro research question. Keep user raw data/token private.
2. Diagnose FRED network separately and build a point-in-time country indicator catalog; start with Mexico, USA.
3. Implement and test likelihood-based trend smoothing, then index candidates, without reading future observations.
4. Freeze event windows and a common external target before confirming outcomes.

## Important files to inspect next
`AGENTS.md`, journal (in prescribed order), `experiments/EXP-0001.md`, `notes/definitions.md`, `paper/main.tex`, `src/latent_risk/`.
