"""Training-only centering and scaling for country indicators."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray


def validated_matrix(values: ArrayLike) -> NDArray[np.float64]:
    """Convert a finite numeric matrix to a validated 2-D array.

    Parameters
    ----------
    values : array_like
        Observations by features, shape (n_times, n_indicators).

    Returns
    -------
    numpy.ndarray
        Read-only-independent floating-point copy.

    Raises
    ------
    ValueError
        If the input is not two-dimensional, empty, or nonfinite.
    """
    matrix = np.asarray(values, dtype=float)
    if matrix.ndim != 2 or min(matrix.shape) == 0:
        raise ValueError("values must be a non-empty two-dimensional matrix")
    if not np.isfinite(matrix).all():
        raise ValueError("values contain NaN or infinite observations")
    return matrix.copy()


@dataclass(frozen=True)
class TrainingStandardizer:
    """Frozen training-sample centering and scaling.

    Parameters
    ----------
    mean : numpy.ndarray
        Training means, shape (n_indicators,).
    std : numpy.ndarray
        Training population standard deviations (ddof=0).
    """

    mean: NDArray[np.float64]
    std: NDArray[np.float64]

    def transform(self, values: ArrayLike) -> NDArray[np.float64]:
        """Standardize samples using training statistics only.

        Parameters
        ----------
        values : array_like
            Observations by features, with identical column ordering.

        Returns
        -------
        numpy.ndarray
            Standardized data; shape equals input matrix.

        Raises
        ------
        ValueError
            On incompatible dimensions or nonfinite input.
        """
        matrix = validated_matrix(values)
        if matrix.shape[1] != len(self.mean):
            raise ValueError("feature count does not match fitted training data")
        return (matrix - self.mean) / self.std


def fit_standardizer(train: ArrayLike) -> TrainingStandardizer:
    """Fit a standardizer using training data exclusively.

    Parameters
    ----------
    train : array_like
        Finite training matrix, shape (n_train >= 2, n_indicators).

    Returns
    -------
    TrainingStandardizer
        Frozen mean and scale; no future data are used.

    Raises
    ------
    ValueError
        If there are fewer than two observations or a zero-variance column.
    """
    X = validated_matrix(train)
    if X.shape[0] < 2:
        raise ValueError("at least two training dates are required")
    std = X.std(axis=0, ddof=0)
    if np.any(std <= 0):
        raise ValueError("constant indicator: drop or predeclare an imputation rule")
    return TrainingStandardizer(mean=X.mean(axis=0), std=std)
