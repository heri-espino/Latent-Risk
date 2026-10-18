# 2026-10-18 — Independent crisis anchors and falsifiable event-score protocol

**Date:** 2026-10-18 (America/Mexico_City). **Contributor branch:** agent/crisis-hypotheses.  
**Objective:** prevent retrospective narrative fitting of large financial-index forecast errors to financial events. **Status:** event evidence and analysis proposal PROPOSED; small score/lead helpers IMPLEMENTED; empirical predictive performance UNKNOWN.

## Motivation and questions

The original international experiment EXP-0001 is proposed, not run, and the current market pilot and CISS benchmark are not a validated latent stress index. What would falsify a claim that smoothed-index prediction errors forecast crises rather than merely occur during them? Exactly when is a forecast error observable, and how can event dates be chosen independently of the error profile?

## Work performed, exact files and rationale

- notes/literature/crisis_protocol.md: primary institution-backed event/citation manifest with start anchors, **unknown** general crisis end dates, discrete operation end dates where source-documented, country/cluster tags, uncertainty and 1994 Mexico out-of-coverage note.
- notes/results/event_study_design.md: three separate falsifiable hypotheses: association, coincident detection and genuine prior-warning. Defined distinct forecast issue / target / publication / event-onset clocks, earlier-only normalization threshold, calm FPR denominator, lead times, shared-event clustering, controls, block placebos and negative findings.
- src/latent_risk/events/__init__.py and scores.py: pure, manually supplied matured-error/finite-scale normalized surprise, strict earlier-available cutoff, and calendar-day pre-anchor lead helper. They do not reconstruct prices, infer historical releases, count true crisis performance or compute exchange-session leads.
- tests/test_events_scores.py: synthetic checks for date/scale validity, unit scale invariance, conformal-rank cutoff, conservatism for small samples, no future release leakage, strict alarm threshold and exclusion of late alarms.
- journal/2026-10/2026-10-18-crisis-hypotheses.md (this entry) and required shared handoff/state/next-steps/latest-pointer files updated on own branch, with merger expected to reconcile shared conflicts.

## Historical primary source research

ECB 2007-08-09 interbank operations; BoE 2007-09-14 Northern Rock support; Lehman 2008-09-15 confirmed in Federal Reserve archival chronology; Banxico 2008-10-08 USD-auction intervention; ECB 2010-05-10 sovereign-market operations; BOJ 2011-03-11 earthquake-market operations; WHO 2020-03-11 pandemic characterization; BoE September–October 2022 LDI/gilt operation with dated **purchase** ending 2022-10-14; FDIC 2023-03-10 SVB closure and 2023-03-12 Signature closure; IMF 1994 Mexico devaluation outside existing data span. Individual primary URLs and distinctions between source announcement date and actual onset are in the manifest. These anchors were fixed without access to experiment forecasts or crisis scores.

## Theory / status

**PROPOSED:** A_t = 1{|e_t|/sigma_t > cutoff}, where e_t becomes observable only after its target's earliest data release; assess prior alerts strictly before independently sourced s_j. Null predictive hypothesis: surprise does **not** improve future-stress warning at a common false-positive budget relative to contemporaneous volatility/drawdown/published-index controls. **KNOWN LIMITS:** global stress exposures not independent country events; published CISS/NFCI/STLFSI4 can share price components with the index; current-vintage history is not first-release data; 2008 Lehman is escalation of 2007 crisis and 2020 WHO date is not onset of asset-price losses.

## Validation, experimental results and failures

**No empirical event-score / lead-time experiment performed.** Code is synthetic-only. This assistant's runtime could not resolve github.com via direct git transport, so local repo checkout, python -m pytest, ruff, Sphinx and research validator were **NOT EXECUTED LOCALLY**; GitHub PR CI is required before any VERIFIED COMPUTATIONALLY status. CI and PR status must be checked separately after opening the draft. No source availability date, observed warning performance, significance, model fit, or input time-zone alignment was fabricated.

## Alternatives considered and rejected

Rejected full-sample-smoothed latent factors as historical live alerts, threshold optimization on events, using WHO declaration as unambiguous financial-onset date, treating each country's GFC exposure as an independent episode, and assigning unknown episode ends retrospectively. A 21-session release-aware event metric is left PROPOSED rather than pretending the simple calendar-day helper computes it.

## Unexpected findings and unresolved decisions

Official intervention dates are usually **later than first market stress**. The relatively few independent event clusters prevent reliable high-powered early-warning significance. The coordinator must approve event/manifest freeze, common external target, risk-index identity anchoring, data vintage and release calendars, and any future shared-interface change. Older source snapshots remain in users' ignored local folders; no licensed PDF, raw market data or secrets added.

## Next steps

Review primary documents and freeze manifest SHA256; audit all historical release dates and eligible country-session calendars; produce genuinely matured rolling-origin forecast-error records; compare warning at identical FPR and controlled independent stress outcomes, preserving false alarms and missed events. Coordinator should integrate shared handoff/state/LATEST changes with other PRs.

## First draft-PR CI attempt and correction (append-only)
GitHub Actions run 39138883244 on initial branch head: **108 synthetic tests PASS; Ruff PASS; research structure FAIL** because journal/LATEST.md mistakenly contained two dated journal links, while the validator requires exactly one. Sphinx and protocol checks skipped after failure. Corrected LATEST.md in commit c1ee2e2efb15956fe6a572aa8673a6b23b1d8b66 by keeping only the new entry as a Markdown link and retaining the previous entry as plain-text provenance. Await follow-up PR CI. This failure and resolution are preserved rather than omitted.
