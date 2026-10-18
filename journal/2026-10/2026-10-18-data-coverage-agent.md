# 2026-10-18 — Data acquisition branch: BIS provenance and coverage

**Date:** 2026-10-18, America/Mexico_City
**Branch:** `agent/data-bis-and-coverage`
**Objective:** continue the data acquisition assignment without repeating previously successful downloads or altering the research model.

## Motivation and questions
The first BIS live attempt failed 0/5; a prior main-branch correction permits explicitly missing SDMX observation rows but had only synthetic validation. How can the next VM retry distinguish legitimate missing cells from malformed values and produce strict, independently verifiable observation coverage without publishing source payloads?

## Exact work
1. Read `AGENTS.md`, journal README/LATEST/linked dated entry, AI_HANDOFF, context STATE/NEXT_STEPS/DECISION_INDEX in that order, then existing BIS, acquisition, QA, catalog and audit code. Reconciled the historical VM failure with main's corrected parser and 88-pass historical CI.
2. Found no existing `agent/data-bis-and-coverage` branch or draft PR; created branch from main, leaving main untouched.
3. Added `src/latent_risk/data/coverage.py` and `scripts/audit_source_coverage.py`: read-only per-catalog-source integrity-gated local manifest coverage, strict failed-file status, exact observed date spans and years/counts, hashes, declared units/frequency/dataset version and null release-time provenance.
4. Added bounded `summarize_bis_payload` diagnostics to `src/latent_risk/data/bis.py` and propagated raw response SHA256 **on parsing failures** in `src/latent_risk/data/acquisition.py`; do not write rejected raw vendor CSV. Existing permissive missing whitelist was not further loosened.
5. Added offline `tests/test_source_coverage.py` and cases to `tests/test_bis_eer.py`, including old-success/new-failure preservation, hash tampering, malformed manifest, missing-versus-malformed diagnosis, and rejected response hash.
6. Documented safe commands in `data/README.md`, source/coverage/licensing evidence and short candidate queue in `data/audits/2026-10-18-data-agent-status.md`, and a coordinator-gated `data/provider_metadata_contract.proposed.json`.

## Scientific evidence, failed attempts and limits
- **USER-REPORTED LIVE VM (previous session):** 34/34 successfully acquired source files passed integrity, one legitimate signed WTI warning; market panel 31,383 rows; 4,293 common equity dates; 23,785 held-out reference observations. Do not call those newly rerun.
- **USER-REPORTED LIVE VM (previous session):** original BIS 0/5, all missing/nonfinite parser failure; no raw payload bytes in the repo. Existing first-failure manifests remain immutable.
- **IMPLEMENTED before this branch / prior CI VERIFIED:** corrected BIS parser with explicit missing rows, 88 total tests on previous commit. No actual successful BIS retry has yet been seen.
- **PUBLIC PROVIDER METADATA:** BIS MX portal documents series 1996-04-11 to 2026-10-06 as of its retrieved portal record; exact current spans for US/UK/JP/EA are still UNKNOWN until a live saved-file audit. This is not downloaded VM file coverage.
- **PROPOSED:** provider metadata contract, candidates BAA10YM / SOFR, historical discontinued TEDRATE for sensitivity; no mass download, no statistical model.

## Tests and reproducibility
The new tests are synthetic only. Run `python -m pytest`, `ruff check .`, `python scripts/validate_research.py`, `python scripts/check_change_protocol.py --base-ref main` and `sphinx-build -b html docs docs/_build/html` in CI or cloned VM environment. **Do not state new test passes until results have actually been observed.** Local execution of full repo suite not possible in this tool environment because a full checked-out repository and VM-held source data are inaccessible.

## Alternatives and tradeoffs
Rejected: silently imputing missing BIS observations; trusting manifests without reading CSV/hash; fabricating provider availability dates; adding credit series blindly; publishing raw BIS responses; modifying the index/forecasting packages or prior source snapshots. The result is intentionally an auditing layer, not a complete financial-risk dataset.

## Next actions
Review draft PR without merging, inspect CI for any failures, and on the user's VM retry only `--sources bis`, followed by `audit_source_coverage.py` and `audit_source_quality.py`. Compare raw response hashes/counts if failures persist. Resolve metadata contract and new credit/funding source licensing with the coordinator before changing shared schema/catalog. Missing actual release-time vintages remain **UNKNOWN**.

## Supported conclusion
Code and documentation implement a strictly limited acquisition audit workflow. This does **not** establish that any BIS series has successfully downloaded, that a complete real-time panel exists or that forecast departures identify disturbances.
