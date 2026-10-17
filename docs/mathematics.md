# Mathematical conventions

- **Measurement**: indicator panel \(X_{c,t}\) maps to an estimated financial-risk index \(f_{c,t}\) with an identified high-stress orientation. Different models need not produce comparable units.
- **Trend extraction**: for \(d=2\), a proposed PLS criterion is \(\lVert f-\tau\rVert_2^2 + \lambda\lVert D_2\tau\rVert_2^2\).
- **Likelihood**: under independent Gaussian measurement variance \(r\) and second-difference state variance \(q\), and appropriate initial states, the smoothing coefficient is \(\lambda=r/q\). Its *marginal* likelihood is not the residual-sum-of-squares function.
- **Forecast assessment**: \(e_{c,t,h}=f_{c,t+h}^{\mathrm{target}}-\widehat f_{c,t+h\mid t}\). Standardized exceedance thresholds require a historically calibrated predictive variance and cannot be justified by Gaussianity alone.

See [definitions](https://github.com/heri-espino/Latent-Risk/blob/main/notes/definitions.md) and [the prospective protocol](https://github.com/heri-espino/Latent-Risk/blob/main/experiments/EXP-0001.md). This documentation describes a proposed mathematical specification; the MLE solver is **not implemented**.
