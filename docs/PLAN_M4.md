# M4: Price and Quantity Uncertainty — implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](../notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Created; calculator, headless presentation and static notebook tests pass. Coherence review complete. Notebook execution/live acceptance deferred by user instruction. **Prerequisites:** M3.
**Notebook:** [notebooks/M4_price_quantity_scenarios.ipynb](../notebooks/M4_price_quantity_scenarios.ipynb).

Read the [canonical roadmap](../notebooks/README.md), [shared planning conventions](PLANNING.md), and [project guidance](../AGENTS.md). Foundation plans remain implementation records; this document specifies only the new lesson or unfinished work.

## Learning decision, assumptions, and worked example

All numeric contract terms and scenarios below are hypothetical teaching assumptions, not market quotes.

Question: what happens when a price hedge survives a change in the business quantity? Reseller commits to 7,200 GPU-hours in a month at supplier rate 5. Customer billed demand initially 5,400 hours at 8. Unhedged contribution=43,200−36,000=7,200. Compare declared scenarios: base; demand cancellation to 2,700 hours; selling price 6; delivery delay by one month with zero service cash in original month and service/receipts shifted later. Contract payments continue unless an explicit remedy is assumed. No automatic lost-service reimbursement.

For a separate buyer hedge panel, take M2's long financial hedge H=7,200, K=5 and actual physical need Q=3,600 with benchmark/physical priceS=3. Buyer pays 10,800 for compute but pays 14,400 on the hedge, combined 25,200. Cancellation to Q=0 leaves the financial obligation; distinguish unused rented capacity from a hedge on a cancelled purchase.

Use a finite scenario table without probabilities in core. An optional named equal-weight average is an illustrative weighting choice, not a forecast or option-pricing measure. Keep time horizon long enough to capture delayed delivery and receipts. No random simulation, correlation estimates or tree pricing.

## Reusable calculations and interfaces

Add `scenarios` records `OperatingScenario(name, customer_rate, billed_gpu_hours, delivery_delay_months)` and `evaluate_reseller_scenarios` composing M1 commitments and F3 receipts when appropriate. Buyer hedge example reuses M2/M3 directly, not a new payoff engine. Return total contribution, cumulative cash, funding requirement, realized quantity and unchanged commitments. Inputs reject billed demand beyond physical capacity unless an explicitly separate purchase is modeled (outside core); cancellation is valid zero demand.

## Cell-by-cell teaching sequence

Use 17 cells: eight Markdown/code pairs below, followed by a final Markdown takeaway with references and the indicated next lesson. Each Markdown cell after an experiment explains the preceding output before introducing the next prediction. Target 10–15 minutes, 800–1,100 prose words; label any extensions optional.

| Cells | Markdown explanation / optional prediction | Executable content |
|---|---|---|
| 1–2 | Question and dimensions | Separate supplier commitment, customer usage, selling price and hedge quantity. |
| 3–4 | Direct base/downside arithmetic | Show cancellation loss with unchanged rent. |
| 5–6 | Scenario table | One change per named scenario; no hidden probability assumptions. |
| 7–8 | Explorer | Scenario contribution bars; controls billed quantity and selling price. |
| 9–10 | Experiment: customer cancellation | 100%→50% of base billed quantity; obligation remains. |
| 11–12 | Experiment: overhedged buyer | 3,600 physical hours at 3 plus hedge payment 14,400. |
| 13–14 | Experiment: delivery delay | Shift service/receipts and extend horizon; distinguish loss from delay. |
| 15–16 | Takeaway and M5 | Explore protection that caps price while retaining favorable-price participation. Display a compact decision summary from the already calculated results; introduce no new model. |
| 17 | Final interpretation, limitations, references and next step. | No diagnostics or hidden answers. |

All direct arithmetic precedes its packaged counterpart. One compact table and one main chart type; explorer controls update calculated outputs in one helper call with a static fallback. Keep experiments fixed independently of prior widget edits.

## Acceptance and implementation checks

Test zero demand/zero hedge separately, unchanged rent after cancellation, capacity bounds, hedge surviving cancellation, delayed horizon totals, basis residual reuse, and no weighted mean without explicit weights in optional extension.

Implement calculations and independent tests first, then education helpers, then notebook. Run the shared lint/type/test/schema/fresh-kernel checks, inspect local rendering and live control recovery, restore defaults and save outputs. Follow the complete checklist in [PLANNING.md](PLANNING.md); Colab remains deferred.

## Boundary with other lessons

M4 owns joint business scenarios, not credit underwriting (F3), debt renewal survival (F7), historical estimation (E5), or pricing probabilities (M6). Keep the reseller and separate hedged buyer roles explicitly labeled.

## Sources and attribution

Use M2/M3 verified contractual sources; any real cancellation/delivery remedy requires its own primary contract. All scenario paths and optional weights are hypothetical; no stochastic market claim needed.

See the [source ledger](PLANNING.md#source-ledger) for inspected sources versus research still required. Place verified citations next to supported explanations; distinguish original inputs and derived results. No live data or new dependencies are required for the core lesson.

## Implementation and coherence review

Reviewed each planned subsection after implementation: reseller supplier commitment stays USD 36,000 under canceled demand, lower price and delay; delay extends the cash horizon without deleting service receipts. The separate buyer pays USD 25,200 with only 3,600 physical hours and the original hedge; zero physical need leaves USD 14,400 financial payment. Uses M1 economics and M2/M3 hedge arithmetic, with no probability weights, automatic remedies, debt model or extra physical purchase. Contribution bars are paired with liquidity figures so equal economic totals do not imply equal funding.

Nine scenario tests plus static notebook and direct bar-height/label tests pass. Checks cover zero demand versus zero hedge, capacity bounds, complete delay horizon, unchanged commitments and reused basis decomposition. No notebook execution was used.

The user requested no notebook execution or repeated execution-permission prompts. Validation calls calculators and presentation helpers directly and checks notebook schema/syntax without executing cells. Fresh-kernel execution, saved runtime outputs and live Jupyter/Colab checks remain deferred. This is not a claim of full presentation verification.
