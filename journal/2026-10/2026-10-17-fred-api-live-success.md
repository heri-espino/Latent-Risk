# 2026-10-17 — Official FRED API succeeds on user's VM

**Date:** 2026-10-17 (America/Mexico_City)  
**Objective:** record verified-by-user FRED API transport, source coverage improvement, and relevant next experimental priorities.

## Context and motivation
FRED website Graph CSV timed out or closed connections on all 12 codes. A separate opt-in official API backend had passed 34 offline tests. The user tested the VM's API hostname and executed the API-only 4-code probe successfully.

## Questions investigated
Does the alternate official endpoint work on the user's VM? Which series and time spans were actually returned? Do remaining missing FRED money/reserves codes block the research goal?

## Work performed
Transcribed the user's CLI success lines and five-manifest audit to `data/audits/2026-10-17-fred-api-live-success.md`, retaining the earlier four-manifest failure evidence. Updated this journal, `journal/LATEST.md`, `AI_HANDOFF.md`, `context/STATE.md`, `context/NEXT_STEPS.md`, and documentation.

## Exact output and evidence
- `Test-NetConnection api.stlouisfed.org -Port 443`: `TcpTestSucceeded: True`.
- `python scripts/download_data.py --start 2000-01-01 --end 2026-10-17 --sources fred --fred-backend api --only DGS2,DGS10,STLFSI4,NFCI`: `4/4 downloaded`.
- `DGS2`, `DGS10`: 6,700 observations each, 2000-01-03 to 2026-10-15.
- `STLFSI4`, `NFCI`: 1,397 observations each, 2000-01-07 to 2026-10-09.
- Snapshot `20261017T235600038504Z`, user VM only; 5-manifest combined audit: **26 OK, 8 FAILED, 6 NEVER_REQUESTED**, catalog size 40.

## Mathematical reasoning
Data access is separate from a research-valid target. Treasury yields need transformations and matched cross-country sources. Published STLFSI4/NFCI benchmark histories (possible revised reconstructions) are neither 2008 point-in-time information nor independent of their own input components. A smaller market-risk factor can support a methodological smoke test while systemic financial-stress claims require multiple conceptually distinct risk domains.

## Implemented vs proposed
The official API code already existed; **no algorithm implementation in this session**. This change records successful real VM acquisition and updates handoff. Preliminary market/CISS forecasting and source-revision audit remain **PROPOSED, NOT EXECUTED**.

## Unexpected results
The alternative `api.stlouisfed.org` hostname completed every selected request, while `fred.stlouisfed.org` Graph CSV consistently failed. Cause of host-specific difference remains unknown (network/routing/policy/endpoint behavior).

## Failures and alternatives
Eight money/reserves FRED IDs remain recorded FAILED solely because of historic Graph CSV attempts; no API attempt exists for them. Re-requesting all codes is not necessary to advance market-based financial-stress estimation, but a restricted API retry can close those gaps if macro context is needed.

## Limitations and uncertainties
The assistant has not inspected VM source CSVs, manifests, SHA256 or internal data quality. Market-source semantic validations, licenses, revision vintages, publication delays and experimental performance remain outstanding. User API key not disclosed or stored.

## Files changed
`data/audits/2026-10-17-fred-api-live-success.md`, this entry, `journal/LATEST.md`, `AI_HANDOFF.md`, `context/STATE.md`, `context/NEXT_STEPS.md`, `data/README.md`.

## Validation commands and results
Source code unchanged; prior `34 passed` offline tests, Ruff, Sphinx and validator on commit `3ccdefb5503edb5e83be883c08b2267cbdf6335b` (GitHub Actions 39080170718). Final journal-only commit CI result should be verified; local VM live provider evidence is user-reported as above.

## Supported conclusions
The official FRED API transport is operational on the user's current VM for 4/4 selected benchmark and yield series. A repeatable acquisition mechanism exists. This is *not* financial risk-model validation.

## Next steps
Audit input transformations and leakage; use current market data and held-out CISS/US stress benchmarks for descriptive pilot. Preserve FRED API provenance, separate current-vintage retrospective from real-time experimental claims. Optionally collect eight money/reserves FRED IDs using API backend.
