# F5: Deployment Delays and Staged Funding — implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](../notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Notebook and calculations created; automated calculation/plot checks and coherence review complete. Fresh-kernel execution and live presentation acceptance deferred by user instruction. **Prerequisites:** F2 and F4.
**Notebook:** [notebooks/F5_deployment_and_staged_funding.ipynb](../notebooks/F5_deployment_and_staged_funding.ipynb).

Read the [canonical roadmap](../notebooks/README.md), [shared planning conventions](PLANNING.md), and [project guidance](../AGENTS.md). Foundation plans remain implementation records; this document specifies only the new lesson or unfinished work.

## Learning decision, assumptions, and worked example

All numeric contract terms and scenarios below are hypothetical teaching assumptions, not market quotes.

Switch to a GPU-owning project and question how much financing must be available before revenue starts. Equipment price 1,000,000: deposit 200,000 at t=0, delivery payment 600,000 at t=3, acceptance payment 200,000 at t=4. Revenue 110,000 and cash operating expense 15,000 monthly for 12 operating months starting t=5. Monthly pre-operation site cost 5,000 at t=1…4. Delaying delivery and acceptance two months also delays revenue and adds two site-cost months; extend the horizon instead of truncating receipts.

Compare drawing all 800,000 debt at t=0 against staged debt equal to 80% of each equipment payment (160,000 at t=0, 480,000 at t=3, 160,000 at t=4). Equity funds the remaining price and interest. Rate 12% nominal annual, interest paid monthly on opening debt; boundary draws affect the next month's interest. No interest capitalization, fee, or debt service before acceptance other than interest. Starting one month after acceptance, fully amortize the outstanding 800,000 over 12 months using F1. Staging saves 20,800 of interest through t=4: immediate 32,000 versus staged 11,200.

Specify purchase rights and delivery as scenario events, not automatic collateral. Funding plan is committed for the illustration; it is not contingent on already delivered collateral. No order-triggered customer prepayment in this lesson.

## Reusable calculations and interfaces

Add `deployment` with `build_deployment_funding_schedule` accepting milestone months/payments, operating-start month, operating cash arrays, draw strategy, debt fraction, rate and repayment term. Rows expose capex, pre-operation expense, operating receipts/costs, draws, paid interest, principal, debt and pre-equity cash. Use F1 repayment builder only after the final draw; construction interest calculated on opening debt. Reuse F4 as a separate feasibility comparison; do not assume the selected 800,000 fits DSCR. Flag any post-acceptance coverage shortfall. Reject out-of-order delivery/acceptance/start, duplicate incompatible milestones and nonfinite totals.

## Cell-by-cell teaching sequence

Use 17 cells: eight Markdown/code pairs below, followed by a final Markdown takeaway with references and the indicated next lesson. Each Markdown cell after an experiment explains the preceding output before introducing the next prediction. Target 10–15 minutes, 800–1,100 prose words; label any extensions optional.

| Cells | Markdown explanation / optional prediction | Executable content |
|---|---|---|
| 1–2 | Project phase change | Draw the equipment milestones and distinguish F2’s short bridge. |
| 3–4 | Direct construction interest | Compute opening-debt interest through t=4 for both draw strategies. |
| 5–6 | Shared full schedule | Join milestone payments to operating receipts and post-acceptance amortization. |
| 7–8 | Explorer | Cumulative pre-equity cash; controls delivery delay and debt fraction. |
| 9–10 | Experiment: staged draws | Hold capex/operations identical; compare interest and required equity. |
| 11–12 | Experiment: delayed acceptance | Shift acceptance and all operating months; include extra site costs. |
| 13–14 | Experiment: reduced debt commitment | 80%→60%; distinguish lower interest from greater equity funding. |
| 15–16 | Takeaway and F6 | Compare funding commitment with what assets actually support a borrowing base. Display a compact decision summary from the already calculated results; introduce no new model. |
| 17 | Final interpretation, limitations, references and next step. | No diagnostics or hidden answers. |

All direct arithmetic precedes its packaged counterpart. One compact table and one main chart type; explorer controls update calculated outputs in one helper call with a static fallback. Keep experiments fixed independently of prior widget edits.

## Acceptance and implementation checks

Test 20,800 interest difference, same-day draw convention, delay extension through final receipt/repayment, capex counted once, no revenue before acceptance, debt roll-forward, zero rate and fee-free equity case. Construction interest must not enter debt principal. Compare post-start debt capacity separately.

Implement calculations and independent tests first, then education helpers, then notebook. Run the shared lint/type/test/schema/fresh-kernel checks, inspect local rendering and live control recovery, restore defaults and save outputs. Follow the complete checklist in [PLANNING.md](PLANNING.md); Colab remains deferred.

## Boundary with other lessons

F2 is repaid by a near-term customer prepayment. F5 funds milestones and operations commencement with term debt/equity. F8 later compares purchasing against leasing; F5 holds equipment procurement form fixed.

## Sources and attribution

World Bank project-finance concepts distinguishes construction from operational cash flows. Milestone prices, timing, availability and lending commitment are assumptions, not reported facility terms.

See the [source ledger](PLANNING.md#source-ledger) for inspected sources versus research still required. Place verified citations next to supported explanations; distinguish original inputs and derived results. No live data or new dependencies are required for the core lesson.

## Implementation and post-implementation review

Reviewed against F2/F4: equipment milestones and deployment are separate from a prepayment bridge. Staging saves USD 20,800 construction interest; two-month delay extends all twelve operating receipts and adds site costs. The selected commitment is checked separately against operating debt capacity.

The original sequence and worked cases above remain the specification. Implemented calculation functions have finite/type/range checks and independent tests. Presentation helpers use lazy imports, ordinary static plots, independent optional controls and editable-cell fallbacks. Notebook source has 17 alternating cells and passes static schema/syntax/teaching-structure checks without executing the lesson.

Verification scope was changed explicitly by the user during implementation: **do not run notebooks; verify calculation and plotting code with tests**. Fresh-kernel, saved-output and live Jupyter acceptance is therefore deferred. F2 alone executed once before that instruction; its subsequent edits are not execution-verified. This record does not claim complete local presentation verification or Colab support.

## Automated validation completed

- 325 tests passed; seven existing notebook-cell execution tests were deliberately deselected using `-k 'not notebook_arithmetic and not visible_arithmetic'`.
- Ruff lint and formatting checks passed across source, tests, scripts and notebooks; strict mypy passed for all 13 calculation/presentation modules.
- All eight new notebooks pass static schema, syntax, 17-cell structure, prose/units, and no-diagnostic checks. No new notebook cells were executed during this verification pass.
- Direct helper tests cover chart data from every lesson, labels and signed values, stacked uses, widget-free plotting, exact initial controls, independence, invalid-input replacement and recovery.
- Local links in both READMEs, the planning index and financing plans resolve.
- F2's initial execution preceded the no-run instruction. Its later changes and all F3–F9 execution/live acceptance remain deferred. No Colab checks were performed.
