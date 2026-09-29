# Financing and market-risk language review

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

Revised 2026-09-28 for **F1–F9 and M1–M7**: 16 notebooks, 147 Markdown cells reviewed, with 106 cells edited in this tone revision. Foundations and advanced electives were outside this requested prose pass. Availability and prerequisites remain in the [canonical roadmap](notebooks/README.md).

The intended reader is an adult with no background in compute finance. The earlier simplification used child-oriented analogies too heavily; this revision replaces them with the actual business decision and uses a professional, accessible tone throughout. Definitions, explicit assumptions, worked amounts and interpretations remain. Clear explanations that already suited this audience were retained rather than rewritten solely for consistency of wording.

Each lesson introduces necessary terminology in context without assuming prior finance knowledge. Direct terms such as principal, receivable, break-even discount and replication are explained rather than replaced with toy, lemonade, playground or cash-jar analogies. The underlying Python and arithmetic remain appropriate to the existing basic-Python curriculum.

## Lesson-by-lesson review

| Lesson | Plain-language approach and meaning preserved |
|---|---|
| F1 | Supplier prepayment discounts and borrowing costs; principal and interest are defined separately; total cost, present value and cash buffer remain separate. Loan proceeds and principal are not counted as extra supplier cost. |
| F2 | A short loan covers the wait for customer money. Proof, payment due and cash arrival remain separate; unmet conditions and late payments differ. A refund does not guarantee full repayment. |
| F3 | Customer payment and cancellation terms introduce offtake agreements. Acceptance, cancellation, credits and collection delays have distinct effects; reseller supplier bills survive cancellation. |
| F4 | Operating cash and a stated coverage requirement determine affordable repayments. Equal and shaped payments retain interest coverage, zero ending debt and the no-payment-holiday rule. |
| F5 | Equipment order, delivery and acceptance payments introduce staged borrowing. Setup cash, later repayment capacity and F2's customer-prepayment bridge remain separate. |
| F6 | Money owed by customers introduces receivables. Eligibility, customer caps, advance percentage, reserve deduction, facility limit and existing debt remain separate steps. |
| F7 | Supplier and loan commitments that outlast customer contracts explain renewal exposure. Earlier savings remain available, and the full supplier/loan tail stays visible. |
| F8 | Equipment purchase and lease agreements establish different ownership and sale rights. Sale cash, book depreciation, present value and loan payoff remain distinct; negative owner exit cash is retained. |
| F9 | Contractual payment priorities explain cash allocation. Interest, principal, reserve savings, sweeps, arrears and owner payouts retain their ordering and meaning. MOIC is explained as total money returned per dollar invested, not an annual return. |
| M1 | Long supplier commitments and shorter customer contracts explain tenor. Actual supplier bills remain distinct from Notebook 3's implied blocks; renewal is an assumption. |
| M2 | Physical fixed-price procurement and financial settlements explain forwards. Physical delivery and cash settlement remain separate; signed payments, seller direction and dated swap payments are retained. |
| M3 | The difference between the supplier invoice price and hedge reference price explains basis. Actual price, reference period, payment date and covered quantity stay separate; excess hedges retain their downside. |
| M4 | Committed compute capacity with uncertain customer demand explains unused hours. The reseller and separate overhedged buyer remain distinct. Delayed cash is kept through its final receipt. |
| M5 | Protection against adverse price changes introduces calls, puts and premiums. Payoff versus total business cost, upfront premium, full versus partial coverage and basis exposure remain explicit. |
| M6 | An asset-and-borrowing portfolio that matches option payoffs explains replication. Half-unit ownership and borrowed cash are worked through in both outcomes. Pricing weights differ from beliefs; model assumptions do not establish compute tradability. |
| M7 | Interim hedge payments before customer collection explain liquidity. Returned margin, actual variation settlements and separate private-forward collateral remain distinct; later collection does not falsely increase the example's peak funding need. |

M1 was subsequently revised against a new user-supplied teaching specification; see [PLAN_04.md](PLAN_04.md). The preservation checks below describe the earlier prose-only pass, not that later calculation and notebook revision.

## Verification

- Compared every notebook with its pre-edit JSON snapshot: **106 of 147 Markdown source cells changed in this revision**; cell count, ordering, cell metadata, notebook metadata and every non-Markdown cell were unchanged. This includes code, execution counts and saved outputs.
- Validated all 16 notebooks with `nbformat` without executing cells.
- Compared Markdown link targets with the snapshot: every original source and navigation link was retained.
- Reviewed all Markdown, including retained passages, for tone and continuity. Checked revised interpretations for amounts, units, dates, signs, business roles, experiment changes and cross-lesson boundaries. Numeric-token differences were limited to punctuation and numbers in removed child-oriented analogies; financial example amounts were preserved.
- **35 existing static tests passed**, covering financing/market/elective formats, teaching structure, code syntax, package import/call signatures, lesson inventory and documentation links. The selected tests inspect notebook source; they do not run cells.
- No notebook, kernel, browser, or notebook-cell execution was used. Calculations and presentation helpers were unchanged, so this prose-only pass did not repeat their previous execution tests or claim new live-rendering acceptance.

The previous implementation review remains a historical record of its own checks. This rewrite does not change any lesson's execution or live-presentation status.
