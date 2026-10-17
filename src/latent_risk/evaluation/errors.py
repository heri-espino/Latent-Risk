"""Elementary diagnostic losses for model-specific factor forecast targets."""
from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray


def forecast_errors(actual: ArrayLike, predicted: ArrayLike) -> NDArray[np.float64]:
    """Compute actual minus predicted factor values.

    Parameters
    ----------
    actual, predicted : array_like
        Finite arrays of equal shape, e.g. (n_origins,).

    Returns
    -------
    numpy.ndarray
        Signed forecast errors of the same shape.

    Raises
    ------
    ValueError
        If shapes differ or a value is nonfinite.

    Notes
    -----
    The target must specify the factor method and data vintage.
    """
    a, p = np.asarray(actual, dtype=float), np.asarray(predicted, dtype=float)
    if a.shape != p.shape or not np.isfinite(a).all() or not np.isfinite(p).all():
        raise ValueError("actual and predicted must match and be finite")
    return a - p


def standardized_errors(
    actual: ArrayLike, predicted: ArrayLike, predictive_sd: ArrayLike
) -> NDArray[np.float64]:
    """Scale forecast errors by positive pre-calibrated predictive uncertainty.

    Parameters
    ----------
    actual, predicted, predictive_sd : array_like
        Arrays of equal shape. `predictive_sd` must contain positive,
        finite values estimated without outcomes from the scored test periods.

    Returns
    -------
    numpy.ndarray
        Forecast-error z-scores, one per corresponding observation.

    Raises
    ------
    ValueError
        If any array has a different shape or uncertainty is invalid.

    Notes
    -----
    This function does not certify normal calibration or interpret errors
    as genuine structural breaks.
    """
    err = forecast_errors(actual, predicted)
    scale = np.asarray(predictive_sd, dtype=float)
    if scale.shape != err.shape or not np.isfinite(scale).all() or np.any(scale <= 0):
        raise ValueError("predictive_sd must be positive, finite and shape-matched")
    return err / scale
