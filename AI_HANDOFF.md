# AI handoff — Latent Risk

**Last updated:** 2026-10-16  
**Latest dated journal entry:** [2026-10-16-source-acquisition.md](journal/2026-10/2026-10-16-source-acquisition.md)  
**Current research stage:** raw-source download infrastructure implemented and CI tested; no live data acquisition or international forecast experiment has been executed.

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

## Proposed but unimplemented algorithms
- `PROPOSED`: country-specific Gaussian DFM, robust factors, Markov-switching index variants.
- `PROPOSED`: constrained local-linear-trend **marginal** MLE/REML with Kalman filtering.
- `PROPOSED`: rolling-origin pseudo-real-time cross-country evaluation and calibrated forecast exceedance analysis.

## Experimental results and limitations
- `UNKNOWN`: no run of the international research design yet. No actual new source download has been run by this assistant. Initial catalog includes 14 Yahoo tickers, 10 FRED series and 3 optional Banxico codes. Mexico's historical FRED M2 ends in 2017.
- `PROPOSED`: point-in-time macro revisions/release-date audit, missing macro series, country yield-curve comparability, and a complete balanced panel.
- The original 2008 exercise reported very different validation and test RMSEs but used factor parameters/standardization estimated through 2026 and a smoothing choice inconsistent with a better refined candidate. See `context/STATE.md`; **do not treat this as an independent early-warning result**.

## Decisions
- [ADR-0003](journal/decisions/ADR-0003.md): acquire raw source snapshots separately from the historically published point-in-time study panel.
- [ADR-0001](journal/decisions/ADR-0001.md): new separate repository, `src/` architecture, journal-first AI workflow.
- [ADR-0002](journal/decisions/ADR-0002.md): measurement, smoothing, and evaluation are independent stages; no retroactive real-time claims.

## Known issues and unresolved status
- Initial source series are candidates; downloads may fail because of network, vendor changes or incomplete coverage. Any failure gives a nonzero exit status and an auditable manifest. There is **no** complete current Mexican M1/M2 acquisition yet.
- No verified international release-date panel exists; source data must be audited.
- Final manuscript authorship and source reuse should be discussed with original collaborators.
- Automated tests must be executed and their outcomes recorded after committing the initial scaffold.

## Current testing status
- `VERIFIED COMPUTATIONALLY` source acquisition module on `8fb85d0`: **19 passed** (three harmless Python invalid-escape deprecation warnings, corrected in next documentation cleanup), Ruff **pass**, structure **pass**, Sphinx **pass**: https://github.com/heri-espino/Latent-Risk/actions/runs/38998827014. These checks use synthetic data; they do not test live network retrieval.
- `VERIFIED COMPUTATIONALLY` on commit `075f9027`: **12 passed**, Ruff **pass**, research structure validator **pass**, Sphinx documentation **pass**. Evidence: https://github.com/heri-espino/Latent-Risk/actions/runs/38994859776.
- PR-only `check_change_protocol.py` and LaTeX PDF compilation were not executed in the push CI run; original setup bugs and corrections are documented in the latest journal entry.

## Exact next actions
1. On a Conda VM, download the candidate raw sources with `python scripts/download_data.py --start 2000-01-01 --end 2026-10-17` after `pip install -e '.[data]'`. Inspect `data/raw/downloads/<UTC timestamp>/manifest.json` and record any missing series; do not copy raw data to public Git.
2. Build and verify a point-in-time country indicator catalog; start with Mexico, USA.
3. Implement and test likelihood-based trend smoothing, then index candidates, without reading future observations.
4. Freeze event windows and a common external target before confirming outcomes.

## Important files to inspect next
`AGENTS.md`, journal (in prescribed order), `experiments/EXP-0001.md`, `notes/definitions.md`, `paper/main.tex`, `src/latent_risk/`.
