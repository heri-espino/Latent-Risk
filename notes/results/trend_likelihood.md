# Penalized trend smoothing and Gaussian diffuse likelihood

**2026-10-18 — mathematical note.** Scope: a **fixed, preconstructed scalar index** observed on a regular grid. Standard results below are **PROVEN under their stated assumptions**; the numerical API is **IMPLEMENTED** and tested synthetically. No latent country indices, historical first-release vintages, or financial-disturbance prediction has been tested.

## Definition: second-difference penalization

For \(n\geq3\), define \(y=(y_1,\ldots,y_n)^\top\), trend \(\tau\), and the \((n-2)\times n\) matrix \(D=D_2\), whose \(j\)th row has entries \((1,-2,1)\) in columns \(j,j+1,j+2\). In particular, there are **no extra endpoint constraints** (no periodic continuation or forced terminal slope).

Consider
\[
J_\lambda(\tau)=\|y-\tau\|_2^2+\lambda\|D\tau\|_2^2,\quad \lambda\geq0.
\]
Set \(Q=D^\top D\), \(A_\lambda=I+\lambda Q\). Differentiation yields
\[
\nabla J_\lambda=2(A_\lambda\tau-y),\quad
v^\top A_\lambda v=\|v\|^2+\lambda\|Dv\|^2>0
\]
for every nonzero \(v\), proving the unique minimizer solves
\[
 A_\lambda\hat\tau=y,\qquad \hat\tau=S_\lambda y,\quad S_\lambda=A_\lambda^{-1}.
\]
The matrix \(A_\lambda\) is **pentadiagonal**, symmetric positive definite. The API solves this sparse system without explicitly forming a dense inverse. Any finite-sample endpoint behavior is determined exactly by \(D^\top D\).

## Proposition T-001: nullspace and degrees of freedom (PROVEN)

The condition \(D\tau=0\) says \(\tau_{t+2}-\tau_{t+1}=\tau_{t+1}-\tau_t\); hence \(\tau_t=a+bt\). Therefore \(\ker D=\operatorname{span}(\mathbf 1,(1,2,\ldots,n)^\top)\), of dimension **two**; \(\operatorname{rank}Q=n-2\), so **exactly two eigenvalues of \(Q\) are zero**, the other \(n-2\) are strictly positive. The affine component is reproduced exactly. Also \(D\mathbf1=Dt=0\) implies preservation of the sum and linear first moment of observations.

Writing the eigenvalues as \(0,0,\mu_3,\ldots,\mu_n\), with \(\mu_j>0\), gives fitting effective degrees of freedom
\[
\mathrm{df}(\lambda)=\mathrm{tr}(S_\lambda)
=2+\sum_{j=3}^n(1+\lambda\mu_j)^{-1}.
\]
Thus \(\mathrm{df}(0)=n\), \(\mathrm{df}(\infty)=2\), and \(\mathrm{df}'(\lambda)<0\) for positive finite \(\lambda\). As \(\lambda\to\infty\), the solution tends to the OLS affine trend. An \(O(n)\) banded Cholesky/selected-inverse recurrence computes the exact trace to floating-point precision, without dense inversion. **Fitting df is different from the \(n-2\) residual contrast dimension used by REML.**

## Proposition T-002: PLS equals a particular state-space smoother (PROVEN)

Assume independent Gaussian innovations:
\[
 y_t=\tau_t+\epsilon_t,\quad\epsilon_t\stackrel{iid}{\sim}N(0,r);
 \qquad \Delta^2\tau_t=\eta_t,\quad\eta_t\stackrel{iid}{\sim}N(0,q)
 \quad(t\geq3).
\]
Here \(r=\sigma_\epsilon^2\), \(q=\sigma_\eta^2\), with \(r,q>0\), and the two initial trend coordinates have a *flat/diffuse prior*. Then
\[
 -2\log p(\tau\mid y,r,q)
 =r^{-1}\|y-\tau\|^2+q^{-1}\|D\tau\|^2+\mathrm{const}.
\]
Multiplication by \(r\) gives the PLS objective with \(\boxed{\lambda=r/q}\). The Gaussian posterior mean equals its mode, so the **full-sample state smoother** equals \(S_{r/q}y\). This equivalence is false in general when the initial slope has a finite informative prior, an extra random level shock is introduced, or the data are irregularly spaced.

Use the two-dimensional state
\[
\alpha_t=\begin{pmatrix}\tau_t\\\tau_{t-1}\end{pmatrix},
\quad F=\begin{pmatrix}2&-1\\1&0\end{pmatrix},
\quad H=(1,0),\quad Q_s=\mathrm{diag}(q,0),
\]
so \(\alpha_t=F\alpha_{t-1}+(\eta_t,0)^\top\) and \(y_t=H\alpha_t+\epsilon_t\). RTS backward smoothing is implemented only for **retrospective estimation** and is not used for forecasts.

## Proposition T-003: exact diffuse/restricted marginal likelihood (PROVEN)

The first two independent measurement updates of the diffuse coordinates give, exactly,
\[
 a_{2|2}=(y_2,y_1)^\top,\qquad P_{2|2}=rI_2.
\]
This is not an approximation using an arbitrary huge initial variance. For \(t=3,\dots,n\):
\[
\begin{aligned}
a_{t|t-1}&=F a_{t-1|t-1},&
P_{t|t-1}&=F P_{t-1|t-1}F^\top+Q_s,\\
v_t&=y_t-Ha_{t|t-1},&
s_t&=HP_{t|t-1}H^\top+r,\\
K_t&=P_{t|t-1}H^\top/s_t,&
a_{t|t}&=a_{t|t-1}+K_tv_t,\\
P_{t|t}&=P_{t|t-1}-K_ts_tK_t^\top.
\end{aligned}
\]
The **variance-dependent normalizer must not be omitted**:
\[
\boxed{\ell_R(r,q)=\frac12\sum_{t=3}^n\left[\log(2\pi s_t)+v_t^2/s_t\right].}
\]
Equivalently, since \(D\tau=\eta\) and \(Dy=\eta+D\epsilon\), the \(n-2\) Gaussian error contrasts \(z=Dy\) satisfy
\[
 z\sim N(0,C),\quad C=qI_{n-2}+rDD^\top,\quad
\ell_R=\tfrac12\big[(n-2)\log(2\pi)+\log|C|+z^\top C^{-1}z\big].
\]
The change of coordinates \(y\mapsto(y_1,y_2,Dy)\) has unit absolute determinant. Integrating out the two diffuse coordinates yields this **proper Gaussian distribution of contrasts**. It is commonly called **restricted maximum likelihood (REML)**, or the exact diffuse marginal likelihood; it is **not** ordinary full-data ML with a proper finite prior. Minimizing the *joint fitted-state penalty* over the trend is not a marginal likelihood because it ignores the determinant term.

For \(A_r=DD^\top\), \(A_q=I\), the reference analytical likelihood derivative is
\[
 \partial_{\theta_j}\ell_R
 =\tfrac12\big[\mathrm{tr}(C^{-1}A_j)-z^\top C^{-1}A_j C^{-1}z\big],
 \quad \theta=(r,q).
\]
Numerical tests compare the Kalman innovations, dense contrast likelihood, and finite differences of this analytical score.

## Identifiability, limits and endpoints

For \(n=3\), \(C=q+6r\), so only this sum is identifiable. For \(n\geq4\), \(DD^\top\) is not a scalar multiple of \(I\), so the covariance parameters are structurally identifiable, but practically weakly estimated with limited data. The fitting API conservatively requires \(n\geq5\). It optimizes log variances with declared finite search bounds, separately compares **exact** \(q=0\) and \(r=0\) models, and reports the selected class: interior, q_zero, r_zero or search_limit. The interpretations are \(\lambda=\infty\) (deterministic affine trend) and \(\lambda=0\) (interpolation), respectively. Both zero gives singular data covariance and is excluded. An exactly affine data series has no finite maximum and is rejected. A boundary optimum **does not prove** a population variance is zero. No confidence intervals or likelihood-ratio boundary reference distributions are implemented.

## Proposition T-004: filtering rather than smoothing for forecasting (PROVEN)

At forecast origin \(t\), fit both variances and the *filtered* state using \(y_1,\dots,y_t\) only. Never extrapolate the retrospective \(E(\tau_t\mid y_{1:n})\), which conditions on future observations. For horizon \(h\geq1\), define \(w_h=(h+1,-h)^\top\). Then
\[
\begin{aligned}
E[y_{t+h}\mid y_{1:t}]&=w_h^\top a_{t|t},\\
\mathrm{Var}(\tau_{t+h}\mid y_{1:t})&=
w_h^\top P_{t|t}w_h+
q\,h(h+1)(2h+1)/6,\\
\mathrm{Var}(y_{t+h}\mid y_{1:t})&=
\mathrm{Var}(\tau_{t+h}\mid y_{1:t})+r.
\end{aligned}
\]
The forecast API accepts a **zero-based** origin and internally slices the observations before filtering. Its optional REML refit also uses that prefix. In the tests, arbitrary changes to every subsequent observation leave the forecast, fitted parameters and uncertainty **exactly unchanged**. Forecast horizons are observation steps, not verified economic release dates.

## Different scientific estimands

| Selection rule | Quantity optimized | Main distinction |
| --- | --- | --- |
| Full marginal ML | Joint data probability after integrating states using a **proper** initial prior | Requires a specified prior and is not implemented |
| Diffuse REML | Gaussian probability of \(n-2\) error contrasts | Implemented for estimating \(r,q,\lambda=r/q\), not for optimizing forecasts |
| GCV | \(n\|y-S_\lambda y\|^2/[n-\mathrm{tr}(S_\lambda)]^2\) | Smoothing-based predictive proxy, not a chronologically held-out forecast |
| Rolling-origin horizon-\(h\) CV | Mean of squared **past-only** \(h\)-step errors at chosen origins | Forecast-risk estimand, distinct from likelihood and GCV; not implemented |

A selected subset of the same full-sample residual vector is not a genuinely held-out forecasting loss.

## Literature and scientific boundaries

The prior work is established: Whittaker (1923), *On a New Method of Graduation*; Guerrero (2007), *Statistics & Probability Letters* 77:1225–1234, DOI [10.1016/j.spl.2007.03.006](https://doi.org/10.1016/j.spl.2007.03.006), whose formulation permits nonzero difference mean and general observation covariance; Weinert (2007), *Computational Statistics & Data Analysis* 52:959–974, DOI [10.1016/j.csda.2006.11.038](https://doi.org/10.1016/j.csda.2006.11.038), for efficient banded smoothing and GCV; Cortés-Toto, Guerrero & Reyes (2017), DOI [10.1080/03610918.2015.1005236](https://doi.org/10.1080/03610918.2015.1005236), for distinct optimality criteria; Biessy (ASTIN Bulletin 2026, first online 2025), DOI [10.1017/asb.2025.10061](https://doi.org/10.1017/asb.2025.10061), for modern marginal likelihood and extrapolation; Koopman (1997), DOI [10.1080/01621459.1997.10473685](https://doi.org/10.1080/01621459.1997.10473685), and Durbin & Koopman (2012), DOI [10.1093/acprof:oso/9780199641178.001.0001](https://doi.org/10.1093/acprof:oso/9780199641178.001.0001), for exact diffuse initialization and state-space likelihood.

**Model failures:** serial correlation or heteroskedasticity, breaks, heavy tails, observations missing on an irregular grid, unmodeled initial trends or seasonality, and weakly identified variance components. A source's **current-vintage history does not establish first-release availability**. Forecast predictiveness and crisis signals remain UNKNOWN.

**Reproduce:** python -m pytest tests/test_trends_gaussian.py; ruff check .; python scripts/validate_research.py; python scripts/check_change_protocol.py --base-ref origin/main; sphinx-build -b html docs docs/_build/html. The synthetic tests require no licensed PDFs, raw files or keys. No licensed PDF is included in this branch.
