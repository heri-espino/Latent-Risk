#!/usr/bin/env python3
"""Audit mandatory repo paths, journal pointers and research-card references."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import re
import sys

DIRECTORIES = (
    "context", "src/latent_risk", "tests", "examples", "notes/results",
    "notes/literature", "journal/decisions", "literature/pdf",
    "literature/markdown", "literature/references", "experiments/configs",
    "data", "results", "figures/paper", "paper/sections", "docs",
    "scripts", ".github/workflows",
)
FILES = (
    "README.md", "AGENTS.md", "AI_HANDOFF.md", "CONTRIBUTING.md",
    "pyproject.toml", ".gitignore", "context/STATE.md", "context/NEXT_STEPS.md",
    "context/DECISION_INDEX.md", "journal/README.md", "journal/LATEST.md",
    "notes/index.md", "notes/definitions.md", "notes/conjectures.md",
    "literature/README.md", "literature/MANIFEST.csv",
    "literature/references/README.md", "literature/references/KEY_RESULTS.md",
    "literature/references/PAPER_TEMPLATE.md", "literature/references/library.bib",
    "paper/main.tex", "paper/sections/problem.tex", "paper/sections/methods.tex",
    "paper/sections/experiments.tex", "docs/conf.py", "docs/index.md",
    "docs/getting-started.md", "docs/api.rst", "docs/mathematics.md",
    "docs/research-workflow.md", "docs/literature.md",
    "experiments/EXP-0001.md", "experiments/configs/EXP-0001.json",
    "scripts/check_change_protocol.py", "scripts/new_literature_entry.py",
    ".github/workflows/ci.yml", ".github/pull_request_template.md",
)
HANDOFF_HEADINGS = (
    "Project identity and objective", "Verified mathematical results",
    "Open mathematical questions", "Implemented algorithms and features",
    "Proposed but unimplemented algorithms", "Experimental results and limitations",
    "Decisions", "Known issues and unresolved status",
    "Current testing status", "Exact next actions", "Important files to inspect next",
)
CARD_HEADINGS = (
    "Bibliographic information", "Available sources and rights",
    "Scientific objective", "Assumptions and notation", "Key mathematical results",
    "Methods and experiments", "Relationship to Latent-Risk", "Verification status",
)


def check(root: Path) -> list[str]:
    """Return actionable structural errors (empty means no detected issues)."""
    errors: list[str] = []
    for path in DIRECTORIES:
        if not (root / path).is_dir():
            errors.append(f"missing directory: {path}")
    for path in FILES:
        if not (root / path).is_file():
            errors.append(f"missing file: {path}")
    latest = root / "journal/LATEST.md"
    if latest.is_file():
        matches = re.findall(r"\]\((\d{4}-\d{2}/\d{4}-\d{2}-\d{2}-[^)#]+\.md)\)", latest.read_text())
        if len(matches) != 1 or not (root / "journal" / matches[0]).is_file():
            errors.append("LATEST.md must link to one existing dated journal entry")
    handoff = root / "AI_HANDOFF.md"
    if handoff.is_file():
        text = handoff.read_text()
        for heading in HANDOFF_HEADINGS:
            if f"## {heading}" not in text:
                errors.append(f"AI_HANDOFF.md missing section: {heading}")
    manifest = root / "literature/MANIFEST.csv"
    if manifest.is_file():
        with manifest.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                key = (row.get("citation_key") or "").strip()
                if not key or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", key):
                    errors.append(f"invalid literature citation_key: {key!r}")
                    continue
                for field in ("reference_path", "pdf_path", "markdown_path"):
                    path = (row.get(field) or "").strip()
                    if path and not (root / path).is_file():
                        errors.append(f"{key}: {field} does not exist: {path}")
                card = root / (row.get("reference_path") or f"literature/references/{key}.md")
                if card.is_file():
                    card_text = card.read_text()
                    for heading in CARD_HEADINGS:
                        if f"## {heading}" not in card_text:
                            errors.append(f"{key}: missing card heading {heading}")
                bib = root / "literature/references/library.bib"
                if bib.is_file() and not re.search(r"@[a-zA-Z]+\s*\{\s*" + re.escape(key) + r"\s*,", bib.read_text()):
                    errors.append(f"{key}: no BibTeX entry")
    if not list((root / "src/latent_risk").rglob("*.py")):
        errors.append("no package source implementation")
    if not list((root / "tests").glob("test_*.py")):
        errors.append("no top-level numerical tests")
    for exp in (root / "experiments").glob("EXP-*.md"):
        if not re.fullmatch(r"EXP-\d{4}\.md", exp.name):
            errors.append(f"invalid experiment identifier: {exp.name}")
        elif not (root / "experiments/configs" / (exp.stem + ".json")).is_file():
            errors.append(f"{exp.stem}: no matching experiment configuration")
    paper = root / "paper/main.tex"
    if paper.is_file():
        tex = paper.read_text()
        for section in ("problem", "methods", "experiments"):
            if f"\\input{{sections/{section}}}" not in tex:
                errors.append(f"paper/main.tex missing section import: {section}")
    return errors


def main() -> int:
    """Validate the repository given via --root and exit with a status code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = check(args.root.resolve())
    if errors:
        for problem in errors:
            print("FAIL:", problem)
        return 1
    print("PASS: repository structure, journal, handoff, literature, and experiments")
    return 0


if __name__ == "__main__":
    sys.exit(main())
