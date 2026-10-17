# Definitions

## DEF-0001 — A point-in-time information set

**Question:** What can a historical forecaster actually use?

Let `observation_date` be the economic measurement date and `available_date` the earliest date the published value could be used. At forecast origin `t` define

$$\mathcal{I}_t = \sigma\!\left(X_{c,s,j}\colon a(c,s,j)\le t\right),$$

where `a` is the available date. The proposed pseudo-real-time estimator must be measurable with respect to `\mathcal I_t`, including its transformations, model parameters and uncertainty estimates.

**Assumptions:** Publication dates and any known vintages are recorded correctly; country/source identifiers are unambiguous.  
**Interpretation:** A measurement from January may not enter a January forecast if released in February.  
**Failure case:** Conditioning on all 2026 indicator values while evaluating a purported 2007 forecast.  
**Status:** `PROVEN` as a definition of information availability, not a claim of empirical point-in-time data availability.  
**Reference:** General chronological forecasting principle; exact source auditing remains open.

## DEF-0002 — Gaussian penalized trend and likelihood ratio

**Question:** Which variance ratio plays the role of the smoothing parameter?

For an extracted scalar index `y_t`, propose

$$y_t = \tau_t+\epsilon_t,\qquad
\epsilon_t\overset{iid}{\sim}N(0,r),\qquad
\Delta^2\tau_t=\eta_t,\quad
\eta_t\overset{iid}{\sim}N(0,q).$$

Under independent innovations, a compatible diffuse treatment of the polynomial nullspace, and `r,q>0`, the conditional quadratic objective is, up to a positive factor and boundary terms,

$$\|y-\tau\|^2+\lambda\|D_2\tau\|^2,
\qquad \lambda=\frac{r}{q}.$$

**Mechanism:** Gaussian negative log densities are scaled sums of squared innovations; multiply by `2r`.  
**Important distinction:** Marginal-likelihood MLE integrates over latent states; simply minimizing this quadratic for each `\lambda` does **not** estimate `\lambda` by ML.  
**Failure case:** A generic local linear trend with an additional unconstrained level shock is not exactly the stated penalty.  
**Status:** `PROVEN` for the stated standard Gaussian model; exact numerical state-space implementation equivalence `UNKNOWN`.  
**References:** Guerrero (2007); Durbin and Koopman (2012). Pages/equations have not yet been cross-verified in this new corpus.

## DEF-0003 — Model-specific forecast failure

**Question:** What does it mean for an index trend forecast to fail?

For country `c`, index model `m`, origin `t`, and horizon `h`, define

$$ e^{(m)}_{c,t,h} =
f^{(m),\mathrm{target}}_{c,t+h}-\widehat f^{(m)}_{c,t+h\mid t},
\qquad z^{(m)}_{c,t,h} =e^{(m)}_{c,t,h}/\widehat\sigma^{(m)}_{c,t,h}.$$

**Assumptions:** Model-defined target and its vintage are disclosed; `\widehat\sigma>0` is estimated using only the origin information set.  
**Mechanism:** Standardization makes the error interpretable in units of historical forecast uncertainty under an explicit calibration scheme.  
**Failure case:** Raw cross-model RMSE rankings compare different factor targets and are not automatically meaningful.  
**Status:** `PROPOSED` operational statistical definition; thresholds and calibration not frozen.  
**Reference:** See research protocol in `experiments/EXP-0001.md`.
