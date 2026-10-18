---
orphan: true
---

# Cross-agent integration checklist — QA review of 2026-10-18

**Status:** PROPOSED interfaces and integration gates; not an assertion that EXP-0001 has been executed. Cross-check every item against the code and the current journal before changing ownership. No production engine modifications are authorized by this document.

## Evidence and state

- [x] Reviewed `AGENTS.md`, journal reading order and latest 2026-10-17 BIS correction, handoff/state/decision index, `pyproject.toml`, relevant modules/tests and `.github/workflows/ci.yml`.
- [x] Existing train-only `fit_pca` / `fit_signed_composite` and forecast-error arithmetic APIs are public; vintage validation is **date-only**, not first-release verified; source hash audit is read-only.
- [x] Existing `market_features` keeps ECB CISS/FRED STLFSI4/NFCI as references, and `build_country_market_panel` joins exact trading dates with no automatic forward-fill.
- [ ] **Data agent:** define provenance schema, time-zone offset/close time, verified release date evidence and multi-vintage revision keys; mark unknown explicitly null.
- [ ] **Data agent:** separate raw downloaded **response** hash from archived CSV hash; preserve both when truly measured, plus derivative hash and unmodified source lineage.
- [ ] **Data agent:** obtain licensing verdict before any source or PDF enters Git; ensure synthetic test fixture distributions are invented and vendor-free.
- [ ] **Index agent:** factor feature allowlist based on `is_external_benchmark=False`; forbid CISS/STLFSI4/NFCI/IEMF in concordance input; if directly forecasting a benchmark, register a distinct target/experiment ID.
- [ ] **Index agent:** freeze schema feature order, units, directions, anchor, training origin, factor identity and scale; test the result against future-row perturbations.
- [ ] **Trend agent:** distinguish **filtering** `p(x_t | information through origin)` from retrospective smoothing. No two-sided/full-series state estimate may appear in pseudo-real-time scores.
- [ ] **Trend agent:** publish filtered covariance and fitted hyperparameters with training cutoff; use sparse/banded/state-space solves instead of dense inverse materialization when needed.
- [ ] **Forecaster agent:** define issue instant in UTC, horizon `h` unit, target date, nested CV cutoff, deterministic seed, predictive uncertainty and target identity.
- [ ] **Event/evaluation agent:** freeze signal threshold and calibration data before held-out evaluation; score only when realization is available; assess false alarms and benchmark independence.
- [ ] **Coordinator:** approve runtime dataclass/Protocol package path and major version; reconcile journal/hand-off conflicts before merge; require evidence for every “VERIFIED” label.

## Contract tests and how to run them

From a fresh clone **without any vendor data, credentials or network requests**:

```bash
python -m pip install -e ".[dev]"
python -m pytest -q tests/test_public_contracts.py
python -m pytest -q
ruff check .
python scripts/validate_research.py
sphinx-build -b html -W --keep-going docs docs/_build/html
python scripts/check_change_protocol.py --base-ref origin/main
```

The initial contract suite checks: public imports/exports; no reference stress indicators entering production market features; PCA sign and train-only scale; unavailable/future releases; strict calendar/UTC rejection; original-byte SHA256 audit; fixed random seed; and forecast-origin invariance using **synthetic local reference trend/forecast stubs**. The latter tests a design invariant, not an implemented production state-space model.

## Specific review findings / evidence

| Priority | Observed issue | Risk and proposed narrow action |
| --- | --- | --- |
| P0 | `data/vintages.py` requires non-null timezone-naive `available_date` while market downloads carry observation dates but no verified release instants | Do not label the current contract as publication-timestamp safe; approve new opt-in strict UTC adapter that rejects unknown release instants |
| P0 | `indices.fit_pca` takes a numeric matrix and `stress_anchor` position, without metadata or benchmark exclusion at its boundary | The model can accidentally receive external benchmarks; require an upstream metadata gate before the numeric fit |
| P0 | No public state/trend/forecaster/event-score engine API exists | Do not add misleading exports or check nonexistent classes; agree on Protocol shape first |
| P1 | `market_features` accepts equity close dates without verified international close times; `build_country_market_panel` aligns by session **date** only | Document descriptive status; prohibit same-day cross-market pseudo-real-time claims |
| P1 | `quality.inspect_source_file` compares SHA256 of saved CSV; `acquisition` can record additional response SHA | Clarify byte-domain and propagate original input hashes without altering raw snapshots |
| P1 | `docs/getting-started.md` uses 2026-10-17 end date and acquisition instructions predating BIS source additions; handoff includes historical, potentially contradictory status fragments | Date documentation explicitly; request data agent/coordinator to revise narrative rather than edit their owned files |
| P2 | ``src/latent_risk/__init__.py`` exports index functions only; subpackages separately export data/evaluation utilities | Public import works from submodules, but a universal "pipeline" API cannot be assumed; decide on versioned exports after approval |
| P2 | `.github/workflows/ci.yml` has one Ubuntu Python 3.11 job, no explicit wheel/sdist build check, no coverage reporting and no CI package matrix | Coordinator-approved isolated packaging job (Python 3.10–3.12) and wheel install smoke test; preserve current PR change-protocol gate |
| P2 | The only required developer extras are pip editable `data/dev/docs` in every CI run; no dependency caching or artifact reuse is configured | CI may spend time resolving providers even though tests use mocks; benchmark before optimizing; no hard performance numbers claimed |

**Numerical inverse audit:** GitHub default-branch code search on 2026-10-18 returned no matches for `np.linalg.inv`, `linalg.inv` or `pinv`. This is a *textual scan only*, **not** proof that no dense solve or equivalent operation exists. Any future penalized/trend implementation should be profiled and audited independently.

## PR acceptance gates

1. Run the full workflow on the **PR head SHA**, preserve Actions URL and exact pass/failure counts in the PR.
2. Pass all synthetic contracts **offline**. No condition may depend on `FRED_API_KEY`, `BANXICO_TOKEN`, user data/raw/downloads, or a vendor API.
3. Confirm benchmark exclusion on both source-to-feature and feature-to-index boundaries before claiming end-to-end enforcement.
4. Confirm historical publication-time proof or explicitly restrict conclusions to a **retrospective current-vintage** study.
5. Require target/version/release-aware reconciliation before scoring a factor from a different fit or vintage.
6. Approve any shared package/CI changes; do not modify another agent's source, merge, or force-push.
7. Preserve negative findings; integrate journal and handoff conflicts on coordinator-owned integration branch.

**Release decision:** Hold the research-pipeline v1 release until strict release-time handling, factor anchoring, end-to-end interfaces and calibration tests are implemented. Documentation and test-only QA can merge separately after review.
