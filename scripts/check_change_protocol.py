#!/usr/bin/env python3
"""Require a new dated journal entry and fresh handoff for substantive PR changes.

Structural enforcement cannot prove that documents were actually read
or that scientific mathematics is correct.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

MANDATORY_UPDATES = (
    "AI_HANDOFF.md", "journal/LATEST.md",
    "context/STATE.md", "context/NEXT_STEPS.md",
)


def changed_paths(base_ref: str, root: Path) -> set[str]:
    """Get changed files between the merge base of two Git refs and HEAD."""
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        cwd=root, text=True, check=True, capture_output=True,
    )
    return set(result.stdout.splitlines())


def check_protocol(changed: set[str]) -> list[str]:
    """Return missing documentation updates for substantive scientific changes."""
    substantive = any(
        p.startswith(("src/", "tests/", "notes/", "experiments/", "paper/"))
        for p in changed
    )
    if not substantive:
        return []
    missing = [f"substantive change requires updated {p}" for p in MANDATORY_UPDATES if p not in changed]
    if not any(
        p.startswith("journal/") and len(p.split("/")) == 3 and p.endswith(".md")
        for p in changed
    ):
        missing.append("substantive change requires new dated journal/YYYY-MM entry")
    return missing


def main() -> int:
    """Check Git change-documentation protocol relative to the requested base."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        changed = changed_paths(args.base_ref, args.root)
    except subprocess.CalledProcessError as exc:
        print(f"FAIL: cannot compare Git refs: {exc.stderr.strip()}")
        return 2
    problems = check_protocol(changed)
    for problem in problems:
        print("FAIL:", problem)
    if not problems:
        print("PASS: documentation change protocol")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
