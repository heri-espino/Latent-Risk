# 2026-10-18 — BIS daily broad NEER acquired and source-audited (five countries)

**Status:** `USER-REPORTED VM VERIFIED BY LOCAL TOOLS`; vendor CSV bytes not copied into the public repository or independently reviewed by assistant.

## Download and source provenance

- Successful BIS snapshot: `data/raw/downloads/20261018T145643915821Z/manifest.json`
- Command: `python scripts/download_data.py --start 2000-01-01 --end 2026-10-18 --sources bis`
- Outcome: `COMPLETE_SOURCE_DOWNLOAD: 5/5 downloaded`.
- Every series contains **6,987** positive finite observations from **2000-01-03 through 2026-10-13**. Each source also returned **2,796 explicitly missing observation rows**, which were excluded without interpolation, zero-fill or future information. Within downloaded source rows, missing fraction is `2796 / (6987 + 2796)` = approximately **28.58%**. The equal counts strongly suggest nontrading calendar dates, but exact excluded dates must be inspected before classifying every one as weekend.
- MEX `D.N.B.MX`, USA `D.N.B.US`, GBR `D.N.B.GB`, JPN `D.N.B.JP`, EA `D.N.B.XM`.

## Catalog and file integrity

Eight raw-source manifests, **45** registered codes: **39 OK, 0 FAILED, 6 NEVER_REQUESTED** (optional two Banxico monetary + two BoE + two BoJ). The previous 0/5 BIS failure is retained as historical evidence and is not the latest effective status. `audit_source_quality.py` subsequently reported **39/39 PASS, 0 failed, 1 existing WTI signed-price warning**. That warning concerns historical WTI `CL=F` on 2020-04-20, **not BIS**.

These are local file integrity and temporal *observation* span checks. They do not prove past BIS release/vintage availability, or that a NEER level is a financial-stress scalar.

## New versioned preprocessing

**IMPLEMENTED / OFFLINE TESTED; NOT YET RUN ON ACTUAL VM DATA:** `src/latent_risk/data/bis_market_features.py` and `scripts/build_bis_market_pilot.py` generate a **separate** output under ignored `data/processed/market_pilot_bis/<UTC snapshot>/`:
- `country_bis_market_features.csv`: equity return/21-session volatility/63-session drawdown and BIS level, `-Δlog(NEER)` depreciation and trailing 21-reported-observation volatility, all countries including USA.
- `five_country_common_equity_dates.csv`: exact common equity-date panel (like legacy, independent of BIS missing).
- `five_country_complete_neer_equity_dates.csv`: the more restrictive all-five complete-case equity **and** BIS NEER panel on exact observation dates.
- `external_stress_references.csv`: 3 ECB CISS + 2 US FRED stress/conditions references, **not used as predictors**.
- `manifest.json`: source identifier/hash/vintage metadata, BIS missing-source counts, generated output hashes, per-country country/FX coverage, code commit and limitations.

The existing dated `data/processed/market_pilot/` and all raw vendor CSVs are never touched. The BIS new builder is *retrospective descriptive*, not a point-in-time prediction panel.

## Next command

```powershell
git pull --ff-only origin main
python scripts/build_bis_market_pilot.py
```

No redownload is required. Compare per-country NEER complete/missing and new common complete-case observation count against the legacy equity-only panel. **No market-feature empirical output counts are currently claimed for this new builder.**
