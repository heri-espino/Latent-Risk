# 2026-10-17 — Derived market-feature pilot prepared on user VM

**Evidence:** User-provided output from `python scripts/build_market_pilot.py`, saved output files and actual manifest bytes NOT independently reviewed by assistant.

## VM output (confirmed by user CLI)

```text
[OK] country_market_features.csv: 31383 rows, 2000-03-30 to 2026-10-16
[OK] five_country_common_equity_dates.csv: 4293 rows, 2007-07-05 to 2026-10-16
[OK] external_stress_references.csv: 23785 rows, 2000-01-03 to 2026-10-15
RESULT MARKET_FEATURES_PREPARED_ONLY; no models fitted
```

The pasted local manifest path was truncated, but the generated program saves it under a timestamped directory inside `data/processed/market_pilot/`. No specific timestamp is asserted here.

There are 31,383 country/date market-feature observations across five countries **in total**, not 31,383 for each. The common equity-only panel has 4,293 dates. Its earliest common date is July 5, 2007, after 63-observation feature warmup on the shortest-covered country series. No conclusion about the dates/coverage of the four FX transformations is yet supported by these aggregate counts.

Five *separately stored* official benchmark series have 23,785 observations: three ECB CISS (3×6,997) plus FRED STLFSI4 and NFCI (2×1,397). External benchmark observations do not automatically align with market dates, publication timestamps, or weekly report release dates.

## New derived-data diagnostic

`src/latent_risk/data/market_diagnostics.py` and `scripts/audit_market_pilot.py` now validate:
- each of the three derived CSV SHA256 hashes and row counts against its *derived* manifest;
- five-country source identity, unique country-date rows, finite equity features;
- designed structurally missing USA FX, source-specific FX missingness and paired feature validity;
- five-way equity calendar intersection AND equity feature equality with long country data;
- benchmark identity/value schema and actual same-date overlap with each local equity series; benchmark data are never used as model inputs.

A local Git-ignored JSON summary is written under `results/runs/market_diagnostics/summary.json`. It is **not** a model-quality, causal-predictive, statistical-calibration or real-time availability validation.

## Next VM command

```powershell
git pull --ff-only origin main
python scripts/audit_market_pilot.py
```

No rerun of source downloader or `build_market_pilot.py` is necessary. The diagnostic automatically discovers the most recent successful derived pilot directory, or accepts `--pilot-dir` to select another.

## Scientific limitations

- Cross-country equity returns at the same date are *not guaranteed simultaneously known* before one universal forecast cutoff because markets close at different times.
- CISS and US financial-condition series are current-vintage observational histories, not verified historical first-release series; publication date semantics are not audited.
- No factor, smoother, interval or forecast computed; EXP-0001 is **PROPOSED/NOT EXECUTED**.
- Missing credit/funding/bank risk domains prevent claiming the input panel represents full systemic financial stress.
