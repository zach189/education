# F3: What Makes an Offtake Financeable? — implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](../notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Notebook and calculations created; automated calculation/plot checks and coherence review complete. Fresh-kernel execution and live presentation acceptance deferred by user instruction. **Prerequisites:** 2 and F1.
**Notebook:** [notebooks/F3_offtake_financeability.ipynb](../notebooks/F3_offtake_financeability.ipynb).

Read the [canonical roadmap](../notebooks/README.md), [shared planning conventions](PLANNING.md), and [project guidance](../AGENTS.md). Foundation plans remain implementation records; this document specifies only the new lesson or unfinished work.

## Learning decision, assumptions, and worked example

All numeric contract terms and scenarios below are hypothetical teaching assumptions, not market quotes.

Question: why can contracts with equal headline value provide different support for repayment? Use a capacity reseller with twelve monthly USD 20,000 service billings and USD 12,000 committed supplier payments. Introduce CFADS as this example's customer cash less supplier cash, before debt and equity; taxes and other costs remain excluded.

Compare three explicit hypothetical contracts: fixed unconditional monthly payment; payment conditional on service acceptance; and cancellation allowed after month 6. All start with a 240,000 headline schedule, but do not label conditional future amounts as unconditional receivables. Base receipts occur month-end t=1…12; supplier payments also month-end. Fixed CFADS=8,000/month. Acceptance at t=3 releases the first three months' accumulated billings (60,000); early cash deficit=24,000, with unchanged full-horizon receipts. Cancellation after six delivered months removes future billings: receipts 120,000, supplier cost 144,000, CFADS total −24,000. No cancellation penalty unless explicitly added.

Customer reliability is demonstrated using a deterministic missed month-7 payment collected at month 10, not an invented credit rating or probability. A service-credit experiment reduces month-4 cash by 20%=4,000; monthly CFADS then 4,000. Do not claim legal enforceability or offer a lender approval score.

## Reusable calculations and interfaces

Add `offtake` with a small frozen `OfftakeTerms` record for payment amount, service months, lag, acceptance condition, cancellation boundary and credit schedule; scenario events are separate inputs. `build_offtake_receipts` returns billings, amounts due, receipts, unpaid amounts, and credits by month. `cash_available_for_debt_service_usd(receipts, operating_payments)` returns a signed tuple with explicit exclusions. Separate billing elimination on cancellation from merely delayed collection; return traceable reasons. This becomes the shared receipt layer for F4/F7/C1; do not create credit-score or default-probability APIs.

## Cell-by-cell teaching sequence

Use 17 cells: eight Markdown/code pairs below, followed by a final Markdown takeaway with references and the indicated next lesson. Each Markdown cell after an experiment explains the preceding output before introducing the next prediction. Target 10–15 minutes, 800–1,100 prose words; label any extensions optional.

| Cells | Markdown explanation / optional prediction | Executable content |
|---|---|---|
| 1–2 | Question and three contract summaries | State the same headline contract value and compare obligations, conditions and rights. |
| 3–4 | Direct CFADS arithmetic | Calculate 20,000−12,000, plus the credit and cancellation totals. |
| 5–6 | Receipt recognition versus cash | Build one acceptance-release schedule manually before shared calls. |
| 7–8 | Comparison and explorer | Table headline/owed/received/CFADS/funding; receipt timelines with acceptance and cancellation controls. |
| 9–10 | Experiment: acceptance delay | Hold service constant, delay collection; distinguish timing from revenue loss. |
| 11–12 | Experiment: cancellation | Stop future service billings while committed rent continues; explain economic loss. |
| 13–14 | Experiment: reliability and credits | Separate a late payment from a permanent 4,000 credit; compare full-horizon totals. |
| 15–16 | Takeaway and F4 | Use explicit dependable receipts to ask how much debt they can support. Display a compact decision summary from the already calculated results; introduce no new model. |
| 17 | Final interpretation, limitations, references and next step. | No diagnostics or hidden answers. |

All direct arithmetic precedes its packaged counterpart. One compact table and one main chart type; explorer controls update calculated outputs in one helper call with a static fallback. Keep experiments fixed independently of prior widget edits.

## Acceptance and implementation checks

Test no conditions baseline, catch-up collection without duplication, cancellation boundary, delayed receipts beyond service, credit bounds, zero receipts, negative CFADS and unchanged supplier obligations. Reject credit exceeding its bill and inconsistent accepted/cancelled dates. Distinguish due balance from scenario cash loss.

Implement calculations and independent tests first, then education helpers, then notebook. Run the shared lint/type/test/schema/fresh-kernel checks, inspect local rendering and live control recovery, restore defaults and save outputs. Follow the complete checklist in [PLANNING.md](PLANNING.md); Colab remains deferred.

## Boundary with other lessons

F3 owns contractual receipt quality, not debt capacity or market-price simulation. F4 consumes its cash scenarios. M4 addresses price/quantity exposure; it must reuse receipt logic when conditions matter rather than redefine contract enforceability.

## Sources and attribution

World Bank transaction issues support cash-flow/contract review; SEC financial-statement guide supports cash versus income. Any legal enforceability claims require separate jurisdiction-specific primary research; omit them from this lesson.

See the [source ledger](PLANNING.md#source-ledger) for inspected sources versus research still required. Place verified citations next to supported explanations; distinguish original inputs and derived results. No live data or new dependencies are required for the core lesson.

## Implementation and post-implementation review

Reviewed against Notebook 2/F1/F2: unconditional due amounts, conditional billings and actual receipts are separate; USD 24,000 early acceptance funding differs from the USD 24,000 cancellation loss. Credits permanently reduce cash, while late collection preserves full-horizon totals. Supplier obligations do not vanish.

The original sequence and worked cases above remain the specification. Implemented calculation functions have finite/type/range checks and independent tests. Presentation helpers use lazy imports, ordinary static plots, independent optional controls and editable-cell fallbacks. Notebook source has 17 alternating cells and passes static schema/syntax/teaching-structure checks without executing the lesson.

Verification scope was changed explicitly by the user during implementation: **do not run notebooks; verify calculation and plotting code with tests**. Fresh-kernel, saved-output and live Jupyter acceptance is therefore deferred. F2 alone executed once before that instruction; its subsequent edits are not execution-verified. This record does not claim complete local presentation verification or Colab support.

## Automated validation completed

- 325 tests passed; seven existing notebook-cell execution tests were deliberately deselected using `-k 'not notebook_arithmetic and not visible_arithmetic'`.
- Ruff lint and formatting checks passed across source, tests, scripts and notebooks; strict mypy passed for all 13 calculation/presentation modules.
- All eight new notebooks pass static schema, syntax, 17-cell structure, prose/units, and no-diagnostic checks. No new notebook cells were executed during this verification pass.
- Direct helper tests cover chart data from every lesson, labels and signed values, stacked uses, widget-free plotting, exact initial controls, independence, invalid-input replacement and recovery.
- Local links in both READMEs, the planning index and financing plans resolve.
- F2's initial execution preceded the no-run instruction. Its later changes and all F3–F9 execution/live acceptance remain deferred. No Colab checks were performed.
