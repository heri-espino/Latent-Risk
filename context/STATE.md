# Research state (2026-10-16)

**Status:** `IMPLEMENTED` baseline source-package infrastructure; CI `VERIFIED COMPUTATIONALLY` on commit `075f9027` (12 tests, Ruff, validator, Sphinx pass: https://github.com/heri-espino/Latent-Risk/actions/runs/38994859776). The international empirical evaluation remains `PROPOSED`, not completed.

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
