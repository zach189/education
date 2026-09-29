# Notebook 2: Cash Flows Through Time

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

## Curriculum context

This is the implementation record for foundation Notebook 2; its settled calculations remain unchanged. The [canonical roadmap](notebooks/README.md) now organizes an independent Liquid Compute curriculum into a shared foundation, financing and market-risk tracks, electives, and an original transaction capstone. Financing can begin after Notebook 2; Notebook 3 prepares readers for Notebook 4 / M1, the tenor trade. See [PLAN_03.md](PLAN_03.md) for the third foundation lesson.

## Approved learning sequence

A 10–15 minute continuation of Notebook 1. Show core arithmetic before shared functions, save worked outputs, follow every experiment with explanatory Markdown, and keep diagnostic checks in tests. Payment arrangements are hypothetical contract assumptions, not industry conventions. Distinguish invoice dates from actual payment dates.

1. Start with matched month-end supplier payments and customer receipts. Show boundaries t=0,1,2 manually, then the full schedule and cumulative-cash chart.
2. Experiment 1: move supplier payment to month-start, then add one month of customer lag. Isolate how the funding gap arises while contribution stays constant.
3. Experiment 2: collect the full customer contract at t=0 before the first supplier debit. Keep revenue recognition over service months and show how customer cash can fund rent.
4. Introduce present value with a friend offering USD 100 now or in one year: compare a hypothetical 5% one-year bond, identify USD 5 of forgone return, and calculate USD 95.24 present value before returning to the operator’s 12% assumption. Explain discount-rate selection using alternative returns and cost of capital, with primary-source citations. Add a supporting plot of one unchanged bill at alternative payment dates, keeping the cumulative-cash chart as the main business chart. Calculate a month-1 payment's PV manually. Sum supplier payments at t=1,...,12 for the matched baseline.
5. Compare matched monthly supplier payments with supplier prepayment, both without a price reduction and with an 8% discount. Allocate prepaid expense evenly over service months.
6. Explorer: regular supplier timing, customer terms, customer lag, annual valuation rate, and supplier discount. Operating inputs and duration remain in editable cells. Customer upfront requires lag zero.
7. Experiment 3: raise only the valuation rate from 12% to 24%. Keep contractual schedules fixed.
8. Takeaways, limitations, linked references, and the transition: “We can now compare payment schedules. What can different contract lengths tell us about the implied price of future delivery periods?”

The notebook has 24 cells. Three experiment result cells each have an immediate “What this shows” explanation. Currency prose uses USD to avoid Markdown math ambiguity.

## Hypothetical inputs and reference results

10 GPUs × 720 hours/month, 75% billed utilization, USD 2 rental and USD 4 customer price per GPU-hour. Monthly revenue is USD 21,600; base rental expense USD 14,400. Service duration 12 months, starting cash zero, effective annual valuation rate 12%, supplier prepayment discount 8%.

Service month m runs from t=m-1 to t=m. Service amounts recorded at boundary m represent the completed month. Monthly supplier payments can occur at m-1 or m. Monthly customer receipts occur at m+lag. Supplier or customer upfront payments occur at t=0; customer upfront assumes cash clears before the supplier debit. All same-boundary flows are netted; the model does not estimate intraday funding. Include every boundary through T+lag and the opening zero balance.

| Arrangement | Contribution (USD) | Maximum funding (USD) |
|---|---:|---:|
| Matched month-end | 86,400 | 0 |
| Supplier month-start, customer month-end | 86,400 | 14,400 |
| Supplier month-start, customer lag 1 | 86,400 | 28,800 |
| Customer full upfront, supplier month-start | 86,400 | 0 |
| Supplier upfront without discount, customer month-end | 86,400 | 172,800 |
| Supplier upfront with 8% discount, customer month-end | 100,224 | 158,976 |

Total revenue is USD 259,200. Discounted rental expense is USD 158,976, allocated USD 13,248/month. Without a discount, total rent is USD 172,800. Timing alone preserves contribution and final cash; price concessions change both.

At 12%, a month-1 USD 14,400 payment has PV USD 14,264.65. Month-end monthly payments have PV USD 162,597.83, and equivalent prepayment discount 5.9040%. The 8% offer saves USD 3,621.83 in PV but requires USD 158,976 funding rather than zero. At 24%, monthly PV is USD 154,088.96 and the equivalent discount is 10.8281%; the 8% offer has the higher PV. Valuation rates do not change payments or funding.

## Equations and package interfaces

- Net cash N(t) = receipts(t) − payments(t); cumulative cash B(t) = sum of net flows through t.
- Funding = max(0, −min(0, B(0), ..., B(T+lag))).
- Discount factor DF(t) = (1+r)^(-t/12), with an effective annual rate; do not use r/12 as the effective monthly rate.
- Monthly supplier PV = sum(C × DF(t)) at the selected payment dates.
- Upfront U = TC(1-d); expense per service month = U/T; contribution = TR-U.
- Break-even prepayment discount = 1 − monthly supplier PV/(TC).

`liquid_compute.cashflows` holds immutable `MonthlyCashFlow` and `CashFlowSummary` dataclasses, `build_cash_flow_schedule`, `maximum_funding_requirement_usd`, and `summarize_cash_flow_schedule`. The schedule accepts supplier terms `monthly_in_advance`, `monthly_in_arrears`, or `upfront`; customer terms are `monthly_in_arrears` or `upfront`. Nonzero lag with customer upfront is rejected. Nonzero supplier discount with either monthly term is rejected.

`liquid_compute.discounting` provides `discount_factor`, `present_value_usd`, and `break_even_prepayment_discount_fraction`. The last accepts explicit `payment_timing` for start/end monthly payments. Existing public defaults retain advance timing for compatibility; Notebook 2 explicitly selects month-end timing. Dense PV sequence index zero means t=0; signed flows and empty sequences remain supported.

Calculation modules have no presentation dependencies. Fully annotated interfaces validate types, finite values, ranges, and overflow. Negative valuation rates remain outside the teaching scope. `liquid_compute.education` owns tables, step plots, and self-contained widget controls, preserving exact initialization and editable-cell fallback. No dependencies or environment changes are needed.

## Sources and scope

- [SEC: Beginners’ Guide to Financial Statements](https://www.sec.gov/about/reports-publications/investorpubsbegfinstmtguide): income and cash flow differ; the lesson's simplified contribution is not net income.
- [OpenStax: Applications of Time Value of Money](https://openstax.org/books/principles-finance-2e/pages/7-4-applications-of-tvm-in-finance): discount future amounts to a common date.
- [OpenStax: Timing of Cash Flows](https://openstax.org/books/principles-finance-2e/pages/9-1-timing-of-cash-flows): timelines and valuation of individual payments.

Payment terms, constant operations, equal expense allocation, rates and discounts are explicit example assumptions. Exclude interest, taxes, defaults, collateral, derivatives, ancillary costs, and returns on cash. Customer prepayment assumes agreement and collection; supplier PV comparisons exclude delivery and credit risk. No accounting-compliance or standard-market-terms claims.

## Acceptance and validation

- Verify matched/end/start/lagged/customer-upfront funding, service recognition, conservation of cash, and all trailing receipts, including lags longer than service duration.
- Verify zero rate, time-zero PV, signed and empty PV inputs, both regular payment timings, single-month cases, and equivalence at the calculated discount.
- Verify invalid types, bools, nonfinite values, invalid modes, contradictory terms, and overflow.
- Check exact control initialization, independent explorers, invalid-edit recovery, widget-free fallback, and selected timing in PV comparisons.
- Compare visible notebook arithmetic to independently calculated references; keep assertions in tests.
- Run Ruff, strict mypy, pytest, and fresh-kernel execution of both notebooks using the existing Python 3.10.11 environment. Preserve worked outputs and check local rendering. Colab verification remains deferred.

Validation completed locally: the 164-test suite passed after the timing changes; the added zero-display regression and affected calculation/presentation tests also passed. Ruff, formatting, and strict mypy passed. Both notebooks executed from fresh kernels, and Notebook 2 was re-executed after final display refinements with outputs saved. Local Jupyter controls were checked for month-start funding and customer prepayment, then restored to the matched baseline.
