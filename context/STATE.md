# Research state (2026-10-17)

**Status:** `IMPLEMENTED` baseline source-package infrastructure; CI `VERIFIED COMPUTATIONALLY` on commit `075f9027` (12 tests, Ruff, validator, Sphinx pass: https://github.com/heri-espino/Latent-Risk/actions/runs/38994859776). The international empirical evaluation remains `PROPOSED`, not completed.

## Initial data collection (2026-10-16)
`IMPLEMENTED` source acquisition module: 14 daily Yahoo market tickers, 10 FRED macro/financial series and three optional Banxico token-based series in `data/source_catalog.json`. Local isolated UTC snapshots under `data/raw/downloads/` include CSVs, hashes, historical-coverage ranges and failures. `VERIFIED COMPUTATIONALLY`: 19 offline tests, Ruff, structure and Sphinx pass on `8fb85d0` (https://github.com/heri-espino/Latent-Risk/actions/runs/38998827014). **No live download has been run**, so coverage and actual provider success are `UNKNOWN`.

FRED is current revised history, **not** available-date vintage history. No release dates have been fabricated. The old Mexico M2 FRED code `MYAGM2MXM189N` ends in 2017. Current Mexican M1/M2 and other country monetary aggregates require audited official identifiers. Neither the point-in-time balanced panel nor EXP-0001 exists as completed empirical results.

## Official-source expansion (2026-10-17)
`IMPLEMENTED` additional candidate source series: ECB M1/M2, BoE sterling M4/SONIA, BOJ M1/M2, modern Banxico M1/M2 (codes `SF311408`/`SF311418`). Retrieval uses source-specific CSV/JSON parsers and independently stored raw snapshots; `scripts/audit_downloads.py` combines status evidence across snapshots. New-provider HTTP requests have not been executed by assistant, and the user reports Banxico ran before these two codes were added. Full manifests have not yet been provided. All FRED downloads previously failed from the VM with HTTPS `ConnectionError`; no claim of complete US macro coverage is justified. ECB euro area changes composition; BoE M4 != US/ECB M2. Historical availability and real-time data vintages remain `UNKNOWN`.

## Indicator domain reprioritization (2026-10-17)
The user clarified that M1/M2 were examples, not preferred core predictors. Per `data/indicator_priorities.md` and `ADR-0005` (proposed), prioritize directly market-based stress observables and distinguish slower credit/balance-sheet vulnerability indicators. Exact validated published external references: Banxico IEMF (36 variables, six financial-market domains), ECB daily new CISS for UK/US/EA; STLFSI4 and NFCI are US reference candidates. They are **not** model input data for a concordance experiment. ECB CISS source keys now in downloader. Source coverage in Japan remains a gap. US ICE corporate spreads FRED limit to three-year history since Apr 2026; cannot reconstruct 2008 with FRED now.

## Research question
When and why do forecasts based on smoothed country financial-risk indices fail during financial disturbances? Are unusually large forecast errors informative beyond volatility changes and conventional benchmarks?

## What counts as risk?
There is no observed universal scalar risk series. The index is a model-based measurement: (a) signed standardized composites, (b) PCA, (c) dynamic factors, and later robust or regime-specific versions. Factor signs and scale conventions must be frozen from training vintages. A smaller forecast RMSE for one index does not establish that it is the better index because targets differ.

## Role of smoothing
The baseline proposed smoother is the Gaussian integrated random walk with a second-difference trend penalty and ratio `lambda = measurement_noise_variance / trend_second_difference_variance`, estimated by marginal likelihood. It is a method for forecasting a chosen index, not a substitute for the index itself.

## Two distinct experiments
1. **Retrospective** DFM/index built with full historical sample: description only.
2. **Pseudo-real-time** factor fitting, normalization, drift/tuning, and calibration restricted to publication-date information available by forecast origin: primary forecasting evidence.

## Pilot scope
Mexico, USA, UK, Japan, euro area; monthly data where market and monetary data can be matched with release dates. Proposed horizons 1, 3, 6 months; source availability and feasible start dates unconfirmed. Mexican 1994–95 crisis requires separate older-source data. Include quiet controls and the 2008–09, 2011–12, 2020, 2022 and 2023 event candidates when feasible.

## Legacy project findings (not replicated here)
The old U.S. DFM input series were logged VIX, WTI, GLD and DXY. The run used 2004–2026 full-sample DFM fitting before performing a 2008 train/validation/test analysis: this is **ex-post factor definition**, not pseudo-real-time measurement. Saved Gaussian DFM diagnostics did not pass. Its best refined validation candidate differed from the selected grid minimum. Historical 2008 validation RMSE ~1.92 and June–Dec test RMSE ~30.10 are motivation, not conclusive crisis prediction.

## Constraints
- Do not copy the earlier project's risk manuscript and label it as new original results.
- Preserve citation and joint-author contribution issues from original U.S. poster.
- No country-indicator dataset has been validated for real-time historical availability.
- Do not declare an event detector operational until false-alarm rates, calibration and matched controls exist.

## Linked prior resources
- Legacy risk project: https://github.com/heri-espino/Estimation-of-latent-risk-in-the-U.S.-market-using-representative-variables
- Smoothing-methods theory: https://github.com/heri-espino/Trend-Estimation
