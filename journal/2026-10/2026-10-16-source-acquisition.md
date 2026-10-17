# 2026-10-16 — Initial raw data downloader for Conda VM

**Date:** 2026-10-16 (America/Mexico_City)  
**Objective:** provide an executable PowerShell+Conda workflow to acquire the initial cross-country financial and macro source series.

## Context and motivation
An installable source package existed, but no historical source downloader. The user requested one complete PowerShell command sequence to fetch all the initial candidate data on a Windows Conda VM.

## Questions investigated
Which market and macro series have verifiable identifiers? How should release-date leakage be prevented? How to keep source data from silently becoming research findings?

## Work performed
- Added `data/source_catalog.json` with **14 Yahoo Finance market series**, **10 FRED financial/macro series**, and **3 optional Banxico SIE series**.
- Added `src/latent_risk/data/acquisition.py`, CLI entrypoint `scripts/download_data.py`, and seven new offline tests.
- Implemented per-run UTC timestamped local CSV snapshots with manifest containing sources, actual coverage, SHA256, errors and explicit vintage caveats. The CLI returns nonzero when a requested series fails.
- Added optional `BANXICO_TOKEN` environment-header access; token is never written to a file.
- Updated package `data` optional dependencies, GitHub CI, README, docs, acquisition instructions and EXP-0001 references.
- Repaired Ruff import formatting.

## Mathematical reasoning
Observation date and availability date differ for monetary data. FRED Graph CSV returns a revised history, not historical point-in-time vintages. No fabricated `available_date` is attached to macro observations. The downloaded raw sources remain distinct from the regression-ready empirical panel, per ADR-0003.

## Implementation decisions
Each provider series is fetched separately to make missing coverage and individual network failures visible; a snapshot is not silently overwritten. Yahoo daily prices are stored with the dated market observation and without invented release metadata. The old Mexico M2 FRED series ends in 2017 and is marked as legacy.

## Experiments and outcomes
No real source has been downloaded by the assistant and **no international scientific experiment has been run**. The independent unit tests are entirely synthetic/in-memory.

## Unexpected results
The CI linter enforced exact module-import grouping; this was repaired. The recorded passing validation on `8fb85d0` included three nonfatal invalid-escape Python warnings in docstrings, which this commit removes.

## Failed approaches
Earlier CI pushes failed Ruff import-order rules; their Actions logs remain available and are not overwritten.

## Alternative hypotheses
Yahoo ticker sources may have unexpectedly short coverage, FRED series may be discontinued or blocked, and tokenized Banxico calls may fail or change. Each is recorded in `manifest.json` rather than treated as a complete dataset.

## Limitations and uncertainties
Current Mexico M1/M2 under modern definitions and comparable macro panels for UK/Japan/euro area are not yet downloaded. Country interest-rate spreads, truly historic release dates, source licenses and economic comparability remain unverified. No downloaded series may be represented as point-in-time real-time historical information.

## Validation commands and results
On source commit `8fb85d0`: `python -m pytest -q` **19 passed**, `ruff check .` **pass**, `python scripts/validate_research.py` **pass**, `sphinx-build -b html -W --keep-going docs docs/_build/html` **pass**. Evidence: https://github.com/heri-espino/Latent-Risk/actions/runs/38998827014. The user's VM live download and internet retrieval are **not yet tested**.

## Supported conclusions
An auditable source-acquisition command now exists and passes offline quality checks. Historical data availability and real-time forecasting validity are not established.

## Next steps
Run the downloader on the user's Conda VM; inspect the per-series manifest and communicate missing series; identify Banxico M1/M2 and audited release-date metadata; later build a transformation/feature panel with frozen forecasts and conventional baseline comparisons.
