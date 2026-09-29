# M5: Calls and Puts — implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Created; calculator, headless presentation and static notebook tests pass. Coherence review complete. Notebook execution/live acceptance deferred by user instruction. **Prerequisites:** M4.
**Notebook:** [notebooks/M5_calls_and_puts.ipynb](notebooks/M5_calls_and_puts.ipynb).

Read the [canonical roadmap](notebooks/README.md), [shared planning conventions](PLANNING.md), and [project guidance](AGENTS.md). Foundation plans remain implementation records; this document specifies only the new lesson or unfinished work.

## Learning decision, assumptions, and worked example

All numeric contract terms and scenarios below are hypothetical teaching assumptions, not market quotes.

Question: can a buyer cap a benchmark cost, or a supplier protect a floor, while retaining favorable price moves? One-month delivery Q=7,200 GPU-hours at t=12, strike 5 USD/GPU-hour. Illustrative call premium 0.40 and put premium 0.30 per covered GPU-hour paid at t=0. European cash settlement at t=12; no early exercise or collateral. Benchmark equals actual physical price in base.

Call payoff Q·max(S−K,0); buyer net nominal procurement cost QS−payoff+premium. For S=3,5,7 costs 24,480; 38,880; 38,880. Premium-inclusive cap is 5.4 USD/hour, not 5. Put payoff Q·max(K−S,0); supplier net nominal receipts QS+payoff−premium, with floor 4.7 USD/hour. Premium payment timing stays in a separate cash schedule; these simple sum totals are not time-zero PVs.

Explain gross payoff versus net economic result, premium per hour versus total premium, and buyer versus option writer exposures. Compare partial coverage 3,600 hours and basis+0.5 using M3. No option price calibration; premiums are assumed offers for the example.

## Reusable calculations and interfaces

Add `options` functions `european_option_payoff_usd(kind, settlement_price_usd_per_gpu_hour, strike_usd_per_gpu_hour, covered_gpu_hours)` and `option_cash_flows` for upfront premium and terminal payoff with explicit long/short sign. Reuse M2/M3 combination of physical/financial cash and monthly discounting only for an optional timing comparison. Validate finite nonnegative rates, strike, premium and quantity; zero strike valid, negative rates excluded in this lesson. Keep payoff functions independent of pricing models.

## Cell-by-cell teaching sequence

Use 17 cells: eight Markdown/code pairs below, followed by a final Markdown takeaway with references and the indicated next lesson. Each Markdown cell after an experiment explains the preceding output before introducing the next prediction. Target 10–15 minutes, 800–1,100 prose words; label any extensions optional.

| Cells | Markdown explanation / optional prediction | Executable content |
|---|---|---|
| 1–2 | Buyer cap and supplier floor | Distinguish a right/payout from a delivery commitment. |
| 3–4 | Direct call and put arithmetic | Use S=7 for call and S=3 for put before helpers. |
| 5–6 | Scenario table and premium dates | Compare gross payoff, premium, net physical outcome. |
| 7–8 | Explorer | Payoff/combined-cost chart; controls strike and premium, switch call/put. |
| 9–10 | Experiment: higher premium | Same gross payoff, worse net cost/floor. |
| 11–12 | Experiment: partial coverage | Half the units protected; remaining exposure visible. |
| 13–14 | Experiment: basis mismatch | Actual supplier +0.5; nominal cap holds only on benchmark component. |
| 15–16 | Takeaway and M6 | A payoff is specified; what assumptions could produce a model premium? Display a compact decision summary from the already calculated results; introduce no new model. |
| 17 | Final interpretation, limitations, references and next step. | No diagnostics or hidden answers. |

All direct arithmetic precedes its packaged counterpart. One compact table and one main chart type; explorer controls update calculated outputs in one helper call with a static fallback. Keep experiments fixed independently of prior widget edits.

## Acceptance and implementation checks

Test below/at/above strike, call/put signs, writer versus holder zero-sum gross cash, premium counted once, zero quantity/strike/premium, exact 5.4 cap and 4.7 floor under matching assumptions, and partial/basis coverage failures.

Implement calculations and independent tests first, then education helpers, then notebook. Run the shared lint/type/test/schema/fresh-kernel checks, inspect local rendering and live control recovery, restore defaults and save outputs. Follow the complete checklist in [PLANNING.md](PLANNING.md); Colab remains deferred.

## Boundary with other lessons

M5 owns option payoffs and premium-inclusive outcomes, not model valuation (M6), staged option purchase (E1), or minimum-revenue commercial sharing terms (E2). Never infer physical availability from a cash payoff.

## Sources and attribution

OCC/OIC option pricing material supports premium/payoff terminology. Their listed securities examples are conceptual references; the compute option and premiums are hypothetical.

See the [source ledger](PLANNING.md#source-ledger) for inspected sources versus research still required. Place verified citations next to supported explanations; distinguish original inputs and derived results. No live data or new dependencies are required for the core lesson.

## Implementation and coherence review

Reviewed all eight subsection pairs against the spec and M2–M4. Direct call/put arithmetic precedes packaged payoff schedules; month-zero premium is counted once and kept separate from month-12 physical/financial netting through M2. Matched nominal cap/floor, higher premium, partial coverage and provider basis are interpreted with their actual inputs. The call/put explorer snapshots quantity and price scenarios and leaves fixed experiments independent. Both parties shown in the main comparison buy protection; writer cash is the opposite option leg, not the physical supplier automatically. No physical delivery promise or fair-price claim is inferred. M6 remains the next step; no valuation framework is added to payoff functions.

37 targeted option, market-presentation and financing-presentation tests passed. Tests cover below/at/above strike, premium timing and long/short signs, cap/floor, partial/basis exposure, zero boundaries and invalid/overflow inputs; direct chart rendering and dropdown changes, invalid-edit recovery and input independence passed. Static notebook schema/structure/AST checks passed without executing cells. Repository-wide Ruff lint/format checks and strict mypy (17 source files) passed.

The user requested no notebook execution or repeated execution-permission prompts. Validation calls calculators and presentation helpers directly and checks notebook schema/syntax without executing cells. Fresh-kernel execution, saved runtime outputs and live Jupyter/Colab checks remain deferred. This is not a claim of full presentation verification.
