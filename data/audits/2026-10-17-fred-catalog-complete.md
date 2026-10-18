# 2026-10-17 — Completion of initial FRED catalog on VM

**Status: USER-REPORTED COMMAND OUTPUT, NOT INDEPENDENT RAW-DATA VERIFICATION**

After the successful four-series FRED official API probe, the user requested
the eight remaining entries over the same `api.stlouisfed.org` backend
with a private key, held in the PowerShell environment temporarily.

## Successful new source snapshot

- Local manifest: `data/raw/downloads/20261018T000222516029Z/manifest.json`
  (UTC timestamp, research session local date October 17).
- Invocation:
  `python scripts/download_data.py --start 2000-01-01 --end 2026-10-17 --sources fred --fred-backend api --only M1SL,M2SL,TRESEGUSM052N,TRESEGMXM052N,TRESEGGBM052N,TRESEGJPM052N,MYAGM2MXM189N,MANMM101MXM189S`
- CLI: `RESULT COMPLETE_SOURCE_DOWNLOAD: 8/8 downloaded`.

| Series | Country | Rows | Earliest date | Latest date |
| --- | --- | ---: | --- | --- |
| `M1SL` | USA | 320 | 2000-01-01 | 2026-08-01 |
| `M2SL` | USA | 320 | 2000-01-01 | 2026-08-01 |
| `TRESEGUSM052N` | USA | 320 | 2000-01-01 | 2026-08-01 |
| `TRESEGMXM052N` | MEX | 320 | 2000-01-01 | 2026-08-01 |
| `TRESEGGBM052N` | GBR | 320 | 2000-01-01 | 2026-08-01 |
| `TRESEGJPM052N` | JPN | 320 | 2000-01-01 | 2026-08-01 |
| `MYAGM2MXM189N` | MEX | 209 | 2000-01-01 | 2017-05-01 |
| `MANMM101MXM189S` | MEX | 228 | 2000-01-01 | 2018-12-01 |

## Overall catalog status

`python scripts/audit_downloads.py` read **six manifests** with expected
catalog size **40**, yielding **34 OK, 0 FAILED, 6 NEVER_REQUESTED**.

Successful by source: 14 market, 12 FRED, 3 Banxico, 5 ECB.
Never requested: Banxico `SF311408`/`SF311418`;
Bank of England `LPMAUYN`/`IUDSOIA`;
Bank of Japan `MAM1NAM3M1MO`/`MAM1NAM2M2MO`.
They are *optional in the first stress-factor methodology pilot*, not inherently
unnecessary to every later international study.

## Scientific interpretation and limitations

FRED's Graph CSV hostname was unusable from the user's VM but its official
API hostname worked for all 12 selected sources across two API snapshots.
Do not erase or reinterpret the earlier transport failures; manifests retain
their status by run. The completed catalog has 34 successful acquisitions,
not 34 validated historically available predictor series. Numeric content,
source hashes, calendars, units and outliers still require an independent
read of the VM's raw files. Every source may have revisions; FRED monthly
reference-month labels are not publication dates. The two Mexico legacy
money-stock series end in 2017/2018 and must not be used as if current.

No financial stress-factor model, forecast, early-warning prediction or
cross-country event-detection result has been computed.

## Next gate

1. Run `python scripts/audit_source_quality.py` on VM to verify all 34 actual
   CSV files against their source manifest SHA256, schema, dates, row counts and
   numeric completeness (no redownload).
2. Inspect `results/runs/source_quality/report.json`, keep private raw data
   out of Git; report errors/warnings.
3. Audit common market dates and returns; distinguish per-country component
   sources from external CISS/STLFSI4/NFCI reference indices.
4. Freeze one exploratory historical CISS/market pilot and only later claim
   real-time validity with proper release/vintage evidence.
