# 2026-10-18 — Agent-specific second-difference trend and exact diffuse REML

**Date:** 2026-10-18 (America/Mexico_City)  
**Agent branch:** agent/trend-likelihood (not main)  
**Objective:** implement mathematically defensible classical smoothing and causal forecasting for a **fixed index** without changing earlier research claims.

## Motivation and research questions

The repository's existing DEF-0002 had stated the Gaussian penalty ratio \(r/q\) but the specific sparse, state-space and properly integrated likelihood computations had not been implemented. The questions were: how to treat the two unpenalized boundary coordinates; whether full-sample Gaussian smoothing agrees exactly with second-difference PLS; whether a **proper restricted marginal likelihood** can be optimized without confusing a joint state fit with marginal ML; and whether every forecast uses only information available at its origin.

## Sources and context inspected

Read AGENTS.md, journal/README.md, journal/LATEST.md, its linked 2026-10-17 BIS dated entry, AI_HANDOFF.md, context/STATE.md, context/NEXT_STEPS.md and context/DECISION_INDEX.md, in that order. Then inspected pyproject.toml, notes/definitions.md, src/latent_risk, repository tests, the structural validator, the change protocol and docs configuration. Consulted user-provided Guerrero (2007), Cortés-Toto et al. (2017), Weinert (2007), Biessy (2025 online/2026 print) PDFs and established Koopman (1997)/Durbin–Koopman (2012) bibliographic resources. Did not copy licensed articles.

## Implementation and reasoning

**IMPLEMENTED:** src/latent_risk/trends/gaussian.py defines a sparse second-difference operator; sparse positive-definite PLS solve; banded-Cholesky selected-inverse trace degrees of freedom; Gaussian state recursion with exactly diffuse initial \((\tau_1,\tau_2)\); exact restricted negative log likelihood of the \(n-2\) innovation contrasts including each log variance; finite interior variance optimization compared against exact \(q=0\) and \(r=0\) boundaries; retrospective RTS smoother; and separate filtered-state \(h\)-step forecasts with trend and observation variances. src/latent_risk/trends/__init__.py exposes the API.

**PROVEN as standard theory:** rank \(D_2=n-2\), affine nullspace, exactly two zero eigenvalues of \(D_2^\top D_2\); strict convexity of PLS; \(S_\lambda\) degrees-of-freedom identity; \(\lambda=r/q\) and Gaussian posterior mean/smoother equivalence with flat initial coordinates; innovations likelihood equivalence to Gaussian contrasts \(Dy\sim N(0,qI+rDD^\top)\); conditional forecast mean and variances. Detailed derivations in notes/results/trend_likelihood.md.

**Important modeling decision:** This implementation delivers **REML/exact diffuse marginal likelihood**, not ordinary full-data ML requiring a proper initial prior. It does not claim likelihood optimization targets rolling-origin forecasting error.

## Tests, evidence and failures

**VERIFIED COMPUTATIONALLY (local isolated Python environment):** python -m pytest -q tests/test_trends_gaussian.py, **9 passed**, with numpy 2.3.5, scipy 1.17.0, pytest 9.0.2. Tests include sparse/dense numerical agreement, trace against a small dense inverse, affine nullspace and limiting behavior, exact RTS/PLS equality over four variance ratios, Kalman/dense-contrast REML equality including q=0 and r=0, analytical small-sample score vs finite differences, eight synthetic stochastic-trend recovery replicates, extreme variance ratios, and identical estimates/forecasts when all future observations are perturbed.

**Preserved failure and correction:** A local intermediate edit to bind a loop variable in a likelihood-boundary callback (required to avoid Ruff B023 late binding) inadvertently also replaced a reference outside that closure and produced two NameError test failures. The edit was corrected immediately; the final local run returned **9 passed**. The branch version includes the corrected closure binding.

**NOT RUN here:** the full project-wide test suite, Ruff, project structure checker, Sphinx, and change-protocol checker could not be executed against a complete local checkout with dependencies (Ruff was unavailable in the isolated local runtime). GitHub CI should establish repository-wide status; do not claim it succeeded without checking its run.

## Exact files changed on this agent branch

New: src/latent_risk/trends/__init__.py, src/latent_risk/trends/gaussian.py, tests/test_trends_gaussian.py, notes/results/trend_likelihood.md, and this dated entry.

Updated for coordinated handoff **on the branch only**: journal/LATEST.md, AI_HANDOFF.md, context/STATE.md, context/NEXT_STEPS.md. These shared summary edits should be reconciled by the integrator; no edits to data acquisition, factor indices, earlier Trend-Estimation, paper methodological claims, EXP-0002, other agents' branches or private source files.

## Alternative models/selection methods

- Proper finite-initial-prior ML: not chosen because it introduces different endpoint assumptions and loses exact diffuse-PLS correspondence; may be added in separate scoped work.
- Minimizing fitted-state residual objective as marginal ML: **rejected** because it lacks Gaussian determinant and state integration.
- GCV and rolling-origin horizon-specific CV: distinct scientific estimands; not implemented by this agent and not portrayed as interchangeable with REML.
- General local-linear trend with independent level disturbance, structural breaks, robust tails and irregular time spacing: not part of the equivalence and deferred.
- Full-sample smoothed-state extrapolation for forecasting: **rejected** because it leaks future observations.

## Limits, uncertainty and decisions still open

No five-country index has been constructed by this branch; no real market/index results or crisis-detection claims exist. Variance components can be weakly identified, particularly for short/approximately affine samples. Log-variance optimization uses finite search limits, and extreme ratios may challenge floating-point conditioning. Boundary optima do not prove true zero-variance parameters. No confidence intervals, formal model diagnostics, or forecast calibration have been validated. The workflow assumes regular, equally spaced observations without missing entries or publication delays. Historic first-release vintages remain UNKNOWN.

## Next steps

Review the draft PR, inspect GitHub CI and resolve any lint/test issues. After coordination, evaluate on a **fixed, independently defined** index target with locked temporal availability and forecast-origin protocol; only then compare against baselines at matched origins and horizons. Do not merge this agent branch autonomously.
