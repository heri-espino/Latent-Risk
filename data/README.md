# Source-data policy

No new dataset is included. Long-form file schema: `country, observation_date, available_date, variable, value, source`. `observation_date` describes the economic measurement; `available_date` is the earliest released/observable date. Retain vendor/source IDs, transformations, calendars, release lags, revisions/vintage IDs, licensing and checksums in future metadata.

The CSV values in examples and tests are **synthetic**. Do not mistake them for actual Banxico or market observations.

Potential official sources for audit:
- [Banco de México SIE API](https://www.banxico.org.mx/SieAPIRest/swagger/index.html)
- [IMF data](https://data.imf.org/)
- [OECD Data Explorer](https://data-explorer.oecd.org/)

Store raw/processed data locally (gitignored). Only commit small, legally redistributable fixtures or metadata manifests as appropriate; record exact download date and observations available by each backtest origin.
