# F4: How Much Debt Can the Deal Support? — implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](../notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Notebook and calculations created; automated calculation/plot checks and coherence review complete. Fresh-kernel execution and live presentation acceptance deferred by user instruction. **Prerequisites:** F1 and F3.
**Notebook:** [notebooks/F4_debt_capacity.ipynb](../notebooks/F4_debt_capacity.ipynb).

Read the [canonical roadmap](../notebooks/README.md), [shared planning conventions](PLANNING.md), and [project guidance](../AGENTS.md). Foundation plans remain implementation records; this document specifies only the new lesson or unfinished work.

## Learning decision, assumptions, and worked example

All numeric contract terms and scenarios below are hypothetical teaching assumptions, not market quotes.

Question: how much initial borrowing can a stated CFADS schedule support while meeting a coverage requirement? Use the reseller's hypothetical CFADS of 8,000 USD/month at t=1…12, no terminal value, 12% nominal annual interest (j=1%), minimum DSCR k=1.25. Cash available is after operating payments but before debt, reserves or distributions; no new owner cash counted in CFADS.

DSCR_t=CFADS_t/(interest_t+principal_t). If no debt service, display N/A rather than infinite coverage. For level payments A, enforce A≤min(CFADS)/k; debt capacity D=A·[1−(1+j)^−n]/j (at zero j use nA). Here A=6,400. For shaped repayments set DS_t=CFADS_t/k and D=sum(DS_t/(1+j)^t), then interest=j·opening_debt and principal=DS_t−interest.

Use uneven CFADS [4,000]*6+[12,000]*6 as the main experiment, keeping total 96,000 unchanged. Level service becomes 3,200; shaped capacity is larger but must pass every debt roll-forward. If desired shaped service is below interest, label the profile infeasible under this lesson's no-capitalization rule instead of hiding negative principal. Capacity is conditional on the assumed schedule and coverage threshold, not a lender's offer.

## Reusable calculations and interfaces

Extend `financing` only with `debt_service_coverage`, `level_payment_debt_capacity_usd`, and `shape_debt_service` returning a frozen result with capacity, payment/debt rows, minimum defined DSCR and feasibility reason. Reuse F1 amortization for level loans and F3 CFADS arrays; internal loan-rate discounting is distinct from chosen business PV. Input arrays begin service month 1; returned cash schedules include t=0. Validate finite nonnegative CFADS for sizing, k≥1, nonnegative loan rate and positive horizon. Negative CFADS is displayed as a scenario that supports no debt under this method, not fed into the annuity sizing routine.

## Cell-by-cell teaching sequence

Use 17 cells: eight Markdown/code pairs below, followed by a final Markdown takeaway with references and the indicated next lesson. Each Markdown cell after an experiment explains the preceding output before introducing the next prediction. Target 10–15 minutes, 800–1,100 prose words; label any extensions optional.

| Cells | Markdown explanation / optional prediction | Executable content |
|---|---|---|
| 1–2 | Debt capacity question | Define CFADS and hypothetical minimum coverage. |
| 3–4 | Hand-worked coverage | 8,000/6,400=1.25; calculate annuity PV before helper. |
| 5–6 | Level schedule | Build capacity loan and table proving every monthly payment and final zero debt. |
| 7–8 | Shaped schedule and explorer | Compare debt balances; controls coverage target and loan rate. |
| 9–10 | Experiment: uneven cash | Keep annual cash unchanged, compare level versus shaped capacity. |
| 11–12 | Experiment: tighter coverage | Move 1.25→1.50; explain why borrowing falls. |
| 13–14 | Experiment: weak early period | Use low/zero early CFADS; visibly reject negative amortization in shaped schedule. |
| 15–16 | Takeaway and F5 | Capacity from operating cash does not fund the period before operations begin. Display a compact decision summary from the already calculated results; introduce no new model. |
| 17 | Final interpretation, limitations, references and next step. | No diagnostics or hidden answers. |

All direct arithmetic precedes its packaged counterpart. One compact table and one main chart type; explorer controls update calculated outputs in one helper call with a static fallback. Keep experiments fixed independently of prior widget edits.

## Acceptance and implementation checks

Check level/shaped equality for flat CFADS, zero-interest capacity, every DSCR constraint, present value of debt service equals draw, principal conservation, no terminal balance, zero CFADS, N/A coverage and infeasible shaped service. Verify rate and coverage monotonicity with independent arithmetic.

Implement calculations and independent tests first, then education helpers, then notebook. Run the shared lint/type/test/schema/fresh-kernel checks, inspect local rendering and live control recovery, restore defaults and save outputs. Follow the complete checklist in [PLANNING.md](PLANNING.md); Colab remains deferred.

## Boundary with other lessons

F4 sizes term debt, not collateral availability (F6), renewal predictions (F7), or distributions (F9). It reuses F1 amortization rather than reteaching interest/principal.

## Sources and attribution

World Bank transaction issues directly describes revenue available for debt service and coverage review. Coverage target and shaping rules are hypothetical, not universal covenant standards.

See the [source ledger](PLANNING.md#source-ledger) for inspected sources versus research still required. Place verified citations next to supported explanations; distinguish original inputs and derived results. No live data or new dependencies are required for the core lesson.

## Implementation and post-implementation review

Reviewed against F1/F3: level debt reuses the original amortizer, service-month CFADS explicitly drops t=0, shaping uses the loan rate, and no-capitalization infeasibility is distinct from a mathematical PV. Flat-case capacity is USD 72,032.50 at 1.25 coverage.

The original sequence and worked cases above remain the specification. Implemented calculation functions have finite/type/range checks and independent tests. Presentation helpers use lazy imports, ordinary static plots, independent optional controls and editable-cell fallbacks. Notebook source has 17 alternating cells and passes static schema/syntax/teaching-structure checks without executing the lesson.

Verification scope was changed explicitly by the user during implementation: **do not run notebooks; verify calculation and plotting code with tests**. Fresh-kernel, saved-output and live Jupyter acceptance is therefore deferred. F2 alone executed once before that instruction; its subsequent edits are not execution-verified. This record does not claim complete local presentation verification or Colab support.

## Automated validation completed

- 325 tests passed; seven existing notebook-cell execution tests were deliberately deselected using `-k 'not notebook_arithmetic and not visible_arithmetic'`.
- Ruff lint and formatting checks passed across source, tests, scripts and notebooks; strict mypy passed for all 13 calculation/presentation modules.
- All eight new notebooks pass static schema, syntax, 17-cell structure, prose/units, and no-diagnostic checks. No new notebook cells were executed during this verification pass.
- Direct helper tests cover chart data from every lesson, labels and signed values, stacked uses, widget-free plotting, exact initial controls, independence, invalid-input replacement and recovery.
- Local links in both READMEs, the planning index and financing plans resolve.
- F2's initial execution preceded the no-run instruction. Its later changes and all F3–F9 execution/live acceptance remain deferred. No Colab checks were performed.
