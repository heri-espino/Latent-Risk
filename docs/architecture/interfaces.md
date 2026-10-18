---
orphan: true
---

# Integration interfaces — proposed contract v1

**Status:** PROPOSED, not a new exported package API. **Owner:** library QA. **Reviewed against:** `pyproject.toml`, `src/latent_risk/data/vintages.py`, `data/market_features.py`, `indices/`, `evaluation/errors.py`, and CI as of 2026-10-18. Implementation of factor, trend, forecasting, and scoring boundaries requires coordinator approval.

## 1. Goals and non-goals

The research flow is **raw observation → feature observation → country index → one-sided state/trend → forecast → forecast departure/event score**. Every edge has a declared target, information cutoff, time unit, and data provenance. Its invariant is *no information that was unavailable at the forecast origin enters estimation or calibration*. A successful offline/backtest integrity audit does **not** establish historical first-release availability.

Supported geography identifiers are `MEX`, `USA`, `GBR`, `JPN`, and `EA` (euro area). These are research IDs, not a promise of interchangeable national definitions. No universal observable "risk" index exists; composite, PCA, and future DFM are distinct estimated targets.

Current APIs: `latent_risk.data.validate_long_panel` and `available_as_of` accept date-level, timezone-naive `observation_date` / `available_date`, requiring non-null dates; `latent_risk.indices.fit_signed_composite` / `fit_pca` produce fixed-train transforms; `latent_risk.evaluation.forecast_errors` / `standardized_errors` compute descriptive errors. This is **IMPLEMENTED**, but the versioned adapters below are **PROPOSED**. In particular, the existing vintage validator cannot certify observed release times.

## 2. Canonical source-to-model observation (v1 proposal)

One record per source/feature/observation/snapshot; revisions may have multiple snapshots. A typed frozen dataclass or typed Arrow schema is appropriate *only after* the agents agree on serialization and compatibility. Recommended Python field types and semantics:

| Field | Type | Mandatory rule |
| --- | --- | --- |
| `contract_version` | `Literal["1.0"]` | Unknown major versions rejected, no implicit coercion |
| `country_id` | `Literal["MEX","USA","GBR","JPN","EA"]` | Canonical identifier; euro-area composition metadata belongs in source version |
| `feature_name` | `str` | Stable, explicit economic orientation and transform definition |
| `observation_date` | `date` | Source's economic/reporting date, not automatically a market-close time |
| `observation_timestamp` | `datetime | None` | UTC-aware event/close timestamp if **verified**; null if only a trade/reporting date is known |
| `verified_available_at` | `datetime | None` | UTC-aware actual historical publication/availability time, if independently justified; **null means unknown**, never approximate with observation day or snapshot download time |
| `value` | `float | None` | Finite iff `missing_reason == "present"` |
| `provider` / `source_id` | `str` / `str` | Original producer/distributor and vendor series identifier |
| `transformation` | `str` | Versioned formula, lookback, parameters, direction, handling of warmup |
| `units` / `frequency` | `str` / `str` | E.g. index points, log-return, percentage points; business-day/monthly, with observation-step convention |
| `snapshot_id` / `source_sha256` | `str` / `64-hex str` | Immutable source snapshot and SHA256 of **exact archived source bytes**; derivative file has its own different hash |
| `missing_reason` | `enum` | `present`, `provider_missing`, `market_closed`, `warmup`, `not_applicable`, `not_yet_released`; do not coerce to zero or forward-fill |
| `license` | `str` | Named/verified reuse restrictions or explicit `unknown`; never upload restricted raw sources |
| `is_external_benchmark` | `bool` | Exclude from country factor and concordance-model inputs by default; benchmarks may be **targets in a separately labeled direct-forecast experiment** |
| `source_revision` | `str | None` | Vendor vintage/release identifier when available; null does not imply original vintage |

The manifest's `sha256` currently hashes a **saved CSV**, not necessarily the original HTTP response: never describe these as identical. A transformation propagates the exact original source SHA256 as lineage **without replacing it** with the derived output hash. The composite lineage may reference several distinct hashes. A current-vintage download is not a 2008-vintage dataset.

### Availability gate

For UTC-aware forecast origin `o`, admissible feature records satisfy both: (1) `verified_available_at is not None` and `verified_available_at <= o`; and (2) if `observation_timestamp` is verified, it is not later than `o`. Unknown release timestamps are excluded from **strict point-in-time** analysis, not silently defaulted to midnight. Retrospective/descriptive analysis must explicitly opt into a separate mode and cannot be relabeled pseudo-real-time.

When a provider reports date-only observations, exact same-date joins remain descriptive until close/session and release conventions are audited. The current `available_as_of` uses timezone-naive dates; an explicit, reviewed adapter must convert *verified* release instants to the proposed UTC contract. Reject ambiguous/unaware timestamp comparisons, DST ambiguity, implicit business-calendar conversions, and future forward-fill. "Last available" imputations, if ever accepted, require a separately versioned as-of join rule, age limit and missingness mask, never a silent operation.

A feature must be computed only from source records admitted by the origin's information set. If the latest value has unknown availability, exclude it even if an older snapshot was downloaded later.

## 3. Four model boundaries (version 1 proposal)

Define `FeatureBatchV1` containing a single `country_id`, ordered feature names, row dates, values/missing masks, observation-level release provenance, source-hash lineage, `origin_utc`, and `contract_version`. Reject a mixed-country batch unless it is explicitly a cross-country model, unequal feature ordering, non-finite accepted values, or any `is_external_benchmark=True` row. Declare the allowed missingness treatment **before** training.

- **Country factor:** `fit_as_of(batch: FeatureBatchV1, *, origin_utc, seed: int) -> FactorSnapshotV1`. Return an immutable model/specification identifier, country ID, sign anchor (precommitted stress-positive feature), training-end cutoff, fitted means/scales/loadings, score series through origin, source lineage and target ID. A PCA orientation sign alone does not guarantee **scale or identity** continuity across refits. Frozen reference scale or explicitly justified alignment is required before forecast errors are compared across origins.
- **One-sided state/trend:** `filter_as_of(factor: FactorSnapshotV1, *, origin_utc) -> StateSnapshotV1`. Return a filtered state at origin, method/version, sufficient statistics, uncertainty, hyperparameter calibration cutoff and factor target ID. Never use a full-sample smoother for an earlier origin. Penalized least squares and Gaussian local-linear state-space interpretations are research proposals, **not implemented** here.
- **Forecaster:** `predict(state: StateSnapshotV1, *, issued_at_utc, horizon: HorizonSpecV1) -> ForecastV1`. Declare whether horizon means calendar duration, local trading observations or source observations; include forecast target timestamp/date, predicted factor target ID, point estimate, positive predictive SD when available, fit/calibration provenance and seed. Parameters selected by CV must use origins strictly before the issued forecast.
- **Event scorer:** `score(forecast: ForecastV1, realized: RealizationV1, *, calibration: CalibrationV1) -> EventScoreV1`. The realized **same identifiable target** and its release vintage must be declared; score only after its value is available. An event threshold and coverage/calibration dataset are separately frozen from the evaluation window. A standardized departure can be computed via the existing `standardized_errors`; exceeding a threshold is **not** automatically proven financial-crisis detection.

If adapters are introduced, `Protocol` typing is suitable for interchangeable factor/trend/forecaster implementations; frozen dataclasses validate messages at runtime. Avoid a monolithic base engine or importing experimental scripts inside `latent_risk`. Numerical implementations should use stable factorizations/solvers, not explicit dense inverses for structured penalties.


## 4. Typed, non-exported interface sketch

This illustrative Python 3.10+ signature block is **PROPOSED ONLY**. The classes do **not** exist in `src/latent_risk` and are not meant to be imported by the contract test suite. Runtime validators, provenance serialization and actual estimators must be agreed before implementation.

```python
from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal, Protocol

CountryID = Literal["MEX", "USA", "GBR", "JPN", "EA"]
MissingReason = Literal[
    "present", "provider_missing", "market_closed", "warmup",
    "not_applicable", "not_yet_released",
]


@dataclass(frozen=True, slots=True)
class FeatureObservationV1:
    contract_version: Literal["1.0"]
    country_id: CountryID
    feature_name: str
    observation_date: date
    observation_timestamp: datetime | None   # verified UTC instant or null
    verified_available_at: datetime | None    # null means UNKNOWN, never midnight
    value: float | None
    provider: str
    source_id: str
    transformation: str
    units: str
    frequency: str
    snapshot_id: str
    source_sha256: str
    missing_reason: MissingReason
    license: str
    is_external_benchmark: bool
    source_revision: str | None = None


@dataclass(frozen=True, slots=True)
class FeatureBatchV1:
    country_id: CountryID
    origin_utc: datetime
    ordered_features: tuple[str, ...]
    observations: tuple[FeatureObservationV1, ...]
    contract_version: Literal["1.0"] = "1.0"


@dataclass(frozen=True, slots=True)
class FactorSnapshotV1:
    country_id: CountryID
    target_id: str
    origin_utc: datetime
    score_history: tuple[float, ...]
    feature_order: tuple[str, ...]
    anchor_feature: str
    fixed_scale_id: str
    lineage_sha256: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class StateSnapshotV1:
    target_id: str
    origin_utc: datetime
    state_mean: float
    state_variance: float
    fit_cutoff_utc: datetime
    filter_version: str


@dataclass(frozen=True, slots=True)
class HorizonSpecV1:
    steps: int
    clock: Literal["calendar_days", "trading_sessions", "source_observations"]


@dataclass(frozen=True, slots=True)
class ForecastV1:
    target_id: str
    issued_at_utc: datetime
    target_date: date
    horizon: HorizonSpecV1
    location: float
    predictive_sd: float
    calibration_cutoff_utc: datetime


@dataclass(frozen=True, slots=True)
class EventScoreV1:
    target_id: str
    target_date: date
    scored_at_utc: datetime
    standardized_departure: float
    calibration_id: str
    threshold_exceeded: bool


class CountryFactor(Protocol):
    def fit_as_of(
        self, batch: FeatureBatchV1, *, origin_utc: datetime, seed: int
    ) -> FactorSnapshotV1: ...


class OneSidedTrend(Protocol):
    def filter_as_of(
        self, factor: FactorSnapshotV1, *, origin_utc: datetime
    ) -> StateSnapshotV1: ...


class Forecaster(Protocol):
    def predict(
        self, state: StateSnapshotV1, *, horizon: HorizonSpecV1
    ) -> ForecastV1: ...


class EventScorer(Protocol):
    def score(
        self, forecast: ForecastV1, realized: float,
        *, realized_available_at: datetime, calibration_id: str
    ) -> EventScoreV1: ...
```

Actual implementations must validate at runtime: UTC-aware timestamps (not merely annotated `datetime`); nonnegative uncertainty and strictly positive predictive SD; SHA256 format; aligned country/target IDs; anchor/scale identity; no benchmark inputs; no future origin/fit/calibration information; and strict missingness rules. The minimal `EventScorer` signature above does not identify the complete realization vintage/uncertainty and should be expanded through the evaluation-agent decision before becoming stable.

## 5. Precise invariants and test oracle

Let `I(o)` be the admissible, verified information set at origin `o`. For a deterministic seeded pipeline `A`, the forecast-origin invariance property is:

`A(I(o) union F) = A(I(o))` for any future rows `F` whose verified release time is later than `o`.

This is a **proposed contract property**, not a proof about an unimplemented engine. It assumes no future-dependent preprocessing, training cutoff, hyperparameter optimization, exogenous benchmark feature, or random-state contamination.

A complete regression test should also check: (a) no benchmark as index feature or leakage target; (b) factor sign **and scale** anchoring across refits; (c) same feature order and units; (d) unchanged original raw hashes in the lineage; (e) explicit null/market-closure/date-only release semantics; (f) source-local trading calendars and UTC conversions; (g) forecast horizon/target identity alignment; (h) fixed seeds and tie-breaking; (i) offline tests without vendor credentials or raw files; and (j) test data never contaminated by tuning.

## 6. Current adapters and gaps

| Stage | Status | Existing entry point | Unresolved integration point |
| --- | --- | --- | --- |
| Immutable source hash | IMPLEMENTED | `data.acquisition._save_frame`, `data.quality.inspect_source_file` | Agree on response-hash vs archived-byte hash and lineage serialization |
| Date-vintage filtering | IMPLEMENTED (date-only) | `data.available_as_of` | UTC release instants, null availability and revision-key semantics |
| Descriptive market features | IMPLEMENTED | `data.market_features.build_country_market_panel` | Audited close clocks, source licenses, feature schema, instrument calendars |
| Signed composite / PCA | IMPLEMENTED | `indices.fit_signed_composite`, `fit_pca` | Canonical feature order, benchmark gate, per-origin target identity/scale |
| DFM and probabilistic trend | PROPOSED | none in current public API | Factor output Protocol; filtered vs retrospectively smoothed state |
| Forecast departure | IMPLEMENTED (arithmetic only) | `evaluation.forecast_errors`, `standardized_errors` | Predictive distribution calibration, comparable target, event outcomes |

### Coordination requests (no engine code changed)

1. **Data agent:** freeze feature naming, source-hash/response-hash meaning, data licenses, `available_at` verification evidence, market-close clocks, missingness and cross-source calendars.
2. **Index agent:** agree on batch column order, benchmark prohibition, factor model/spec ID, training-only anchor, scale alignment and uncertainty output.
3. **Trend agent:** provide one-sided filtered-state contract, exact origin/horizon indexing and no retrospective-smoothing reuse.
4. **Forecast/event agent:** specify realizations, score target identity, calibration split and exceedance evaluation; direct CISS forecasting must remain a distinct experiment.
5. **Coordinator:** approve runtime validators/export locations, schema versioning and CI integration before any package or engine modification. 

See [integration checklist](integration_checklist.md) and `tests/test_public_contracts.py`. The tests combine real existing public APIs with explicitly test-local reference stubs; they do **not** certify the future factor→trend→forecast→event engine.
