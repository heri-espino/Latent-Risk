# 2026-10-17 — Official provider expansion and cross-snapshot audit

**Date:** 2026-10-17 (America/Mexico_City)  
**Objective:** add a documented path to fill missing macro sources after a reported Banxico VM run, without pretending an international panel is complete.

## Motivation
The first source downloader covered market, FRED and three Banxico series; ten FRED VM requests failed with `ConnectionError`. The user reports succeeding with a Banxico token, but has not shared a manifest. Current Mexico M1/M2, Euro monetary aggregates, UK money data and Japanese monetary data were absent.

## Questions
What official country series and programmatic access syntax are verifiable? Can we avoid the false inference that period-labeled money stocks were available within their month? How do we report individual successes accumulated across separate raw-source snapshots?

## Work performed
- Researched ECB SDMX data API and exact published keys for seasonally adjusted euro-area M1 and M2 stocks.
- Researched Bank of England IADB CSV endpoint and identified sterling monthly M4 (`LPMAUYN`) and SONIA (`IUDSOIA`).
- Researched Bank of Japan's new 2026 time series API and monthly M1/M2 data codes `MD02'MAM1NAM3M1MO` and `MD02'MAM1NAM2M2MO`.
- Corroborated Banxico modern M1 `SF311408` and M2 `SF311418` across open SIE client examples and the official monetary aggregate definition, then added those two IDs to the catalog.
- Implemented `src/latent_risk/data/official.py` with strict parse/identity/period/finiteness validation and integrated `ecb`, `boe`, and `boj` source switches into `src/latent_risk/data/acquisition.py`.
- Added `tests/test_official.py` and `scripts/audit_downloads.py` plus `tests/test_data_audit.py`. Updated package documentation and metadata/handoff.

## Files changed
`data/source_catalog.json`, `src/latent_risk/data/official.py`, `src/latent_risk/data/acquisition.py`, `scripts/audit_downloads.py`, `tests/test_official.py`, `tests/test_data_audit.py`, `README.md`, `data/README.md`, `docs/getting-started.md`, `experiments/EXP-0001.md`, `journal/LATEST.md`, this dated journal, `journal/decisions/ADR-0004.md`, `AI_HANDOFF.md`, `context/STATE.md`, `context/NEXT_STEPS.md` and `context/DECISION_INDEX.md`.

## Reasoning
Price-return shocks, nominal money levels and term structures are not automatically commensurate index inputs. British M4 differs from euro-area, Japanese and US M2. ECB monetary series have a changing geographic composition. Monthly period labels are not release dates. These measurements require explicit units, transformations, release lags and common forecast origin constraints.

## Design decisions
Source-specific API parsers fail clearly when HTML/error payloads or wrong series IDs arrive. BOJ responses can return HTTP 200 with logical `STATUS` errors and are checked. Cross-snapshot audit preserves earlier successful source data even if a later retry fails; it labels never requested codes separately. No raw downloads or tokens are uploaded to Git.

## Experiments and outcomes
No financial model was fitted and no historical event was tested. The user's Banxico download status is reported but its manifest has not been supplied. All network requests to the newly added provider API endpoints are `UNVERIFIED` until the user runs the VM collection. Data tests are synthetic and offline.

## Unexpected results and failures
The first test-enhancement CI run reported only an import sorting issue in `tests/test_official.py`; corrected. FRED access failures remain unresolved. Real-provider CSV/JSON format changes may still cause explicit per-series errors.

## Alternatives
Reinterpreting BoE M4 as M2 or interpolating monthly publications to observation months would introduce unjustified comparability and lookahead. Using only FRED would prevent continuing the international pilot in the face of VM connectivity failures.

## Limitations
User's Banxico manifest unknown; no live new provider coverage verified. Provider data may contain retrospective revisions. Needs official vintage calendars, yields beyond US, external validation target, transformation policy and cross-country source comparability audit.

## Validation
Automated tests, Ruff, structural research validator and Sphinx documentation run through GitHub Actions for the last source commit. Record final checks in a follow-up correction if CI has not completed by this journal commit. First tests prior to import formatting had passing unit tests but Ruff import sorting failure. No live-data and no scientific experiment command was executed.

## Supported conclusions
Official candidate source catalog and independent source parsers are implemented with an auditable local coverage report; complete real-time comparable country histories and forecasting efficacy remain unestablished.

## Next steps
Run `git pull --ff-only origin main` and `python scripts/download_data.py --sources ecb,boe,boj --start 2000-01-01 --end 2026-10-17` in activated `latent-risk`; rerun Banxico privately for M1/M2; run `python scripts/audit_downloads.py`. Diagnose FRED network and audit historical release dates before selecting comparable model covariates.
