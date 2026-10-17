# Contributing

Start by reading [AGENTS.md](AGENTS.md), then the journal, AI handoff and context in the specified order. Propose changes with a documented mathematical convention and a testable objective; never silently alter a frozen experiment. Add a dated research journal entry and synchronize `AI_HANDOFF.md`, `context/STATE.md`, `context/NEXT_STEPS.md` for substantive changes.

## Suggested local checks
```bash
python -m pip install -e ".[dev,docs]"
python -m pytest
ruff check .
python scripts/validate_research.py
sphinx-build -b html docs docs/_build/html
```

Publication results require exact data vintages, configuration, seeds and immutable outputs. Small proposed experiments remain labeled unrun until executed and audited. Cite and license third-party material properly; do not commit downloaded third-party PDFs into this public repository without redistribution permission.
