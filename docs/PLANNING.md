# Curriculum implementation plans and coherence review

## Publication and execution update — 2026-09-29

The user authorized running every notebook, saving outputs, adding GitHub package installation in Colab, and publishing to `zach189/education`. All 26 existing notebooks passed fresh-kernel execution locally and have saved outputs. The first code cell installs the package in Colab; local execution reuses `.venv`. All 740 tests, Ruff checks, formatting checks, and mypy passed. Live Colab interaction remains unverified.

**Ready:** notebooks 1–4 (4 is M1), M2 forwards and swaps, M5 calls and puts, M6 option valuation, and the compute lab financing case study. **WIP:** all other existing lessons, including E1 compound options. C1 remains planned. Release readiness is the user's teaching selection, separate from execution success. See the [notebook index](../README.md) for Colab links and the [canonical roadmap](../notebooks/README.md) for prerequisites.

Earlier dated execution deferrals below are historical and superseded by this update. Live-presentation checks remain pending where not already recorded as complete.

This is the plan index and shared implementation contract. The [notebook roadmap](../notebooks/README.md) remains the source of truth for curriculum scope and prerequisites. Planning documents are specifications, not claims that the corresponding notebooks or calculators exist.

## Current inventory

All 26 existing lessons have notebook source, reusable calculations, tests, and saved outputs from fresh-kernel execution on 2026-09-29. Release readiness and live-presentation status are recorded in the [canonical roadmap](../notebooks/README.md). C1 remains planned.

The original planning update changed documentation only. A subsequent F1 completion pass repaired math rendering and live explorer output, verified local behavior, and saved fresh-kernel results. No dependencies or environment were added.

| Lesson | Plan | Required predecessors | Status |
|---|---|---|---|
| F1 Financing a compute prepayment | [PLAN_F1](PLAN_F1.md) | 1, 2 | Implemented locally; implementation record |
| F2 OEM deposit bridge | [PLAN_F2](PLAN_F2.md) | F1 | Created/tested; fresh-kernel outputs saved; live review pending |
| F3 Offtake financeability | [PLAN_F3](PLAN_F3.md) | 2, F1 | Created/tested; fresh-kernel outputs saved; live review pending |
| F4 Debt capacity | [PLAN_F4](PLAN_F4.md) | F1, F3 | Created/tested; fresh-kernel outputs saved; live review pending |
| F5 Deployment and staged funding | [PLAN_F5](PLAN_F5.md) | F2, F4 | Created/tested; fresh-kernel outputs saved; live review pending |
| F6 Receivables and collateral | [PLAN_F6](PLAN_F6.md) | F3, F4 | Created/tested; fresh-kernel outputs saved; live review pending |
| F7 Renewal and maturity mismatch | [PLAN_F7](PLAN_F7.md) | F3, F4 | Created/tested; fresh-kernel outputs saved; live review pending |
| F8 Ownership, leasing and residual value | [PLAN_F8](PLAN_F8.md) | 2, F4 | Created/tested; fresh-kernel outputs saved; live review pending |
| F9 Waterfalls and investor returns | [PLAN_F9](PLAN_F9.md) | F4, F7; F6/F8 only for those extensions | Created/tested; fresh-kernel outputs saved; live review pending |
| M1 / Notebook 4 Tenor trade | [PLAN_04](PLAN_04.md) | 3 | Revised/tested; fresh-kernel execution passed and outputs saved; live UI/Colab unverified |
| M2 Forwards and swaps | [PLAN_M2](PLAN_M2.md) | M1 | Created/tested; coherence reviewed, fresh-kernel outputs saved; live review pending |
| M3 Basis Risk: When the Index Isn’t Your Price | [PLAN_M3](PLAN_M3.md) | M2 | Revised/tested; fresh-kernel execution and saved outputs complete; live widget updates unverified (local connection issue) |
| M4 Price and quantity uncertainty | [PLAN_M4](PLAN_M4.md) | M3 | Created/tested; coherence reviewed, fresh-kernel outputs saved; live review pending |
| M5 Calls and puts | [PLAN_M5](PLAN_M5.md) | M4 | Created/tested; coherence reviewed, fresh-kernel outputs saved; live review pending |
| M6 Option valuation | [PLAN_M6](PLAN_M6.md) | M5, 2 | Created/tested; coherence reviewed, fresh-kernel outputs saved; live review pending |
| M7 Hedge collateral and liquidity | [PLAN_M7](PLAN_M7.md) | M2, M3, 2; M5 for optional option example | Created/tested; coherence reviewed, fresh-kernel outputs saved; live review pending |
| E1 Compound options | [PLAN_E1](PLAN_E1.md) | M6, 2 | Created/tested; coherence reviewed, fresh-kernel outputs saved; live review pending |
| E2 Minimum revenue/shared upside | [PLAN_E2](PLAN_E2.md) | M5 | Created/tested; coherence reviewed, fresh-kernel outputs saved; live review pending |
| E3 Power and margins | [PLAN_E3](PLAN_E3.md) | 1, 2 | Created/tested; coherence reviewed, fresh-kernel outputs saved; live review pending |
| E4 Floating-rate financing | [PLAN_E4](PLAN_E4.md) | F4, M2 | Created/tested; coherence reviewed, fresh-kernel outputs saved; live review pending |
| E5 Historical risk measurement | [PLAN_E5](PLAN_E5.md) | M3, M4 | Created/tested; coherence reviewed, fresh-kernel outputs saved; live review pending |
| E6 Useful-output costs | [PLAN_E6](PLAN_E6.md) | 1 | Created/tested; coherence reviewed, fresh-kernel outputs saved; live review pending |
| C1 Transaction structuring | [PLAN_C1](PLAN_C1.md) | 1–3, F1–F9, M1–M7 | Planned; electives only if used |

Use the filename printed in each plan; only M1 retains global numbering as `04_the_tenor_trade.ipynb`. Named tracks use their ID prefix. Never renumber F1 as Notebook 4 or link to an uncreated notebook. Keep foundation plans as records rather than rewriting settled assumptions to match new examples.

## Shared lesson and engineering contract

Every plan extends the existing teaching style: one decision, one primary chart type, an editable assumption cell, visible worked arithmetic before reusable calls, compact tables, two or three fixed experiments, and explanatory Markdown immediately after each result. Use 10–15 minutes of core material and 800–1,100 words as the target; F1 retains its approved 23-cell structure. For complex C1 keep detailed ledgers and hedge integration optional. End with the named next lesson or an explicit optional-track return.

The 17-cell paired outlines are content slots, not a requirement to hide explanations: cells 11, 13, 15 and 17 interpret the preceding experiment where applicable. A source/limitations paragraph can share the final cell. Predictions are optional; save answers and baseline outputs for book-like reading. Render math with the notebook's tested `$...$` / `$$...$$` convention and use USD in currency prose. Avoid diagnostics/assertions in lesson cells.

All example values, rates, discounts, contract conditions and scenarios are hypothetical unless attributed to inspected primary sources. Distinguish contractual calculations, illustrative accounting amounts, cash movements, conditional forecasts, and model-dependent valuations. Do not carry terms or ownership silently between examples. New scenarios may intentionally change rates or timing; their first Markdown/input cell must say so. Keep actual payment terms separate from invoice dates.

Reuse the existing `.venv`, editable installation and `pyproject.toml`. No core lesson needs new dependencies, APIs, credentials or local absolute paths. A standalone uploaded notebook does not include `liquid_compute`; explain package installation via the repository. Preserve local Jupyter compatibility and editable-cell fallback. Colab links and setup are now included; live Colab interaction remains unverified.

Reusable code stays in small pure, fully annotated functions, frozen records where helpful, and no broad finance framework. Module names proposed in plans are created only when that lesson is implemented. Presentation and widget mechanics remain in `liquid_compute.education`, with lazy imports, exact initial values, independent explorer state, invalid-edit recovery and ordinary saved static outputs. Public functions document units, time indexing and supported ranges. Reject bools/wrong types with TypeError and invalid/nonfinite values or overflow with ValueError; distinguish computational errors from valid economic losses, insufficient funds or untradeable model results.

Dates and units:

- Dense monthly cash arrays use index 0 for time zero. Service arrays, unless explicitly adapted, use their first element for service month 1. Adapt explicitly rather than shifting an array silently.
- Same-boundary cash is netted with receipts/draws available for payments, unless a plan explicitly models event ordering. Include opening zero balance and every trailing receipt, debt payment and collateral return.
- F2 uses integer day offsets and ACT/365 simple interest on outstanding principal. It must not feed daily indices into monthly discounting. C1 declares its day-to-month mapping.
- Loan rates explicitly state nominal monthly-accrual conventions; business PV uses the existing effective annual discount factor. M6 uses its declared effective annual risk-free model rate and year-length tree steps. E4 rates multiply stated accrual fractions. Do not compare differently quoted rates without conversion.
- Positive payment/receipt components and signed net cash are separate. Principal, loan proceeds, restricted reserves and margin transfers are not operating revenue/expense. Sum principal repayments and subtract draws in net financing-cost PV.

Historical user override (2026-09-28; superseded by 2026-09-29 publication update): create the financing notebooks without running them. Test calculations, plots and widget mechanics directly; validate notebook format and syntax without executing cells. Defer the fresh-kernel, saved-output and live UI portions below. F2 executed before this instruction; its later changes and F3–F9 remain unexecuted. Do not mark this narrower acceptance as full presentation verification.

Implementation gates for every notebook:

1. Read current guidance and prerequisite code; resolve source gaps before adding supported claims. Keep source-specific examples optional and attributed.
2. Implement only required typed calculations, meaningful independent tests and overflow/range checks. Reuse the ownership map below.
3. Add presentation helpers and notebook content. Keep direct arithmetic visible; avoid duplicate implementations hidden in plotting code.
4. Run `.venv/bin/ruff check src tests scripts notebooks`, `.venv/bin/ruff format --check src tests scripts notebooks`, `.venv/bin/mypy`, and `.venv/bin/pytest -q`. Validate notebook schema and run the existing `scripts/validate_notebook.py` with its path in a fresh kernel; its default stays Notebook 1.
5. Inspect local rendered math, USD/percentage/unit labels, tables, negative values, temporal boundaries, interactive changes/recovery and widget-free rendering. Restore defaults and save outputs. Report only actually completed checks; hosted Colab remains unverified.
6. Update the canonical status and root links only after acceptance. Earlier notebooks and their settled behavior remain unchanged unless a separately justified compatibility fix is needed.

## Calculation ownership and nonredundancy review

| Concept or overlap | Owning lesson / module | Later use and boundary |
|---|---|---|
| Operating economics | 1 / `economics` | New lessons call it; no repeated utilization derivation. |
| Cash timing, funding and chosen-rate PV | 2 / `cashflows`, `discounting` | Preserve monthly indexing/netting; other lessons add movements rather than fork funding arithmetic. |
| Implied package blocks | 3 / `forward_curves` | M1 uses actual flat supplier invoices, not inferred rates as offers. |
| Fixed amortizing prepayment loan | F1 / `financing` | F4 sizes loans; F5/F8 use schedules; no second amortization implementation. |
| Conditional short bridge | F2 / `bridge_financing` | Repayment source is customer prepayment; stops before deployment operations. |
| Contractual receipt conditions and CFADS | F3 / `offtake` | F4/F7/C1 consume receipt schedules; no subjective financeability score. |
| Coverage-based debt capacity | F4 / `financing` extension | F6 borrowing base is a separate limit, not additional capacity to add. |
| Milestone/deployment funding | F5 / `deployment` | Longer funding phase than F2; F8 changes procurement form, not timing mechanics. |
| Receivable eligibility and availability | F6 / `collateral` | Does not create collateral from an offtake or assign hardware to a reseller. |
| Renewal against outstanding debt | F7 / `offtake` extension | M1 introduces unfinanced tenor exposure; F7 adds debt survival and retained cash. |
| Ownership/lease/exit proceeds | F8 / `equipment` | F9/C1 consume terminal proceeds once; book value is never cash. |
| Debt/reserve/equity priority | F9 / `waterfalls` | E2 bilateral revenue sharing is not a capital-structure waterfall. |
| Long-buy/short-sell exposure, placement and selling fees | M1 / `tenor_trade` | Owns whole-deal break-even and monthly placement schedules; zero-fee defaults preserve M4 reuse. No debt model, forecast from implied quotes, or resale guarantee. |
| Linear financial settlement | M2 / `hedging` | M3/M4/M7 reuse signs and payoffs; no duplicate engine. |
| Benchmark alignment | M3 / `hedging` extension | M4 varies realized demand/delivery rather than redoing basis algebra. |
| Business stress scenarios | M4 / `scenarios` | E5 measures samples; M6 pricing weights are not business probabilities. |
| Option payoff | M5 / `options` | M6 values that payoff; E1 adds exercise stage, E2 uses payoff decomposition. |
| Replication/tree valuation | M6 / `option_valuation` | E1 reuses the tree; no unrelated valuation framework or implied market quote. |
| Hedge liquidity | M7 / `collateral_liquidity` | Separate futures settlement from OTC collateral; F6 is lending eligibility. |
| Staged protection | E1 / existing options modules | Optional, never a core financing prerequisite. |
| Guaranteed/shared operating revenue | E2 / `revenue_sharing` | Counterparty economics, not F9 distributions. |
| Electricity input costs | E3 / `power` | No duplicate power in all-in rent; technical load distinct from billed use. |
| Floating reference exposure | E4 / `floating_rates` | Reuses M2 settlement concepts; collateral optional via M7. |
| Sample risk estimates | E5 / `risk_statistics` | Synthetic core, sourced real data optional; not a forecast or automatic pricing calibration. |
| Useful-output productivity | E6 / `workload_costs` | Output quality/count/mix distinct from GPU utilization and power draw. |
| Transaction integration | C1 / `transactions` composition | No new finance mechanism or universal DSL; optional hedge appendix. |

Review outcome: all 23 roadmap entries have one plan. The prerequisite graph has no cycles; financing begins after Notebook 2 independently of the market-risk track. M1 remains Notebook 4 and precedes M2. Electives are not required for C1 unless their feature is selected. Deliberate reuse is retained; duplicate derivations and competing calculation ownership are excluded by the table above.

## Source ledger

This ledger distinguishes inspected source pages from remaining research gates. Page inspection is not verification of any hypothetical contract term. Each lesson must cite the relevant original explanation near the claim, and recheck sources before adding real product details. Do not copy facility numbers from the imported chat.

| Primary source | Status and permitted use |
|---|---|
| [AWS Reserved Instance payment options](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-reserved-instances.html) | Inspected during F1 planning. Supports existence of upfront/monthly compute payment choices, not the hypothetical GPU loan or rates. |
| [CFPB amortization](https://www.consumerfinance.gov/ask-cfpb/what-is-amortization-and-how-could-it-affect-my-auto-loan-en-771/) and [interest versus APR](https://www.consumerfinance.gov/ask-cfpb/what-is-the-difference-between-a-loan-interest-rate-and-the-apr-en-733/) | Inspected during F1 planning. Conceptual interest/principal/fee explanations; do not transfer consumer legal requirements to business lending. |
| [World Bank project-finance concepts](https://ppp.worldbank.org/financing/project-finance-concepts) and [transaction issues](https://ppp.worldbank.org/financing/issues-in-project-financed-transactions) | Inspected in this review. Support phase separation and attention to repayment cash; no specific compute terms or standard DSCR assumed. |
| [OCC Asset-Based Lending](https://www.occ.treas.gov/publications-and-resources/publications/comptrollers-handbook/files/asset-based-lending/index-asset-based-lending.html) | Official handbook landing page inspected. F6 implementation inspected the linked booklet, printed pages 16–18 and 21, for concentration, delinquency, eligibility and reserves; our ordering and percentages remain hypothetical. |
| [CME futures margins](https://www.cmegroup.com/education/courses/understanding-the-benefits-of-futures/the-benefits-of-futures-margins) | Inspected in this review. Supports futures performance-bond concept; no quoted margin percentage used. OTC thresholds require separately stated assumptions. |
| [OIC options pricing](https://prd-web.optionseducation.org/optionsoverview/options-pricing) | Pricing page and OIC long-call/long-put pages inspected for M5. Support premium versus payoff terminology; listed-security concepts do not establish tradable compute replication. |
| [New York Fed reference rates](https://www.newyorkfed.org/markets/reference-rates) | New York Fed SOFR definition page inspected for E4: supports the overnight Treasury-secured reference description only. E4 uses synthetic simple monthly reference rates, not claimed SOFR fixings or compounded benchmark methodology. |
| [EIA delivered electricity price definition](https://www.eia.gov/tools/faqs/faq.php?id=507&t=5) | Full FAQ inspected for E3: EIA average retail prices include generation, transmission, distribution, taxes and fees, and are not individual utility rates. Supports distinguishing energy components from delivered costs; no real tariff or GPU power specification is asserted. |
| [SEC financial-statements guide](https://www.sec.gov/about/reports-publications/investorpubsbegfinstmtguide) | Existing Notebook 2 reference. Reinspect for F3/F8 claims about cash versus accounting amounts; no accounting-compliance assertion planned. |
| [Ornn methodology](https://data.ornn.com/docs/forward-curves) and [source article](https://wafer.substack.com/p/lets-talk-about-trading-compute) | Inspected for Notebook 3; attribution stays with those methods/examples, not the curriculum narrative. M1 does not treat implied blocks as executable offers. |

M6 source gate: Andrew W. Lo’s [MIT Finance Theory options lectures](https://ocw.mit.edu/courses/15-401-finance-theory-i-fall-2008/c40ecc0cc0dce0fbf2d229bc4027c43b_MIT15_401F08_lec10.pdf), slides 16–21, inspected for one-period replication and independence from business probabilities. Our effective annual rate is converted to a per-step growth factor; the source uses a gross growth factor in its replication equations. Compute tradability is not established by this source.

E1 source gate: original Geske paper retrieval was inaccessible (publisher denied access; repository timed out). The lesson discloses that gap and derives its two-step example from M6 rather than reproducing the continuous-time formula. [Damodaran’s NYU chapter](https://pages.stern.nyu.edu/~adamodar/pdfiles/val3ed/c05.pdf), page 108, was inspected for compound-option terminology.

E5 source gate: [NIST Measures of Scale](https://www.itl.nist.gov/div898/handbook/eda/section3/eda356.htm) inspected for sample variance/standard deviation with the n−1 denominator. No actual compute data has been imported.

Additional implementation research gates: MLCommons methods only if E6 adds real benchmark evidence. If a source is inaccessible, disclose the gap and omit the unsupported claim/example. Synthetic arithmetic does not require external citation. No real historical-data appendix is required for E5 unless provenance, units and redistribution rights are verified.

## Historical completion audit for the planning update

The audit below records the documentation-only planning pass. F1’s presentation checks mentioned here were subsequently completed; see [its implementation record](PLAN_F1.md#completed-validation).

- Coverage checked against the canonical roadmap: **F1–F9, M1–M7, E1–E6 and C1**, 23 distinct lesson plans with unique target filenames. F1 is a completion plan, not a second implementation. M1 is reserved as Notebook 4.
- Every plan contains its learning decision, hypothetical inputs/timing, arithmetic, reusable-component boundary, teaching sequence, meaningful acceptance checks, source requirements, and an explicit non-overlap section.
- Every roadmap entry links to its plan; all relative links in the new plans, index, guidance and both READMEs resolve. No uncreated notebook is linked as an available artifact.
- Checked the full prerequisite graph, including optional predecessor edges: no cycles. Financing does not depend on the market-risk track; electives remain optional. C1 consumes prior models rather than adding a new pricing or loan engine.
- Independently recalculated 21 numerical references across the bridge, contract cash, staged funding, borrowing base, tenor trade, hedges, options, electricity, floating-rate, output-cost and capstone examples. Corrected E3’s electricity bill to USD 804.80 and contribution to USD 6,395.20.
- Reviewed all plans for conflicting business ownership, duplicated cash flows, time/rate conventions and horizons. Clarified F9’s debt balance/interest/repayment horizon and reserve funding, F8’s exit payoff after the scheduled payment, F2’s maturity, and C1’s bridge-to-term refinancing and prepaid-service offsets.
- Existing foundation plans remain implementation records. This was a documentation review; notebook implementation checks in the plans are future acceptance gates, not claims of completed execution or Colab verification. F1’s known unfinished presentation checks remain explicit.

## Financing implementation coherence review (2026-09-28)

Each notebook was created in sequence, then reviewed against its plan and prior lessons before moving to the next. All retain 17 alternating teaching/code cells, visible arithmetic before corresponding packaged calculations, hypothetical inputs, explicit role changes, worked interpretations, editable assumptions, optional independent controls and next-lesson transitions.

- **F2:** daily ACT/365 bridge stays separate from monthly loans/PV and F5 deployment; documentation conditions differ from overdue cash. Refund principal-first allocation is explicit; remaining principal continues accruing interest to maturity.
- **F3:** billing, due obligations and cash are separate; credits/cancellation remove value, delays move cash. Fixed supplier commitments remain unchanged. No financeability score.
- **F4:** consumes F3 CFADS, reuses F1 amortization, distinguishes loan discounting from business PV and rejects capitalizing shapes. N/A at zero debt service.
- **F5:** owns milestone timing; interest uses opening debt, operations and loan tails extend with delay. Selected borrowing is checked separately against F4 coverage.
- **F6:** receivables-only reseller, customer aggregation before the declared pre-cap-denominator rule; overadvance remains visible. Collateral and repayment capacities are not added.
- **F7:** contracted versus assumed renewals stay separate; debt and rent survive expiry. Retained early cash distinguishes post-expiry drawdown from new cash required. Shorter maturity is checked for affordability.
- **F8:** role changes to owned/leased equipment before resale is introduced. Lease has no sale rights; book value is not cash. Sale after scheduled payment clears remaining debt and cancels the later loan tail.
- **F9:** recomputes interest after sweeps; preserves reserve/unrestricted cash and arrears without implicit equity. Release occurs only after obligations clear; MOIC is not annualized. Core excludes equipment exit to avoid double counting.

Scope adaptation: reusable typed calculators and rendering helpers implement the plans; notebook-local experiment callbacks hold immutable/copy snapshots and delegate arithmetic to them. Headless tests replace kernel/live acceptance during this pass at the user's request. No external data, new environment, package dependency, market-risk implementation or speculative pricing framework was added.

## Financing validation record

- 325 tests passed; seven existing notebook-cell execution tests were deliberately deselected using `-k 'not notebook_arithmetic and not visible_arithmetic'`.
- Ruff lint and formatting checks passed across source, tests, scripts and notebooks; strict mypy passed for all 13 calculation/presentation modules.
- All eight new notebooks pass static schema, syntax, 17-cell structure, prose/units, and no-diagnostic checks. No new notebook cells were executed during this verification pass.
- Direct helper tests cover chart data from every lesson, labels and signed values, stacked uses, widget-free plotting, exact initial controls, independence, invalid-input replacement and recovery.
- Local links in both READMEs, the planning index and financing plans resolve.
- F2's initial execution preceded the no-run instruction. Its later changes and all F3–F9 execution/live acceptance remain deferred. No Colab checks were performed.

## Market-risk and elective implementation audit

All thirteen requested lessons M1–M7 and E1–E6 have been created and reviewed against their subsection specifications. The [cross-track audit](../MARKET_ELECTIVES_REVIEW.md) records scope, subsection coverage, calculation ownership, source limits and final automated checks. C1 remains planned and was not implemented. The current user override defers all notebook-cell execution, saved runtime outputs and live presentation checks.

Final automated result for this pass: **561 passed, 7 deselected**. Ruff lint/format passed; strict mypy passed for 24 source files. Exact M1–M7/E1–E6 inventory, schema/syntax, package imports/direct-call keywords and local documentation links were checked without notebook execution.

## M3 focused revision (2026-09-28)

The subsequent attached request explicitly authorized execution for M3. Its [revised implementation record](PLAN_M3.md) supersedes the original mixed basis/quantity outline: equal quantities and aligned settlement now isolate basis changes around a stated budget. M2 settlement ownership and all existing broader decomposition APIs are preserved. The canonical roadmap records current acceptance; earlier no-execution audit results above describe their original pass, not this revision. Other lessons retain their individually recorded scope.

## M1 article-alignment revision (2026-09-28)

The user approved replacing M1’s contracted-first-year/tail framing with recurring monthly resale across the whole commitment, and specifically requested the actual price curve and differences by tenor. The [current M1 record](PLAN_04.md) separates the sourced published B300 term-price snapshot from an independent hypothetical trade, adds explicit prepayment allocation under the cashflows owner, and previews M2 using its existing seller-settlement engine. Earlier first-year/tail descriptions are superseded for notebook teaching; reusable APIs remain compatible. The [canonical roadmap](../notebooks/README.md) carries current validation status.

## Supplemental lab-financing case (2026-09-28)

[Case specification](PLAN_LAB_CASE.md) · [Notebook](../notebooks/case_lab_gpu_financing.ipynb).
User-requested supplemental deal case, separate from C1 and all track IDs. Composes
F1 equal-payment debt and F4 coverage conventions in `lab_financing`; presentation
stays in `education`. Adds explicit capacity allocation, retained-cash funding,
interest-only balloon comparison and equipment-only delayed liquidation stress.
Unverified prompt terms are distinguished from hypothetical inputs. No external
facility or lender claims. Schema/syntax and direct helper checks only; execution,
saved generated outputs and live checks deferred.
