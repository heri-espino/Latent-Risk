# 2026-10-17 — Real market pilot audited; first exploratory CISS forecast experiment implemented

**Date:** 2026-10-17 (America/Mexico_City)  
**Objective:** close the derived-pilot integrity and coverage gate, and implement a genuinely chronological observation-sequence forecasting test distinct from the substantive latent-risk forecasting hypothesis.

## Motivation and questions
The user ran `scripts/audit_market_pilot.py` successfully on 31,383 country/date market observations, 4,293 exact common five-equity dates, and 23,785 separate benchmark rows. Mexico/UK have approximately 14% FX gaps because their downloaded equity histories begin before the FX feeds. Can we model the three daily CISS targets using matched rolling-origin baselines without leaking observations beyond each origin? Will release-time problems remain visible rather than silently declared solved?

## User-reported empirical descriptive diagnostics
- Pilot source: `data/processed/market_pilot/20261018T003625232736Z`.
- Long market rows: **31,383**. Common five-equity trading dates: **4,293**, 2007-07-05 to 2026-10-16. External benchmarks: **23,785**.
- Equity/FX rows (complete / missing): MEX 6,664 (5,720/944); USA 6,676 (N/A); GBR 6,706 (5,743/963); JPN 6,498 (6,466/32); EA 4,839 (4,814/25).
- Same-date CISS vs country equity overlap: EA 4,838; US 6,675; UK 6,705. US weekly FRED STLFSI4/NFCI: each 1,338.
- Diagnostic exit output `RESULT DESCRIPTIVE_COVERAGE_DIAGNOSTIC_ONLY; no model fitted`. Data only on user's VM; assistant has not examined raw derived CSV bytes.
- Preserved user evidence in `data/audits/2026-10-17-market-diagnostics-complete.md`.

## Implementation
Added `EXP-0002` independently of `EXP-0001` for an exploratory current-vintage CISS observation-index forecast-methods check. Three prespecified CISS countries; outer origin starting no earlier than 2008-01-01; horizons 1,5,21 observation steps and 21-observation outer stride; 504-previous-observation minimum training.

Numerical methods: past-value persistence, OLS AR1 trained only through each origin, and causal EWMA with gain from nested earlier chronological h-step CV (predeclared gain candidates, 504-observation inner window, 252 min inner training). Do **not** mislabel EWMA as the desired marginalized Gaussian second-difference PLS smoother.

`scripts/run_ciss_baselines.py` validates the derived reference checksum, keeps CISS as forecast TARGET only (no market equity/FX/factor inputs), writes per-origin predictions, matched score summaries and hash/provenance manifest under a new ignored `results/runs/EXP-0002` folder.

Synthetic tests for causal nested scoring, future appended data invariance, target-date offset, data identity and matched score requirement. No actual VM forecasting experiment was run by assistant.

## Mathematical rationale
A chronological error measure is `e_{t,h}=y_{t+h}-\hat y_{t+h|t}`, with forecasts fit on the sequence `y_1,…,y_t`. Nested tuning must use inner forecasts and targets `≤t`; pooled CISS samples across country identities are not silently interchangeable. Choosing EWMA alpha by forecast CV operationalizes *one* aspect of forecast-optimal smoothing but is **not** the paper's PLS/REML design.

## Unexpected results / interpretation
The 4,293-date exact five-way intersection is far smaller than each single-country equity sample because national holidays and shorter EA equity history constrain it. Mexico/UK FX historical starts explain much of their missingness; none was artificially filled. ECB CISS same-date coverage is extensive, but no official publication-time release vintage was validated.

## Alternatives rejected
Full-series forward-backward smoothing, retrospective tuning on future crises, treating weekly FRED observation labels as publication timestamps, and claiming same-day multi-timezone synchronized information. We chose a bounded external-target forecast-mechanics pilot before model-based stress factor construction.

## Validation/results
**IMPLEMENTED / synthetic offline CI:** code committed, GitHub Actions tests/lint/structure/docs verified. **NOT EXECUTED on VM empirical CISS histories**. Therefore no numerical RMSE, statistical inference, standardized exceedance or early-warning signal is supported. Outcome remains `UNKNOWN` until user runs the command.

## Files changed
`src/latent_risk/data/ciss_baselines.py`, `scripts/run_ciss_baselines.py`, `tests/test_ciss_baselines.py`, `experiments/configs/EXP-0002.json`, `experiments/EXP-0002.md`, `experiments/README.md`, `data/audits/2026-10-17-market-diagnostics-complete.md`, this journal, `journal/LATEST.md`, `AI_HANDOFF.md`, `context/STATE.md`, `context/NEXT_STEPS.md`, `data/README.md`.

## Reproducible commands and next steps
`git pull --ff-only origin main`; `python scripts/run_ciss_baselines.py --start 2008-01-01 --horizons 1,5,21 --stride 21` on user activated VM. Inspect paired scores, potential weak candidate or AR1 control, code hash and origin grids. Then draft proper vintage-aware information rules and implement the main penalized-smoothness method and market-stress factor with separate bank/credit/funding measures. No inferential crisis or point-in-time validity claim.
