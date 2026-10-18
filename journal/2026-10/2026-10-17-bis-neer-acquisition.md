# 2026-10-17 — BIS five-economy broad daily NEER downloader

**Date:** 2026-10-17 (America/Mexico_City)  
**Objective:** replace asymmetric US-dollar bilateral FX measurements with a future, uniformly sourced option across MEX, USA, GBR, JPN, EA, without changing historical source snapshots or the existing derived pilot.

## Motivation and scientific question
The US does not have a meaningful USD/USD rate. For a comparable FX measurement across our five economies, should we use BIS broad-basket nominal effective exchange rates instead of the existing bilateral USD quotes and US DXY? BIS daily broad NEERs provide a common statistical definition: a trade-weighted nominal currency strength index, indexed to 2020=100, whose increase means appreciation. A CISS and a global FX shock still measure conceptually different risks.

## Official source verification
- BIS dataset `BIS,WS_EER,1.0`; daily nominal broad-basket keys `D.N.B.MX`, `D.N.B.US`, `D.N.B.GB`, `D.N.B.JP`, `D.N.B.XM` (XM = euro area).
- Official BIS API v2 documentation https://stats.bis.org/api-doc/v2/ and official portal https://data.bis.org/topics/EER .
- Official series landing pages: https://data.bis.org/topics/EER/BIS%2CWS_EER%2C1.0/D.N.B.MX and analogues with final codes US, GB, JP, XM.
- API shape: `GET https://stats.bis.org/api/v2/data/dataflow/BIS/WS_EER/1.0/D.N.B.<ISO>?format=csv&labels=id&startPeriod=<YYYY-MM-DD>&endPeriod=<YYYY-MM-DD>`; last period is inclusive, converted from our exclusive CLI `--end`.
- BIS states daily series are updated in periodic mid-week releases; historical `TIME_PERIOD` dates are not releases and currency-basket weights may be revised; observations are current-vintage snapshots.
- Permitted use requires attribution and compliance with BIS terms https://www.bis.org/about/legal/permitted-use-statistics ; source files remain ignored and are not redistributed.

## Implemented code
- `src/latent_risk/data/bis.py`: strict SDMX CSV parser requiring frequency D, nominal type N, broad basket B and expected reference area; strict unique ISO days and finite, positive index values; exclusive-end date filtering.
- `src/latent_risk/data/acquisition.py`: `--sources bis` and existing `--only` support, one official API request per series with bounded retries/timeout, independent source metadata, immutable per-series CSV/SHA256 manifests and failures; no BIS API key required.
- `scripts/audit_downloads.py`: BIS entries included in catalog inventory, latest-success status per series.
- `data/source_catalog.json`: five canonical source codes, country identifiers, units, roles, official portal URLs and revision/release caveats.
- `tests/test_bis_eer.py`: synthetic response format, five country-code identities, exclusive date filter, duplicate and wrong series defenses, positivity/malformed payload defenses, mock download and manifest checking, unknown-ID refusal.
- New ADR-0008: primary *candidate* future FX domain is BIS daily broad NEER; old bilateral USD FX and DXY retained for sensitivity. **No automatic rewrite of the previous 31,383-row market pilot or any completed model outputs**.

## Mathematical interpretation
Let `E_{c,t}>0` be BIS NEER. Positive appreciation is `Δlog(E_{c,t})`; country depreciation can be consistently defined as `-Δlog(E_{c,t})`. Its trailing realized volatility is computed using only observations prior to or at an explicitly defined close/release origin. The same basket methodology does not imply each currency uses the same partner weights. BIS historical trade weights can be revised ex post; incorporating `E_{c,t}` directly on its observation date is NOT an archived true-time-vintage forecast feature.

## Testing and actual execution
**Offline code CI successful:** 79 pytest tests, Ruff, structural validator and Sphinx on commit `dd5e4909c8b4d3cb105a7b13ef33fa892ca681a2` ([GitHub CI](https://github.com/heri-espino/Latent-Risk/actions/runs/39088582188)). The assistant's execution environment could not resolve `stats.bis.org`; **live BIS API connectivity, vendor CSV schema and five real series observations have not been verified**. Some live schema surprises may require corrections without changing any raw snapshots.

## Reproduction command and expected outputs
On user's activated local VM:
```powershell
git pull --ff-only origin main
python scripts/download_data.py --start 2000-01-01 --end 2026-10-18 --sources bis
python scripts/audit_downloads.py
python scripts/audit_source_quality.py
```
This will attempt 5 BIS series only, preserving older downloads in a new UTC-stamped manifest. If all five succeed, inventory will be 45 catalog sources, **39 OK / 0 FAILED / 6 NEVER_REQUESTED**, assuming no other new requests. Do not assert this result until reported by user. Existing prior source quality 34/34 remains historical evidence regardless of BIS success.

## Alternatives, failure conditions and limits
- Keep DXY for the United States only: asymmetric and euro-heavy currency basket; keep for robustness, not the primary uniform-country setup.
- Treat BIS NEER as a dedicated global "risk" index: rejected; this is exchange rate competitiveness/strength, not a complete financial-stress measurement.
- Download all BIS series as a single unverified bulk source: rejected; per-series manifest provenance is easier to audit.
- Backfill prior derived market panel automatically: rejected; derived vintages must be regenerated with a new explicit feature definition, not silently overwritten.
- Later release dates, daily data revisions, BIS API timeouts, and CSV header schema compatibility may require further audit.

## Files changed
`src/latent_risk/data/bis.py`, `src/latent_risk/data/acquisition.py`, `scripts/audit_downloads.py`, `data/source_catalog.json`, `tests/test_bis_eer.py`, this journal, `journal/LATEST.md`, `journal/decisions/ADR-0008.md`, `context/DECISION_INDEX.md`, `AI_HANDOFF.md`, `context/STATE.md`, `context/NEXT_STEPS.md`, `data/README.md`, `data/indicator_priorities.md`.

## What remains proposed or unknown
No BIS vendor bytes have been retrieved on user's VM; the live five-series coverage and compatibility remain **UNKNOWN**. The revised market-feature pilot, optimal smoothing / historical forecast experiment and source publication-time controls remain **UNIMPLEMENTED** for BIS. The existing CISS baseline experiment EXP-0002 has not been run on real CISS observations.

## Next steps
Run BIS source request on VM and share console status + source audit. Inspect BIS parser/schema and calendar; then propose an explicit new version of `build_market_pilot.py` consuming BIS NEER with trailing transforms and all five countries instead of overwriting previous bilateral market features.
