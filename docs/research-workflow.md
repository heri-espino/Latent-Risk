# Research workflow and reproducibility

1. Follow [AGENTS.md](../AGENTS.md) and the journal-first session reading order.
2. Make one scientific question explicit; document its assumptions and estimand in `notes/`.
3. Register sources, copyright status, and availability dates before a historical evaluation.
4. Implement reusable algorithms under `src/latent_risk/` with typed NumPy-style docstrings and unit tests.
5. Give every experiment an `EXP-####` protocol, frozen configuration, seeds and input checksums. Separate pilot decisions from confirmatory evaluations.
6. Run `pytest`, `ruff check .`, `python scripts/validate_research.py`, and the Sphinx build.
7. Append a dated journal entry, point `journal/LATEST.md` to it, and update `AI_HANDOFF.md` plus relevant context indexes.
8. Write manuscript claims only after audit-ready results exist. Any failure to reproduce remains a recorded result.

Conventional estimation, factor identification, and smoothing are separate tasks. A retrospective full-sample index cannot justify a purported real-time warning claim. See [EXP-0001](../experiments/EXP-0001.md).
