# Decision index

| ADR | Date | Decision | Status |
| --- | --- | --- | --- |
| [ADR-0001](../journal/decisions/ADR-0001.md) | 2026-10-16 | A new project-specific repository with a `src/` library and journal-first handoff | Accepted |
| [ADR-0002](../journal/decisions/ADR-0002.md) | 2026-10-16 | Keep index construction, trend smoothing, and evaluation distinct; separate retrospective from pseudo-real-time claims | Accepted |
| [ADR-0003](../journal/decisions/ADR-0003.md) | 2026-10-16 | Immutable raw vendor snapshots precede release-date audit and chronologically valid panels | Accepted |
| [ADR-0004](../journal/decisions/ADR-0004.md) | 2026-10-17 | Official ECB, BoE and BoJ acquisition; preserve distinct monetary aggregate definitions | Accepted |
| [ADR-0005](../journal/decisions/ADR-0005.md) | 2026-10-17 | Market-stress-first indicator selection and separation of official external benchmarks | Proposed |
| [ADR-0006](../journal/decisions/ADR-0006.md) | 2026-10-17 | Instrument-aware signed WTI futures prices; audit warnings without mutating history | Accepted |
| [ADR-0007](../journal/decisions/ADR-0007.md) | 2026-10-17 | First descriptive end-of-day five-market feature panel and separate stress reference indices | Proposed |
| [ADR-0008](../journal/decisions/ADR-0008.md) | 2026-10-17 | BIS daily nominal broad effective FX indices for all five economies, source acquisition only | Accepted / feature replacement proposed |

Follow the latest dated journal entry for changes to this index.

**Coordinator decision pending (2026-10-18, crisis-hypotheses agent):** The proposed event anchors, exact time-availability semantics and thresholds are documented in `notes/literature/crisis_protocol.md` and `notes/results/event_study_design.md`. These are **not yet an accepted ADR or empirical results**. Before data scoring, decide whether to register a new ADR and pin the event-manifest hash; no pre-existing ADR was superseded.
