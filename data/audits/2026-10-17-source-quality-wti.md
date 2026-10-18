# 2026-10-17 — First physical source-file integrity audit and WTI exception

**Evidence status:** USER-REPORTED program output; raw user vendor files remain on the VM and were not independently inspected by assistant.

## Result of `python scripts/audit_source_quality.py`

All **34** successfully downloaded sources were inspected by the script, including 14 Yahoo market symbols, 12 FRED, 5 ECB, and 3 Banxico.

- **33 PASS**.
- **1 FAIL: `market CL=F` (WTI crude oil front-month futures), 6,566 rows**.
- The sole reported failure message was **"market close prices must be strictly positive"**.
- The user's output did not provide the actual nonpositive CL=F observation value(s) or date(s), so we **do not claim** the failed data point is definitely the known April 2020 event.

No file-hash, missing date, duplicate, missing numeric-value, or other error appeared in the printed audit output. The program reports only one class of displayed failure, so this evidence does **not** independently validate all raw bytes.

## Research-backed reason for revising the check

A **negative NYMEX WTI front-month futures settlement is possible**. The expiring May 2020 contract settled at **−$37.63 per barrel on April 20, 2020**, verified by U.S. Commodity Futures Trading Commission reporting (https://www.cftc.gov/PressRoom/PressReleases/8315-20) and U.S. Energy Information Administration reporting (https://www.eia.gov/TODAYINENERGY/detail.php?id=43495). This event is a property of delivery-constrained futures, **not proof that any arbitrary negative value in the user's continuously selected front-month series is correct**.

## Corrected algorithm

- An explicit `price_domain="signed"` catalog attribute applies to WTI `CL=F`.
- Older immutable snapshots predate that metadata; the validator applies a **narrow series-specific compatibility rule** for exactly `CL=F` with role `global_oil`, without rewriting their CSV or original manifests.
- If the series has any nonpositive closes, quality status is **PASS with a prominent warning**, and the report records count, up to ten first observation dates, minimum close and corresponding date; the researcher must validate these against vendor/contract roll conventions.
- All unmarked market prices still must be **strictly positive**. Non-finite price observations, duplicate dates, bad hashes, invalid counts etc. still **FAIL**.
- Downstream ordinary log returns `log(P_t/P_{t-1})` are not valid for zero or negative ratios. WTI prices may be represented by absolute dollar-per-barrel differences or a *predeclared* signed transform with scale fitted only from past training observations; futures contract-roll changes also require audit.

## Next verification

In the existing `(latent-risk)` environment:

```powershell
git pull --ff-only origin main
python scripts/audit_source_quality.py
```

Expected: same 34 series audited, WTI now **PASS with WARNINGS** if its close values are finite and the other checks still pass. **This expectation is not a completed VM test**. Inspect WTI's observed dates and minimum from `results/runs/source_quality/report.json`, and report them before asserting vendor fidelity or applying a feature transform. Do not commit raw data or secrets.
