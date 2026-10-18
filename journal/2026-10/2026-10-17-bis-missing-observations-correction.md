# 2026-10-17 — Live BIS parser failure and explicit-missing observation correction

**Date:** 2026-10-17 (America/Mexico_City)  
**Objective:** reconcile a failed first BIS live download on user VM with valid-but-missing daily SDMX observations, without erasing failed attempts or compromising data quality.

## Motivation and scientific question
Why did five verified BIS series codes all fail with the same `BIS SDMX has missing or nonfinite index values` error? Should a missing observation date be treated as a malformed numeric series, a zero exchange-rate index level, or an explicitly unobserved row? For financial observations, the last interpretation is safe **only when the missing token can be identified unambiguously**.

## User-reported results / original failure (preserved)
- VM command: `python scripts/download_data.py --start 2000-01-01 --end 2026-10-18 --sources bis`.
- Snapshot UTC `20261018T021112030837Z`: **0/5 BIS** codes successfully parsed; all report the same missing-or-nonfinite validation error.
- Catalog now **45**, audit across **seven** manifests **34 OK, 5 FAILED, 6 NEVER_REQUESTED**. Earlier 34 source snapshots unchanged.
- Read-only QA: **34/34 PASS, 0 FAIL, 1 WTI signed-price warning**, because no BIS series was saved successfully. User saw exactly the same validated older sources as before.
- Raw BIS API responses were not provided; exact missing field count and whether rows are weekends or holidays remain **UNKNOWN**.
- Non-sensitive details recorded in `data/audits/2026-10-17-bis-first-live-failure.md`.

## Work performed
- Read mandatory repo handoff and previous BIS acquisition journal before code edits.
- Reviewed BIS SDMX CSV format; its observation `OBS_VALUE` may be absent. Official SDMX CSV format examples and BIS API docs: https://stats.bis.org/api-doc/v2/ ; https://data.bis.org/help/export . Do not assume a specific BIS missing observation date without live payload.
- `src/latent_risk/data/bis.py`: preserve literal missing markers (`keep_default_na=False`) instead of collapsing them with malformed numeric strings; define a narrow explicit missing-token whitelist, filter those rows after validating dates/identity, reject any other NaN/Inf/invalid/nonpositive index. Record dropped-row count, fraction and first ten dates as DataFrame attributes. No interpolation or post-hoc value editing.
- `src/latent_risk/data/acquisition.py`: carry source response SHA256, missing counts/rates/example dates into each immutable successful manifest record; print BIS `missing_source_rows` on success.
- `tests/test_bis_eer.py`: synthetic tests cover missing token drop and provenance, all missing failure, malformed nonmissing numeric cells, duplicate missing date defense, and successful mock download with reported missing count. A deliberately malformed unquoted CSV comma is rejected for dimension inconsistency rather than numeric coercion.
- Updated latest journal, handoff, state, next steps and data acquisition docs.

## Validation
**VERIFIED COMPUTATIONALLY** for synthetic BIS responses: GitHub Actions on code commit `7e7002978d171e0c990941267149a8af572fe97a`: **88 tests passed**, Ruff, structure, Sphinx green: https://github.com/heri-espino/Latent-Risk/actions/runs/39089446309 . A previous intermediary code push had a test expectation failure on unquoted comma CSV (regex mismatch; actual wrong-dimension rejection was correct), then fixed in a separate commit. Preserve that as normal testing provenance.

**UNVERIFIED live:** cannot reach stats.bis.org directly from assistant runtime, no actual provider CSV inspected. Updated BIS downloader must be rerun on user's VM. Neither 39 success nor real BIS coverage is asserted.

## Scientific reasoning
An observation date `t` with missing value is not a zero NEER index and cannot be used for logarithmic changes or regressors. Dropping explicitly absent observations retains real observed levels while leaving market-date gaps explicit; later volatility should use source-observation windows or publication-safe conventions, never fill future values. BIS nominal broad EER weights may be revised, and periodic releases mean that observation dates do not establish historical availability. A valid source file also does not establish stress-index predictiveness.

## Alternatives rejected
- Override validation by accepting NaN as numerically valid: rejected.
- Forward-fill or interpolate holiday observation values: rejected.
- Delete the entire series on a single legitimate missing marker: rejected.
- Automatically replace older derived USD-based FX features: rejected.
- Continue loosening parser to accept arbitrary source tokens without inspecting live CSV if retry fails: rejected.

## Exact files changed
`src/latent_risk/data/bis.py`, `src/latent_risk/data/acquisition.py`, `tests/test_bis_eer.py`, `data/audits/2026-10-17-bis-first-live-failure.md`, this entry, `journal/LATEST.md`, `AI_HANDOFF.md`, `context/STATE.md`, `context/NEXT_STEPS.md`, `data/README.md`.

## Next steps
Pull latest main; rerun `--sources bis`; inspect per-code success count, `bis_missing_observation_count`, source first/latest dates and quality summary. Only then construct a new versioned BIS-based five-country depreciation/FX-volatility feature panel. Primary EXP-0001 still requires time-aware release vintage and multi-domain credit/bank/funding features.
