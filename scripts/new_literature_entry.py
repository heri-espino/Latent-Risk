#!/usr/bin/env python3
"""Register a literature reference card, BibTeX record and manifest entry."""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

FIELDNAMES = (
    "citation_key", "title", "authors", "year", "venue", "doi",
    "pdf_path", "markdown_path", "reference_path",
    "verification_status", "redistribution_status",
)


def register(
    root: Path, *, key: str, title: str, authors: str, year: int,
    venue: str = "", doi: str = "",
) -> Path:
    """Create an unverified reference without downloading source material.

    Parameters
    ----------
    root : pathlib.Path
        Repository root.
    key, title, authors : str
        Citation key and bibliographic metadata.
    year : int
        Publication year (not a source verification guarantee).
    venue, doi : str
        Optional publication venue and DOI.

    Returns
    -------
    pathlib.Path
        Relative reference-card destination resolved under root.

    Raises
    ------
    ValueError
        On unsafe citation keys, empty metadata or duplicate records.
    """
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", key):
        raise ValueError("unsafe citation key")
    if not (title.strip() and authors.strip() and 1800 <= year <= 2100):
        raise ValueError("title, authors and plausible year are required")
    folder = root / "literature/references"
    card = folder / f"{key}.md"
    manifest = root / "literature/MANIFEST.csv"
    bib = folder / "library.bib"
    with manifest.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    if card.exists() or any(row["citation_key"] == key for row in rows):
        raise ValueError("citation key already exists")
    if any(ch in title + authors + venue + doi for ch in "{}\\"):
        raise ValueError("metadata contains BibTeX control characters")
    content = (
        f"# {key}: {title}\n\n## Bibliographic information\n"
        f"{authors}; {year}; {venue or 'venue not verified'}; DOI: {doi or 'unverified'}; "
        f"citation key: {key}.\n\n## Available sources and rights\n"
        "PDF absent; Docling Markdown absent; redistribution rights unknown.\n\n"
        "## Scientific objective\nNot read or verified yet.\n\n"
        "## Assumptions and notation\nNot verified.\n\n"
        "## Key mathematical results\nNot verified. Do not invent results.\n\n"
        "## Methods and experiments\nNot verified.\n\n"
        "## Relationship to Latent-Risk\nPending source review.\n\n"
        "## Verification status\nMetadata unverified; original PDF not checked.\n"
    )
    card.write_text(content, encoding="utf-8")
    with manifest.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writerow({
            "citation_key": key, "title": title, "authors": authors, "year": year,
            "venue": venue, "doi": doi, "pdf_path": "", "markdown_path": "",
            "reference_path": f"literature/references/{key}.md",
            "verification_status": "unverified", "redistribution_status": "unknown",
        })
    with bib.open("a", encoding="utf-8") as file:
        file.write(
            f"\n@misc{{{key},\n  title = {{{title}}},\n"
            f"  author = {{{authors}}},\n  year = {{{year}}},\n"
            f"  note = {{Unverified metadata}}\n}}\n"
        )
    return card


def main() -> int:
    """Register one paper from CLI without downloading copyrighted content."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--key", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--authors", required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--venue", default="")
    parser.add_argument("--doi", default="")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        card = register(
            args.root, key=args.key, title=args.title,
            authors=args.authors, year=args.year, venue=args.venue, doi=args.doi,
        )
    except (OSError, ValueError) as exc:
        print("FAIL:", exc)
        return 1
    print(f"Created unverified reference: {card}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
