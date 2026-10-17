# 2026-10-17 — Reassessing primary financial-stress indicators

**Date:** 2026-10-17 (America/Mexico_City)  
**Objective:** verify more economically relevant latent-financial-stress inputs rather than mechanically expand M1 and M2.

## Motivation
The user clarified M1/M2 were arbitrary examples, not privileged model predictors. The initial catalog mainly followed source availability rather than documented financial-stress measurement theory.

## Questions
Which input domains are supported by official stress indices? Which external observed stress references exist for Mexico, UK, US, euro area, Japan? Can a different source be downloaded within the existing auditable architecture?

## Work performed
Reviewed official OFR FSI components, ECB CISS construction and New CISS keys, Banxico IEMF 36-indicator methodology, BIS credit-gap/DSR evidence, FRED STLFSI4/NFCI data and the post-April-2026 three-year ICE OAS FRED constraint. Created `data/indicator_priorities.md` with a ranked source/transform/benchmark plan and `ADR-0005` (proposed, not adopted). Added three daily ECB CISS series for EA/USA/GBR to the catalog as `external_stress_benchmark`; added FRED `STLFSI4` and `NFCI` as external reference only. Extended `parse_ecb_csv` for daily and monthly series while retaining strict frequency/key validation. Updated period-bound query construction for daily ECB sources. Added two parser tests and updated all source count expectations. Updated journal-first handoff, context, EXP-0001, and acquisition docs.

## Reasoning
Market price volatility/losses, FX shifts, funding spreads, credit risk premia and bank financial-sector strain directly operationalize contemporaneous stress. Monetary quantity levels are not conceptually equivalent. BIS credit/debt variables fit a slower vulnerability/horizon target. IEMF and CISS are not independent forecast outcomes when they share raw input categories with our index. CISS 3-country coverage is not 5-country coverage.

## Implementation
A source downloader can now retrieve the three daily CISS series with the existing `--sources ecb` command. ECB monthly queries remain monthly. No new Mexican IEMF scraper or Japan stress indicator has been invented. FRED remains blocked on VM until network resolved.

## Experiments and outcomes
**No historical financial data were retrieved by the assistant, no new factor fitted, and no experimental performance claims.** Official series and their currently documented data-provider pages were verified; actual VM series availability requires a manifest.

## Failures and alternatives
An M1/M2-first factor was rejected as an unexamined default; monetary series remain candidates for slower macro context. A 2008–2026 US HY spread from FRED was not added as a long-range input because the ICE source now restricts FRED downloads to approximately three years from April 2026.

## Limitations
Bank and credit/funding sources for all five countries remain missing or uncertain. Published stress references can be revised or reestimated. Dates of observation are not dates of release. The data definition, weekly vs monthly sampling and outcome should be fixed before forecasting. No proof of a superior indicator family from this theoretical/source review alone.

## Validation
Repository automated pytest, lint, structural and Sphinx checks run on this change's GitHub Actions workflow. Live ECB historical data retrieval is not executed in CI; report CI final result separately in completion status.

## Supported conclusion
The market-stress-first feature selection is better motivated by existing institutional indices, and explicit external CISS data sources are now registered. This supports an empirical candidate design, **not an empirical result**.

## Next steps
Pull GitHub changes, download ECB CISS/BSI records, run coverage audit, obtain Banxico IEMF source table and inspect exposure of published series to retrospective reconstruction. Verify sovereign/credit/funding market source coverage before freezing an index specification.
