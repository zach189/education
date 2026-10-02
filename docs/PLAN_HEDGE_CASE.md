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
