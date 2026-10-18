# 2026-10-18 — Country-level index candidates and diagnostics (agent/index-models)

**Date:** 2026-10-18 (America/Mexico_City)  
**Owner:** index-models subsystem agent; branch agent/index-models; draft PR https://github.com/heri-espino/Latent-Risk/pull/1  
**Objective:** add source-free, cutoff-bounded country-index model selection and inspection without altering existing downloaders, external benchmark targets, or core forecasting EXP-0002.

## Motivation and questions

The repository previously supported signed composite and PCA fitted to finite NumPy training matrices, without an explicit dated cutoff contract or time-dynamic factor option. The separate index construction stage needs explicit training and information cutoffs, missingness accounting, factor anchoring, and diagnostics before later forecast evaluation. Questions: Can future data perturbations change previously frozen factor values? What additional assumptions are required for a Gaussian state-space factor? Is a transparent composite preferable when PCA loadings are weak?

## Files implemented in this PR

- src/latent_risk/indices/country.py — typed result, strict dated DataFrame validation, train-only standardization, signed composite, static PCA and a cautious *two-stage*, frozen-loading Gaussian AR(1) state-space with filtered-only estimates and conditional standard deviations; incomplete input panels named accurately.
- src/latent_risk/indices/__init__.py — additive export, existing APIs preserved.
- tests/test_indices_country.py — deterministic stress/no-stress synthetic examples, missing-data and benchmark exclusions, insufficient identification, cutoff perturbation and frozen-training tests.
- notes/results/index_models.md — PCA-versus-state-space tradeoffs, assumptions, diagnostic interpretation, source-free runnable smoke example, limitations.
- This dated research-log entry, plus branch-only shared handoff/state/latest updates for integrator reconciliation.

## Why these methods

Economic stress signs are explicit for every feature. For composite, missing features drop from the date-specific mean; for PCA, absent features are filled with their **training-only** column mean. For the state-space filter, unavailable inputs are **omitted** from that date's measurement update and the Kalman recursion is strictly forward. The parameters and anchors are fitted from training dates only; the origin bounds scoring. PCA computes descriptive score weights; state-space computes estimated measurement loadings and conditional filtered state variances but NOT loading parameter uncertainties.

The optional Gaussian model is calibrated via PCA and residual-moment estimates (two-stage). It is **NOT** a jointly estimated maximum-likelihood DFM; there is no iterative parameter optimizer, thus reporting a finite filter is not a likelihood optimizer convergence check. Its identification gates (sample/feature count, singular-value ratio, anchor loading, coverage) are **heuristics**, not theoretical identification proofs. A full-sample smoothed factor would use future rows and is explicitly not returned. Model-family outputs are not automatically comparable forecast targets.

## Experiments, results and unexpected behavior

- Deterministic simulations use NumPy Generator seed 4107. Synthetic disturbance shifts latent values for dates indexed 65:85; clean control omits this shift. These examples exercise code only and are **not empirical event prediction evidence**.
- First observed GitHub CI run on commit b5c3e55, https://github.com/heri-espino/Latent-Risk/actions/runs/39138392594 : **106 passed, 1 failed**. Only failure: exact bitwise equality across PCA score prefixes, in which shape-dependent floating-point operations differed by at most 2.77555756e-17. It did not indicate leaked future data or a parameter change.
- Fix on commit 326f2d1: use numerical absolute tolerance 1e-14 for this prefix comparison. Subsequent CI status is to be checked independently (do not infer passage before its logs complete).

## Later CI evidence (same day)

- On commit f3c2016, GitHub Actions run 39138756329 **passed 107 tests, Ruff, structural validation and Sphinx**. The change-protocol check alone failed because shared handoff files had not yet been updated. Those files were subsequently changed on this branch.
- On commit 4d962a0, GitHub Actions run 39138821630 **passed unit tests and Ruff** but failed structural validation because journal/LATEST.md linked to two dated journal entries. The validator requires exactly one. Commit c9a2d95 corrected the pointer. End-to-end green CI on that later commit is **NOT YET VERIFIED**.
- No failed test was deleted, no real data were downloaded, and no evidence of financial-crisis prediction is claimed.

## Validation commands

CI steps: python -m pytest -q ; ruff check . ; python scripts/validate_research.py ; sphinx-build -b html docs docs/_build/html ; python scripts/check_change_protocol.py --base-ref origin/main (on PR). Local container cannot access github.com directly; tests are therefore verified through GitHub Actions, not falsely described as locally executed. Exact latest CI outcomes are in the PR Actions checks.

## Failures, tradeoffs and limits

The transparent signed composite is easily audited but can change its weights as features become missing. PCA may capture scale-of-variation rather than stress; its first direction may be unstable across sample halves/refits. State-space can attenuate noise, but independent Gaussian observation errors, AR(1) state persistence and frozen PCA loadings may fail in regime shifts. All first-release vintage contracts and timezone-close conventions are **UNKNOWN**. No CISS/STLFSI4/NFCI are used as predictors; BIS has no verified contractual integration. Equity/FX alone does not justify a five-domain systemic financial stress name.

## Alternatives considered

- Joint likelihood DFM: deferred until identification/diagnostic requirements and availability-safe data are met; do not assume it dominates PCA.
- Full-sample backward smoothing: excluded from pseudo-real-time estimation because it revises past information using future observations.
- Full-sample imputation/normalization: rejected as time leakage.
- Cross-model factor RMSE ranking: rejected because distinct latent targets have no common observable ground truth.

## Conclusions and next steps

**IMPLEMENTED:** typed cutoff-bounded three-model candidate family and diagnostics. **VERIFIED COMPUTATIONALLY:** only tests explicitly shown as passing in CI logs, never real market performance. **PROPOSED:** external common-outcome chronological model comparison, factor reference calibration across refits, stronger factor identification tests and parameter uncertainty. **UNKNOWN:** historical source release vintages, financial stress predictiveness, whether DFM improves outcomes.

Coordinator should review and reconcile shared handoff changes, agree on dated feature-panel contract, and keep PR draft until all checks pass and scientific assumptions receive review. No merge or force-push requested.
