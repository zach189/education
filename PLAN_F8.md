# F8: GPU Ownership, Leasing, and Residual Value — implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Notebook and calculations created; automated calculation/plot checks and coherence review complete. Fresh-kernel execution and live presentation acceptance deferred by user instruction. **Prerequisites:** 2 and F4.
**Notebook:** [notebooks/F8_ownership_leasing_residual_value.ipynb](notebooks/F8_ownership_leasing_residual_value.ipynb).

Read the [canonical roadmap](notebooks/README.md), [shared planning conventions](PLANNING.md), and [project guidance](AGENTS.md). Foundation plans remain implementation records; this document specifies only the new lesson or unfinished work.

## Learning decision, assumptions, and worked example

All numeric contract terms and scenarios below are hypothetical teaching assumptions, not market quotes.

Explicitly use a GPU-owning or leasing project, not the renter/reseller. Compare acquisition cost cash flows for identical equipment availability over 36 months. Purchase price USD 300,000 at t=0; illustrative resale receipt 60,000 at t=36. Lease costs 8,000/month t=1…36, no deposit, no buyout, no ownership or resale rights. Same operating receipts and costs omitted from procurement comparison; maintenance assumed included identically for this comparison. PV rate 12% effective annual.

Unlevered purchase cost=300,000−60,000=240,000 versus lease 288,000, but PV uses different timing. For financing overlay, borrow 210,000 at t=0, 10% nominal annual, fully amortize over 48 months; evaluate sale at month 36 after that month’s scheduled payment, with mandatory repayment of remaining debt from sale plus any owner cash shortfall. No monthly principal beyond sale after the payoff. Residual after debt=max or signed sale proceeds−outstanding debt; report negative equity need rather than hiding it.

Straight-line illustrative book depreciation=(300,000−60,000)/36, yielding month 36 book value 60,000. Change resale to 20,000 or 100,000 without changing the originally assumed book depreciation. Book value is not cash, market value, tax depreciation or a guarantee.

## Reusable calculations and interfaces

Add `equipment` with `compare_purchase_lease_cash_flows` (price, lease sequence, exit month/proceeds, common discount rate) and `equipment_exit_equity_usd` (sale proceeds, debt payoff). A separate `straight_line_book_values` makes the arithmetic distinction explicit without accounting-compliance claims. Reuse F1 debt rows and monthly PV; do not encode a legal lease classifier or change reseller economics. Validate positive useful life/horizon, nonnegative price/residual and explicit resale rights. Lease returns no resale receipt unless an explicitly modeled purchase option is exercised (outside core).

## Cell-by-cell teaching sequence

Use 17 cells: eight Markdown/code pairs below, followed by a final Markdown takeaway with references and the indicated next lesson. Each Markdown cell after an experiment explains the preceding output before introducing the next prediction. Target 10–15 minutes, 800–1,100 prose words; label any extensions optional.

| Cells | Markdown explanation / optional prediction | Executable content |
|---|---|---|
| 1–2 | Business model and alternatives | State ownership and lease rights before numbers. |
| 3–4 | Visible cost arithmetic | Compare nominal purchase/lease costs and time-zero versus future amounts. |
| 5–6 | Shared procurement table | Original schedule PVs; distinguish nominal winner from discounted comparison. |
| 7–8 | Explorer | Cumulative procurement cash; controls residual proceeds and lease price. |
| 9–10 | Experiment: resale loss | 60,000→20,000; retain book assumptions, show changed actual cash. |
| 11–12 | Experiment: financed exit | Add F1 debt; repay remaining balance at month 36, show equity shortfall. |
| 13–14 | Experiment: lease versus purchase risk | Compare 100,000 upside and 20,000 downside, identical service. |
| 15–16 | Takeaway and F9 | Ownership changes who bears exit risk; remaining cash still follows financing restrictions. Display a compact decision summary from the already calculated results; introduce no new model. |
| 17 | Final interpretation, limitations, references and next step. | No diagnostics or hidden answers. |

All direct arithmetic precedes its packaged counterpart. One compact table and one main chart type; explorer controls update calculated outputs in one helper call with a static fallback. Keep experiments fixed independently of prior widget edits.

## Acceptance and implementation checks

Test sale counted once, no lease resale, terminal debt payoff cancels later payments, zero debt case, residual below debt, book depreciation sum and independent resale changes, PV at zero rate, and equal service horizons.

Implement calculations and independent tests first, then education helpers, then notebook. Run the shared lint/type/test/schema/fresh-kernel checks, inspect local rendering and live control recovery, restore defaults and save outputs. Follow the complete checklist in [PLANNING.md](PLANNING.md); Colab remains deferred.

## Boundary with other lessons

F8 owns asset rights and terminal proceeds. F5 owns deployment timing. F9 allocates available cash; it must consume F8 exit cash without adding proceeds again. Do not imply book depreciation is available to pay debt.

## Sources and attribution

SEC financial-statements guide for depreciation and cash distinction; inspect relevant IFRS/IAS16 primary guidance before any accounting-standard claim. This plan uses illustrative book arithmetic only, not tax/legal advice.

See the [source ledger](PLANNING.md#source-ledger) for inspected sources versus research still required. Place verified citations next to supported explanations; distinguish original inputs and derived results. No live data or new dependencies are required for the core lesson.

## Implementation and post-implementation review

Reviewed against Notebook 2/F1/F4/F5: explicit ownership precedes sale proceeds, lease has no resale, PV uses the existing effective-rate convention, book depreciation is noncash. Exit follows month-36 scheduled payment; remaining USD 60,582.25 debt is paid once and later loan payments are canceled.

The original sequence and worked cases above remain the specification. Implemented calculation functions have finite/type/range checks and independent tests. Presentation helpers use lazy imports, ordinary static plots, independent optional controls and editable-cell fallbacks. Notebook source has 17 alternating cells and passes static schema/syntax/teaching-structure checks without executing the lesson.

Verification scope was changed explicitly by the user during implementation: **do not run notebooks; verify calculation and plotting code with tests**. Fresh-kernel, saved-output and live Jupyter acceptance is therefore deferred. F2 alone executed once before that instruction; its subsequent edits are not execution-verified. This record does not claim complete local presentation verification or Colab support.

## Automated validation completed

- 325 tests passed; seven existing notebook-cell execution tests were deliberately deselected using `-k 'not notebook_arithmetic and not visible_arithmetic'`.
- Ruff lint and formatting checks passed across source, tests, scripts and notebooks; strict mypy passed for all 13 calculation/presentation modules.
- All eight new notebooks pass static schema, syntax, 17-cell structure, prose/units, and no-diagnostic checks. No new notebook cells were executed during this verification pass.
- Direct helper tests cover chart data from every lesson, labels and signed values, stacked uses, widget-free plotting, exact initial controls, independence, invalid-input replacement and recovery.
- Local links in both READMEs, the planning index and financing plans resolve.
- F2's initial execution preceded the no-run instruction. Its later changes and all F3–F9 execution/live acceptance remain deferred. No Colab checks were performed.
