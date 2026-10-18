"""Chronological country-level index candidates on validated feature panels.

This interface deliberately does not perform release-date validation: callers must
supply observations actually available by each requested information cutoff.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
from numpy.typing import NDArray

IndexKind = Literal["composite", "pca", "state_space"]
_BLOCKED_REFERENCES = ("CISS", "STLFSI4", "NFCI")


@dataclass(frozen=True)
class CountryIndexResult:
    """A cutoff-bounded measurement, NOT a verified financial-stress outcome.

    Parameters
    ----------
    model : str
        Selected model family.
    origin : pandas.Timestamp
        Requested origin for the measurement; no later rows were accessed.
    information_cutoff : pandas.Timestamp
        Information cutoff, equal to origin; input release dates are the caller's duty.
    training_cutoff : pandas.Timestamp
        Last admissible training date for the frozen model parameters.
    factor : pandas.Series
        Measurements through origin; missing entirely unobserved rows remain NaN.
    uncertainty : pandas.Series or None
        Filtered conditional state standard deviations, for state_space only.
        Excludes parameter-estimation uncertainty and model misspecification.
    loadings : pandas.Series
        Coefficients on TRAIN-standardized ORIGINAL indicator directions.
        Composite loadings are normalized weights, not inferred factor loadings.
    diagnostics : dict
        Descriptive checks (not formal calibrated hypothesis tests).
    metadata : dict
        Estimator, training statistics, missingness and normalization conventions.
    warnings : tuple of str
        Identification and numerical cautions.
    estimate_kind : str
        Always 'filtered' for the state-space method; point-in-time scores otherwise.
    """

    model: IndexKind
    origin: pd.Timestamp
    information_cutoff: pd.Timestamp
    training_cutoff: pd.Timestamp
    factor: pd.Series
    uncertainty: pd.Series | None
    loadings: pd.Series
    diagnostics: dict[str, object]
    metadata: dict[str, object]
    warnings: tuple[str, ...]
    estimate_kind: str


def _timestamp(value: object, name: str) -> pd.Timestamp:
    result = pd.Timestamp(value)
    if pd.isna(result) or result.tz is not None:
        raise ValueError(f"{name} must be a finite timezone-naive timestamp")
    return result


def _validate_features(frame: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        raise ValueError("features must be a nonempty pandas DataFrame")
    if not isinstance(frame.index, pd.DatetimeIndex):
        raise ValueError("features need an explicit DatetimeIndex")
    if frame.index.tz is not None or frame.index.hasnans:
        raise ValueError("feature dates must be timezone-naive and nonmissing")
    if not frame.index.is_monotonic_increasing or not frame.index.is_unique:
        raise ValueError("feature dates must be increasing and unique")
    if not frame.columns.is_unique or any(not isinstance(c, str) for c in frame.columns):
        raise ValueError("feature names must be unique strings")
    for column in frame.columns:
        upper = column.upper()
        if any(reference in upper for reference in _BLOCKED_REFERENCES):
            raise ValueError(f"external stress benchmark is not an input: {column}")
    if not all(pd.api.types.is_numeric_dtype(t) for t in frame.dtypes):
        raise ValueError("all indicator columns must be numeric")
    result = frame.astype(float).copy()
    if np.isinf(result.to_numpy()).any():
        raise ValueError("infinite features are forbidden; NaN denotes missingness")
    return result


def _directions(columns: pd.Index, directions: dict[str, int]) -> NDArray[np.float64]:
    if not isinstance(directions, dict) or set(directions) != set(columns):
        raise ValueError("supply an explicit +1/-1 direction for every feature")
    values = np.asarray([directions[c] for c in columns], dtype=float)
    if not np.isin(values, [-1.0, 1.0]).all():
        raise ValueError("directions must be exactly +1 or -1")
    return values


def _corr(x: NDArray[np.float64], y: NDArray[np.float64]) -> float | None:
    good = np.isfinite(x) & np.isfinite(y)
    if good.sum() < 4 or np.std(x[good]) < 1e-12 or np.std(y[good]) < 1e-12:
        return None
    return float(np.corrcoef(x[good], y[good])[0, 1])


def _residual_checks(resid: NDArray[np.float64], columns: pd.Index) -> dict[str, object]:
    return {
        "residual_lag1_correlation": {
            c: _corr(resid[:-1, i], resid[1:, i]) for i, c in enumerate(columns)
        },
        "residual_pairwise_correlation": {
            a: {b: (_corr(resid[:, i], resid[:, j]) if i != j else None)
                for j, b in enumerate(columns)}
            for i, a in enumerate(columns)
        },
        "residual_observation_count": {
            c: int(np.isfinite(resid[:, i]).sum()) for i, c in enumerate(columns)
        },
    }


def _first_component(signed: NDArray[np.float64], anchor: int) -> tuple[
    NDArray[np.float64], NDArray[np.float64], float
]:
    _, singular, vt = np.linalg.svd(signed, full_matrices=False)
    if singular[0] < 1e-10:
        raise ValueError("no variance available for a PCA factor")
    vec = vt[0].copy()
    if abs(vec[anchor]) < 1e-8:
        raise ValueError("anchor loading nearly zero: stress orientation unidentified")
    if vec[anchor] < 0:
        vec *= -1
    variance_fraction = float(singular[0] ** 2 / np.sum(singular ** 2))
    return vec, singular, variance_fraction


def _split_stability(
    train_signed: NDArray[np.float64], anchor: int, reference: NDArray[np.float64]
) -> dict[str, float | None]:
    values: dict[str, float | None] = {}
    for name, block in (
        ("first_half", train_signed[:len(train_signed) // 2]),
        ("second_half", train_signed[len(train_signed) // 2:]),
    ):
        try:
            direction, _, _ = _first_component(block, anchor)
            values[name] = float(np.dot(direction, reference))
        except (ValueError, np.linalg.LinAlgError):
            values[name] = None
    return values


def _kalman_filter(
    signed: NDArray[np.float64],
    loadings: NDArray[np.float64],
    observation_variance: NDArray[np.float64],
    phi: float,
    process_variance: float,
) -> tuple[NDArray[np.float64], NDArray[np.float64], float]:
    """Univariate AR(1) filtering with exact sequential scalar measurement updates.

    Each date conditions ONLY on that date's observed features and earlier dates.
    """
    state = 0.0
    variance = process_variance / (1.0 - phi * phi)
    means = np.empty(len(signed))
    variances = np.empty(len(signed))
    loglike = 0.0
    for t, row in enumerate(signed):
        state *= phi
        variance = phi * phi * variance + process_variance
        for j in np.flatnonzero(np.isfinite(row)):
            loading = loadings[j]
            innovation = row[j] - loading * state
            innovation_variance = loading * loading * variance + observation_variance[j]
            gain = variance * loading / innovation_variance
            state += gain * innovation
            variance *= 1.0 - gain * loading
            loglike -= 0.5 * (
                np.log(2 * np.pi * innovation_variance)
                + innovation * innovation / innovation_variance
            )
        if not np.isfinite(state) or not np.isfinite(variance) or variance < -1e-10:
            raise ArithmeticError("Kalman recursion became nonfinite")
        means[t] = state
        variances[t] = max(variance, 0.0)
    return means, variances, loglike


def fit_country_index(
    features: pd.DataFrame,
    training_cutoff: object,
    *,
    origin: object | None = None,
    model: IndexKind = "composite",
    directions: dict[str, int],
    stress_anchor: str | None = None,
    max_training_missing: float = 0.40,
) -> CountryIndexResult:
    """Fit a frozen model through training_cutoff and filter/score through origin.

    Parameters
    ----------
    features : pandas.DataFrame
        Country-specific, indexed, chronological numeric features, already
        validated for observation AND publication availability by the caller.
        NaN indicates unavailable feature, never a source-level zero.
    training_cutoff : date-like
        Inclusive last date permitted for means, scales, loadings and AR parameters.
    origin : date-like, optional
        Inclusive information cutoff; defaults to training_cutoff. Rows beyond it
        cannot affect returned estimates. May extend training without refitting.
    model : {'composite', 'pca', 'state_space'}
        Transparent signed mean, static first PC, or a two-stage Gaussian AR(1)
        state-space candidate with PCA-fixed loadings and diagonal observation noise.
        The last is NOT a joint maximum-likelihood fitted dynamic factor model.
    directions : dict of str to int
        Explicit high-stress sign (+1 or -1) for every column; no inferred signs.
    stress_anchor : str, optional
        Original column whose SIGNED loading anchors the PCA/SS direction. Required
        for PCA and state_space. Fails if its loading is approximately zero.
    max_training_missing : float
        Maximum permitted fraction of missing TRAINING rows per feature, [0,1).

    Returns
    -------
    CountryIndexResult
        Cutoff-bounded index with frozen estimation, factor, warnings and diagnostics.

    Raises
    ------
    ValueError
        On invalid feature identities/dates, benchmark leakage, missing or constant
        training features, or insufficient identifiable state-space structure.

    Notes
    -----
    Train-only observed moments standardize columns. For PCA/state_space, missing
    entries are explicitly imputed to ZERO *after* train standardization (equivalent
    to a frozen training mean). The state-space FILTER instead treats each missing
    observation as absent in its measurement update. For the transparent composite,
    missing components are omitted and remaining equally weighted; all-missing rows
    have NaN factor. No two-sided smoother is provided. Updating parameters across
    refits can revise old indices: sign anchoring alone cannot prevent that.
    """
    panel = _validate_features(features)
    if model not in ("composite", "pca", "state_space"):
        raise ValueError("unknown index model")
    train_end = _timestamp(training_cutoff, "training_cutoff")
    at = _timestamp(origin if origin is not None else training_cutoff, "origin")
    if at < train_end or train_end < panel.index[0]:
        raise ValueError("origin must be on/after training_cutoff within the panel")
    if not (0 <= max_training_missing < 1):
        raise ValueError("max_training_missing must be in [0,1)")
    observed = panel.loc[:at]
    training = observed.loc[:train_end]
    if len(training) < 8:
        raise ValueError("at least eight training rows are required")
    signs = _directions(panel.columns, directions)
    train_raw = training.to_numpy()
    missing_fraction = np.isnan(train_raw).mean(axis=0)
    if np.any(missing_fraction > max_training_missing):
        raise ValueError("training missingness exceeds declared threshold")
    n_observed = np.isfinite(train_raw).sum(axis=0)
    if np.any(n_observed < 3):
        raise ValueError("each feature requires at least three observed training values")
    mean = np.nanmean(train_raw, axis=0)
    std = np.nanstd(train_raw, axis=0)
    if np.any(std <= 1e-12):
        raise ValueError("training feature is constant")
    raw = observed.to_numpy()
    standardized = (raw - mean) / std
    signed = standardized * signs
    train_signed = signed[:len(training)]
    mask = np.isfinite(signed)
    filled = np.where(mask, signed, 0.0)
    filled_train = filled[:len(training)]
    warnings: list[str] = []
    uncertainty: pd.Series | None = None
    metadata: dict[str, object] = {
        "input_columns": list(panel.columns),
        "train_mean": dict(zip(panel.columns, mean.tolist(), strict=True)),
        "train_std_ddof0": dict(zip(panel.columns, std.tolist(), strict=True)),
        "economic_directions": directions.copy(),
        "missing_policy": "composite available-case; PCA training-mean; state-space absent update",
        "source_availability_verification": "CALLER_RESPONSIBILITY_NOT_VERIFIED",
        "external_benchmarks_excluded": list(_BLOCKED_REFERENCES),
        "training_rows": len(training),
        "training_missing_fraction": dict(zip(panel.columns, missing_fraction.tolist(), strict=True)),
        "factor_target": "feature-specific constructed market factor; not systemic stress",
    }
    diagnostics: dict[str, object] = {
        "observed_feature_count": pd.Series(mask.sum(axis=1), index=observed.index).to_dict(),
        "all_missing_dates": [str(x.date()) for x in observed.index[~mask.any(axis=1)]],
        "training_sample_end": str(training.index[-1].date()),
        "numerical_convergence": "not_optimized",
    }
    if np.any(~mask):
        warnings.append("Some input features are missing; see missing policy and diagnostics.")
    if model == "composite":
        counts = mask.sum(axis=1)
        scores = filled.sum(axis=1) / np.maximum(counts, 1)
        scores[counts == 0] = np.nan
        load = signs / len(signs)
        resid = signed - scores[:, None]
        estimate_kind = "pointwise"
        metadata["normalization"] = "available signed component average; not re-standardized"
        metadata["loading_interpretation"] = "equal weights, not estimated loadings"
    else:
        if stress_anchor not in panel.columns:
            raise ValueError("PCA/state_space requires a named stress_anchor column")
        anchor = panel.columns.get_loc(stress_anchor)
        pc, singular, share = _first_component(filled_train, anchor)
        score_scale = float(np.std(filled_train @ pc))
        if score_scale <= 1e-10:
            raise ValueError("first component score scale unidentified")
        eigengap = (
            float(singular[0] / singular[1]) if len(singular) > 1 and singular[1] > 0
            else float("inf")
        )
        stability = _split_stability(filled_train, anchor, pc)
        diagnostics.update({
            "pca_explained_variance_ratio": share,
            "pca_singular_value_ratio_1_to_2": eigengap,
            "pca_split_loading_cosine": stability,
        })
        if eigengap < 1.15:
            warnings.append("First PCA direction weakly separated from second (ratio < 1.15).")
        if any(v is not None and v < 0.7 for v in stability.values()):
            warnings.append("PCA loading direction unstable across training halves.")
        metadata["stress_anchor"] = stress_anchor
        metadata["normalization"] = "first PC divided by training population score SD"
        if model == "pca":
            scores = filled @ pc / score_scale
            scores[~mask.any(axis=1)] = np.nan
            load = signs * pc / score_scale
            resid = signed - (scores * score_scale)[:, None] * pc[None, :]
            estimate_kind = "pointwise"
            metadata["loading_interpretation"] = "linear scoring weights"
        else:
            if len(training) < 40 or len(panel.columns) < 3:
                raise ValueError("state_space needs >=40 training rows and >=3 features")
            if eigengap < 1.15 or abs(pc[anchor]) < 0.1:
                raise ValueError("state_space factor identification is too weak")
            if np.mean(mask[:len(training)].sum(axis=1) >= 2) < 0.9:
                raise ValueError("state_space requires at least 2 train features on 90% of dates")
            proxy = filled_train @ pc / score_scale
            phi_denom = float(proxy[:-1] @ proxy[:-1])
            if phi_denom < 1e-10:
                raise ValueError("state-space AR coefficient unidentified")
            phi_unclipped = float((proxy[:-1] @ proxy[1:]) / phi_denom)
            phi = float(np.clip(phi_unclipped, -0.975, 0.975))
            if phi != phi_unclipped:
                warnings.append("State AR(1) persistence truncated to stable [-0.975, 0.975].")
            innovation = proxy[1:] - phi * proxy[:-1]
            q = max(float(np.mean(innovation ** 2)), 0.02)
            measurement_loading = pc * score_scale
            training_residual = train_signed - proxy[:, None] * measurement_loading
            # Each variance is estimated ONLY where that series was observed.
            obs_var = np.array([
                max(float(np.nanmean(training_residual[:, j] ** 2)), 0.025)
                for j in range(len(pc))
            ])
            scores, state_var, loglike = _kalman_filter(
                signed, measurement_loading, obs_var, phi, q
            )
            uncertainty = pd.Series(
                np.sqrt(state_var), index=observed.index, name="conditional_filtered_se"
            )
            load = signs * measurement_loading
            resid = signed - scores[:, None] * measurement_loading
            estimate_kind = "filtered"
            metadata.update({
                "estimation": "two_stage_PCA_loadings_and_AR1_moments_NOT_joint_MLE",
                "state_transition": "AR(1)",
                "state_phi": phi,
                "state_innovation_variance": q,
                "observation_variance": dict(zip(panel.columns, obs_var.tolist(), strict=True)),
                "loading_interpretation": "observation equation loadings on state factor",
                "uncertainty_scope": "conditional_on_frozen_estimated_parameters",
                "smoothed_estimates": "not computed; would use future observations",
            })
            diagnostics.update({
                "numerical_convergence": "finite_forward_filter; no iterative MLE",
                "conditional_loglikelihood": loglike,
                "min_filtered_variance": float(np.min(state_var)),
                "parameter_optimizer": "not_applicable_two_stage",
            })
            if any(v <= 0.025000001 for v in obs_var):
                warnings.append("At least one observation variance reached numerical floor.")
    diagnostics.update(_residual_checks(resid, panel.columns))
    diagnostics["factor_finite_count"] = int(np.isfinite(scores).sum())
    if at > observed.index[-1]:
        warnings.append("Origin is after final available observation; no calendar interpolation.")
    return CountryIndexResult(
        model=model,
        origin=at,
        information_cutoff=at,
        training_cutoff=train_end,
        factor=pd.Series(scores, index=observed.index, name=f"{model}_country_factor"),
        uncertainty=uncertainty,
        loadings=pd.Series(load, index=panel.columns, name=f"{model}_loadings"),
        diagnostics=diagnostics,
        metadata=metadata,
        warnings=tuple(warnings),
        estimate_kind=estimate_kind,
    )
