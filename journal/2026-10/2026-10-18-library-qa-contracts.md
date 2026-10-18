# 2026-10-18 — Library boundary contracts and independent synthetic QA

**Date:** 2026-10-18 (America/Mexico_City)  
**Branch/owner:** `agent/library-qa-contracts` / independent release QA  
**Objective:** document interoperable non-leaky feature→factor→state→forecast→event-score contracts and exercise existing public boundaries without changing another agent's numerical or acquisition engines.

## Motivation and questions

The existing package supports acquisition/audit, train-only PCA/composite scores, date-vintage filtering and standardized-error arithmetic. It does not implement a unified one-sided trend/forecaster/event scorer or strict historical UTC availability times. What exact contracts would let independent agents integrate without accidentally claiming current-vintage retrospection is genuine real-time forecasting? Can we catch critical leaks with synthetic tests and no vendor files?

## Work performed and reasoning

- Followed mandatory reading sequence (`AGENTS.md`; `journal/README.md`; `journal/LATEST.md`; linked 2026-10-17 BIS correction; `AI_HANDOFF.md`; `context/STATE.md`; `context/NEXT_STEPS.md`; `context/DECISION_INDEX.md`), then `pyproject.toml`, `scripts/validate_research.py` / `check_change_protocol.py`, code modules, tests, documentation and CI workflow.
- Created `docs/architecture/interfaces.md`: proposal for a versioned country/source-level metadata contract; UTC-aware verified availability timestamp is nullable (not guessed), observation date is separate from unverified intraday event time, raw snapshot lineage and derivative hashes are separate, missing values are explicit, external benchmarks have an exclusion flag. State/trend/forecast/event protocols remain proposals.
- Created `docs/architecture/integration_checklist.md`: cross-agent approval gates, retrospective-vs-pseudo-real-time restrictions, release decision, and ordered tests.
- Created `tests/test_public_contracts.py` using invented synthetic data and existing exports (`data.available_as_of`, `market_features.build_country_market_panel`, `quality.inspect_source_file`, `indices`, `evaluation`). Assertions cover benchmark noninclusion in current market pilot, PCA anchored training scale, dated releases, absent release rejection, exact calendar matching, timezone rejection, immutable-source SHA256 checking, fixed RNG seed, and future extension invariance. A test-local causal EWMA/forecast stub only checks proposed composability; it does NOT test an unimplemented numerical engine.
- Textually searched the default branch for `np.linalg.inv`, `linalg.inv` and `pinv`: no matches; not a complete numerical audit. Observed that `docs/getting-started.md` still carries an earlier acquisition date and main API does not export trend or event classes.
- Deliberately **not modified:** data/index/trend/evaluation numerical engines; `pyproject.toml` and GitHub CI workflow pending coordinator approval; any raw market/vendor data or licensed literature.

## Findings, alternatives, uncertainty

- **IMPLEMENTED** existing date-level vintage selection checks a supplied date but cannot verify its historical truth; a proposed separate UTC adapter must exclude unknown release instants from strict real-time estimation.
- **IMPLEMENTED** `market_features` excludes external CISS/FRED inputs by source mapping; generic numeric `fit_pca` itself does not consume metadata and therefore cannot independently enforce this policy. A feature-batch gate is **PROPOSED**, not fully enforced.
- **PROPOSED** frozen/versioned factor ID, anchor/sign/scale alignment, causal filtered state, forecast issue/horizon/realization, and calibrated event score.
- **UNKNOWN**: historical first-release vintages, cross-country session close clocks, numerical one-sided trend correctness, cross-agent interface agreement, predictive validity of any event score.
- Rejected giant refactor, pretending retrospective smoothers are filters, filling missing release dates with source observation dates, distributing raw provider observations, and installing new public exports without coordination.

## Exact changed files

- `docs/architecture/interfaces.md` (new)
- `docs/architecture/integration_checklist.md` (new)
- `tests/test_public_contracts.py` (new)
- `journal/2026-10/2026-10-18-library-qa-contracts.md` (new)
- `journal/LATEST.md`, `AI_HANDOFF.md`, `context/STATE.md`, `context/NEXT_STEPS.md` (minimal branch-local change-protocol updates; integrator must reconcile if parallel research work advances)

## Tests and reproducibility

Synthetic, vendor-free test command: `python -m pytest -q tests/test_public_contracts.py`. Required full checks: `python -m pytest -q`; `ruff check .`; `python scripts/validate_research.py`; `sphinx-build -b html -W --keep-going docs docs/_build/html`; `python scripts/check_change_protocol.py --base-ref origin/main`. **Status when first authored:** results pending GitHub PR CI, no results asserted. CI's sole matrix is Ubuntu/Python 3.11, and the workflow installs all optional data dependencies. No wall-time or bottleneck measurements claimed.

## Supported conclusions and next steps

Documentation and tests provide an integration proposal, not proof of model predictiveness. Independent agents must agree on release-timestamp and factor-target semantics before production integration. Run CI against exact PR head, record any failures and remediation, seek coordinator approval on shared exports/adapters/CI upgrades, preserve other agents' ownership, and leave the PR as draft. Do not merge.
