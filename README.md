# Latent Risk

**Status:** research infrastructure established; no international empirical study has yet been run.

Latent Risk is a research project on financial-stress indices and the reliability of smoothed-trend forecasts across countries and crisis episodes. Initial candidate markets include Mexico, the United States, the United Kingdom, Japan, and a euro-area aggregate. The central question is whether unusually large forecast failures reveal information about financial disturbances beyond ordinary forecast uncertainty.

We distinguish three stages:

1. **Measurement:** construct comparable financial-risk indices from market and macrofinancial indicators (transparent composite, PCA, DFM, and conditional robust alternatives).
2. **Trend forecasting:** fit a statistically specified trend model, primarily a constrained Gaussian local-linear trend with smoothing chosen by marginal likelihood (planned, not implemented).
3. **Evaluation:** compare forecast failures across country, event, index method, and forecast horizon, with pseudo-real-time checks and retrospective analysis clearly separated.

## Development stage

The installable `src/latent_risk/` package will initially provide small, tested index-construction and data-vintage utilities. Neither MLE smoothing nor the international experiment is claimed implemented. Research decisions, implementation status and negative findings are documented in the journal.

## Quick start

```bash
python -m pip install -e ".[dev]"
python -m pytest
python scripts/validate_research.py
```

Minimal API:

```python
import numpy as np
from latent_risk.indices import fit_pca, fit_signed_composite

X_train = np.array([[1., 0.], [2., 1.], [0., -1.], [4., 2.]])
pca = fit_pca(X_train, stress_anchor=0)
scores = pca.transform(X_train)
composite = fit_signed_composite(X_train, directions=[1, -1])
```

## Research and AI collaboration

**Start every session by reading `AGENTS.md` and the journal sequence it specifies.** Use `AI_HANDOFF.md` for status after reading the dated history. Mathematical results belong in `notes/`, source materials in `literature/{pdf,markdown,references}/`, research protocols in `experiments/`, manuscript in `paper/`, and generated outputs under `results/`.

The source of the earlier U.S.-specific pilot is [Estimation of Latent Risk in the U.S. Market Using Representative Variables](https://github.com/heri-espino/Estimation-of-latent-risk-in-the-U.S.-market-using-representative-variables). Its 2008 results are **not** transferred as validated results here: its DFM parameters and standardization used later data, its smoothness selection contained an inconsistency, and diagnostic tests were rejected. See `context/STATE.md`.

See `docs/getting-started.md`, `docs/research-workflow.md`, and `experiments/README.md` for details.

## Attribution and reuse

Earlier project material had additional credited collaborators. Reuse and manuscript authorship require confirmation. No final manuscript authorship is asserted here. Original source code in this repository is not automatically licensed for third-party redistribution; choose a license with collaborators before a public software release.
