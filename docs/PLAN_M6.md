# M6: Option Valuation — implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](../notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Created; calculator, headless presentation and static notebook tests pass. Coherence review complete. Notebook execution/live acceptance deferred by user instruction. **Prerequisites:** M5 and 2.
**Notebook:** [notebooks/M6_option_valuation.ipynb](../notebooks/M6_option_valuation.ipynb).

Read the [canonical roadmap](../notebooks/README.md), [shared planning conventions](PLANNING.md), and [project guidance](../AGENTS.md). Foundation plans remain implementation records; this document specifies only the new lesson or unfinished work.

## Learning decision, assumptions, and worked example

All numeric contract terms and scenarios below are hypothetical teaching assumptions, not market quotes.

Question: what does a small replicating model imply about an option premium, and where do its assumptions fail for compute? Use an explicitly idealized tradable proxy price S0=5, up factor 1.2, down 0.8, one-year step, effective annual risk-free rate 5%, strike 5, call on one normalized unit. No dividends, frictionless trading, shorting and borrowing/lending at same rate are declared idealizations, not established compute-market facts.

Terminal prices 6/4 yield payoffs 1/0. Replication delta=(1−0)/(6−4)=0.5 units; cash position B=(0−0.5·4)/1.05=−1.9047619; value=delta·5+B=0.5952381. Equivalent pricing weight q=(1.05−0.8)/(1.2−0.8)=0.625; value=(q·1+(1−q)·0)/1.05. These weights are not real-world up/down forecasts. Require d<growth<u; invalid trees produce an explanation, not clipped weights.

Extend to a two-step recombining tree, same per-step duration one year, so expiry two years. Do not compare one- and two-step results as discretizations of the same maturity unless duration is adjusted (optional, excluded from core). Explain that physical compute cannot simply be stored and traded like the ideal proxy; result is conditional model value, never an executable quote.

## Reusable calculations and interfaces

Add `option_valuation`, separate from `options` payoff: `one_step_replication` returns delta, cash, pricing weight and PV; `binomial_european_option_value_usd` uses explicit step_years, steps, up/down factors, effective annual rate and M5 terminal payoff. Unit notional one underlying unit; scale by GPU-hours only under an explicitly assumed proxy-to-payoff mapping. Validate positive spot,0<d<u, positive step duration/count, nonnegative rate and strike, finite node values and strict no-arbitrage bound. No Black–Scholes, American exercise or inferred volatility in core.

## Cell-by-cell teaching sequence

Use 17 cells: eight Markdown/code pairs below, followed by a final Markdown takeaway with references and the indicated next lesson. Each Markdown cell after an experiment explains the preceding output before introducing the next prediction. Target 10–15 minutes, 800–1,100 prose words; label any extensions optional.

| Cells | Markdown explanation / optional prediction | Executable content |
|---|---|---|
| 1–2 | Model versus quote | State trading assumptions and why compute is not a storable asset. |
| 3–4 | Direct terminal payoffs | Construct 6/4 prices and 1/0 payoffs. |
| 5–6 | Visible replication | Solve delta and B, verify both terminal outcomes before shared calls. |
| 7–8 | Shared model and explorer | Two-state/tree diagram; controls up/down factors and chosen rate. |
| 9–10 | Experiment: business probabilities | Change a separate forecast probability without altering replicating value; show difference. |
| 11–12 | Experiment: wider state prices | Change factors within bounds; retain payoff and declared horizon. |
| 13–14 | Experiment: invalid tree | Growth outside(d, u); explain failed model, not a meaningful premium. |
| 15–16 | Takeaway and M7 | Even well-matched economic protection may demand interim cash; E1 is optional. Display a compact decision summary from the already calculated results; introduce no new model. |
| 17 | Final interpretation, limitations, references and next step. | No diagnostics or hidden answers. |

All direct arithmetic precedes its packaged counterpart. One compact table and one main chart type; explorer controls update calculated outputs in one helper call with a static fallback. Keep experiments fixed independently of prior widget edits.

## Acceptance and implementation checks

Test 0.5952381 replication, both terminal payoff matches, pricing-weight equivalence, zero-volatility degenerate case rejected with clear message, intrinsic terminal behavior, call-put parity within model, invalid bounds, overflow and two-step backward recursion against hand calculation.

Implement calculations and independent tests first, then education helpers, then notebook. Run the shared lint/type/test/schema/fresh-kernel checks, inspect local rendering and live control recovery, restore defaults and save outputs. Follow the complete checklist in [PLANNING.md](PLANNING.md); Colab remains deferred.

## Boundary with other lessons

M6 owns valuation assumptions and pricing weights. E5 empirical volatility is not automatically a model input. E1 reuses tree nodes; no second tree engine. M5 premiums remain illustrative contractual inputs, not retroactively asserted fair prices.

## Sources and attribution

OIC pricing sources support theoretical versus quoted premiums. Inspect a primary binomial-option research paper or original university-authored derivation before publication; model-specific replication arithmetic here is explicitly derived, not attributed to an inaccessible source.

See the [source ledger](PLANNING.md#source-ledger) for inspected sources versus research still required. Place verified citations next to supported explanations; distinguish original inputs and derived results. No live data or new dependencies are required for the core lesson.

## Implementation and coherence review

Reviewed all eight subsection pairs against the specification. Terminal payoff and delta/cash arithmetic precede package calls; replication reproduces both states. The independent example and MIT derivation use an explicitly reconciled rate convention. One normalized proxy unit is not silently scaled to GPU-hours; no real compute tradability is asserted. The two-step tree appears in the shared-model subsection and explicitly expires in two years. Business forecast probabilities affect a separate expectation, not pricing weights. Wider states retain the one-year horizon. Invalid-tree handling is a requested teaching experiment rather than test assertions. The final summary only reuses existing results and routes to M7/E1. M5 payoffs are reused by the shared recursion; E1 can consume tree nodes without another pricing engine.

50 targeted valuation, market presentation and financing presentation tests passed. Checks cover two-state replication, pricing-weight equivalence, two-step manual recursion, put-call parity, invalid/degenerate/overflow inputs, tree branch/recombination data, proxy-unit labeling and invalid-control recovery. Notebook schema/structure/AST checks passed without execution. Ruff and strict mypy passed after presentation-unit changes.

The user requested no notebook execution or repeated execution-permission prompts. Validation calls calculators and presentation helpers directly and checks notebook schema/syntax without executing cells. Fresh-kernel execution, saved runtime outputs and live Jupyter/Colab checks remain deferred. This is not a claim of full presentation verification.


## Ready presentation update — 2026-09-29

See the [Ready notebook review](READY_NOTEBOOK_REVIEW.md) for updated chart/control behavior, package boundaries, fresh-kernel outputs, automated checks, and live-check limitations. This update supersedes the historical execution deferrals above.
