# Next steps

- [x] Review OFR FSI, ECB CISS, Banxico IEMF and BIS vulnerability literature; propose direct stress-factor domains separate from money stocks and external benchmark series (`data/indicator_priorities.md`, `ADR-0005`).
- [x] Register ECB CISS keys for US/UK/EA, FRED STLFSI4/NFCI for external validation; support daily ECB CSV and date-scoped API requests, with offline tests.
- [ ] Confirm which market-based indicators can actually be fetched across all five geographies; the user has not uploaded complete download manifests.
- [ ] Design a 2008-compatible credit/funding proxy without ICE FRED corporate credit spreads (restricted to 3 years since Apr 2026).
- [ ] Examine original historical Banxico IEMF tables for external evaluation and find a credible Japan reference index or explicitly report its absence.

- [x] Audit the repository bootstrap: 12 tests, Ruff, structural validator and Sphinx passed on commit `075f9027` (https://github.com/heri-espino/Latent-Risk/actions/runs/38994859776); PR-only change checker and LaTeX compilation were not run.
- [x] Implement an initial candidate source catalog and downloader with 19 offline tests passing, Ruff, structure and Sphinx pass (https://github.com/heri-espino/Latent-Risk/actions/runs/38998827014); **no live data have been retrieved yet**.
- [x] Add ECB M1/M2, BoE M4/SONIA, BOJ M1/M2 and Banxico modern M1/M2 to the audited catalog; add independent source parsers and local multi-snapshot auditor (all new live-provider fetches `UNVERIFIED`).
- [ ] Run expanded downloader (`--sources ecb,boe,boj` and again `--sources banxico` for the new M1/M2), inspect all manifests with `scripts/audit_downloads.py`, preserve SHA256 provenance and report missing or short series.
- [ ] Diagnose and repair ten FRED VM `ConnectionError` failures; do not consider US rates/M1/M2/reserves downloaded yet.
- [x] Identify Banxico current money aggregates as M1 `SF311408`, M2 `SF311418` (modern methodology). Independently confirm API metadata and observed coverage on VM.
- [ ] Identify comparable money aggregates and rates for all five study geographies; UK M4, BoJ M2, ECB M2 have different definitions. Audit historical release dates and revisions.
- [ ] Establish a source/availability-date catalog for Mexico, USA, UK, Japan and euro area. Prefer a small comparable core indicator panel.
- [ ] Decide point-in-time index identification, sign convention, standardization and missing-data rules.
- [ ] Implement constrained Gaussian d=2 local-linear trend with marginalized likelihood; derive and verify equivalent PLS optimization.
- [ ] Implement a country-panel experimental loader with strict observation_date / available_date semantics.
- [ ] Benchmark signed average, PCA and Gaussian DFM on the same vintage information set.
- [ ] Specify a common external outcome for cross-index predictive validity; never compare raw factor RMSEs as if factors were identical.
- [ ] Freeze the pilot test years, crisis windows, quiet controls, horizons and primary evaluation metrics before running confirmation.
- [ ] Complete bibliography/Docling annotations only after verifying source availability and rights.
- [ ] Discuss authorship and prior-work citation with the earlier U.S. latent-risk collaborators.
