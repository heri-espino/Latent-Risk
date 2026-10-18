# Country-level index candidates and diagnostics

**2026-10-18 — IMPLEMENTED, computational validation must be independently checked.** This is a methodological memo, not evidence of crisis prediction. There are no real-data performance claims.

## Question and notation

For one country, let X[t,j] denote feature j observed at date t, already validated by the caller for actual source publication/release availability. Let train_end be an inclusive training cutoff, and origin the inclusive information cutoff, with train_end <= origin. This module constructs a *feature-specific market factor*, not a five-domain systemic stress index or an observed financial-risk target. CISS, STLFSI4, and NFCI must remain independent external concordance references; BIS integration is deferred pending a validated data-agent contract.

With predetermined high-stress direction s[j] in {-1,+1}, define z[t,j] = s[j] * (X[t,j] - mean_train[j]) / std_train[j]. Train-only observed data determine column moments. The default maximum fraction of missing training rows per feature is 40%; constant and mostly missing features are rejected. No full-sample scaling or imputation is permitted.

## Three models

**Signed equal-weight composite.** At time t let O[t] contain observed indicators. The factor is the arithmetic mean of z[t,j] over j in O[t]. When there are no observed inputs the value is NaN. Available-case renormalization changes the effective weights as indicators drop out: explicitly reported, not suppressed. Returned signed weights are design choices, not statistical loading estimates.

**PCA baseline.** Train-only column-mean imputation replaces missing *training-standardized* observations with zero. Fit the first principal direction by SVD and orient it so the predeclared signed anchor loading is positive. Divide scores by their training-only population standard deviation for a scale convention. Report first-component explained variance fraction, first/second singular-value ratio, and split-half loading-vector cosine. Fully unobserved dates yield NaN. PCA optimizes variance, not financial-stress relevance.

**Gaussian AR(1) state-space candidate (two-stage, NOT joint DFM MLE).** Fix the PCA loading direction using training data. Estimate phi by least squares on training PCA scores and q plus diagonal measurement variances r[j] from training residual moments with documented variance floors. The Gaussian equations are

\[
f_t=\phi f_{t-1}+\eta_t,\qquad \eta_t\sim N(0,q),
\]
\[
z_{tj}=\Lambda_j f_t+e_{tj},\qquad e_{tj}\sim N(0,r_j).
\]

Run a **forward-only** Kalman filter with scalar measurement updates, skipping absent features without imputing them to zero. Return E[f_t | observations through t, frozen estimated parameters] and its conditional state standard deviation. This excludes parameter estimation and model uncertainty. The algorithm uses no optimizer: a finite Kalman recursion is NOT proof of ML convergence. Requirements of 40 training rows, at least three indicators, at least two observed per row on 90% of training dates, 1st/2nd singular-value ratio >=1.15, and substantial anchor loading are heuristic admissibility checks, not identification theorems. Smoothed backward estimates are deliberately not returned: they use observations dated after t.

## Diagnostics and caveats

| Aspect | Composite | PCA | Two-stage state space |
| --- | --- | --- | --- |
| Complexity | Predetermined signs | Static SVD | Frozen-loadings AR(1) filter |
| Missingness | Observed-case average | Training-mean zero imputation | Missing measurement omitted |
| Loadings | Design weights | Static projection weights | Measurement loadings |
| Reported uncertainty | None | None | Conditional filtered state SE |
| Residual diagnostics | Lag-one and pairwise correlation | Same plus loading stability | Same plus finite filtering |
| Principal limitation | Changing observed components | Factor rotation across refits | Gaussian/diagonal-error and AR(1) misspecification |

All models report descriptive lag-one residual serial correlation, pairwise residual correlation, observed counts, training missingness, and warnings. Correlation numbers are not calibrated significance tests. A weak eigengap or unstable split loading is a warning for PCA and reason to reject the optional state-space candidate. Sign-and-training-scale anchoring does NOT make latent factors from independently refitted origins identical: complete cross-refit anchor calibration and a common downstream forecast target remain research questions.

### Thesis, antithesis and synthesis

**Thesis:** a persistent latent state can reduce observation noise. **Antithesis:** stress disturbances are regime-changing, markets close asynchronously, factors may be weak, and idiosyncratic shocks may be correlated. **Synthesis:** retain transparent composite and PCA as compulsory baselines, treating the two-stage state space only as a candidate; evaluate predictive relevance against the same independent outcome at the same origin with fully audited data.

## Reproducible, data-free smoke test

Install with: python -m pip install -e '.[models,dev]'

~~~python
import numpy as np
import pandas as pd
from latent_risk.indices import fit_country_index

rng = np.random.default_rng(20261018)
dates = pd.date_range("2010-01-01", periods=120)
latent = rng.normal(0, 0.15, len(dates))
latent[55:70] += 2.0  # artificial shock, not an actual financial event
frame = pd.DataFrame({
    "vol": latent + rng.normal(0, 0.12, len(dates)),
    "drawdown": -latent + rng.normal(0, 0.12, len(dates)),
    "fx_depreciation": 0.8 * latent + rng.normal(0, 0.12, len(dates)),
}, index=dates)
signs = {"vol": 1, "drawdown": -1, "fx_depreciation": 1}
for method in ("composite", "pca", "state_space"):
    result = fit_country_index(
        frame, dates[95], origin=dates[100], model=method,
        directions=signs, stress_anchor="vol",
    )
    print(method, result.factor.iloc[-1], result.warnings)
    assert result.factor.index.max() == dates[100]
~~~

Relevant checks: python -m pytest tests/test_indices.py tests/test_indices_country.py -q ; python -m pytest ; ruff check . ; python scripts/validate_research.py ; sphinx-build -b html docs docs/_build/html

## Open issues

1. Publication-date and historical first-release vintages are **UNKNOWN**; current-vintage histories cannot establish pseudo-real-time validity.
2. Need complete cross-refit factor alignment, uncertainty in fitted loadings/AR parameters, robustness to correlated idiosyncratic residuals, and a common external downstream outcome.
3. Equities plus FX proxies are **NOT** enough to call a constructed market factor five-domain systemic financial stress; additional credit, banking and funding domains await source contracts.
4. No real downloaded data, episode outcomes, model comparisons or early-warning performance have been computed by this contribution.
