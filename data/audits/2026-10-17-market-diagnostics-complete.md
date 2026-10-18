# 2026-10-17 — First derived-market coverage diagnostic on user VM

**Evidence level:** user-supplied CLI output from `python scripts/audit_market_pilot.py`.
No direct access to user generated CSVs or the local `summary.json` bytes.

## Input and aggregate outputs

Pilot selected by command: `data/processed/market_pilot/20261018T003625232736Z`.

- `country_market_features.csv`: **31,383** rows.
- Strict common five-country equity panel: **4,293** observation dates, 2007-07-05 through 2026-10-16.
- Separate external ECB CISS / FRED stress/conditions dataset: **23,785** rows.
- `RESULT DESCRIPTIVE_COVERAGE_DIAGNOSTIC_ONLY; no model fitted`.

## Country panel and FX observation-date coverage

| Country | Equity feature rows | FX complete | FX missing | FX observed share |
|---|---:|---:|---:|---:|
| MEX | 6,664 | 5,720 | 944 | 85.83% |
| USA | 6,676 | N/A | N/A | N/A — no fictitious USD/USD |
| GBR | 6,706 | 5,743 | 963 | 85.64% |
| JPN | 6,498 | 6,466 | 32 | 99.51% |
| EA | 4,839 | 4,814 | 25 | 99.48% |

Mexico and UK equity records exist before their Yahoo FX downloads start (approximately December 2003). Missing FX must **NOT** be filled with zeros and need not force loss of valid equity-only observations. Date gaps later in history still require separate review.

## Same-date external reference overlap (NOT publication-time proof)

| External index | Country | Country equity same-date overlap |
|---|---|---:|
| ECB CISS EA | EA | 4,838 |
| ECB CISS US | USA | 6,675 |
| ECB CISS UK | GBR | 6,705 |
| FRED STLFSI4 | USA | 1,338 |
| FRED NFCI | USA | 1,338 |

The three CISS indices overlap with nearly all local equity observation dates; the weekly FRED indices have sparser observation-date coverage. **Weekly label ≠ value release date; retrospective CISS samples can have later data revisions.**

## Source model status

- This is a **successful derived data consistency / coverage test**, not a cross-country latent-index validation or a forecast experiment.
- Exact five-equity cross-country trading-date intersection is a descriptive panel. Different markets close in different time zones and the actual common information set is not verified.
- The additional six monetary catalog entries remain unrequested; the project's core financial-stress limitations (credit, banking, funding) remain.
- WTI oil future remains excluded from this stage, despite passing source integrity with signed-price warning.

## Methodological next step

Implement a separate, clearly labeled **exploratory retrospective CISS observation-index forecasting baseline** (EXP-0002) to test chronological rolling-origin forecasting and nested historical hyperparameter selection without contaminating the main latent-risk experiment EXP-0001. No historical release vintage assumptions are made.
