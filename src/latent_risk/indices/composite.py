"""Transparent signed financial-stress composite benchmark."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

from ._scaling import TrainingStandardizer, fit_standardizer


@dataclass(frozen=True)
class SignedCompositeModel:
    """Economically signed, standardized component-average index.

    Parameters
    ----------
    standardizer : TrainingStandardizer
        Scaling fitted solely on historical training data.
    directions : numpy.ndarray
        Signed component weights, shape (n_indicators,). Positive components
        have a declared higher-stress orientation.

    Notes
    -----
    The absolute weights sum to one. The resulting index is a
    *constructed measurement*, not a directly observed risk target.
    """

    standardizer: TrainingStandardizer
    directions: NDArray[np.float64]

    def transform(self, values: ArrayLike) -> NDArray[np.float64]:
        """Score an indicator panel using fixed training weights.

        Parameters
        ----------
        values : array_like
            Matrix shape (n_times, n_indicators).

        Returns
        -------
        numpy.ndarray
            Composite score, shape (n_times,).
        """
        return self.standardizer.transform(values) @ self.directions


def fit_signed_composite(
    train: ArrayLike, directions: ArrayLike
) -> SignedCompositeModel:
    """Fit a signed, standardized equal-weight-style stress composite.

    Parameters
    ----------
    train : array_like
        Training-only indicator matrix, shape (n_times, n_indicators).
    directions : array_like
        Explicit signs/weights chosen from economic reasoning; shape
        (n_indicators,). Each value must be finite and nonzero. For
        equal weights pass only +1 and -1.

    Returns
    -------
    SignedCompositeModel
        Scorer with training-fitted scaling, orientation and normalized weights.

    Raises
    ------
    ValueError
        On mismatched shape, zero/nonfinite weight, or constant indicator.

    Notes
    -----
    Input series must already be transformed into economically sensible
    indicators. Gold and oil returns need not have a universal stress sign.
    See notes/definitions.md and experiments/EXP-0001.md.
    """
    scaler = fit_standardizer(train)
    weights = np.asarray(directions, dtype=float)
    if (weights.ndim != 1 or len(weights) != len(scaler.mean)
            or not np.isfinite(weights).all() or np.any(weights == 0)):
        raise ValueError("directions must contain one finite nonzero weight per feature")
    weights = weights / np.abs(weights).sum()
    weights.setflags(write=False)
    return SignedCompositeModel(standardizer=scaler, directions=weights)
