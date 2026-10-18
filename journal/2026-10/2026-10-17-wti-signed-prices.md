# 2026-10-17 — Oil futures negative-price integrity gate correction

**Date:** 2026-10-17 (America/Mexico_City)  
**Objective:** fix a false-positive market-source integrity validation failure without concealing potentially genuine futures price observations.

## Motivation and question
User ran `python scripts/audit_source_quality.py` in their VM. Its output listed 33 source series PASS and `CL=F` FAIL out of 34 downloaded sources. The error was strictly about nonpositive market close prices. Is this necessarily invalid data, or an inappropriate price-domain assumption for a physically deliverable futures contract?

## Work performed
1. Verified primary institutional evidence: CFTC 2020 staff reporting and EIA 2020 report document the NYMEX May WTI futures contract closing at −$37.63/b on April 20, 2020.
2. Updated `data/source_catalog.json` so `CL=F` explicitly has `price_domain="signed"`; all other market series continue to default to `strictly_positive`.
3. Updated `src/latent_risk/data/quality.py` to permit finite, nonpositive closes **only when explicitly designated signed**; produce warning, nonpositive close count/first dates/minimum value and date, while preserving all hash, date, row-count and finite-value checks.
4. Added narrow historical compatibility for existing immutable raw manifest records with `id=CL=F` and `role=global_oil`, without changing the original snapshot or manifest.
5. Added synthetic tests for legacy WTI futures record, negative/zero closes, negative unmarked equities, invalid price domains, and retention of other failures.
6. Recorded the user-supplied audit result in `data/audits/2026-10-17-source-quality-wti.md` and updated data docs, handoff, state, next steps, decision index, and proposed experimental precautions.

## Exact source evidence
- User reported 33 PASS and 1 FAIL (`CL=F`, 6,566 rows). The sole reason printed: `market close prices must be strictly positive`.
- Institutional source: https://www.cftc.gov/PressRoom/PressReleases/8315-20
- Supplemental source: https://www.eia.gov/TODAYINENERGY/detail.php?id=43495

## Interpretation and mathematical consequences
Negative values are theoretically and historically valid on WTI futures; this does not ensure the vendor's particular nonpositive observations coincide with the historical settlement event. Ordinary real log returns are undefined when the price ratio is nonpositive and log price levels require positive values. Replacing negative price with an absolute value changes economic meaning; dropping the historical event biases crisis-period measurements. Use carefully specified signed price differences or predeclared transforms, and audit back-adjustments/contract rolls before using WTI as a control.

## Rejected alternatives
- Modify/delete negative rows to force positivity: rejected as destructive and inconsistent with 2020 market history.
- Allow negative close values for every equity/FX symbol: rejected; preserve strict positivity unless a source explicitly defines a signed market price domain.
- Auto-mark negative WTI records fully clean without a warning: rejected; physical price semantics and continuous-series construction still demand inspection.

## Experiments/results
No numerical forecasting model has been fitted. No user WTI observation dates/values have been inspected in this session; the updated VM re-audit remains outstanding. The update changes the integrity checker and model feature constraints, **not** the downloaded data.

## Validation
Synthetic tests and CI checks run on GitHub for the implemented code revision, with exact CI outcome recorded in the response; no live VM rerun performed by assistant.

## Limitations
Signed price acceptance is limited to instrument metadata and a narrowly scoped historical WTI fallback. Extreme returns, roll conventions, adjustments and actual historical publication/vintage are not automatically validated.

## Files changed
`data/source_catalog.json`, `src/latent_risk/data/quality.py`, `tests/test_source_quality.py`, `data/audits/2026-10-17-source-quality-wti.md`, `journal/2026-10/2026-10-17-wti-signed-prices.md`, `journal/LATEST.md`, `journal/decisions/ADR-0006.md`, `context/DECISION_INDEX.md`, `AI_HANDOFF.md`, `context/STATE.md`, `context/NEXT_STEPS.md`, `data/README.md`, `data/indicator_priorities.md`, and `experiments/EXP-0001.md`.

## Next steps
VM: pull updated GitHub files and rerun `python scripts/audit_source_quality.py`; inspect WTI warnings and minimum date in `results/runs/source_quality/report.json`. Complete scientific market-date and contract-roll audit before including oil in index or event forecasting.
