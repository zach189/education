# E4: Floating-Rate Financing and Interest-Rate Hedging — implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](../notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Created/tested; optional elective. Coherence reviewed; execution/live acceptance deferred by user instruction. **Prerequisites:** F4 and M2.
**Notebook:** [notebooks/E4_floating_rate_financing.ipynb](../notebooks/E4_floating_rate_financing.ipynb).

Read the [canonical roadmap](../notebooks/README.md), [shared planning conventions](PLANNING.md), and [project guidance](../AGENTS.md). Foundation plans remain implementation records; this document specifies only the new lesson or unfinished work.

## Learning decision, assumptions, and worked example

All numeric contract terms and scenarios below are hypothetical teaching assumptions, not market quotes.

Optional question: does a fixed-pay/receive-floating swap stabilize this loan's interest bill? Use an existing project debt balance 1,000,000 USD, twelve interest-only months and principal paid at t=12. This is an explicit extension beyond F1's fully amortizing core. Monthly reference rates are known at period start; illustrative nominal annual path 4% for months 1…6 and 6% for 7…12; spread 3%; monthly year fraction 1/12. Rates are hypothetical, not SOFR observations.

Unhedged interest=1,000,000·[(.04+.03)·.5+(.06+.03)·.5]=80,000. Swap notional 1,000,000, fixed 5%, receive reference; payer swap outflow=N·(fixed−reference)/12. Full-period swap net 0; combined interest 80,000=8% annual on principal. Under flat reference 8%, unhedged 110,000; swap receives 30,000 and combined remains 80,000. A matched notional/reference/payment convention is essential.

Experiment with half hedge (500,000 notional) and loan reference floor 5% while received swap reference remains 4%: remaining floor exposure is real, not cancelled by a swap on the unfloored rate. Exclude collateral in core; route liquidity questions to M7. No SOFR compounding implementation, live rates or fair swap-strike pricing.

## Reusable calculations and interfaces

Add `floating_rates` with `floating_loan_interest_usd(opening_principal_sequence, reference_rates, spread, year_fractions, floor)` and `fixed_pay_swap_settlements_usd(notional_sequence, reference_rates, fixed_rate, year_fractions)`. Align dates/lengths; positive loan costs and signed swap outflows use explicit docstrings. Reuse M2 sign conventions through an adapter rather than mislabeling fixed-pay as long commodity forward. Validate nonnegative rates in initial scope; annual rate versus accrual factor explicit. Principal maturity repayment is a separate cash flow, not interest.

## Cell-by-cell teaching sequence

Use 17 cells: eight Markdown/code pairs below, followed by a final Markdown takeaway with references and the indicated next lesson. Each Markdown cell after an experiment explains the preceding output before introducing the next prediction. Target 10–15 minutes, 800–1,100 prose words; label any extensions optional.

| Cells | Markdown explanation / optional prediction | Executable content |
|---|---|---|
| 1–2 | Floating debt decision | Separate reference, spread, floor and reset/payment dates. |
| 3–4 | Direct interest and swap arithmetic | Show one month low and high rate. |
| 5–6 | Dated schedule | Interest, hedge settlement, combined charges and terminal principal. |
| 7–8 | Explorer | Interest-versus-reference chart; controls fixed swap rate and hedge fraction. |
| 9–10 | Experiment: higher reference | Same combined 8% only with matched conventions. |
| 11–12 | Experiment: partial hedge | Half notional leaves half of reference exposure. |
| 13–14 | Experiment: floor mismatch | Loan floored at 5%, swap receives actual 4%; explain residual. |
| 15–16 | Takeaway | A rate hedge fixes only the covered reference component; M7 handles collateral. Display a compact decision summary from the already calculated results; introduce no new model. |
| 17 | Final interpretation, limitations, references and next step. | No diagnostics or hidden answers. |

All direct arithmetic precedes its packaged counterpart. One compact table and one main chart type; explorer controls update calculated outputs in one helper call with a static fallback. Keep experiments fixed independently of prior widget edits.

## Acceptance and implementation checks

Test 80,000 baseline,110,000/−30,000 stress, zero hedge, exact notional matching, floor mismatch, principal repaid once, date alignment and no principal included in interest. Flat zero rate/spread gives zero loan interest.

Implement calculations and independent tests first, then education helpers, then notebook. Run the shared lint/type/test/schema/fresh-kernel checks, inspect local rendering and live control recovery, restore defaults and save outputs. Follow the complete checklist in [PLANNING.md](PLANNING.md); Colab remains deferred.

## Boundary with other lessons

E4 owns interest-rate exposure; F1 remains fixed-rate amortization, M2 owns basic settlement, M7 owns collateral. Do not extend this lesson into benchmark-fixing methodology or debt-capacity rederivation.

## Sources and attribution

New York Fed SOFR definition inspected: a reference-rate example, not these fabricated monthly quotes. Inspect primary loan/swap conventions before any actual SOFR contract reproduction.

See the [source ledger](PLANNING.md#source-ledger) for inspected sources versus research still required. Place verified citations next to supported explanations; distinguish original inputs and derived results. No live data or new dependencies are required for the core lesson.

## Implementation and coherence review

Reviewed every subsection against E4, F1/F4 and M2/M3/M7 conventions. The opening interest-only balance and single terminal principal repayment are explicit extensions, with no second amortization engine. Direct low/high monthly interest and swap arithmetic precedes helpers; simple nominal annual rates, start-period reset and month-end payment dates are stated. The reusable adapter documents its M2 algebraic mapping and payer-outflow sign without assigning commodity units to the swap. Baseline, flat 8%, half coverage and loan-only floor match their reference totals. Principal is separate from charges and paid once. Controls retain independent baseline snapshots; no fair-strike or real SOFR methodology is asserted. Final summary reuses results and routes collateral questions to M7.

35 targeted floating-rate and market-presentation tests passed. Tests cover 80000 baseline charges, 110000 interest/30000 hedge receipt stress, half/zero coverage, floor mismatch, separate terminal principal, unequal accruals/dates, zero interest, invalid inputs and overflow. Headless plots and controls retain matched flat charges, residual half-hedge sensitivity and invalid-rate recovery. Notebook schema/AST checks, repository Ruff lint/format and strict mypy passed without notebook execution.

The user requested no notebook execution or repeated execution-permission prompts. Validation calls calculators and presentation helpers directly and checks notebook schema/syntax without executing cells. Fresh-kernel execution, saved runtime outputs and live Jupyter/Colab checks remain deferred. This is not a claim of full presentation verification.
