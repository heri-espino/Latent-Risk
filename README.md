# Latent Risk

**Status:** source acquisition is implemented, but **no actual international source download or empirical study has been executed in this repository**.

Latent Risk is a research project on financial-stress indices and the reliability of smoothed-trend forecasts across countries and crisis episodes. Initial candidate markets are Mexico, the United States, the United Kingdom, Japan and an explicitly defined euro-area aggregate. The central question is whether unusually large forecast failures contain information about financial disturbances beyond ordinary forecast uncertainty.

We distinguish three stages:

1. **Measurement:** construct comparable indices (signed composite, PCA, DFM and conditional robust/regime alternatives).
2. **Trend forecasting:** fit a statistically specified trend model, primarily a Gaussian state-space trend with smoothness selected by marginal likelihood (proposed, not implemented).
3. **Evaluation:** compare forecast failures across countries, market episodes, methods and horizons, separating retrospective descriptions from pseudo-real-time prediction.

## Setup and initial data download (PowerShell/Conda)

```powershell
git clone https://github.com/heri-espino/Latent-Risk.git
Set-Location Latent-Risk
conda create -n latent-risk python=3.11 -y
conda run -n latent-risk python -m pip install -e '.[data,dev,docs]'
conda run -n latent-risk python scripts/download_data.py --start 2000-01-01 --end 2026-10-17
```

Each series is saved in a separate timestamped snapshot under `data/raw/downloads` with an auditable success/failure `manifest.json`. **This source snapshot is not point-in-time historical data:** the catalog includes legacy macro series with limited coverage. Inspect the manifest before interpreting it.

See [full data acquisition documentation](data/README.md) and [source catalog](data/source_catalog.json).

## Development

```bash
python -m pip install -e ".[data,dev,docs]"
python -m pytest
ruff check .
python scripts/validate_research.py
sphinx-build -b html -W --keep-going docs docs/_build/html
```

Initial source APIs: training-only PCA, signed-composite estimators, source acquisition, published-date filtering utilities, elementary forecast-error diagnostics. No pseudo-real-time country panel or MLE smoother has been fitted.

## AI research continuity

Read `AGENTS.md` first, then `journal/README.md`, `journal/LATEST.md`, its latest dated entry, `AI_HANDOFF.md`, `context/STATE.md`, `context/NEXT_STEPS.md` and `context/DECISION_INDEX.md`. Mathematical notes belong in `notes/`; source PDFs/Docling Markdown/annotated references are separated under `literature/{pdf,markdown,references}/`; experiments and manuscripts are `experiments/` and `paper/`.

Earlier U.S. source is [Estimation of Latent Risk in the U.S. Market Using Representative Variables](https://github.com/heri-espino/Estimation-of-latent-risk-in-the-U.S.-market-using-representative-variables). Its retrospective 2008 experiment is not a validated early-warning result. Theoretical smoothing-methodology research remains in the [Trend-Estimation](https://github.com/heri-espino/Trend-Estimation) repository.

## Attribution and publication

Original U.S. pilot materials name additional collaborators. Confirm authorship and permissions before transferring original manuscript or source data. External source licenses and publication rights must be respected.
