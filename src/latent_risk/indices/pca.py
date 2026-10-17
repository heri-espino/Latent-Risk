"""First principal component benchmark with frozen high-stress orientation."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

from ._scaling import TrainingStandardizer, fit_standardizer


@dataclass(frozen=True)
class PCAIndexModel:
    """First-component training PCA score with predetermined stress direction.

    Parameters
    ----------
    standardizer : TrainingStandardizer
        Fitted training-only indicator centering and scale.
    component : numpy.ndarray
        Unit-norm first right singular vector, shape (n_features,).
    explained_variance_ratio : float
        Fraction of total standardized training-panel variance explained.

    Notes
    -----
    The component sign is oriented toward a declared stress-anchor indicator
    on training data. Future scores use the same component and centering.
    """

    standardizer: TrainingStandardizer
    component: NDArray[np.float64]
    explained_variance_ratio: float

    def transform(self, values: ArrayLike) -> NDArray[np.float64]:
        """Apply frozen PCA to future or retrospective indicator rows.

        Parameters
        ----------
        values : array_like
            Indicator panel, shape (n_dates, n_features).

        Returns
        -------
        numpy.ndarray
            First component scores, shape (n_dates,).
        """
        return self.standardizer.transform(values) @ self.component


def fit_pca(train: ArrayLike, stress_anchor: int = 0) -> PCAIndexModel:
    """Fit first-component PCA with a training-only sign convention.

    Parameters
    ----------
    train : array_like
        Training indicator panel, shape (n_train >= 2, n_features).
    stress_anchor : int, optional
        Zero-based column that has been signed so higher values represent
        stress (for example local equity volatility). The PCA loading for
        this column is forced positive, and must not be negligible.

    Returns
    -------
    PCAIndexModel
        Frozen standardization and component.

    Raises
    ------
    ValueError
        For invalid or constant input, invalid anchor, or ambiguous orientation.

    Notes
    -----
    PCA maximizes training variance, not the association with true financial
    stress. This model constructs a different target than a DFM.
    """
    scaler = fit_standardizer(train)
    X = scaler.transform(train)
    if not isinstance(stress_anchor, (int, np.integer)) or not 0 <= stress_anchor < X.shape[1]:
        raise ValueError("stress_anchor must select an existing feature")
    _, singular_values, Vt = np.linalg.svd(X, full_matrices=False)
    component = Vt[0].copy()
    if abs(component[stress_anchor]) < 1e-8:
        raise ValueError("first PCA component has no identifiable stress-anchor loading")
    if component[stress_anchor] < 0:
        component *= -1
    component.setflags(write=False)
    share = float(singular_values[0] ** 2 / np.sum(singular_values ** 2))
    return PCAIndexModel(scaler, component, share)
