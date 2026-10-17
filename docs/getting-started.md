# Installation and quick start

Install Python 3.10 or newer. From the repository root:

```bash
python -m pip install -e ".[data,dev,docs]"
python -m pytest
python scripts/validate_research.py
sphinx-build -b html docs docs/_build/html
```

## First data acquisition

The initial source-acquisition command (run after installing the `data` extra) is:

```bash
python scripts/download_data.py --start 2000-01-01 --end 2026-10-17
```

The end date is exclusive. Individual CSV files and an auditable manifest are created under gitignored `data/raw/downloads/<UTC timestamp>/`. Source failures are visible and yield a nonzero process exit code. Read the [data-acquisition documentation](https://github.com/heri-espino/Latent-Risk/blob/main/data/README.md) for optional Banxico sources and critical historical-availability limitations. This command does not yet construct the final international panel.

## Official macro data and local audit

Run these in an activated `latent-risk` environment:

```bash
python scripts/download_data.py --start 2000-01-01 --end 2026-10-17 --sources ecb,boe,boj
python scripts/audit_downloads.py
```

This downloads six official ECB/BoE/BoJ sources. The newly registered Banxico M1/M2 require `--sources banxico` and a private `BANXICO_TOKEN`; the audit shows which series actually succeeded. For FRED connection troubleshooting and caveats, see the [data-acquisition documentation](https://github.com/heri-espino/Latent-Risk/blob/main/data/README.md).

## Index-only example (synthetic)

```python
import numpy as np
from latent_risk.indices import fit_signed_composite, fit_pca

train = np.array([[0.1, 0.0], [0.2, 0.3], [0.5, -0.2]])
future = np.array([[0.8, -0.1]])
signed = fit_signed_composite(train, directions=[+1, -1])
pca = fit_pca(train, stress_anchor=0)
print(signed.transform(future), pca.transform(future))
```

These example numbers are invented toy inputs, not financial observations. The library does not yet fit DFM likelihoods, smooth latent trends or detect crises.
