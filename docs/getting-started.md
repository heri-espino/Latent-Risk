# Installation and quick start

Install Python 3.10 or newer. From the repository root:

```bash
python -m pip install -e ".[dev,docs]"
python -m pytest
python scripts/validate_research.py
sphinx-build -b html docs docs/_build/html
```

The initial concrete API constructs model-specific indices **from already transformed, aligned financial measurements**. Training-only preprocessing is required for honest historical forecasts.

```python
import numpy as np
from latent_risk.indices import fit_signed_composite, fit_pca

train = np.array([[0.1, 0.0], [0.2, 0.3], [0.5, -0.2]])
future = np.array([[0.8, -0.1]])
signed = fit_signed_composite(train, directions=[+1, -1])
pca = fit_pca(train, stress_anchor=0)
print(signed.transform(future), pca.transform(future))
```

**These example numbers are invented toy inputs**, not financial observations. The library does not download country panels, estimate DFM likelihoods, smooth latent trends, or detect crises yet.
