# F2: Bridging an OEM Deposit to Customer Prepayment — implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](../notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Notebook and calculations created; automated calculation/plot checks and coherence review complete. Fresh-kernel execution and live presentation acceptance deferred by user instruction. **Prerequisites:** F1.
**Notebook:** [notebooks/F2_oem_deposit_bridge.ipynb](../notebooks/F2_oem_deposit_bridge.ipynb).

Read the [canonical roadmap](../notebooks/README.md), [shared planning conventions](PLANNING.md), and [project guidance](../AGENTS.md). Foundation plans remain implementation records; this document specifies only the new lesson or unfinished work.

## Learning decision, assumptions, and worked example

All numeric contract terms and scenarios below are hypothetical teaching assumptions, not market quotes.

Switch explicitly to a GPU-purchasing project, not the reseller. Question: can a short bridge be repaid by the agreed customer prepayment when the accepted order is documented?

Use USD 1,000,000 equipment order, USD 200,000 deposit at day 0, accepted order documented day 10, customer prepayment USD 250,000 due day 15 and received day 20. Signed offtake precedes day 0. The bridge matures at day 60; report unpaid amounts at that horizon without assuming refinancing. Borrow 200,000 at day 0, pay a 1% fee separately, accrue 12% nominal simple annual interest ACT/365, and repay principal plus interest on receipt. Day-20 interest=1,315.07; payoff=201,315.07; residual customer cash=48,684.93; owner cash for the fee=2,000. Remaining order cost and customer performance obligations do not disappear; they are outside this short bridge window.

Sequence: signed offtake → OEM deposit required → accepted order documented → prepayment becomes due → cash received → bridge repaid. The intended repayment source is customer prepayment, not operating revenue. If documentation condition fails, no customer amount becomes due; if satisfied but cash is late, it is an overdue obligation. No automatic hardware collateral before delivery. Distinguish contractual refund rights from assumed recovery cash.

Stress receipt day 50 (interest 3,287.67); an unmet condition with no receipt through day 60 (debt plus accrued interest 203,945.21, not automatic repayment); and deposit cancellation with an explicitly assumed 80% cash refund at day 30 (principal shortfall 40,000 plus interest 1,972.60). These are independent scenarios, not probabilities.

## Reusable calculations and interfaces

Add `bridge_financing` with frozen `BridgeEvent(day_offset, kind, amount_usd)` and `BridgeRow` (opening principal, draw, accrued interest, repayment, cash, remaining principal/interest). Provide `build_deposit_bridge_schedule` with explicit condition_met, documentation/due/receipt dates, horizon, deposit/prepayment/refund amounts, draw, nominal rate, and fee. Return dense event rows plus outstanding debt at horizon. Use elapsed-day simple interest only on unpaid principal; no interest-on-interest. A payoff uses customer/refund cash up to principal plus accrued interest, with any shortage shown separately rather than silently adding equity. Validate chronological conditions; None means absent event, not zero-day receipt. Add an event-cash funding helper with explicit netting; never send day offsets to monthly PV functions.

## Cell-by-cell teaching sequence

Use 17 cells: eight Markdown/code pairs below, followed by a final Markdown takeaway with references and the indicated next lesson. Each Markdown cell after an experiment explains the preceding output before introducing the next prediction. Target 10–15 minutes, 800–1,100 prose words; label any extensions optional.

| Cells | Markdown explanation / optional prediction | Executable content |
|---|---|---|
| 1–2 | Decision and role change | State equipment order, deposit rights, and fixed hypothetical inputs. |
| 3–4 | Event sequence | Display condition/due/receipt table; separate obligation from actual cash. |
| 5–6 | Direct bridge arithmetic | Calculate 20-day interest, fee, payoff, remaining customer cash by hand. |
| 7–8 | Shared schedule and explorer | Show debt and cumulative cash over event days; receipt-day and prepayment-amount controls. |
| 9–10 | Experiment: payment owed but delayed | Move receipt from day 20 to 50, keeping documentation/due dates fixed. |
| 11–12 | Experiment: condition never met | Remove accepted-order event and receipt, retain horizon debt; explain no receivable yet. |
| 13–14 | Experiment: cancellation and refund | Apply only the stated 80% refund at day 30; show uncovered principal/interest. |
| 15–16 | Takeaway and transition | Explain all prior results; connect contract reliability to F3 and deployment to F5. Display a compact decision summary from the already calculated results; introduce no new model. |
| 17 | Final interpretation, limitations, references and next step. | No diagnostics or hidden answers. |

All direct arithmetic precedes its packaged counterpart. One compact table and one main chart type; explorer controls update calculated outputs in one helper call with a static fallback. Keep experiments fixed independently of prior widget edits.

## Acceptance and implementation checks

Validate day-count interest, same-day draw/payoff, zero interest, no draw, fee once, delayed versus unmet status, horizon unpaid debt, partial recovery conservation, and rejection of receipt before satisfied condition. The USD 200,000 draw and deposit offset at day 0, leaving only the fee funding need in the base case.

Implement calculations and independent tests first, then education helpers, then notebook. Run the shared lint/type/test/schema/fresh-kernel checks, inspect local rendering and live control recovery, restore defaults and save outputs. Follow the complete checklist in [PLANNING.md](PLANNING.md); Colab remains deferred.

## Boundary with other lessons

F2 ends at bridge payoff or a stated unresolved horizon. It does not model delivery, acceptance, multi-year amortization, DSCR sizing, or revenue commencement; F5 owns that longer construction/deployment period. Use a separate daily event module, not changes to F1 monthly conventions.

## Sources and attribution

World Bank project-finance concepts support phase separation. Before notebook implementation inspect primary order/prepayment clauses if making any factual claim about such terms; none are presumed here. Do not repeat pasted facility disclosures as verified evidence.

See the [source ledger](PLANNING.md#source-ledger) for inspected sources versus research still required. Place verified citations next to supported explanations; distinguish original inputs and derived results. No live data or new dependencies are required for the core lesson.

## Implementation and post-implementation review

Reviewed the role change from F1, ACT/365 versus monthly conventions, conditional versus overdue cash, fee funding and maturity debt. The explicit principal-first USD 160,000 refund leaves USD 40,000 principal plus USD 1,972.60 interest at day 30 and USD 42,367.12 total unpaid at day 60. No recovery or refinancing is assumed.

The original sequence and worked cases above remain the specification. Implemented calculation functions have finite/type/range checks and independent tests. Presentation helpers use lazy imports, ordinary static plots, independent optional controls and editable-cell fallbacks. Notebook source has 17 alternating cells and passes static schema/syntax/teaching-structure checks without executing the lesson.

Verification scope was changed explicitly by the user during implementation: **do not run notebooks; verify calculation and plotting code with tests**. Fresh-kernel, saved-output and live Jupyter acceptance is therefore deferred. F2 alone executed once before that instruction; its subsequent edits are not execution-verified. This record does not claim complete local presentation verification or Colab support.

## Automated validation completed

- 325 tests passed; seven existing notebook-cell execution tests were deliberately deselected using `-k 'not notebook_arithmetic and not visible_arithmetic'`.
- Ruff lint and formatting checks passed across source, tests, scripts and notebooks; strict mypy passed for all 13 calculation/presentation modules.
- All eight new notebooks pass static schema, syntax, 17-cell structure, prose/units, and no-diagnostic checks. No new notebook cells were executed during this verification pass.
- Direct helper tests cover chart data from every lesson, labels and signed values, stacked uses, widget-free plotting, exact initial controls, independence, invalid-input replacement and recovery.
- Local links in both READMEs, the planning index and financing plans resolve.
- F2's initial execution preceded the no-run instruction. Its later changes and all F3–F9 execution/live acceptance remain deferred. No Colab checks were performed.
