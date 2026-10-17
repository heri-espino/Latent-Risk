"""Show two train-only index baselines on deliberately synthetic values."""
import numpy as np

from latent_risk.indices import fit_pca, fit_signed_composite

training = np.array([[0.1, 0.0], [0.2, 0.1], [0.4, -0.1], [0.3, 0.2]])
future = np.array([[0.5, -0.2]])
pca = fit_pca(training, stress_anchor=0)
composite = fit_signed_composite(training, directions=[1, -1])
print("Synthetic PCA score:", pca.transform(future))
print("Synthetic signed composite score:", composite.transform(future))
print("These outputs are not financial-market findings.")
