# Latent Risk

**Status:** download infrastructure supports six providers; the user reports a VM Banxico run, but its manifest has not been audited. **No international empirical experiment has been executed.**

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

## Additional official macroeconomic sources (activated Conda environment)

```powershell
git pull --ff-only origin main
python -m pip install -e '.[data,dev,docs]'
python scripts/audit_downloads.py
python scripts/download_data.py --start 2000-01-01 --end 2026-10-17 --sources ecb,boe,boj
python scripts/audit_downloads.py
```

The ECB data are M1/M2; Bank of England data include **M4** (not M2) and SONIA; Bank of Japan adds M1/M2. Banxico now includes modern M1 `SF311408` and M2 `SF311418`, requiring a fresh `--sources banxico` download with a private SIE token. FRED access failed on the user's VM; do not treat US macro data as available until connectivity is repaired and a manifest shows success. This is source collection, not a historical real-time dataset.

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

## Raw-data quality gate after first live source collection

The user reported 34/40 catalog series downloaded across six local snapshots; the six other series are not requested, not failed. Before constructing any factor, run in an already activated Conda environment:

```powershell
git pull --ff-only origin main
python scripts/audit_source_quality.py
```

The command verifies raw CSV hashes, date integrity and numeric structure against historical download manifests. It writes `results/runs/source_quality/report.json` (Git-ignored) and never modifies source data. This does **not** prove real-time publication-date correctness, cross-country indicator comparability or stress prediction. See `data/README.md` and `experiments/EXP-0001.md`.
