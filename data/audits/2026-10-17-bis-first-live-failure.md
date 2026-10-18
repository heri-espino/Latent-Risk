# 2026-10-17 — BIS daily NEER source parsing failed on user VM

**Evidence:** pasted PowerShell command output, *not* captured raw BIS HTTP response bytes.

## Actual BIS download attempt

On user's activated environment:
```powershell
python scripts/download_data.py --start 2000-01-01 --end 2026-10-18 --sources bis
```

Immutable source manifest: `data/raw/downloads/20261018T021112030837Z/manifest.json`, UTC timestamp.

All five nominal broad daily BIS EER sources (`D.N.B.MX`, `D.N.B.US`, `D.N.B.GB`, `D.N.B.JP`, `D.N.B.XM`) failed with the same exception: `ValueError: BIS SDMX has missing or nonfinite index values`. **No BIS CSV passed into a successful snapshot.** The failure appears inside the parser, after request/HTTP/CSV header/dimension/date checking, but the exact offending cells or dates have not been observed by this assistant.

Seven-manifest `python scripts/audit_downloads.py` output:
- Registered series: **45**.
- Successful historic source snapshots: **34 OK**.
- BIS: **5 FAILED** on the newest request (distinct from the 34 older source successes).
- Other optional macro source records: **6 NEVER_REQUESTED**.
- `python scripts/audit_source_quality.py`: **34/34 PASS, zero failed, one signed WTI warning**. This program verifies *successfully saved raw CSVs*, not failed download attempts, so 34/34 does not imply successful BIS data.

## Root cause hypothesis and correction

Old parser unconditionally rejected any `OBS_VALUE` cell that parsed to NaN. SDMX CSV permits explicit missing observation-value records; holiday/non-observation placeholders are a plausible explanation for five identical errors. **This remains a diagnosis by exclusion, not a direct inspection of BIS response bytes**.

A revised parser treats a narrow set of *explicit missing-value markers* (`""`, `.`, `..`, `-`, `NA`, `N/A`, `NaN`, `null`, case insensitive) as missing *observation rows*. Within requested dates it excludes only those cells from the published positive numeric series, without imputing, interpolating or fabricating observations. It continues rejecting malformed or nonfinite **nonmissing** values, duplicate dates (including duplicate missing rows), wrong BIS series/dimensions, non-ISO dates, nonpositive index levels and all-empty series.

New successful BIS manifests record `bis_response_sha256`, `bis_source_rows_in_window`, `bis_missing_observation_count`, `bis_missing_first_dates` (first ten) and `bis_missing_fraction`. One per-series successful output is still `observation_date,value` with finite positive values.

**Status:** Correction `IMPLEMENTED` and **offline CI tested**; **no successful live BIS retry yet**. We must verify counts, missingness share and observation dates after running on VM. Missing dates must not be treated as zero and full current BIS history is *not* known at historical forecast origins.

## Immediate reproducible verification

```powershell
git pull --ff-only origin main
python scripts/download_data.py --start 2000-01-01 --end 2026-10-18 --sources bis
python scripts/audit_downloads.py
python scripts/audit_source_quality.py
```

A second UTC snapshot will be created. The failure manifest remains preserved. If any still fail, *do not loosen numeric validation further without seeing source CSV field/date/status evidence*; use a bounded BIS API diagnostic retaining no credentials and no uploaded vendor dataset. If all succeed, expect inventory **39 OK / 0 FAILED / 6 NEVER_REQUESTED**, plus QA of 39 successfully saved source files (WTI warning remains). These are expectations, **not empirical results**.
