# Experiment registry

Experiments use stable IDs `EXP-####`, each with a prose protocol in `experiments/EXP-####.md` and machine configuration in `experiments/configs/`. Their outputs belong in `results/runs/<experiment-id>/` (usually gitignored); attach metadata with data vintage, code revision, exact settings and validation/confirmation labels.

**EXP-0001 is proposed and unrun.** Do not generate tables or claim empirical significance until a frozen protocol and logged execution exist.

Scientific isolation:
1. Index measurement: transparent signed average, PCA, Gaussian DFM; conditional robustness methods only later.
2. Smoother: Gaussian constrained local-linear trend; choose variance ratio by **marginal likelihood**, implementation pending.
3. Evaluation: retrospective reconstruction for description; pseudo-real-time with actual release dates for claims of predictive ability.
4. Score against predeclared external observable outcomes for direct between-index comparability.

Record unsuccessful runs and diagnostic failures, including factors violating residual tests.
