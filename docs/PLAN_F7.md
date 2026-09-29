# F7: Renewal Risk and Maturity Mismatch — implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](../notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Notebook and calculations created; automated calculation/plot checks and coherence review complete. Fresh-kernel execution and live presentation acceptance deferred by user instruction. **Prerequisites:** F3 and F4.
**Notebook:** [notebooks/F7_renewal_and_maturity_mismatch.ipynb](../notebooks/F7_renewal_and_maturity_mismatch.ipynb).

Read the [canonical roadmap](../notebooks/README.md), [shared planning conventions](PLANNING.md), and [project guidance](../AGENTS.md). Foundation plans remain implementation records; this document specifies only the new lesson or unfinished work.

## Learning decision, assumptions, and worked example

All numeric contract terms and scenarios below are hypothetical teaching assumptions, not market quotes.

Question: how much of a debt obligation relies on customer business that is not yet contracted? Reseller has 24 months of fixed supplier payments of 12,000 USD/month. Customer receipts of 20,000 are contracted only for months 1…12; later business is a scenario, not secured revenue. Use initial loan 120,000, 12% nominal annual interest, 24 monthly repayments from t=1. No hardware residual value.

Show two ledgers: legally contracted receipts and assumed renewals. Base scenario renews immediately for months 13…24 at 20,000, keeping CFADS 8,000. Stress a three-month gap (months 13…15 receipts zero), then 17,000/month for months 16…24; rent and debt service continue. Contract-only scenario has no receipts after 12. Count contracted debt service coverage only through contracted revenue, and show debt outstanding at month 12 from the F1 schedule.

Use F4 to compare a debt term ending at month 12 with the 24-month debt on the same principal. Do not size a new loan from uncertain renewal cash in the core. Gap-period cash cost equals three months of 12,000 rent plus scheduled debt service. Keep early accumulated cash available; report both post-month 12 incremental drawdown and whole-schedule initial buffer so a gap is not automatically called an external funding need.

## Reusable calculations and interfaces

Extend `offtake` with `build_renewal_receipt_scenarios` separating contracted, assumed-renewal and total receipts. Return dense monthly rows through all obligations. Reuse F1 amortization, F3 CFADS, F4 DSCR and existing cumulative funding calculations. Add only a small `renewal_exposure_summary` for debt at contract expiry, uncovered obligation months and cash drawdown; do not create another debt calculator or generic probability model.

## Cell-by-cell teaching sequence

Use 17 cells: eight Markdown/code pairs below, followed by a final Markdown takeaway with references and the indicated next lesson. Each Markdown cell after an experiment explains the preceding output before introducing the next prediction. Target 10–15 minutes, 800–1,100 prose words; label any extensions optional.

| Cells | Markdown explanation / optional prediction | Executable content |
|---|---|---|
| 1–2 | Question and expiry mismatch | Timeline of 12 contracted revenue months versus 24 supplier/debt months. |
| 3–4 | Direct gap calculation | Three rent payments plus three debt payments; explain retained cash. |
| 5–6 | Full scenarios | Contract-only, immediate renewal, delayed/lower-price renewal; label assumed cash. |
| 7–8 | Explorer | Cumulative cash and contract-end marker; renewal gap and renewal price controls. |
| 9–10 | Experiment: downtime | 0→3 months, fixed renewed price; isolate quantity/timing loss. |
| 11–12 | Experiment: renewal price | 20,000→17,000, fixed gap; isolate lower debt cover. |
| 13–14 | Experiment: shorter debt maturity | 12 versus 24-month debt; higher earlier service, less debt after contract expiry. |
| 15–16 | Takeaway and F8 | Ask what changes if the business owns equipment with uncertain resale proceeds. Display a compact decision summary from the already calculated results; introduce no new model. |
| 17 | Final interpretation, limitations, references and next step. | No diagnostics or hidden answers. |

All direct arithmetic precedes its packaged counterpart. One compact table and one main chart type; explorer controls update calculated outputs in one helper call with a static fallback. Keep experiments fixed independently of prior widget edits.

## Acceptance and implementation checks

Test no-renewal horizon, receipts exactly zero in gap, no double counted renewal month, continued fixed obligations, debt-at-expiry reconciliation, shorter-term debt zeros after maturity, and cash retained from earlier periods. Negative CFADS is an economic result, not invalid input.

Implement calculations and independent tests first, then education helpers, then notebook. Run the shared lint/type/test/schema/fresh-kernel checks, inspect local rendering and live control recovery, restore defaults and save outputs. Follow the complete checklist in [PLANNING.md](PLANNING.md); Colab remains deferred.

## Boundary with other lessons

M1 introduces unfinanced buying long/selling short. F7 focuses on debt survival after contracted revenue expires, explicitly reusing F3/F4 rather than repeating the M1 implied-curve lesson. No new hedging or forecasting here.

## Sources and attribution

World Bank transaction issues supports review of demand and debt-service cash flow. Renewal rates/gaps are illustrative scenarios; no empirical GPU-renewal claim is required.

See the [source ledger](PLANNING.md#source-ledger) for inspected sources versus research still required. Place verified citations next to supported explanations; distinguish original inputs and derived results. No live data or new dependencies are required for the core lesson.

## Implementation and post-implementation review

Reviewed against F3/F4 and the planned M1 boundary: contracted and renewal cash stay separate, debt service reuses F1, gap costs retain earlier cash, and shorter debt maturity does not erase the supplier tail. No hardware proceeds or renewal forecasts are inferred.

The original sequence and worked cases above remain the specification. Implemented calculation functions have finite/type/range checks and independent tests. Presentation helpers use lazy imports, ordinary static plots, independent optional controls and editable-cell fallbacks. Notebook source has 17 alternating cells and passes static schema/syntax/teaching-structure checks without executing the lesson.

Verification scope was changed explicitly by the user during implementation: **do not run notebooks; verify calculation and plotting code with tests**. Fresh-kernel, saved-output and live Jupyter acceptance is therefore deferred. F2 alone executed once before that instruction; its subsequent edits are not execution-verified. This record does not claim complete local presentation verification or Colab support.

## Automated validation completed

- 325 tests passed; seven existing notebook-cell execution tests were deliberately deselected using `-k 'not notebook_arithmetic and not visible_arithmetic'`.
- Ruff lint and formatting checks passed across source, tests, scripts and notebooks; strict mypy passed for all 13 calculation/presentation modules.
- All eight new notebooks pass static schema, syntax, 17-cell structure, prose/units, and no-diagnostic checks. No new notebook cells were executed during this verification pass.
- Direct helper tests cover chart data from every lesson, labels and signed values, stacked uses, widget-free plotting, exact initial controls, independence, invalid-input replacement and recovery.
- Local links in both READMEs, the planning index and financing plans resolve.
- F2's initial execution preceded the no-run instruction. Its later changes and all F3–F9 execution/live acceptance remain deferred. No Colab checks were performed.
