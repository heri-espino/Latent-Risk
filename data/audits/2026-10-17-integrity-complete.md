# 2026-10-17 — Completed 34-source integrity audit, WTI negative settlement confirmed

**Evidence:** User's own local `python scripts/audit_source_quality.py` CLI output, with 34 source files checked against their manifests. Raw CSVs remain on user's VM, not shared externally.

## Confirmed quality result

- **34/34 PASS; 0 FAIL; 1 WARNING.**
- WTI front-month future `CL=F`: 6,566 observations; exactly **one** nonpositive close, on **2020-04-20**, with the saved minimum `-37.630001068115234` USD/barrel, equivalent to **−37.63** at two decimal places.
- The nonpositive date and close agree with primary historical reports on the May 2020 WTI NYMEX contract settlement. However, the precise continuous-contract chain, adjusted vendor history and daily release-time fidelity have not been examined separately.
- All other 33 source files PASS, including 13 other Yahoo sources, 12 FRED, 5 ECB and 3 Banxico. Zero other warnings reported.
- The reported audit checks SHA256, saved row counts, unique/ordered ISO observation dates, finite closes and other numeric fields; this does **not** verify financial-series semantics, publication vintages or validity of forecasting assumptions.
- Remaining catalog still has 6 **NEVER_REQUESTED** macro series (Banxico 2, BoE 2, BoJ 2); none failed.

## Research policy

- **No more raw data acquisition required for the first market-feature preparation experiment.**
- WTI is a signed commodity futures instrument; it remains excluded from the new market-factor input panel pending explicit difference/roll handling.
- Five country equity indices and four FX quotes are the preliminary market-feature inputs; current-country CISS and STLFSI4/NFCI are **external references**, never blended into the same factor construction.
- Source observations are current revised vendor snapshots and labeled by observation date, **not historical `available_date`**.
- Preliminary market data processing can be done with past-only rolling calculations, exact calendar intersections, and separate no-leakage validation; the code does not yet create a latent risk factor or forecast.

## Next command

```powershell
git pull --ff-only origin main
python scripts/build_market_pilot.py
```

It writes timestamped, Git-ignored derivatives under `data/processed/market_pilot/`, and a manifest with original source SHA256 metadata. The raw source files remain immutable.
