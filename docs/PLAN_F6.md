# F6: Receivables and Collateral — implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](../notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Notebook and calculations created; automated calculation/plot checks and coherence review complete. Fresh-kernel execution and live presentation acceptance deferred by user instruction. **Prerequisites:** F3 and F4.
**Notebook:** [notebooks/F6_receivables_and_collateral.ipynb](../notebooks/F6_receivables_and_collateral.ipynb).

Read the [canonical roadmap](../notebooks/README.md), [shared planning conventions](PLANNING.md), and [project guidance](../AGENTS.md). Foundation plans remain implementation records; this document specifies only the new lesson or unfinished work.

## Learning decision, assumptions, and worked example

All numeric contract terms and scenarios below are hypothetical teaching assumptions, not market quotes.

Question: how much can a lender advance today against explicitly eligible receivables? Use the reseller, with receivables only—no hardware assigned to it. Snapshot invoice amounts A=100,000, B=80,000, C=20,000 USD, all eligible initially. Eligibility requires an unconditional issued receivable, not merely a signed future offtake; illustrative age limit 60 days and exclusions for disputes.

Specify a deliberately simple concentration rule: cap each customer's eligible balance at 40% of total eligible receivables **before concentration deductions**. Thus total E=200,000, cap=80,000, adjusted balances=80,000/80,000/20,000 and adjusted E=180,000. At 80% advance rate minus 10,000 reserve, borrowing base=134,000. Facility limit=150,000 and current debt=100,000; availability=max(0, min(limit, base)−debt)=34,000. Report overadvance=max(0, debt−min(limit, base)) separately; do not let negative availability disappear without explanation.

Age B beyond 60 days: E=120,000, cap=48,000, adjusted E=68,000, base=44,400, overadvance=55,600. A concentration rule referencing post-cap total is a different contract and is excluded. A default scenario is not necessary: eligibility alone can change liquidity.

## Reusable calculations and interfaces

Add `collateral` records `Receivable(customer_id, amount_usd, age_days, unconditional, disputed)` and `BorrowingBaseResult` including per-invoice eligibility/reasons, concentration deductions, adjusted eligible amount, gross advance, reserves, base, limit, debt, availability and overadvance. `calculate_receivables_borrowing_base` implements the stated ordering exactly. Validate nonnegative finite amounts, integer days, flags and advance/concentration fractions; invoices sharing a customer aggregate before the cap. Empty pools yield zero base and possible overadvance; reserve cannot create a negative base.

## Cell-by-cell teaching sequence

Use 17 cells: eight Markdown/code pairs below, followed by a final Markdown takeaway with references and the indicated next lesson. Each Markdown cell after an experiment explains the preceding output before introducing the next prediction. Target 10–15 minutes, 800–1,100 prose words; label any extensions optional.

| Cells | Markdown explanation / optional prediction | Executable content |
|---|---|---|
| 1–2 | Decision and rights | Define eligible receivable versus conditional future promise. |
| 3–4 | Visible borrowing-base arithmetic | 200,000→180,000→144,000−10,000=134,000; availability 34,000. |
| 5–6 | Invoice eligibility table | Show every inclusion/exclusion and the fixed concentration denominator. |
| 7–8 | Explorer | Bridge chart from face receivables to borrowing base; controls age limit, advance fraction, reserve. |
| 9–10 | Experiment: aged invoice | Make B ineligible; explain shrinking denominator and overadvance. |
| 11–12 | Experiment: concentration | Compare the same total across three versus one customer. |
| 13–14 | Experiment: facility ceiling | Increase collateral while holding commitment fixed; availability eventually stops growing. |
| 15–16 | Takeaway and F7 | Collateral-based capacity does not replace dependable future revenue. Display a compact decision summary from the already calculated results; introduce no new model. |
| 17 | Final interpretation, limitations, references and next step. | No diagnostics or hidden answers. |

All direct arithmetic precedes its packaged counterpart. One compact table and one main chart type; explorer controls update calculated outputs in one helper call with a static fallback. Keep experiments fixed independently of prior widget edits.

## Acceptance and implementation checks

Test both worked results, aggregation before cap, exact age cutoff inclusive, disputed/conditional exclusion, no double deductions, empty pool, reserve floor, facility ceiling, overadvance, and order-independent invoice input. No invented hardware collateral.

Implement calculations and independent tests first, then education helpers, then notebook. Run the shared lint/type/test/schema/fresh-kernel checks, inspect local rendering and live control recovery, restore defaults and save outputs. Follow the complete checklist in [PLANNING.md](PLANNING.md); Colab remains deferred.

## Boundary with other lessons

F6 owns snapshot collateral availability, not DSCR term-debt capacity (F4). F3 owns whether payment becomes due. C1 may apply both limits, but must never add them as independent funding sources.

## Sources and attribution

OCC Asset-Based Lending handbook is the primary research source for borrowing-base structures, reserves and monitoring. Verify the linked booklet before implementation; the 40% pre-cap denominator is our declared teaching rule, not an OCC mandate.

See the [source ledger](PLANNING.md#source-ledger) for inspected sources versus research still required. Place verified citations next to supported explanations; distinguish original inputs and derived results. No live data or new dependencies are required for the core lesson.

## Implementation and post-implementation review

Reviewed against F3/F4: unconditional invoice eligibility is distinct from future contract value; customer balances aggregate before concentration. Baseline availability USD 34,000 and aged-B overadvance USD 55,600 match the plan. Facility and borrowing-base limits are applied together, never added.

The original sequence and worked cases above remain the specification. Implemented calculation functions have finite/type/range checks and independent tests. Presentation helpers use lazy imports, ordinary static plots, independent optional controls and editable-cell fallbacks. Notebook source has 17 alternating cells and passes static schema/syntax/teaching-structure checks without executing the lesson.

Verification scope was changed explicitly by the user during implementation: **do not run notebooks; verify calculation and plotting code with tests**. Fresh-kernel, saved-output and live Jupyter acceptance is therefore deferred. F2 alone executed once before that instruction; its subsequent edits are not execution-verified. This record does not claim complete local presentation verification or Colab support.

## Automated validation completed

- 325 tests passed; seven existing notebook-cell execution tests were deliberately deselected using `-k 'not notebook_arithmetic and not visible_arithmetic'`.
- Ruff lint and formatting checks passed across source, tests, scripts and notebooks; strict mypy passed for all 13 calculation/presentation modules.
- All eight new notebooks pass static schema, syntax, 17-cell structure, prose/units, and no-diagnostic checks. No new notebook cells were executed during this verification pass.
- Direct helper tests cover chart data from every lesson, labels and signed values, stacked uses, widget-free plotting, exact initial controls, independence, invalid-input replacement and recovery.
- Local links in both READMEs, the planning index and financing plans resolve.
- F2's initial execution preceded the no-run instruction. Its later changes and all F3–F9 execution/live acceptance remain deferred. No Colab checks were performed.
