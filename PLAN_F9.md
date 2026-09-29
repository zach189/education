# F9: Waterfalls, Reserves, and Investor Returns — implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Notebook and calculations created; automated calculation/plot checks and coherence review complete. Fresh-kernel execution and live presentation acceptance deferred by user instruction. **Prerequisites:** F4 and F7; F6/F8 only for those extensions.
**Notebook:** [notebooks/F9_waterfalls_reserves_returns.ipynb](notebooks/F9_waterfalls_reserves_returns.ipynb).

Read the [canonical roadmap](notebooks/README.md), [shared planning conventions](PLANNING.md), and [project guidance](AGENTS.md). Foundation plans remain implementation records; this document specifies only the new lesson or unfinished work.

## Learning decision, assumptions, and worked example

All numeric contract terms and scenarios below are hypothetical teaching assumptions, not market quotes.

Question: how much cash may equity actually receive after expenses, debt and reserve requirements? Start with the reseller's monthly cash after operating costs, no hardware exit in core. Use USD 10,000 cash available before debt, scheduled interest 1,000 and principal 4,000, opening reserve 2,000 and target reserve 6,000. After scheduled debt 5,000, top up reserve 4,000, leaving 1,000; sweep 50%=500 to extra principal and distribute 500. Opening debt USD 100,000 at 12% nominal annual interest closes USD 95,500. Reserve is restricted cash, not an expense or new revenue.

Priority: operating expenses already paid → scheduled interest → scheduled principal → restore reserve → extra-principal cash sweep → permitted equity distribution. Shortfalls draw reserve before recording unpaid debt; no new owner cash is automatically inserted. Pay carried interest arrears before current interest, then principal arrears before current principal; arrears never capitalize or accrue additional interest in this simple model. Block distributions while arrears remain. An optional explicit contractual distribution lock also blocks payouts until lifted. Excess cash remains unrestricted if distributions are blocked. Specify reserve release only on full debt repayment with no unpaid amounts. Recompute future interest after sweeps; scheduled principal follows the original schedule but is capped by remaining debt.

Base scheduled principal is USD 4,000 per month for 25 months, capped at remaining debt after sweeps. Show the first three and final rows in the core table; keep the full ledger optional. Use a 25-month case with initial equity outflow 30,000 (2,000 establishes the opening reserve and 28,000 is already committed to the operating business; no extra opening unrestricted cash) and the displayed cash sequence [10000,10000,3000] + [10000]*22; final liquid cash is distributed only after obligations are paid. Report equity cash invested, returned, net gain and MOIC; chosen-rate equity NPV optional. Do not introduce IRR or confuse a positive MOIC with annual return.

## Reusable calculations and interfaces

Add `waterfalls` frozen `WaterfallRow` exposing cash available, reserve opening/draw/top-up/release/closing, paid/unpaid interest and principal, sweep, distribution, unrestricted closing cash and debt. `allocate_period_cash` handles one period; `build_cash_waterfall` iterates and recomputes interest on actual debt. `equity_return_summary` returns invested/returned/net/MOIC (None for zero investment), reusing PV only in optional extension. Reject negative component inputs and contradictory debt/reserve states; negative cash after operating costs is handled by an explicit operating-shortfall input: use unrestricted cash then reserve, record any unpaid operating expense, and block distributions. Never insert unrequested borrowing or equity. A zero cash input is valid.

## Cell-by-cell teaching sequence

Use 17 cells: eight Markdown/code pairs below, followed by a final Markdown takeaway with references and the indicated next lesson. Each Markdown cell after an experiment explains the preceding output before introducing the next prediction. Target 10–15 minutes, 800–1,100 prose words; label any extensions optional.

| Cells | Markdown explanation / optional prediction | Executable content |
|---|---|---|
| 1–2 | Decision and priority | Show who is paid first and where restricted cash sits. |
| 3–4 | Direct one-period allocation | Work 10,000→5,000→1,000→500 sweep/500 distribution. |
| 5–6 | Shared 25-month waterfall | Reconcile cash, reserve and debt in a compact table. |
| 7–8 | Explorer | Stacked allocations over months; reserve target and sweep fraction controls. |
| 9–10 | Experiment: weak month | Use 3,000 cash; reserve draws prevent or reduce scheduled shortfall. |
| 11–12 | Experiment: larger sweep | 0→50→100%; lower future debt versus later distributions. |
| 13–14 | Experiment: distribution lock | Compare permitted versus blocked payouts; retained cash stays on ledger. |
| 15–16 | Takeaway and C1 | Assess whole transaction outcomes, not contribution profit alone. Display a compact decision summary from the already calculated results; introduce no new model. |
| 17 | Final interpretation, limitations, references and next step. | No diagnostics or hidden answers. |

All direct arithmetic precedes its packaged counterpart. One compact table and one main chart type; explorer controls update calculated outputs in one helper call with a static fallback. Keep experiments fixed independently of prior widget edits.

## Acceptance and implementation checks

Test one-period reference, priority under shortage, reserve cash conservation, no distributions while unpaid amounts remain, sweep capped by debt, zero debt reserve release, recalculated interest, no duplicate terminal cash, and MOIC N/A at zero investment.

Implement calculations and independent tests first, then education helpers, then notebook. Run the shared lint/type/test/schema/fresh-kernel checks, inspect local rendering and live control recovery, restore defaults and save outputs. Follow the complete checklist in [PLANNING.md](PLANNING.md); Colab remains deferred.

## Boundary with other lessons

F9 owns cash allocation and realized equity cash metrics. F4 determines scheduled debt capacity; F8 determines exit proceeds. No preferred-return tiers, compound options or tax waterfall in core.

## Sources and attribution

World Bank finance structures and transaction issues for debt/equity cash-flow concepts; reserve size, priority and distribution blocks are expressly hypothetical contractual rules, not universal lender requirements.

See the [source ledger](PLANNING.md#source-ledger) for inspected sources versus research still required. Place verified citations next to supported explanations; distinguish original inputs and derived results. No live data or new dependencies are required for the core lesson.

## Implementation and post-implementation review

Reviewed against F4/F7/F8: cash priorities preserve principal, cash reserves and arrears; future interest is recalculated after sweeps. No implicit injections or duplicate terminal cash. Baseline equity returned is USD 136,215.39 on USD 30,000 invested, giving 4.5405x MOIC, not an annual return.

The original sequence and worked cases above remain the specification. Implemented calculation functions have finite/type/range checks and independent tests. Presentation helpers use lazy imports, ordinary static plots, independent optional controls and editable-cell fallbacks. Notebook source has 17 alternating cells and passes static schema/syntax/teaching-structure checks without executing the lesson.

Verification scope was changed explicitly by the user during implementation: **do not run notebooks; verify calculation and plotting code with tests**. Fresh-kernel, saved-output and live Jupyter acceptance is therefore deferred. F2 alone executed once before that instruction; its subsequent edits are not execution-verified. This record does not claim complete local presentation verification or Colab support.

## Automated validation completed

- 325 tests passed; seven existing notebook-cell execution tests were deliberately deselected using `-k 'not notebook_arithmetic and not visible_arithmetic'`.
- Ruff lint and formatting checks passed across source, tests, scripts and notebooks; strict mypy passed for all 13 calculation/presentation modules.
- All eight new notebooks pass static schema, syntax, 17-cell structure, prose/units, and no-diagnostic checks. No new notebook cells were executed during this verification pass.
- Direct helper tests cover chart data from every lesson, labels and signed values, stacked uses, widget-free plotting, exact initial controls, independence, invalid-input replacement and recovery.
- Local links in both READMEs, the planning index and financing plans resolve.
- F2's initial execution preceded the no-run instruction. Its later changes and all F3–F9 execution/live acceptance remain deferred. No Colab checks were performed.
