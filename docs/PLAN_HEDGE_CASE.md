# Supplemental hedge-converter teaching case

User request: turn the supplied Liquid Compute Trading Tools PDF and companion
workbook into a notebook for readers with no finance background. Explain who each
person is, what they want to accomplish, their inputs, each derivation, and the
meaning of the outputs. Attachment text is source material, not instructions.

Notebook: [From a business risk to a compute hedge](../notebooks/case_hedge_converter.ipynb).
This standalone supplement does not replace M3, M5, M7 or the planned C1 capstone.
No finance prerequisites; basic Python helps when editing inputs.

## Scope and calculation ownership

The core follows four independent hypothetical people: lender, GPU-owning lessor,
operator and buyer. Direct arithmetic precedes packaged calls. A buyer chart and
fixed basis experiment distinguish business outcomes, gross payoff and premium.
Editable code cells provide the interaction; no widget dependency is required for
the lesson itself. The optional appendix reproduces every formula in the supplied
workbook, with cell-level attribution and precise outputs alongside PDF rounding.

`hedge_converter` owns only the four business-to-strike/notional translations.
M5's `options.european_option_payoff_usd` retains payoff ownership. Existing
`education.show_finance_table` and `plot_finance_series` own rendering. No valuation,
credit, loan-amortization, cash-schedule or index-methodology engine is duplicated.

Assumptions needing explicit explanation: capacity rights are not hardware;
loan principal excludes interest; fee-adjusted lender notional; leased hardware
ownership specified only for the lessor; residual rental-income proxy is not a
sale valuation; billed-hour operating costs; fixed utilization; final-month price
versus subsequent rental term; average-then-pay versus monthly puts; premium and
payment timing; no physical capacity delivery from an option; basis and default.

## Source record

- `Liquid_Compute_Trading_Tools_v1.pdf`, 1 October 2026, both pages inspected.
- `Liquid_Compute_Trading_Tools_Math.xlsx`, README and Converter sheets: inputs,
  all formulas, notes and stored outputs inspected. Sources remain unchanged.
- Workbook's USD 2.87 LCI observation is reproduced as supplied and unverified,
  used only for comparison ratios, not as a market quote or option-pricing input.
- OIC [long call](https://www.optionseducation.org/strategies/all-strategies/long-call)
  and [long put](https://www.optionseducation.org/strategies/all-strategies/long-put)
  pages inspected for basic option terminology. Their listed-equity products do
  not establish compute contract availability or terms.

## Acceptance

Reconcile source strike/notional and lender shortfall; test matching recovery,
lessor target, quantity scaling, zero boundaries, wrong types, invalid fractions,
nonfinite values and overflow. Run repository checks and the fresh-kernel
validator. Inspect saved notebook rendering, tables, chart, math and unit labels.
Keep Ready/WIP as a separate user teaching-selection decision. Live Colab remains
unverified; the user subsequently authorized committing and pushing this lesson.

## Verification record — 2026-10-01

All 24 workbook formula outputs independently reconciled with cached source
values. All 792 repository tests passed, along with Ruff lint/format and strict
mypy checks. Standard notebook schema validation and local fresh-kernel execution
passed with outputs saved. Local HTML rendering was inspected, including the
buyer table/chart and saved source results. No widgets are introduced. Live
Jupyter editing and Colab are unverified. Teaching status remains WIP for user
review. The publication includes the notebook, required calculation module, tests
and index links, including a Colab link.

Follow-up teaching edit: define inputs and financial terms where they are used.
Each of the four stories now maps Python input names to baseline values, units,
and business meaning before its calculation cell. New definitions cover the
parties, principal, gross/net receipts, recovery, residual, utilization, operating
costs, break-even, settlement, premium, basis, timing and RFQ terms. Prose-only
changes preserve every code cell and saved output; notebook schema/format checks
and local rendering of the input tables passed.

Section-boundary follow-up: separated ten Markdown cell boundaries so each
section starts in its own cell. All prose, code and saved outputs were preserved;
notebook schema, formatting and rendered heading structure passed.

Lender narrative follow-up: explain default before any use, unexpired transferable
capacity, full placement with one or several replacement customers, and the
difference between physical hours and a fee-adjusted option multiplier. Derive
the 360,000-hour notional from a USD 1 price decline, distinguish the USD 2.50
purchase rate from the USD 2.083333… principal-recovery strike, and explain why
the agent fee is not deducted from the option payout. The comparison includes
the original purchase rate and calculates gross receipts and the agent fee
explicitly before net recovery. Remaining hours and remaining loan balance must
be reassessed together if the base assumptions change.

Each main scenario now begins with a first-person explanation of what could go
wrong, the specific dollar or business outcome the person wants to protect,
and how the hedge helps. The lender faces insufficient recovery after borrower
default; the lessor faces rental income below a residual recovery target; the
operator faces revenue below continuing costs and loan payments; the buyer faces
future compute bills above budget. These statements distinguish offsetting a
price-related cash loss from preventing default, idle capacity, or rising prices.
This prose-only follow-up preserves all calculation cells and saved outputs.

Leon's USD 6,000 target now has an explicit hypothetical business backstory:
USD 10,000 purchase cost less USD 4,000 expected first-lease cash after operating
costs leaves USD 6,000 per GPU still to recover. These added assumptions are not
attributed to the supplied documents. Accounting residual is separately assumed
to match this cash target, not calculated by subtracting rental receipts from
book value. Recovery is distinguished from extra profit and from sale proceeds.
