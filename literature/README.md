# Literature corpus

Only three primary subfolders belong directly under `literature/`:

- `pdf/`: original PDFs, only with redistribution permission. A copyright-restricted personal copy must **not** be placed in this public GitHub repository.
- `markdown/`: corresponding Docling text/math extraction when permitted. Do not treat extraction alone as equation verification.
- `references/`: structured research cards keyed to BibTeX records.

[MANIFEST.csv](MANIFEST.csv) tracks each source, licensing and verification status; [references/KEY_RESULTS.md](references/KEY_RESULTS.md) synthesizes verified results and gaps. Add one new bibliography card with `python scripts/new_literature_entry.py --key CitationKey --title "..." --authors "..." --year 2020`.

Filename convention: `CitationKey.pdf`, `CitationKey.md` (Docling extraction), `references/CitationKey.md`. Leave a path blank in the manifest if the associated source file is absent. An annotated card is not proof that PDF distribution is permitted.

Study background papers include Guerrero (2007) PLS smoothing, Islas et al. (2019) Mexican remittance trend + switching model, and Biessy (2026) Whittaker–Henderson marginal-likelihood framework. These are **related work**, not Latent-Risk results. Confirm any reused technical theorem or page label from an authorized PDF before assigning stronger verification status.
