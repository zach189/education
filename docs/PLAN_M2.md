# M2: Forwards and Swaps — implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](../notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Created; calculator, headless presentation and static notebook tests pass. Coherence review complete. Notebook execution/live acceptance deferred by user instruction. **Prerequisites:** M1.
**Notebook:** [notebooks/M2_forwards_and_swaps.ipynb](../notebooks/M2_forwards_and_swaps.ipynb).

Read the [canonical roadmap](../notebooks/README.md), [shared planning conventions](PLANNING.md), and [project guidance](../AGENTS.md). Foundation plans remain implementation records; this document specifies only the new lesson or unfinished work.

## Learning decision, assumptions, and worked example

All numeric contract terms and scenarios below are hypothetical teaching assumptions, not market quotes.

Question: how can buyer and seller lock a benchmark price without confusing financial settlement with physical compute? One future monthly block Q=7,200 GPU-hours, strike K=5 USD/GPU-hour, settlement at month 12. Compare physical fixed-price delivery at K with spot physical purchase plus a hypothetical cash-settled long forward Q(S−K); no premium or collateral in this first payoff lesson. Signed settlement received by buyer is opposite seller payment.

At S=3/5/7, settlements=−14,400/0/+14,400. Buyer spot cost QS minus settlement=36,000 in all three cases when quantity and benchmark match exactly. Supplier spot receipts minus its payment likewise lock 36,000. Physical fixed-price agreement actually requires specified capacity delivery; cash settlement alone does not. Failure/default excluded, not guaranteed away.

Extend to a three-month swap as a strip of settlements at t=12,13,14 with spot prices[3,5,7], strike 5 and 7,200 hours each. Net total settlement zero does not mean no dated payments. K is an assumed executable contract term for the model, not Notebook 3's inferred rate or a calculated fair strike. Defer pricing and carry assumptions.

## Reusable calculations and interfaces

Add `hedging` with frozen `Settlement(month_offset, amount_usd)` and `forward_settlements_usd(benchmark_usd_per_gpu_hour, strike_usd_per_gpu_hour, hedge_gpu_hours, settlement_months, side)`; arrays equal length, months positive ascending, side buyer/seller explicit. `combined_physical_and_hedge_cash_flows` records physical cost/receipts and settlement separately. Signed settlements valid; input rates/quantities finite nonnegative. This is the settlement source reused in M3/M4/M7; no valuation or exchange-margin logic here.

## Cell-by-cell teaching sequence

Use 17 cells: eight Markdown/code pairs below, followed by a final Markdown takeaway with references and the indicated next lesson. Each Markdown cell after an experiment explains the preceding output before introducing the next prediction. Target 10–15 minutes, 800–1,100 prose words; label any extensions optional.

| Cells | Markdown explanation / optional prediction | Executable content |
|---|---|---|
| 1–2 | Business question and contracts | Table physical delivery versus financial settlement obligations. |
| 3–4 | Hand-worked payoff | Q(7−5)=14,400 received; 50% coverage left for later experiment. |
| 5–6 | Shared scenario table | Buyer and seller signs reconcile; lock price only on matched units. |
| 7–8 | Explorer | Effective buyer cost against benchmark; control strike and hedge quantity. |
| 9–10 | Experiment: buyer versus seller | Flip side and show equal/opposite financial settlements. |
| 11–12 | Experiment: monthly swap strip | Three dated settlements, not one ambiguous final net amount. |
| 13–14 | Experiment: partial quantity | Hedge 3,600 of 7,200; residual cost responds to S. |
| 15–16 | Takeaway and M3 | A benchmark price lock works only when it matches the actual business exposure. Display a compact decision summary from the already calculated results; introduce no new model. |
| 17 | Final interpretation, limitations, references and next step. | No diagnostics or hidden answers. |

All direct arithmetic precedes its packaged counterpart. One compact table and one main chart type; explorer controls update calculated outputs in one helper call with a static fallback. Keep experiments fixed independently of prior widget edits.

## Acceptance and implementation checks

Test S below/equal/aboveK, buyer/seller zero-sum, zero quantity, exact locked cost, no double counted physical delivery, dated strip preserving payment dates and nonfinite/length/order validation.

Implement calculations and independent tests first, then education helpers, then notebook. Run the shared lint/type/test/schema/fresh-kernel checks, inspect local rendering and live control recovery, restore defaults and save outputs. Follow the complete checklist in [PLANNING.md](PLANNING.md); Colab remains deferred.

## Boundary with other lessons

M2 owns linear settlement and physical-versus-financial distinction. M3 owns basis mismatch, M5 nonlinear options, M6 valuation assumptions, M7 collateral cash. Avoid calling the hypothetical strike a market fair value.

## Sources and attribution

CME educational primary materials on hedging and forward/futures distinctions are research targets; do not apply exchange futures margin rules to these assumed OTC forwards. Inspect exact source passages during implementation.

See the [source ledger](PLANNING.md#source-ledger) for inspected sources versus research still required. Place verified citations next to supported explanations; distinguish original inputs and derived results. No live data or new dependencies are required for the core lesson.

## Implementation and coherence review

Reviewed all eight planned subsections after implementation: fixed physical delivery remains a separate alternative to spot-plus-cash-settled forward, buyer/seller settlements are opposite, exact matched cost is USD 36,000, the strip retains months 12/13/14 despite a zero total, and half coverage leaves costs USD 28,800/36,000/43,200. The assumed strike is not an inferred forward quote or fair-value output. Physical and settlement dates are preserved separately; no collateral, options or valuation are introduced. M1’s unfinanced physical-business boundary remains intact.

14 settlement/cash tests pass. Headless price-axis, partial-coverage, precision and control-recovery tests and static notebook checks pass; shared finance presentation tests also pass. Strict mypy and lint pass. CME forward/futures and cash-timing primary pages were inspected; cited claims do not import exchange margin rules into OTC terms.

The user requested no notebook execution or repeated execution-permission prompts. Validation calls calculators and presentation helpers directly and checks notebook schema/syntax without executing cells. Fresh-kernel execution, saved runtime outputs and live Jupyter/Colab checks remain deferred. This is not a claim of full presentation verification.


## Ready presentation update — 2026-09-29

See the [Ready notebook review](READY_NOTEBOOK_REVIEW.md) for updated chart/control behavior, package boundaries, fresh-kernel outputs, automated checks, and live-check limitations. This update supersedes the historical execution deferrals above.
