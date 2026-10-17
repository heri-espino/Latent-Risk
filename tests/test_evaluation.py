"""Scale checks for model-specific errors."""
import numpy as np
import pytest

from latent_risk.evaluation import forecast_errors, standardized_errors


def test_forecast_error_sign():
    np.testing.assert_allclose(forecast_errors([3, 5], [1, 8]), [2, -3])


def test_standardization():
    np.testing.assert_allclose(standardized_errors([3, 5], [1, 8], [2, 3]), [1, -1])


def test_invalid_sd_rejected():
    with pytest.raises(ValueError, match="predictive_sd"):
        standardized_errors([3], [1], [0])
