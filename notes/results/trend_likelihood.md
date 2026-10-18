# Exact second-difference trends and Gaussian diffuse REML

**Scope (2026-10-18).** A conventional smoothing-and-forecasting module for one **fixed** observed country-level index. It does not estimate a latent-risk index, establish financial-disturbance prediction, implement the separate Trend-Estimation research method, or claim real-time historical data. **PROVEN** below denotes algebra under explicit assumptions; **IMPLEMENTED** means source code in the underlying trend branch; **VERIFIED COMPUTATIONALLY** requires separately recorded test execution.

## 1. Model, notation, boundary conditions

Let observations be \(y=(y_1,\ldots,y_n)^\top\), \(n\ge3\), on an equally spaced grid, with \(y_t=\tau_t+\epsilon_t\). Define the \((n-2)\times n\) second-difference matrix \(D\): row \(i\) has \(1,-2,1\) at columns \(i,i+1,i+2\). There are no wrapped, clamped or extra artificial endpoint penalties. Let \(Q=D^\top D\). The Whittaker–Henderson / Hodrick–Prescott objective is

\[
J_\lambda(\tau)=\lVert y-\tau\rVert_2^2+\lambda\lVert D\tau\rVert_2^2,\qquad\lambda\ge0.
\]

**PROVEN (unique optimum):** Differentiation gives
\[
\nabla J_\lambda(\tau)=2(I+\lambda Q)\tau-2y,\quad
(I+\lambda Q)\widehat\tau=y.
\]
For nonzero \(v\), \(v^\top(I+\lambda Q)v=\lVert v\rVert^2+\lambda\lVert Dv\rVert^2>0\); the solution is unique. The matrix is symmetric positive definite and pentadiagonal. The code uses sparse linear solves, not an explicit inverse. The formula \(S_\lambda=(I+\lambda Q)^{-1}\) is analytical notation only. The branch additionally supports \(\lambda=\infty\) as the affine least-squares limit.

**PROVEN (nullspace and zero eigenvalues):** \(D\tau=0\) exactly when
\(\tau_{i+2}-\tau_{i+1}=\tau_{i+1}-\tau_i\) for every \(i\). All first differences are then identical, so \(\tau_i=a+bi\). Conversely, every affine sequence is annihilated by \(D\). Hence \(\dim\ker D=2\), \(\operatorname{rank}D=n-2\), and \(Q\) has **exactly two zero eigenvalues**, with all others strictly positive. The smoother fixes the affine subspace; \(S_\lambda y=y\) for affine \(y\). Also \(D\mathbf1=D(1,\ldots,n)^\top=0\), so smoothing preserves the first two time moments of \(y\).

**PROVEN (effective degrees of freedom):** If \(0,0,\mu_3,\ldots,\mu_n\) are the eigenvalues of \(Q\),
\[
\mathrm{edf}(\lambda)=\operatorname{tr}S_\lambda
=2+\sum_{j=3}^n(1+\lambda\mu_j)^{-1},
\quad \mathrm{edf}(0)=n,\quad
\lim_{\lambda\to\infty}\mathrm{edf}(\lambda)=2.
\]
The selected-inverse recursion in the underlying implementation computes this trace using banded Cholesky factors in \(O(n)\) space and time (subject to floating-point conditioning). A distinct implementation can use \(\mathrm{edf}=n-\lambda\,d[\log\det(I+\lambda Q)]/d\lambda\), deriving the derivative through a banded LDL factorization.

## 2. Gaussian model and exact PLS equivalence

Assume \(\epsilon_t\overset{\mathrm{iid}}\sim N(0,r)\), \(\eta_t\overset{\mathrm{iid}}\sim N(0,q)\), mutually independent, and
\[
\tau_t-2\tau_{t-1}+\tau_{t-2}=\eta_t \quad(t\ge3).
\]
The initial \(\tau_1,\tau_2\) receive **flat/diffuse** priors: no independent penalty on starting level and slope. For positive \(r,q\), the latent posterior density conditional on all \(y\) is proportional to
\[
\exp\left[-\frac{\lVert y-\tau\rVert^2}{2r}
-\frac{\lVert D\tau\rVert^2}{2q}\right].
\]
Multiplying its negative log by \(2r\) proves \(\lambda=r/q\). The Gaussian posterior mean and mode coincide. An RTS *retrospective* state smoother therefore recovers the exact PLS trend with these compatible boundaries.

Use the state \(x_t=(\tau_t,\tau_{t-1})^\top\),
\[
x_t=Fx_{t-1}+u_t,\quad
F=\begin{pmatrix}2&-1\\1&0\end{pmatrix},\quad
\operatorname{Var}u_t=\operatorname{diag}(q,0),\quad
y_t=(1,0)x_t+\epsilon_t.
\]
After observing \(y_1,y_2\), diffuse initialization gives \(m_{2|2}=(y_2,y_1)^\top\), \(P_{2|2}=rI_2\). For \(t\ge3\), let \(m_t^-=Fm_{t-1|t-1}\), \(P_t^-=FP_{t-1|t-1}F^\top+\operatorname{diag}(q,0)\), \(v_t=y_t-Hm_t^-\), \(s_t=HP_t^-H^\top+r\), \(K_t=P_t^-H^\top/s_t\). Then \(m_{t|t}=m_t^-+K_tv_t\), with a corresponding covariance update. The smoothing backward gain is \(J_t=P_{t|t}F^\top(P_{t+1}^-)^{-1}\); use a solve, not a dense inverse.

**Boundary caveat:** An additional stochastic level shock, a nonzero deterministic curvature drift, an informative initial-state prior, correlated or heteroskedastic measurement noise, or another endpoint convention changes the stochastic penalty or its equivalence.

## 3. Proper restricted likelihood versus joint-state residual fitting

Let \(m=n-2\) and define contrasts \(z=Dy\). Then
\[
z=\eta+D\epsilon\sim N_m(0,C),\qquad
C=qI_m+rDD^\top.
\]
Thus the **proper Gaussian restricted likelihood** (REML) is
\[
\ell_R(r,q)=-\tfrac12\left[
m\log(2\pi)+\log|C|+z^\top C^{-1}z
\right].
\]
The first two unrestricted polynomial coordinates have been eliminated. In the diffuse Kalman filter, the innovation likelihood
\[
\ell_R=-\tfrac12\sum_{t=3}^n
\{\log(2\pi s_t)+v_t^2/s_t\}
\]
is exactly the same likelihood. It is **not** an ordinary full-data marginal ML likelihood under a proper normalized prior for the initial state. Genuine finite-prior marginal ML would need a stated prior and its first two likelihood terms. **Minimizing the fitted latent-state joint quadratic is neither ML nor REML.**

For finite positive \(\lambda=r/q\), put \(q=r/\lambda\) and calculate normalized innovations \(v_t^*,s_t^*\) with \(r=1,q=1/\lambda\). Kalman gains and \(v_t^*\) do not depend on the common scale \(r\). Profiling yields
\[
\widehat r(\lambda)=\frac1m\sum_{t=3}^n(v_t^*)^2/s_t^*,\qquad
\widehat q=\widehat r/\lambda.
\]
Compare the resulting profile likelihood across ratio candidates and against relevant boundaries; the branch implementation instead optimizes the two log variances with explicit \(r=0\) and \(q=0\) alternatives. The numerical boundary report must be distinguished from any optimum on imposed optimization limits.

**Identifiability:** With \(n=3\), a single contrast has variance \(q+6r\); the two components are not separately identifiable. For \(n\ge4\), the off-diagonal structure of \(DD^\top\) distinguishes \(r\) and \(q\) in population, but a short, nearly affine or severely misspecified series can yield weak identification and/or a boundary optimum. A perfectly affine sample has an unbounded likelihood as both variances approach zero. Evaluate profiles, fitted bounds and uncertainty before interpreting a numerical ratio.

## 4. Causal horizon forecasts

At origin \(t\), **filtered** state \((m_{t|t},P_{t|t})\) uses observations available only through \(t\). Never extrapolate an RTS state smoothed using \(y_{t+1:n}\). For \(h\ge1\),
\[
m_{t+h|t}=F^h m_{t|t},\quad
P_{t+h|t}=F^hP_{t|t}(F^h)^\top+
\sum_{j=0}^{h-1}F^j\operatorname{diag}(q,0)(F^j)^\top.
\]
The mean forecast is \(Hm_{t+h|t}=m_{\mathrm{level}}+
h(m_{\mathrm{level}}-m_{\mathrm{previous}})\). Its **latent** variance is \(HP_{t+h|t}H^\top\); the **observation** variance additionally includes \(r\). The scalar process-noise contribution is \(q\sum_{j=1}^h j^2=q\,h(h+1)(2h+1)/6\). **Every parameter fit, index normalization and source-availability rule must also be origin-restricted.** A fixed-parameter filter that is causal does not excuse full-sample variance estimation.

## 5. Distinct tuning estimands

| Method | Selection objective | Interpretation |
| --- | --- | --- |
| Proper-prior marginal ML | Maximize density of complete observed \(y\), integrating latent states under explicit proper initial prior | Likelihood for that *specified* prior; not implemented |
| Diffuse REML | Maximize \(\ell_R(r,q)\), eliminating two affine coordinates | Gaussian innovation variance components; implemented |
| Generalized CV | Minimize \(n\lVert(I-S_\lambda)y\rVert^2/[n-\operatorname{tr}S_\lambda]^2\) | Observation-level smoothing choice; \(\lambda=0\) has zero denominator |
| Time-series horizon-\(h\) forecast loss | Minimize average \(L(y_{t+h},\widehat y_{t+h|t}(\lambda))\) over past-only origins | Predictive objective depending on horizon, target, loss and refit protocol; not implemented in this module |

The criteria are not interchangeable. This module is not a claim of novelty for forecast-optimal cross-validation or a model comparison across differently scaled country factors.

## 6. Assumptions, numerical checks, and failures

The tests on the underlying trend branch target small-\(n\) sparse-versus-dense solutions; analytic affine nullspace and EDF; RTS–PLS equivalence; exact dense Gaussian-contrast REML; finite-difference/analytic likelihood score; Gaussian synthetic parameter recovery; extremes/boundaries; and invariance of origin forecasts under perturbing *later* observations. Their results require CI evidence rather than an unverified assertion of passing. Separate local alternative code was tested on 2026-10-18 with **81 passing synthetic tests**, but that count **does not validate** the underlying remote implementation.

Model failures include irregular observations, missing dates, measurement serial correlation, non-Gaussian events, structural breaks, seasonal signals, time-varying variances, weakly identified ratios, excessive conditioning and retrospective factor estimation. All physical-country experiments, crisis/event predictive ability, first-release vintage validation, and integrated index forecasts remain **UNKNOWN / NOT RUN**.

## 7. Existing literature, attribution and rights

- Whittaker (1923), *On a New Method of Graduation*, and Hodrick & Prescott (1997), *Postwar U.S. Business Cycles*, provide foundational second-difference regularization.
- Guerrero (2007), “Time series smoothing by penalized least squares,” *Statistics & Probability Letters* 77, 1225–1234; DOI [10.1016/j.spl.2007.03.006](https://doi.org/10.1016/j.spl.2007.03.006). His general formulation allows a nonzero reference mean in differences; here it is fixed at zero. The supplied publisher personal copy **cannot be distributed in this public repository**.
- Weinert (2007), “Efficient computation for Whittaker–Henderson smoothing,” *Computational Statistics & Data Analysis* 52, 959–974; DOI [10.1016/j.csda.2006.11.038](https://doi.org/10.1016/j.csda.2006.11.038). Established banded efficient solution and state-space/GCV linkage.
- Harvey (1989), *Forecasting, Structural Time Series Models and the Kalman Filter*; Durbin & Koopman (2012), *Time Series Analysis by State Space Methods*, 2nd ed. Standard local-linear-trend and diffuse Gaussian state-space references. Precise page/theorem matching not independently verified here.
- Cortés-Toto, Guerrero & Reyes (2017), *Communications in Statistics – Simulation and Computation* 46, 1492–1507; DOI [10.1080/03610918.2015.1005236](https://doi.org/10.1080/03610918.2015.1005236). Distinct smoothing-parameter criteria.
- Biessy (2026), “Whittaker–Henderson smoothing revisited,” *ASTIN Bulletin* 56, DOI [10.1017/asb.2025.10061](https://doi.org/10.1017/asb.2025.10061). Contemporary actuarial framework including marginal-likelihood selection; **preexisting method**.

No PDF, license-restricted source content or raw market file is committed here.