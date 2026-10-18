# 2026-10-18 — BIS five-country download complete; separate effective-FX pilot implemented

**Date:** 2026-10-18 (America/Mexico_City)  
**Objective:** finish the first comparable five-country nominal effective FX source collection, maintain failed-download provenance, and create a versioned alternative to the previously audited bilateral-USD market feature dataset.

## Motivation / question

An earlier US FX feature was N/A because USD/USD has no variation. BIS daily broad NEER supplies a trade-weighted appreciation-strength measurement for *all* five countries under one published methodology. After fixing missing SDMX observation handling, are the five series now valid files, and can we prepare an aligned, causal-on-observation-index alternative panel without overwriting the earlier baseline?

## User VM results (not invented)

- Source snapshot `20261018T145643915821Z`: **5/5 BIS OK**. All keys `D.N.B.MX`, `D.N.B.US`, `D.N.B.GB`, `D.N.B.JP`, `D.N.B.XM` have **6,987 finite positive dated values**, from 2000-01-03 to 2026-10-13.
- Each provider response had `missing_source_rows=2796`, recorded but not numerically imputed. Together with valid values, that represents 9,783 returned source date rows per country. Interpretation as calendar nontrading dates remains plausible but not independently confirmed date by date.
- `audit_downloads.py`: **8 manifests, catalog 45 codes, 39 OK / 0 FAILED / 6 NEVER_REQUESTED**. The original failed BIS 0/5 run is preserved as historical manifest and original dated research-log evidence.
- `audit_source_quality.py`: **39/39 PASS, 0 failures, 1 warning**. WTI `CL=F` 2020-04-20 negative futures settlement remains the sole warning. BIS itself had no reported source-file warning.
- Evidence recorded in `data/audits/2026-10-18-bis-five-series-live-success.md`. Assistant did not download or inspect proprietary vendor raw market CSVs.

## New implementation

1. `src/latent_risk/data/bis_market_features.py`: strict BIS daily positive nominal index validator, depreciation feature `-Δlog(NEER)` (positive means weakening currency), and 21-return trailing sample volatility on source observation steps. Exact original BIS observation dates are preserved, no forward-filling of weekends/holidays or equity sessions without published BIS observation.
2. `build_bis_market_panel`: retains the five equity-return/volatility/drawdown series from existing code, merges five country-specific NEER features on exact calendar dates (including USD), produces a five-equity-only common date panel and a **distinct five-equity-plus-five-BIS complete-case date panel**. Source histories enter only up to each feature's observation date.
3. `scripts/build_bis_market_pilot.py`: verify each of 15 immutable source snapshot hashes and schema (5 Yahoo indices, 5 BIS NEER, 3 ECB CISS, 2 FRED benchmarks), emit 4 CSV products and a timestamped manifest with SHA256 provenance, per-country BIS coverage, exact transform/window definitions. Default destination `data/processed/market_pilot_bis/` differs from the historical bilateral-FX `data/processed/market_pilot/` directory. Refuses overwrite of existing output.
4. `tests/test_bis_market_features.py`: tests inverse appreciation/depreciation sign, future append invariance, exact holiday missingness, meaningful USA FX feature, invalid level/source rejection, immutable source SHA256 tamper detection, output provenance and separate reference indices.
5. ADR-0009 specifies versioned alternative and strict limitations; documentation and journal updated.

## Mathematical and epistemic boundaries

- (E_{c,t}) is the BIS trade-weighted nominal currency index, with (E>0); depreciation is (r_{c,t}=-[\log E_{c,t}-\log E_{c,t-1}]). Different partner weights mean that common *methodology* is not identical risk exposure across countries.
- Returns and volatility use actual **successive reported source observations**, which can be separated by nonreporting days; 21 means 21 observations, *not* 21 calendar days.
- Same-date joins are descriptive only: BIS has a later publication/revision cycle and international equity exchanges close in different time zones. This **does not** establish valid historical `available_date` for a pseudo-real-time forecasting origin.
- Index construction, Gaussian second-difference penalized smoothing and financial-stress forecasting are still distinct, and no model is fitted here. CISS/STLFSI4/NFCI are held in a separate file and never inputs to this feature panel.
- Legacy bilateral USD FX histories, DXY and earlier prepared files remain unchanged for a planned robustness comparison.

## Testing and execution status

**CODE IMPLEMENTED, synthetic CI VERIFIED**: after committing code `d4ce0e9c5f881570fd1fd487f96d192aebd08b5a`, 95 pytest tests passed, Ruff passed, structural check passed, Sphinx build succeeded: https://github.com/heri-espino/Latent-Risk/actions/runs/39138567174.

**NOT YET RUN ON USER VM**: the versioned BIS feature builder has not produced empirical derived market counts. Only the raw BIS download and raw source QA have run in user's VM. The new builder must be run before claiming actual country-specific NEER alignment coverage.

## Alternatives and next steps

Discard the earlier market panel outright: rejected. Replace original USD-based columns in-place: rejected because it would invalidate reproducibility. Impute missing NEER days as zero or via future interpolation: rejected. Next run `git pull --ff-only origin main` and `python scripts/build_bis_market_pilot.py`, examine per-country BIS feature coverage and newly complete common dates; then compare alternative risk input definitions and assess release-date-vintage limitations before fitting main latent factor/smoother. No crisis early-warning claim is made.

## Files

`src/latent_risk/data/bis_market_features.py`; `scripts/build_bis_market_pilot.py`; `tests/test_bis_market_features.py`; `data/audits/2026-10-18-bis-five-series-live-success.md`; this entry; `journal/decisions/ADR-0009.md`; `journal/LATEST.md`; `AI_HANDOFF.md`; `context/STATE.md`; `context/NEXT_STEPS.md`; `context/DECISION_INDEX.md`; `data/README.md`; `experiments/EXP-0001.md`.
