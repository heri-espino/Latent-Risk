"""Audit all locally downloaded source snapshots against the configured catalog.

Uses only local manifests. Prints latest status and historical successes for
each expected vendor series; never uploads raw data or API credentials.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def audit(catalog: dict, manifests: list[tuple[str, dict]]) -> list[dict]:
    """Summarize expected sources across independent raw-data snapshots.

    Parameters
    ----------
    catalog : dict
        Canonical per-source arrays from source_catalog.json.
    manifests : list
        Pairs of snapshot directory name and parsed JSON manifest.

    Returns
    -------
    list of dict
        Each expected series' latest attempt, any verified success,
        available date coverage and status.
    """
    records: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for snapshot_name, manifest in sorted(manifests):
        for row in manifest.get("records", []):
            item = dict(row)
            item["snapshot"] = snapshot_name
            records[(str(row.get("source")), str(row.get("id")))].append(item)

    output = []
    for source in ("market", "fred", "banxico", "ecb", "boe", "boj", "bis"):
        for entry in catalog.get(source, []):
            identifier = entry.get("symbol", entry.get("key", entry.get("series")))
            history = records.get((source, identifier), [])
            successes = [row for row in history if row.get("status") == "OK"]
            last = history[-1] if history else {}
            succeeded = successes[-1] if successes else {}
            output.append({
                "source": source,
                "country": entry["country"],
                "id": identifier,
                "role": entry["role"],
                "result": (
                    "OK" if succeeded else "FAILED" if history else "NEVER_REQUESTED"
                ),
                "last_attempt": last.get("status", "NONE"),
                "last_successful_snapshot": succeeded.get("snapshot"),
                "first_date": succeeded.get("first_date"),
                "last_date": succeeded.get("last_date"),
                "n_rows": succeeded.get("n_rows"),
                "error": last.get("error") if last.get("status") == "FAILED" else None,
            })
    return output


def main() -> int:
    """Inspect local source coverage and write a JSON audit outside Git tracking."""
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[1]
    parser.add_argument("--catalog", type=Path, default=root / "data/source_catalog.json")
    parser.add_argument("--snapshots", type=Path, default=root / "data/raw/downloads")
    parser.add_argument("--output", type=Path, default=root / "results/acquisition_audit.json")
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    manifests: list[tuple[str, dict]] = []
    for path in sorted(args.snapshots.glob("*/manifest.json")):
        try:
            manifests.append(
                (path.parent.name, json.loads(path.read_text(encoding="utf-8")))
            )
        except (ValueError, UnicodeError, OSError) as exc:
            print(f"[INVALID MANIFEST] {path}: {exc}")
    rows = audit(catalog, manifests)
    print(f"Read {len(manifests)} manifests; expected catalog series: {len(rows)}\n")
    print(f"{'SOURCE':7} {'COUNTRY':7} {'ID':43} {'RESULT':17} {'FIRST':10} {'LAST':10}")
    for row in rows:
        print(
            f"{row['source']:7} {row['country']:7} {row['id'][:43]:43} "
            f"{row['result']:17} {row['first_date'] or '-':10} "
            f"{row['last_date'] or '-':10}"
        )
    totals = {status: sum(row["result"] == status for row in rows)
              for status in ("OK", "FAILED", "NEVER_REQUESTED")}
    print(f"\nSUMMARY: {totals}; excludes unregistered series and unverified vintages")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps({"snapshots_read": len(manifests), "counts": totals, "series": rows},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Audit JSON: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
