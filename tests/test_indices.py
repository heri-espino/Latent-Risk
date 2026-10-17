"""Numerical smoke tests for training-fitted index benchmarks."""
import numpy as np
import pytest

from latent_risk.indices import fit_pca, fit_signed_composite


@pytest.fixture
def training():
    return np.array([[1.0, 0.0], [2.0, 2.0], [4.0, 1.0], [0.0, -2.0]])


def test_signed_composite_train_mean_zero(training):
    model = fit_signed_composite(training, [1, -1])
    score = model.transform(training)
    assert score.shape == (4,)
    assert np.isclose(score.mean(), 0.0)
    np.testing.assert_allclose(model.directions, [0.5, -0.5])


def test_signed_composite_uses_training_only(training):
    model = fit_signed_composite(training, [1, -1])
    future = np.array([[200.0, 300.0]])
    manual = ((future - training.mean(axis=0)) / training.std(axis=0)) @ np.array([0.5, -0.5])
    np.testing.assert_allclose(model.transform(future), manual)


def test_pca_sign_and_score_shape(training):
    model = fit_pca(training, stress_anchor=0)
    assert model.component[0] > 0
    assert 0 < model.explained_variance_ratio <= 1
    assert model.transform(training).shape == (4,)


def test_pca_new_value_does_not_refit(training):
    model = fit_pca(training)
    a = model.transform(np.array([[9.0, 8.0]]))
    b = model.standardizer.transform([[9.0, 8.0]]) @ model.component
    np.testing.assert_allclose(a, b)


def test_constant_column_rejected():
    with pytest.raises(ValueError, match="constant"):
        fit_pca([[1, 2], [1, 3], [1, 4]])
