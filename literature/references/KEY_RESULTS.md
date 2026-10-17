# Cross-paper key results and open connections

**No original Latent-Risk theorem or international empirical result is asserted here.** This is an annotated synthesis of prior work and its scope.

## Penalized smoothing and likelihood
- **Guerrero (2007)** formulates time-series PLS trend smoothing with a dth-difference penalty and discusses a smoothness index; `Guerrero2007`. His setup includes a reference mean for differences; our proposed primary trend model restricts it to zero.
- **Biessy (2026)** revisits Whittaker–Henderson smoothing, including selecting smoothing parameters by a marginal likelihood; `Biessy2026`. This establishes that marginal-likelihood smoothing is prior art, not a novel Latent-Risk invention.
- **Important difference:** The proposed exact state-space equivalence with a *constrained* d=2 local-linear trend must be proved/tested numerically for the eventual implementation, especially diffuse initial states and any allowed level innovations.

## Smoothing and regime changes
- **Islas, Guerrero and Silva (2019)** apply a multi-state Markov-switching model to a controlled-smoothness trend in Mexican remittance forecasting; `Islas2019`. Thus trend extraction followed by a regime-switching model is not new by itself.
- **Relevance:** Motivate explicitly testing whether regime changes explain failures of a trend-extrapolation forecast. No assumption that the same result transfers to country latent financial-risk indices.

## Financial risk measurement
- The first financial-stress index candidates are a transparent signed composite, one-component PCA and a conventional DFM. The international relative effectiveness is **UNKNOWN**; exact peer-reviewed sources for these index methods remain to be incorporated and verified before a literature review claim.

## Cross-source gaps
1. No verified evidence yet shows smoothed latent-risk forecast exceedances add information beyond volatility.
2. No standardized cross-country factor scale is established merely by standardizing to unit training variance.
3. No source here establishes that one particular model uniquely distinguishes crises from shocks.
4. Historical release dates and data vintages may be unavailable for some monetary/reserve series.

## Verification convention
These high-level descriptions were checked against the accessible user-provided article text and metadata; **specific page/equation claims remain unset rather than invented**. Consult the authorized PDFs before adding technical proof citations.
