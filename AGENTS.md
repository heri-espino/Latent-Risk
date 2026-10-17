# Mandatory procedure for human and AI contributors

This project prioritizes research continuity, mathematical accuracy, reproducibility and traceability over speed. All contributors, including AI assistants without previous chat history, follow the same procedure. Never treat summaries as proof.

## Beginning of every working session — exact reading order

1. `AGENTS.md` (this file).
2. `journal/README.md`.
3. `journal/LATEST.md`.
4. The latest dated journal entry linked from `journal/LATEST.md`.
5. `AI_HANDOFF.md`.
6. `context/STATE.md`.
7. `context/NEXT_STEPS.md`.
8. `context/DECISION_INDEX.md`.
9. Only then, task-specific primary code, notes, literature or results.

The dated journal is the chronological authority; reconcile contradictions with actual source code and recorded experimental evidence. Read progressively, not the entire repository at once.

## During the session

- Keep reusable source code in `src/latent_risk`, experiments and scripts outside the installable library, theoretical arguments in `notes/`, and publication in `paper/`.
- Distinguish `PROVEN`, `VERIFIED COMPUTATIONALLY`, `IMPLEMENTED`, `EXPERIMENTAL`, `CONJECTURED`, `PROPOSED`, and `UNKNOWN`.
- Add type hints, NumPy-style API docstrings, failure cases, and tests for changes.
- Record assumptions, likelihood parameterization, factor sign and scale, release-date conventions, forecast origins, and metrics.
- Preserve negative results and failed approaches rather than erasing history.
- Never infer crisis detection from a retrospectively smoothed series or call a full-sample fit real-time.
- Do not assume that factors estimated by different index models are directly comparable forecast targets.
- Check source licenses before adding PDFs or copied figures to this public repository.
- Cite real literature; verify exact mathematical claims against PDFs when available; never fabricate data, proof status or experimental success.

## End of every substantive change

1. Run all relevant tests, lint, structural validation, and documentation build if available; report what could not run.
2. Add a dated `journal/YYYY-MM/YYYY-MM-DD-topic.md` entry using the full research-log schema.
3. Update `journal/LATEST.md`.
4. Update `AI_HANDOFF.md`, `context/STATE.md` and `context/NEXT_STEPS.md`.
5. Update `context/DECISION_INDEX.md`, math notes, literature, experiments, and manuscript when the subject demands it.
6. Explicitly describe which changes were implemented versus merely proposed.

Do not conclude a code or scientific change with stale handoff. No new journal entry is necessary for a session with no repository modifications.

## Code and manuscript policy

- Research validation: `python scripts/validate_research.py`; change protocol: `python scripts/check_change_protocol.py --base-ref <git-ref>`.
- Local tests: `python -m pytest`; lint: `ruff check .`; documentation: `sphinx-build -b html docs docs/_build/html`.
- Every EXP record names a config, exact code version, dataset vintage, seeds, uncertainty estimates and output paths.
- The manuscript may state only results grounded in completed records; drafts without results must clearly say so.
- Major decisions use ADRs, never unannounced rewrites of earlier decisions.

## Scientific separation

Index construction (composite/PCA/DFM), likelihood-based trend filtering, and event/forecast-failure assessment are distinct modeling stages. The earlier Trend-Estimation repository holds methodology research; this repository holds an empirical latent-risk application. Neither set of earlier results is automatically validated here.
