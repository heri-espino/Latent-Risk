# 2026-10-18 — Agent forecast-evaluation: source-free chronology and uncertainty

**Date:** 2026-10-18 (America/Mexico_City)  
**Objective:** implement a dedicated reproducible chronology/forecast comparison harness, without claiming that any source-data or latent-index model has been evaluated.

## Motivation and questions
Existing EXP-0002 provides a tested source-specific retrospective CISS benchmark. Its baseline models and current-vintage caveat should remain untouched. Needed: a reusable as-of origin protocol, fresh estimator construction in truly nested inner chronological folds, matched target/date scoring, basic uncertainty estimates and adversarial leakage controls. Can we enforce numeric prefix integrity without falsely claiming real-time release vintages? Yes, by passing only sliced source-free training arrays and explicitly labeling vintage policy, subject to independent review of estimator closures.

## Work performed and reasoning
- Implemented `evaluation/backtesting.py`: typed `Forecaster` protocol, `ForecastFamily`/`Candidate` factory structure, `BacktestConfig`, expanding/rolling origins, horizons measured in observed target points, end-of-day as-of filtering and fail-closed nested inner target selection.
- Implemented `evaluation/baselines.py`: persistence, recursively forecast OLS AR(1), one-sided EWMA with CV-selected gain and a simple upward volatility-adjusted persistence heuristic. The heuristic is not GARCH or a proved conditional-mean model.
- Implemented `evaluation/scoring.py`: strict within-target-scale and vintage matching; per-country/target/horizon MSE/RMSE/MAE; circular block-origin bootstrap percentile intervals; paired squared-loss DM-style Bartlett HAC uncertainty with explicitly stated asymptotic assumptions.
- Added standalone `tests/test_backtesting.py` deterministic synthetic fixture and adversarial modifications of observations after an origin, delayed releases, rolling window, incompatible/missing forecast pairs, and HAC outputs.
- Registered proposed `EXP-0003.md` and separate `configs/EXP-0003.json`. No empirical outputs exist.
- Existing `src/latent_risk/data/ciss_baselines.py`, `scripts/run_ciss_baselines.py`, `EXP-0002`, factor and trend classes deliberately unchanged.

## Exact files changed
`src/latent_risk/evaluation/backtesting.py`, `baselines.py`, `scoring.py`, `__init__.py`; `tests/test_backtesting.py`; `experiments/EXP-0003.md`, `experiments/configs/EXP-0003.json`; this journal entry; `journal/LATEST.md`; `AI_HANDOFF.md`; `context/STATE.md`; `context/NEXT_STEPS.md`.

## Tests, experiments, failures and uncertainty
**IMPLEMENTED, PENDING CI** at initial code authoring. Proposed commands: `python -m pytest tests/test_backtesting.py`, `python -m pytest`, `ruff check .`, `python scripts/validate_research.py`, `python scripts/check_change_protocol.py --base-ref origin/main`, `sphinx-build -b html docs docs/_build/html`. Update this entry with actual CI evidence only once obtained.

**PROPOSED but NOT EXECUTED:** a real-data EXP-0003 run on actually downloaded three-country CISS historical series. Existing CISS dates and values do not constitute historical first-release archives. Current-vintage status is explicit, and the five-country substantive latent-index/financial-disturbance question remains UNKNOWN.

## Alternatives, failures, limits
- Do **not** reuse preprocessed full-sample scaling, factors or trend parameters inside outer folds: reject as leakage.
- Do **not** mix different latent scales or compare model rows on different targets.
- Do **not** conflate h observed-point horizons with calendar days or months.
- A factory could access outside global arrays despite this narrow protocol: pure-interface invariance must be reviewed for each adapter. Availability dates are only as trustworthy as source provenance.
- HAC lag assumptions and stationary circular-block bootstrap do not handle all structural breaks or repeated model comparisons; no inference is automatically valid.

## Supported conclusions and next steps
**IMPLEMENTED** engineering framework and adversarial test definitions; **UNKNOWN** real empirical validity and benchmark ranking. Run/inspect CI; resolve any failures with a separate recorded commit. Coordinator should review the public forecaster API before another agent introduces cross-country factors or multi-feature adapters, and reconcile shared handoff files when integrating this draft PR. Never merge automatically.
