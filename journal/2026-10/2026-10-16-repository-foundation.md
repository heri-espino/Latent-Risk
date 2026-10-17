# 2026-10-16 — Initial Latent-Risk repository architecture

**Date:** 2026-10-16  
**Objective:** establish an AI-resumable scientific repository for comparative financial-risk forecasts.

## Context and motivation
A previous U.S.-focused project found large differences between an old 2008 validation and test period but contained retrospective DFM parameter estimation and model-selection limitations. To avoid conflating smoothing theory with the financial application, the user requested a new empty `Latent-Risk` repository using an installable `src/` architecture and an explicit AI research handoff.

## Questions investigated
How can the financial-risk index, MLE smoothing, and event-based assessment remain independent? What minimal usable code should an empty project contain? Which evidence from the old project must not be treated as verified new results?

## Work performed
Created the initial architecture, modular library entrypoints and validation scaffolding, an Obsidian-compatible notes vault, literature registry, experiment protocol, and a results-free LaTeX article. The exact set of repository files is determined by the bootstrap commit, not by this prose summary.

## Mathematical reasoning
A Gaussian second-difference random-walk trend supports a PLS penalty proportional to the measurement-to-trend innovation variance ratio under suitable diffuse initialization. MLE applies to the marginal observed-data likelihood; do not maximize over unobserved trend states without integrating them out.

## Implementation decisions
A small training-only signed composite and PCA implementation can serve as an explicit reproducible benchmark. The DFM, MLE smoother, and country panel should be separate modules developed after a real data-vintage audit. See ADR-0001 and ADR-0002.

## Experiments and outcomes
No international dataset downloaded, no international forecast experiment executed, and no crisis detection result established. The experiment protocol EXP-0001 is `PROPOSED`, not run.

## Unexpected results
None claimed from new scientific computations. Initial repository was empty.

## Failed approaches and why
No new scientific algorithm attempt failed in this bootstrap. Previously identified legacy issues include future-informed DFM parameters and an inconsistent smoothness candidate selection.

## Alternative hypotheses
A forecast exceedance might arise from variance changes, heavy-tailed errors, factor measurement instability, misspecified persistence or true regime changes. These alternatives are not distinguished yet.

## Limitations and uncertainties
Data coverage, release-calendar accuracy, factor anchor comparability, potential outlier effects, model likelihood specification, and final author list remain unresolved.

## Validation commands and results
Planned post-commit checks: `python -m pytest`, `ruff check .`, `python scripts/validate_research.py`, and `sphinx-build -b html docs docs/_build/html`. These are **not asserted to have passed** merely by creating files; inspect CI or a later validation entry.

## Supported conclusions
The prior U.S. application motivates a separate international assessment; no predictive advantage, detection success or cross-country comparability has been verified.

## Next steps
Run source/structure verification; assemble Mexico/U.S. point-in-time panel; then implement and test the MLE-based smoother and pseudo-real-time evaluation.
