# Experiment registry

Experiments use stable IDs `EXP-####`, each with a prose protocol in `experiments/EXP-####.md` and machine configuration in `experiments/configs/`. Their outputs belong in `results/runs/<experiment-id>/` (usually gitignored); attach metadata with data vintage, code revision, exact settings and validation/confirmation labels.

**EXP-0001 is proposed and unrun. EXP-0002 is implemented/tested offline and not yet run on user CISS files; it is a retrospective observation-index forecasting-engineering study, NOT an early warning evaluation.** Do not generate tables or claim empirical significance until a frozen protocol and logged execution exist.

Scientific isolation:
1. Index measurement: transparent signed average, PCA, Gaussian DFM; conditional robustness methods only later.
2. Smoother: Gaussian constrained local-linear trend; choose variance ratio by **marginal likelihood**, implementation pending.
3. Evaluation: retrospective reconstruction for description; pseudo-real-time with actual release dates for claims of predictive ability.
4. Score against predeclared external observable outcomes for direct between-index comparability.

Record unsuccessful runs and diagnostic failures, including factors violating residual tests.

## Exploratory numerical test

[EXP-0002](EXP-0002.md) isolates forecast-origin mechanics using the three
ECB CISS **observed-target** series. Compare last-observation persistence,
OLS AR(1) and a one-sided EWMA with horizon-specific gain selected by
strictly nested historical CV. It has current revised observations, not
release-vintage data; it neither constructs a financial-risk factor nor
implements the Gaussian d=2 penalized smoothing model. Run with
`python scripts/run_ciss_baselines.py` and record the output manifest under
ignored `results/runs/EXP-0002`. No inferential claims from this exploratory run.
