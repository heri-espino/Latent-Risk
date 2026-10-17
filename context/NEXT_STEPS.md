# Next steps

- [x] Audit the repository bootstrap: 12 tests, Ruff, structural validator and Sphinx passed on commit `075f9027` (https://github.com/heri-espino/Latent-Risk/actions/runs/38994859776); PR-only change checker and LaTeX compilation were not run.
- [x] Implement an initial candidate source catalog and downloader with 19 offline tests passing, Ruff, structure and Sphinx pass (https://github.com/heri-espino/Latent-Risk/actions/runs/38998827014); **no live data have been retrieved yet**.
- [ ] Run the downloader on Conda VM, inspect every manifest status, preserve local SHA256 provenance and report missing or short-coverage series.
- [ ] Obtain current official Mexico M1/M2 IDs and matching macro sources for UK/Japan/euro area and national rates; audit historical release dates and revisions.
- [ ] Establish a source/availability-date catalog for Mexico, USA, UK, Japan and euro area. Prefer a small comparable core indicator panel.
- [ ] Decide point-in-time index identification, sign convention, standardization and missing-data rules.
- [ ] Implement constrained Gaussian d=2 local-linear trend with marginalized likelihood; derive and verify equivalent PLS optimization.
- [ ] Implement a country-panel experimental loader with strict observation_date / available_date semantics.
- [ ] Benchmark signed average, PCA and Gaussian DFM on the same vintage information set.
- [ ] Specify a common external outcome for cross-index predictive validity; never compare raw factor RMSEs as if factors were identical.
- [ ] Freeze the pilot test years, crisis windows, quiet controls, horizons and primary evaluation metrics before running confirmation.
- [ ] Complete bibliography/Docling annotations only after verifying source availability and rights.
- [ ] Discuss authorship and prior-work citation with the earlier U.S. latent-risk collaborators.
