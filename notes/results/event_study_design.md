# Event study and genuinely falsifiable forecast-failure hypotheses

**Authored:** 2026-10-18. **Status:** PROPOSED; synthetic-only score helpers IMPLEMENTED in separate source files; **no empirical test performed**. Historical event list and documentary sources: [crisis_protocol.md](../literature/crisis_protocol.md). This document is not proof of predictive capability.

## 1. Primitive objects and clocks

Countries c ∈ {MX, US, UK, JP, EA}; model m identifies a **frozen, independently constructed** risk-index definition (including standardized signs and factor rotation); forecast origin o; index target period u > o; forecast horizon h = u−o in observation steps. The prediction is \hat y^{(m)}_{c,u|o}, trained exclusively from an information set I_o defined by audited **available** timestamps. The published target is y^{(m,v)}_{c,u}, with declared vintage v and actual earliest availability time a(c,m,u,v) ≥ u. Forecast error e_{c,o,h} = y_{c,u}^{(m,v)} − \hat y_{c,u|o}^{(m)} becomes observable at **alarm time t = a(c,m,u,v)**, not at forecast origin o. If no historical first-release vintage is available, report the reconstruction as *current-vintage pseudo-out-of-sample*, not genuine historical real-time.

Use non-overlapping terminology:
- **H_A: Descriptive association.** Surprise/forecast failure elevated in externally dated stressed **periods** relative to pre-specified calm controls. No timing/predictive assertion.
- **H_D: Concurrent detection.** An alarm at t is associated with a regime/stress change occurring **at or before t**, with its evidence available by t. This cannot be counted as lead time.
- **H_E: Early warning.** An alarm already observable at t forecasts a *different, independently dated* stress onset s with s > t; comparator models must have the same information I_t. An alarm after s is a late/detection alarm and receives **zero** early-warning credit.

Hypotheses must use the same indexed observed outcome within comparisons. Different PCA/composite/DFM indices are not interchangeable scalar targets; compare them instead against a common independent external outcome.

## 2. Scores and calibration (proposed primary)

At t = available time, define the unsigned normalized surprise

    S_{c,o,h}^{(m)} = |e_{c,o,h}| / max( \hat sigma_{c,o,h}^{(m)}, epsilon_c )

where sigma is an estimated conditional forecast-error standard deviation fit strictly on errors whose **targets were available** before o; epsilon is a **predeclared training-only** numerical floor, not hindsight regularization. If a defensible positive sigma is not available, mark score missing, not infinite. A robust alternative uses causal median and MAD from past **matured forecast errors**; prespecify this as *secondary* to avoid choosing normalization ex post. For signed direction report e/sigma separately (direction may reflect scale, not stress).

Threshold theta_{c,m,h} obtained by a fixed earlier training calibration block of size n using the conformal-style empirical rank k = ceil((n+1)(1−alpha)), theta = k-th smallest prior S, or +infinity if k > n. Fix alpha = 0.05; flag **S > theta** (strict) and never tune alpha on event results. Exchangeability required for exact finite-sample conformal coverage; under autocorrelation/nonstationarity this is only an operational historical cutoff, not an exact false-alarm guarantee. Do not pool incomparable country/model index scores blindly. Apply a 21 **eligible local observation-session** cooldown to deduplicate sequential alarm hits into an alarm episode. No alert before its target release and no calibration use of later periods.

Default calibration timeline proposed: eligibility begins after sufficient warmup, calibration restricted to **2000-01-01–2006-12-31** for a first 2007+ study; if any country/index lacks enough matured pre-2007 errors, label that analysis **not evaluable**, not re-tune on GFC. Reserve 2022–2023 events as a late chronological **pseudo-out-of-sample** illustration, without claiming previously unseen truly prospective confirmation. Model training/refitting at t may use prior available information only; threshold remains frozen unless a separately preregistered prospective rolling scheme is accepted.

## 3. Analysis windows and mutually exclusive estimands

Define onset dates s_j directly from the separate citation manifest, **before score evaluation**. Use the local eligible session calendar (not calendar days to count financial sessions): prespecify pre-anchor (s_j−21 sessions,…,s_j−1 session), anchor/post (s_j,…,s_j+20 sessions), and a primary **lead horizon of 21 local sessions**. Pre-window overlapping any independently documented prior stress interval is contaminated and is **excluded from clean early-warning recall**; report it as escalation warning within ongoing stress instead. Secondary lead horizons = 5, 63 local sessions with familywise multiplicity control, not best-of-three selection. For coarse monthly panels use h ∈ {1,3,6} months as per EXP-0001, compare only on verified release chronology; never pass one daily data window as a monthly estimate.

For H_A define Δ_A = P(A_t=1 | predeclared event/post windows) − P(A_t=1 | calm eligible dates) at country-level, with a cluster-level uncertainty interval. Null H0A: Δ_A ≤ 0. Report matched calm windows from non-overlapping, same-country calendar blocks outside *all* event ±63-session buffers, matched by month/season and pre-event availability/coverage **without looking at scores**. Descriptive association cannot demonstrate risk warning.

For H_D define near-onset overlap P(first alarm in [s_j,s_j+20] | evaluable event j) and lag t−s_j. Null H0D: no improvement over the frozen volatility-only contemporaneous detector at matched false-alarm rate. A positive lag is detection latency; do not relabel as a lead.

For H_E define R_E = (# eligible independent event clusters with an alarm observed in [s_j−21,s_j−1] and not in an ongoing earlier-stress regime) / (# eligible independent event clusters). Let lead L_j = s_j − min{t: valid early alarm t in prespecified lookback} in **local sessions**; report distribution with censored misses, not only successes. A multi-country event (GFC/COVID) counts as one cluster for independence; report country exposures separately. Null H0E: at a common calm false-positive budget, the normalized surprise **does not** add future-stress predictive information beyond contemporaneous volatility, drawdown and independently published benchmarks. Failure to reject is not proof of equivalence.

False positive rate FPR = (# eligible *calm country-sessions* with A_t=1) / (# eligible calm country-sessions), along with **false alarm episodes / 100 calm country-weeks**; report both, since a cooldown changes episode counts but not underlying alarm-day prevalence. Event recall is invalid without these denominators and sufficient time coverage. Treat unknown historical event boundaries conservatively: exclude ±63 sessions around every listed anchor from primary calm denominators; distinct documented overlapping clusters should be merged or treated as non-independent.

## 4. Incremental prediction rather than post-hoc narratives

At forecast time t construct future outcome Y_{c,t}^{(H)} = 1 if independently anchored *new* eligible event begins within (t,t+H] (otherwise 0), conditional on full verification of event coverage and not already being in a stressful episode. Fit **matched-origin, matched-target** baselines using ONLY covariates published at/before t: trailing realized volatility, max drawdown, credit/funding controls when obtainable, and external published stress benchmarks CISS (EA/US/UK), NFCI/STLFSI4 (US), Banxico IEMF (if verified), with a missingness indicator and no fictional JP proxy. Proposed incremental model:

    logit P(Y=1 | I_t) = alpha_c + beta' X_{c,t} + gamma S_{c,t}

Contrast out-of-sample event log-loss or precision–recall / Brier loss against gamma=0 using the **same eligible rows**; null H0E: expected incremental loss improvement ≤ 0 (predeclare sign). With very few independent clusters, a learned logistic classifier may be statistically infeasible: in that case report simple threshold sensitivity/recall and FPR with wide intervals, and leave predictive significance **UNKNOWN**.

CISS, NFCI and STLFSI4 are **external references/comparators, not validated independent outcomes**. They may share equity/FX/credit inputs with latent-index construction: correlation or ability to forecast a later **revised CISS** can be common-component circularity, not novel disturbance information. If the outcome is a source-shared published index, quantify direct input overlap or do not claim independent validation.

## 5. Placebo, uncertainty and rejection conditions

1. Lock event-manifest hash, index definitions, target vintages, clocks, horizons, threshold, calm-window selection and controls before scoring any candidate.
2. Exclude event-overlapping historical calibration periods; perform chronological rolling-origin evaluations with temporal embargo until targets mature; log exclusions with precise reasons.
3. Run deterministic placebo anchors sampled from predefined event-free blocks, calendar-matched, *without* selecting dates based on errors; add block-shift placebo distributions preserving time dependence.
4. Cluster bootstrap **by independent episode**, not country×event or observation; with only a handful of clusters report exact per-cluster outcomes and descriptive intervals, and withhold high-powered asymptotic claims. Correct across models, horizons and repeated criteria or fix a single primary statistic.
5. Report counterexamples: false alarms during quiet windows, missing alarms in official stress anchors, sensitivity to heavy tails, lag/as-of choice, benchmark common components, structural breaks, revised sources, factor sign/rotation instability, and measurement error.

**Falsification examples:** no excess event alarms at frozen FPR; no improvement in holdout future-event loss against volatility/drawdown/reference controls; alarms only at t≥s; comparable false-alarm rates in placebo windows; score changes explained by factor re-identification or revised measurements. These are negative findings to preserve, not thresholds to retune.

## 6. Reproducible minimal implementation, boundary and release gate

Proposed score helper at src/latent_risk/events/scores.py implements only pure synthetic unit-scale normalization, *strict earlier-available calibration*, and first pre-anchor lead in **calendar days** for deterministic checking. Calendar-day helper output is **not** the publication metric: later country-exchange-session mapping must transform alerts into eligible local sessions before computing R_E. Helper neither constructs events nor fits models nor reads market data nor treats current-vintage data as historically available.

Before actual scoring, obtain independently reviewed country session calendars, event-window machine-readable manifest hash, point-in-time (or explicitly labeled latest-vintage retrospective) target date-vintage manifest, historical maturity/scale calibration provenance, genuine out-of-sample predictions and independent event-outcome source audit. **No crisis predictive power is asserted.**
