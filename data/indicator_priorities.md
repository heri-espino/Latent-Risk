# Candidate indicator selection for the latent-risk study

**Status: RESEARCHED / PROPOSED; not an empirically validated model or complete dataset.**
**Date:** 2026-10-17. Geographies: Mexico, United States, United Kingdom, Japan, euro area.

## Key decision

The study's primary outcome concerns failures of forecasts of a latent *market financial-stress* index at horizons 1, 3 and 6 months. The earlier catalog prioritized readily accessible money-stock measures M1/M2/M4. These are economic-context variables, **not the strongest first-choice measurements of sudden market stress**. They have lagged release dates, strong trends and cross-country definitional differences. Keep them in the raw-source archive as auxiliary macro features rather than mandatory inputs.

The OFR Financial Stress Index organizes daily stress by credit, equity valuations, funding, safe assets and volatility; the ECB CISS groups 15 raw measures into financial intermediaries, money, equity, bond and FX markets; Banxico's IEMF uses 36 standardized variables in six categories. These provide an external conceptual basis for selecting features.

## Ranked data domains and candidate constructions

| Rank | Domain | Primary measurements or transforms | Coverage | Source/provenance caveat |
| --- | --- | --- | --- | --- |
| 1 | Equity losses and instability | local equity log returns, negative return, 21-day realized volatility, 63-day drawdown | All five have candidate Yahoo equity benchmarks already cataloged | Train-only scaling, no future prices |
| 1 | FX stress | absolute/directional currency depreciation and 21-day FX realized volatility | MEX/GBR/JPN/EA candidates in Yahoo/Banxico; for USA use a distinct reference design, not fictitious USD/USD | Harmonize quotation direction, do not label all FX depreciations identically stressful for reserve currencies |
| 1 | Credit risk premia | corporate IG/HY OAS, bank funding spreads, sovereign credit spreads when licensed | Incomplete; U.S. HY and IG FRED codes known; other local markets less accessible | ICE OAS data on FRED restricted to 3 years since April 2026; cannot cover 2008 unless licensed history procured |
| 1 | Money/funding stress | local money market–risk-free spreads, interbank–OIS spread / post-LIBOR equivalents | UK SONIA is already cataloged; several local spread legs missing | LIBOR discontinued; changes around 2022 require explicit definitions |
| 2 | Bank equity / financial intermediaries | bank-sector returns and realized volatility, market-to-book measures | No consistent five-country official sample acquired yet | Do not mistake a bank index for a total-market stress index |
| 2 | Bond stress | sovereign yields, yield movements, yield-curve slope and unusual volatility | U.S. DGS2/DGS10 attempted but blocked on VM; Mexico CETES downloaded/unconfirmed | Currency-specific yield spread is not automatically a sovereign default-risk spread |
| 3 | Slow vulnerabilities | BIS one-sided credit-to-GDP gap, debt-service ratio, housing-price gap | BIS countries/coverage to verify | Quarterly and generally longer warning horizons; keep separate from daily/weekly stress index |
| 3 | Money/reserves | M1/M2/M4, reserves | Preliminary country series cataloged | Publication delays, definitions, scaling, policy interventions; not primary stress signal |
| Control | Global shocks | VIX, US credit stress, USD broad index, gold/oil | Some Yahoo candidates | Global conditions are shared covariates, not necessarily the local latent factor |

### Example pilot input panel

Start with **country-specific equity returns, equity 21-day trailing realized volatility, drawdowns, FX returns and FX trailing volatility where meaningful**. Add a verified credit/funding measure when history and licensing permit. Use simple fixed transformations and only past observations at each forecast origin. For US, keep FX as a global dollar control instead of forcing an artificial national FX series.

Do not combine equity prices, monetary-stock levels and interest-rate percentages *as raw magnitudes*. Refit normalization and stress direction only on each historical training window. Global VIX should be a control and benchmark, not a universal national risk indicator.

## External reference indices, deliberately separate from inputs

- **Mexico**: Banco de México **IEMF**, from official *Reportes de Estabilidad Financiera* tabular data. Official 2025 tables explain that the index uses 36 standardized indicators across six categories. Linked source published in December 2025: https://www.banxico.org.mx/TablasWeb/reporte-estabilidad-financiera/5-REF-2025-2S-RSF/5046723B-F653-46D4-A92D-A4190FCDFB65.html . Compilation into one full history, version dating and licensing are outstanding.
- **USA, UK, Euro area**: official ECB **New CISS**, daily. Exact keys `CISS.D.US.Z0Z.4F.EC.SS_CIN.IDX`, `CISS.D.GB.Z0Z.4F.EC.SS_CIN.IDX`, `CISS.D.U2.Z0Z.4F.EC.SS_CIN.IDX`. See https://data.ecb.europa.eu/data/datasets/CISS . Added to the `ecb` downloader category as **external_stress_benchmark**, NOT as a model predictor.
- **USA**: Fed of St Louis `STLFSI4` (weekly, 18-series version) and Chicago Fed `NFCI` (weekly *financial conditions*, not equivalent to stress), listed under `fred`; https://fred.stlouisfed.org/series/STLFSI4 and https://fred.stlouisfed.org/series/NFCI . Both affected by user's FRED connectivity problem; model variants and vintages need scrutiny.
- **Japan**: no equivalent independently validated single external stress series selected yet. This is a genuine **gap**, not grounds to silently compare incomparable reference indices.

External published indices can share components with our factor. **Concordance with IEMF/CISS is not independent crisis prediction**. Do not place CISS/IEMF in the latent-factor input panel and simultaneously score that factor against CISS/IEMF. The external outcomes used for forecast utility should be prespecified (e.g., genuinely future realized volatility or crisis-window event dates) and tested against a strong market baseline.

## Evidence from the literature and data institutions

1. Office of Financial Research (OFR): FSI indicator categories and regions: https://www.financialresearch.gov/financial-stress-index/ and https://www.financialresearch.gov/financial-stress-index/files/indicators/
2. European Central Bank, Holló et al., CISS construction: https://data.ecb.europa.eu/data/datasets/ciss/data-information ; https://www.ecb.europa.eu/pub/pdf/scpwps/ecbwp1426.pdf
3. Banco de México, IEMF table/method: https://www.banxico.org.mx/TablasWeb/reporte-estabilidad-financiera/5-REF-2025-2S-RSF/5046723B-F653-46D4-A92D-A4190FCDFB65.html
4. Bank for International Settlements, credit-to-GDP gaps and debt-service ratios as longer-horizon indicators: https://data.bis.org/topics/CREDIT_GAPS and https://www.bis.org/publications/working-paper-421-evaluating-early-warning-indicators-banking-crises-satisfying-policy-requirements
5. FRED ICE corporate credit spread limitation: https://fred.stlouisfed.org/series/BAMLH0A0HYM2 (April 2026 onward, 3 years only).

## Pre-registered pilot comparison (proposal only)

- **Model**: signed fixed composite, one-factor PCA, Gaussian DFM, plus volatility baseline on a matched set of vintage-audited indicators.
- **Frequency**: weekly market inputs are preferable initially, with monthly aggregation only if justified by horizons; weekly and monthly studies are separate protocols.
- **Selection**: eligibility based on actual earliest/latest observation, source coverage, available-date accuracy and concept stability, *before* testing crisis episodes.
- **Validation**: (1) secondary index concordance with independently published IEMF/CISS (with overlap caveat); (2) primary predictive test against future observed market stress not directly copied as the target index; (3) calibration, false alarms, and stress-versus-quiet controls.
- **Limits**: long-run credit and debt measures are a separate vulnerability extension with different horizons. Gold/oil/M1/M2 are optional sensitivity covariates, not required core measurements. No significance, crisis detection, or model superiority claimed.

## Open actions

1. Run updated ECB downloads, inspect CISS coverage; audit Banxico IEMF public historical tables without inventing unavailable data.
2. Inspect VM success/failure manifest before promising full coverage; FRED failed previously.
3. Identify and license sufficiently long corporate/sovereign credit-spread histories and interbank funding series; do not rely on 3-year US credit spreads for 2008.
4. Freeze target definition, factor anchors, index transformations, matched times and available-date rules before experimenting.

## Signed oil-futures price domain (2026-10-17 correction)

WTI `CL=F` can have nonpositive settlements: CFTC records −$37.63/b for the
May 2020 contract on 2020-04-20 (https://www.cftc.gov/PressRoom/PressReleases/8315-20).
No primary latent-factor model should silently compute ordinary log returns
on this series or replace negative futures prices by absolute values. If oil
enters as an optional global shock control, first verify the actual local
nonpositive dates, a continuous-contract roll rule, and a past-only scale for
any signed price-change transform. See ADR-0006 and
`data/audits/2026-10-17-source-quality-wti.md`.

## Bilateral FX versus five-country BIS effective FX (2026-10-17)

**New source candidate now IMPLEMENTED, not live-tested:** BIS daily broad
nominal effective exchange rate, `WS_EER` keys `D.N.B.MX`, `D.N.B.US`,
`D.N.B.GB`, `D.N.B.JP`, `D.N.B.XM`. Source methodology is consistent
across all five economies and has appreciation-positive index orientation.
A uniform depreciation-oriented transform is `-Δlog(E)` with trailing
volatility calculated causally. Country partner baskets/weights differ, so
uniform definition does not mean identical exposure to every partner.
Daily observation labels are **not** BIS public release timestamps, and
trade weights may be revised; no contemporaneous availability claim is made.
Preserve existing bilateral USD FX and DXY as robustness candidates; avoid
silently double-counting overlapping currency measures in the core factor.
See ADR-0008 and `data/README.md`. BIS API docs:
https://stats.bis.org/api-doc/v2/ .
