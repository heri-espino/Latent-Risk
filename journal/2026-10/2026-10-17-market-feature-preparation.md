# 2026-10-17 — All raw files pass and first market-feature builder added

**Date:** 2026-10-17 (America/Mexico_City)  
**Objective:** close the 34-file integrity gate, confirm negative WTI settlement against official historical evidence, and create a traceable preliminary market feature dataset without fitting a financial-stress index.

## Motivation
The user reran the updated source quality tool. All 34 downloaded sources passed integrity checks, with a single expected signed-WTI warning. The next risk is inadvertently treating current reconstructed market histories, CISS or retrospective factors as genuine real-time forecasts.

## Research questions
What do 34/34 passes certify (and not certify)? Can we construct comparable strictly trailing *market-based* observables in all five regions without forward-filling missing trading dates? How should the public CISS and FRED benchmarks be represented without contaminating latent-index inputs?

## Actual user-provided results
- `Quality audit: 34/34 passed, 0 failed, 1 with warnings`.
- Only negative `CL=F` close: date `2020-04-20`; minimum `-37.630001068115234` ≈ −37.63 USD/b. Corrected historical futures event confirmed.
- All 12 FRED, 5 ECB, 3 Banxico and 14 Yahoo market series passed. The additional 6 catalog entries remain never requested.
- No raw files or real model data were downloaded into the assistant's runtime. The shell report is user evidence, and raw hashes were validated by the script on their VM, not rechecked independently by assistant.

## Implementation
- New `src/latent_risk/data/market_features.py`: explicit mapping of 5 local/regional equity indices and 4 FX sources; logarithmic equity price changes, 21-source-observation trailing return volatility and 63-observation drawdown; FX depreciation-direction consistent across quote conventions, 21-observation trailing FX volatility. All use current/past values only.
- Country-specific outputs join FX to local equity on exact dates without forward filling. Cross-country equity panel is exact 5-way date intersection. US FX features deliberately left missing, not synthetically zero.
- New `scripts/build_market_pilot.py` loads each selected source's **latest successful** immutable snapshot, validates source hash/schema before use, saves `country_market_features.csv`, `five_country_common_equity_dates.csv`, and **separate** `external_stress_references.csv` (ECB CISS EA/US/UK; FRED STLFSI4/NFCI), plus a local SHA256/provenance manifest. Rejects overwriting previous output directories. Excludes WTI and all macro data at this stage.
- Synthetic unit tests in `tests/test_market_features.py` verify past-only behavior under future appends, FX quotation signs, strict calendar intersection, missing data rejection and no oil/CISS contamination.
- Added proposal `ADR-0007` defining initial market-data representation, explicit limitations and controls.
- Documentation/handoff/experiment updated after implementation.

## Scientific reasoning and alternative paths
Market close from different time zones does not become simultaneously observable simply because the calendars show the same date. This first derived dataset is **retrospective end-of-day descriptive**, not historical available-date proof or a matched forecast-origin panel. In particular, `equity_vol_21` and `equity_drawdown_63` are defined on trading observations and require full warmup. Different-country equities are not a systemic credit/funding risk index. Relative exchange-rate depreciation has coherent direction only with explicit quote orientation. CISS/STLFSI4/NFCI are kept external because overlap with factor inputs invalidates fully independent agreement tests.

We rejected forward filling across holidays, inventing US USD/USD FX and using full-sample normalization/latent models. WTI is deliberately excluded rather than transformed automatically through negative prices. Daily close vs next-day forecast-origin conventions and optional macro release dates remain to be designed before model fits.

## Execution status and validation
**Implemented** a data-preparation module, CLI and unit tests; GitHub CI runs pytest, Ruff, structure and Sphinx. No computation was performed on user's actual saved source data and no forecast/model result exists. Record final CI outcomes in response.

## Unexpected results
The WTI nonpositive close date/amount exactly matches the historically recorded May 2020 delivery-month futures event; this supports the source's historical plausibility, not its entire adjusted continuous-history construction.

## Failures and limitations
Source-level structural audit cannot guarantee historical vintages, exact close availability, provider corporate adjustments or aligned holidays. New country panel output includes unscaled equity features, partly missing FX and an equity-only matched calendar. This is not a completed internationally comparable stress index.

## Files changed
`data/audits/2026-10-17-integrity-complete.md`, `src/latent_risk/data/market_features.py`, `scripts/build_market_pilot.py`, `tests/test_market_features.py`, `journal/2026-10/2026-10-17-market-feature-preparation.md`, `journal/LATEST.md`, `journal/decisions/ADR-0007.md`, `context/DECISION_INDEX.md`, `AI_HANDOFF.md`, `context/STATE.md`, `context/NEXT_STEPS.md`, `data/README.md`, `experiments/EXP-0001.md`.

## Supported conclusions
We have an integrity-validated **source collection**, plus a separate **offline-verified** market-feature building implementation; source availability and historical forecast validity remain distinct. The first derived dataset must be generated and analyzed on the user's VM before reporting any series-level empirical feature results.

## Next steps
Run `git pull --ff-only origin main`; `python scripts/build_market_pilot.py`; report row counts/dates and inspect quality/missingness (no raw data need enter Git). Decide observable target and strict cross-timezone/publication-time forecast-origin rule before constructing rolling-origin model comparisons.
