"""Matched forecast scoring, dependent bootstrap intervals and HAC comparison.

Neither the bootstrap nor the asymptotic HAC test establishes a valid real-time
design; publication vintages, target scaling and multiple testing must be audited.
"""
from __future__ import annotations

from collections.abc import Iterator

import numpy as np
import pandas as pd
from scipy.stats import norm

GROUP = ["country", "target_id", "target_scale", "vintage_mode", "horizon", "horizon_unit"]
KEY = ["origin_date", "target_date"]
REQUIRED = set(GROUP + KEY + ["model", "actual", "prediction"])


def _groups(frame: pd.DataFrame) -> Iterator[tuple[tuple, pd.DataFrame]]:
    if frame.empty or not REQUIRED.issubset(frame):
        raise ValueError("missing required forecast-result columns or no records")
    data = frame.copy()
    if data[list(REQUIRED)].isna().any().any():
        raise ValueError("forecast-result fields must not be missing")
    if any(not data[x].map(lambda v: isinstance(v, str) and bool(v.strip())).all()
           for x in ("country", "target_id", "target_scale", "vintage_mode",
                     "horizon_unit", "model", *KEY)):
        raise ValueError("invalid identity, date or model labels")
    if (not np.isfinite(data[["actual", "prediction"]].to_numpy(dtype=float)).all()
            or not (data["horizon"] > 0).all()):
        raise ValueError("invalid actual/prediction/horizon")
    if data.duplicated(GROUP + ["model"] + KEY).any():
        raise ValueError("duplicate origin-target forecast identity")
    # A given country/target/date is one observed outcome regardless of model.
    for group, subset in data.groupby(GROUP, sort=True):
        models = sorted(subset["model"].unique())
        expected: pd.DataFrame | None = None
        for model in models:
            series = subset.loc[subset["model"] == model, KEY + ["actual"]]
            series = series.sort_values(KEY).reset_index(drop=True)
            if expected is None:
                expected = series
            elif not series.equals(expected):
                raise ValueError(f"unmatched origin-target pairs or actuals for {group}")
        # A unique series identity must not silently combine target scales.
        yield group, subset


def _errors_by_model(subset: pd.DataFrame) -> dict[str, np.ndarray]:
    return {
        name: (part.sort_values(KEY)["actual"] - part.sort_values(KEY)["prediction"])
        .to_numpy(dtype=float)
        for name, part in subset.groupby("model")
    }


def _circular_sample(rng: np.random.Generator, n: int, block: int) -> np.ndarray:
    """Resample contiguous circular blocks of *origin-indexed* observations."""
    starts = rng.integers(0, n, size=(n + block - 1) // block)
    return ((starts[:, None] + np.arange(block)[None, :]) % n).ravel()[:n]


def score_matched(
    forecasts: pd.DataFrame,
    *,
    n_boot: int = 999,
    block_length: int | None = None,
    confidence: float = 0.95,
    seed: int = 20261018,
) -> pd.DataFrame:
    """Score MSE/RMSE/MAE with within-target moving-block bootstrap intervals.

    All competing methods must have *identical* origin-target pairs and actuals.
    Resamples operate on a jointly matched chronological origin index. Results
    are separate for every country, target identity, scale, vintage and horizon.

    Parameters
    ----------
    forecasts : pandas.DataFrame
        Rows returned by run_backtest or the documented compatible schema.
    n_boot : int
        Positive number of dependent bootstrap replications.
    block_length : int or None
        Circular block size in *forecast origins*, not observations. When
        omitted, exploratory default ceil(n**(1/3)), capped at n.
    confidence : float
        Percentile interval coverage.
    seed : int
        Fixed RNG seed for reproducibility.

    Returns
    -------
    pandas.DataFrame
        Per-model point scores and percentile confidence intervals.

    Raises
    ------
    ValueError
        Unmatched grids, nonfinite data, invalid bootstrap parameters.

    Notes
    -----
    Intervals assume sufficiently stationary/weakly dependent loss blocks
    and do not account for retrospective vintage revisions, multiple
    comparisons, or uncertainty of latent target construction.
    """
    if (type(n_boot) is not int or n_boot < 1 or not 0 < confidence < 1
            or (block_length is not None
                and (type(block_length) is not int or block_length < 1))):
        raise ValueError("invalid block-bootstrap settings")
    rng = np.random.default_rng(seed)
    rows = []
    for group, subset in _groups(forecasts):
        err = _errors_by_model(subset)
        n = len(next(iter(err.values())))
        block = min(n, max(1, int(np.ceil(n ** (1 / 3))))) if block_length is None else block_length
        if block > n:
            raise ValueError("block_length exceeds number of paired origins")
        samples = [_circular_sample(rng, n, block) for _ in range(n_boot)]
        lo, hi = (1 - confidence) / 2, (1 + confidence) / 2
        for model, e in sorted(err.items()):
            s = e * e
            metrics = {
                "mse": (float(np.mean(s)), np.array([np.mean(s[ix]) for ix in samples])),
                "rmse": (
                    float(np.sqrt(np.mean(s))),
                    np.array([np.sqrt(np.mean(s[ix])) for ix in samples]),
                ),
                "mae": (
                    float(np.mean(np.abs(e))),
                    np.array([np.mean(np.abs(e[ix])) for ix in samples]),
                ),
            }
            row = dict(zip(GROUP, group, strict=True))
            row.update({"model": model, "n_pairs": n, "bootstrap_seed": seed,
                        "bootstrap_replications": n_boot,
                        "bootstrap_block_origins": block, "confidence": confidence})
            for label, (point, resamples) in metrics.items():
                lower, upper = np.quantile(resamples, [lo, hi])
                row.update({label: point, f"{label}_ci_low": float(lower),
                            f"{label}_ci_high": float(upper)})
            rows.append(row)
    return pd.DataFrame(rows)


def hac_loss_differentials(
    forecasts: pd.DataFrame,
    *,
    benchmark: str = "persistence",
    lag: int | None = None,
    confidence: float = 0.95,
) -> pd.DataFrame:
    """Two-sided normal-approximation DM-style HAC test of paired squared losses.

    Differential d_t = (actual - challenger)^2 - (actual - benchmark)^2.
    Negative mean is lower MSE for the challenger. Newey-West/Bartlett HAC
    estimates the long-run variance. An exploratory default lag is min(h-1,
    n//4), based on overlap for consecutive observed-index origins; it may be
    inappropriate for a wider stride, model estimation dependence, breaks, or
    nonstationary CISS losses. Prespecify lag and report sensitivity analyses.

    The normal approximation is asymptotic and especially unreliable with
    few origins or extensive model searching; NOT a finite-sample guarantee.
    """
    if not benchmark.strip() or not 0 < confidence < 1:
        raise ValueError("invalid benchmark or confidence")
    if lag is not None and (type(lag) is not int or lag < 0):
        raise ValueError("HAC lag must be nonnegative")
    rows = []
    for group, subset in _groups(forecasts):
        errs = _errors_by_model(subset)
        if benchmark not in errs:
            raise ValueError(f"missing baseline {benchmark} in {group}")
        n = len(errs[benchmark])
        if n < 8:
            raise ValueError("at least 8 paired forecast origins needed for HAC")
        effective_lag = min(int(group[4]) - 1, n // 4) if lag is None else lag
        if effective_lag >= n:
            raise ValueError("HAC lag must be < number of forecast origins")
        ref = errs[benchmark] ** 2
        for challenger, values in sorted(errs.items()):
            if challenger == benchmark:
                continue
            differential = values ** 2 - ref
            mean = float(np.mean(differential))
            centered = differential - mean
            long_run = float(np.mean(centered * centered))
            for k in range(1, effective_lag + 1):
                covariance = float(np.dot(centered[k:], centered[:-k]) / n)
                long_run += 2 * (1 - k / (effective_lag + 1)) * covariance
            if long_run <= 0:
                raise ValueError("nonpositive estimated long-run variance; DM inference undefined")
            se = float(np.sqrt(long_run / n))
            statistic = mean / se
            critical = float(norm.ppf((1 + confidence) / 2))
            row = dict(zip(GROUP, group, strict=True))
            row.update({
                "benchmark": benchmark, "challenger": challenger, "n_pairs": n,
                "mean_loss_diff": mean, "hac_lag": effective_lag,
                "hac_standard_error": se, "dm_z": statistic,
                "p_two_sided_normal": float(2 * norm.sf(abs(statistic))),
                "ci_low": mean - critical * se, "ci_high": mean + critical * se,
                "confidence": confidence,
                "inference": "EXPLORATORY_DM_STYLE_NEWEY_WEST_NORMAL",
            })
            rows.append(row)
    return pd.DataFrame(rows)
