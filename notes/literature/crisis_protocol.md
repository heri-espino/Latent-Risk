# Historical financial-disturbance anchor manifest — design frozen before Latent-Risk event scoring

**Authored:** 2026-10-18. **Status:** PROPOSED (historical event anchors and test protocol); **no forecast/event result computed**. This is *retrospective protocol specification*, not prospective preregistration before historical events occurred. It must be version-pinned before looking at the repository's future forecast errors. Sources were selected independently of those errors. **No observed historical index anomaly was used to choose an event date.**

## Evidence semantics

- **Anchor** = externally dated occurrence or official action. A dated intervention often confirms pre-existing stress; it is **not** necessarily crisis onset. Date precision is one calendar day unless otherwise specified.
- **Historical end** = only a documented event/operation ending (not automatically the end of an economic crisis). Blank/unknown means **UNKNOWN**, not open-ended crisis.
- **Analysis window** = mechanically fixed (see event_study_design.md), and never presented as an externally established crisis end.
- **Geography** = MX (Mexico), US (United States), UK, JP (Japan), EA (euro area). An event described as global is a single shared cluster, not five independent crises.
- **Class**: interbank liquidity, bank distress, global banking panic, FX-market disorder, sovereign-funding stress, exogenous physical shock, global pandemic, gilt/LDI liquidity, bank failure.
- **Dating uncertainty**: L = low uncertainty in the official action date; H = high uncertainty that this date represents onset/end of broader financial stress. All listed anchors have L date precision; every unresolved crisis ending has H boundary uncertainty.
- **Source vintage**: citations are historical institutional documents or explicit retrospective historical chronologies. The date a later historical account was *published* is not the date that market participants observed it.

## Primary-source citation manifest (URLs refer to source documents, not redistributable PDFs)

| Key | Issuer / document | Dated fact established | URL |
| --- | --- | --- | --- |
| ECB07 | European Central Bank, liquidity operations history | 2007-08-09 market tensions and exceptional operation | https://www.ecb.europa.eu/mopo/implement/omo/html/communication-history.mt.html |
| BOE07 | Bank of England, Northern Rock facility, 2007-09-14 | 2007-09-14 liquidity support | https://www.bankofengland.co.uk/news/2007/september/liquidity-support-facility-for-northern-rock-plc |
| FED08 | St. Louis Fed FRASER financial-crisis timeline | Lehman Chapter 11 filing on 2008-09-15 | https://fraser.stlouisfed.org/timeline/financial-crisis |
| FED07 | New York Fed, 2010 retrospective chronology | BNP suspension 2007-08-09 and Lehman bankruptcy 2008-09-15 as *different* crisis phases | https://www.newyorkfed.org/newsevents/speeches/2010/tra100625.html |
| BAN08 | Banco de México, extraordinary dollar auctions | FX liquidity interventions beginning 2008-10-08; individual auctions 8, 9, 10, 16, 23 October | https://www.banxico.org.mx/markets/extraordinary-usd-auctions-ex.html |
| ECB10 | ECB press release 2010-05-10 | Securities Markets Programme introduced owing to severe tensions | https://www.ecb.europa.eu/press/pr/date/2010/html/pr100510.en.html |
| BOJ11 | Bank of Japan earthquake report 2011-03-11 | earthquake at 14:46 JST; BOJ financial market stability response | https://www.boj.or.jp/en/about/release_2011/rel110311a.htm |
| WHO20 | WHO Director-General 2020-03-11 statement | COVID-19 characterised as a pandemic; **not** beginning of market decline | https://www.who.int/news-room/speeches/item/who-director-general-s-opening-remarks-at-the-media-briefing-on-covid-19---11-march-2020 |
| BOE22A | Bank of England, Anatomy of 2022 gilt crisis, 2023 paper | 2022-09-23 fiscal statement, 2022-09-28 intervention, 2022-10-14 operation end | https://www.bankofengland.co.uk/working-paper/2023/an-anatomy-of-the-2022-gilt-market-crisis |
| BOE22B | Bank of England, official intervention announcement | intervention begins 2022-09-28, end planned for 2022-10-14 | https://www.bankofengland.co.uk/news/2022/september/bank-of-england-announces-gilt-market-operation. |
| BOE22C | Bank of England, 2022-10-17 end statement | purchases *did* cease 2022-10-14 | https://www.bankofengland.co.uk/news/2022/october/statement-on-end-of-gilt-market-operations |
| FDIC23 | FDIC 2023-03-10 news release | Silicon Valley Bank closure 2023-03-10 | https://www.fdic.gov/news/press-releases/2023/pr23016.html |
| FDIC23B | FDIC joint release 2023-03-12 | Signature Bank closure 2023-03-12, systemic-risk exception | https://www.fdic.gov/news/press-releases/2023/pr23017.html |
| IMF94 | International Monetary Fund, Mexican peso-crisis historical account | 1994-12-20 devaluation, 1994-12-22 floating-rate transition | https://www.elibrary.imf.org/view/journals/001/1995/112/article-A001-en.xml |

## Frozen event-anchor list

Each anchor below is included without inspecting model errors; **date is documented, classification/analysis eligibility is a proposal**. Column "end" identifies only a documented discrete *operation or announcement sequence end*, never an inferred crisis-resolution date. For every row with end UNKNOWN use an algorithmically defined, equal-length window for outcomes; do not insert a retrospective end after viewing anomalies.

| ID | Country | Cluster | Class | Anchor (ISO) | Documented end | Source | Dating / substantive uncertainty | Role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EA-2007-LIQ | EA | GFC-2007-09 | Interbank liquidity | 2007-08-09 | UNKNOWN | ECB07, FED07 | L / H; liquidity already strained earlier | Primary phase anchor |
| UK-2007-NR | UK | GFC-2007-09 | Bank liquidity distress | 2007-09-14 | UNKNOWN | BOE07 | L / H; assistance date not first distress | Primary phase anchor |
| US-2008-LEH | US | GFC-2007-09 | Banking panic escalation | 2008-09-15 | UNKNOWN | FED08, FED07 | L / H; **not** beginning of 2007 crisis | Primary escalation anchor |
| MX-2008-GFC | MX | GFC-2007-09 | Global panic exposure | 2008-09-15 | UNKNOWN | FED08 | L / H; US anchor is externally transmitted, **not** Mexican-specific onset | Shared exposure |
| UK-2008-GFC | UK | GFC-2007-09 | Global panic exposure | 2008-09-15 | UNKNOWN | FED08 | L / H; same global cluster | Shared exposure |
| JP-2008-GFC | JP | GFC-2007-09 | Global panic exposure | 2008-09-15 | UNKNOWN | FED08 | L / H; same global cluster | Shared exposure |
| EA-2008-GFC | EA | GFC-2007-09 | Global panic exposure | 2008-09-15 | UNKNOWN | FED08 | L / H; same global cluster | Shared exposure |
| MX-2008-FX | MX | GFC-2007-09 | FX-market liquidity | 2008-10-08 | UNKNOWN | BAN08 | L / H; interventions on 8–23 Oct, not proved crisis end on 23 Oct | Domestic-specific escalation |
| EA-2010-SMP | EA | EA-SOV-2010 | Sovereign-bond market stress | 2010-05-10 | UNKNOWN | ECB10 | L / H; policy response after tensions, not onset | Primary action anchor |
| JP-2011-QUAKE | JP | JP-DISASTER-2011 | Physical shock / financial-system exposure | 2011-03-11 | UNKNOWN | BOJ11 | L / H; **not intrinsically a banking crisis** | Specificity / secondary |
| MX-2020-COVID | MX | GLOBAL-COVID-2020 | Pandemic exogenous shock | 2020-03-11 | UNKNOWN | WHO20 | L / H; not market-stress onset | Global |
| US-2020-COVID | US | GLOBAL-COVID-2020 | Pandemic exogenous shock | 2020-03-11 | UNKNOWN | WHO20 | L / H; not market-stress onset | Global |
| UK-2020-COVID | UK | GLOBAL-COVID-2020 | Pandemic exogenous shock | 2020-03-11 | UNKNOWN | WHO20 | L / H; not market-stress onset | Global |
| JP-2020-COVID | JP | GLOBAL-COVID-2020 | Pandemic exogenous shock | 2020-03-11 | UNKNOWN | WHO20 | L / H; not market-stress onset | Global |
| EA-2020-COVID | EA | GLOBAL-COVID-2020 | Pandemic exogenous shock | 2020-03-11 | UNKNOWN | WHO20 | L / H; not market-stress onset | Global |
| UK-2022-GILT | UK | UK-GILT-2022 | Gilt/LDI market dysfunction | 2022-09-23 | 2022-10-14 **purchase scheme only** | BOE22A, BOE22B, BOE22C | L / H; 23 Sep fiscal statement is a defensible trigger, not demonstrated first stress | Primary |
| US-2023-SVB | US | US-BANK-2023 | Bank failure / funding shock | 2023-03-10 | 2023-03-12 **second bank closure only** | FDIC23, FDIC23B | L / H; closure sequence end is not systemic risk end | Primary |
| MX-1994-PESO | MX | MX-PESO-1994 | Currency/banking crisis | 1994-12-20 | UNKNOWN; 1994-12-22 float transition **not crisis end** | IMF94 | L / H; earlier vulnerabilities predate devaluation | **Out-of-coverage archival only** |

**Unit-of-analysis rule:** The globally exposed GFC and COVID rows must not be counted as independent clusters per country. For phase anchors in GFC, either treat all as one connected cluster for inference or report a pre-specified descriptive decomposition without separate independent-sample significance.

**Pre-existing crisis warning:** The Lehman anchor evaluates prediction of a 2008 escalation, not prediction of the original 2007 crisis; even an alarm in August 2008 occurred in an already-stressed era. COVID's WHO anchor was announced after international financial markets had already repriced. Early-warning claims about these *broader episodes* would therefore be overstated.

**Coverage warning:** MX 1994 predates the current project's 2000+ candidate data. Leave it in the citation manifest for future archival study, but mark it excluded from all primary denominator, threshold-fitting, event-recall and test statistics.

## Material unknowns / source diligence pending

Exact market close time, time zones, holiday calendars, provider release and revision history, 2007 full-five-country panel availability, country risk-factor sign/scale, and whether the observed benchmark target shares raw input components remain UNKNOWN. No crisis start date is inferred from factor residuals. Before model scoring, freeze a machine-readable version and a SHA256 of this manifest, assign event-outcome dataset coverage and eligibility, and separately approve any later date corrections through an explicitly versioned amendment. Incompatible older events are reported as not evaluable, never silently dropped.
