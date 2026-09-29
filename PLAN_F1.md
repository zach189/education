# F1: Financing a Compute Prepayment — implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Implemented and verified locally; implementation record. **Prerequisites:** 1 and 2.
**Notebook:** [Financing a Compute Prepayment](notebooks/F1_financing_a_compute_prepayment.ipynb).

Read the [canonical roadmap](notebooks/README.md), [shared planning conventions](PLANNING.md), and [project guidance](AGENTS.md). This document records F1’s approved scope and completed implementation.

## Learning decision, assumptions, and worked example

All numeric contract terms and scenarios below are hypothetical teaching assumptions, not market quotes.

**Completion:** The notebook and `financing` calculations are implemented with saved baseline results. Markdown math rendering has been repaired and inspected in local Jupyter. The explorer synchronizes table and chart output, handles invalid edits, and was verified live with defaults restored. Reuse these components in later lessons.

Use the approved reseller: 10 GPUs, 720 hours/month, 75% billed utilization, supplier USD 2 and customer USD 4/GPU-hour. Twelve service months yield USD 21,600 revenue and USD 14,400 base rent monthly. Supplier payments are month-start t=0…11; customers pay at t=2…13. Compare monthly purchasing, own-cash prepayment, and borrowed prepayment. Same-boundary cash is netted; no intraday gap modeled.

Defaults: 8% supplier discount, 80% financed, 12% nominal annual loan interest divided by 12, twelve monthly amortizing repayments starting t=1, fee 2% of principal paid separately at t=0, 12% effective annual comparison rate. Prepayment U=172,800(1−d)=158,976; loan P=fU=127,180.80; fee=2,543.616. Payment A=Pj/[1−(1+j)^−n]=11,299.8600; at j=0 use P/n.

Supplier saving is 13,824; interest plus fee is 10,961.14. Borrowed prepayment total cost is 169,937.14 and PV is 161,931.37, versus monthly 172,800 and PV 164,140.69. Net procurement outflows include supplier+interest+principal+fee−draw, not principal counted twice. Initial own cash is 34,338.82; whole-schedule buffer is 45,638.68. Own-cash prepayment needs 158,976; monthly purchasing needs 28,800. Threshold supplier discounts are 6.4501% undiscounted and 6.7448% PV. Retain signed thresholds.

## Reusable calculations and interfaces

Retain the existing `LoanCashFlow`, `FinancedCashFlow`, `FinancingSummary`, loan builder, combiner, summary, net procurement outflows, break-even helper, and three-alternative comparison in `financing`. Reuse existing discounting. Complete rather than replace the existing education helpers. Validate zero principal/rate, fractions, finite arithmetic and debt/cash reconciliation. Preserve the current approved 23-cell sequence instead of adopting the shorter default sequence used in later plans.

## Cell-by-cell teaching sequence

Retain the approved 23 cells for F1; the pairs below group the existing sequence.

| Cells | Markdown explanation / optional prediction | Executable content |
|---|---|---|
| 1–2 | Question and inputs (cells 1–2) | Use approved setup; explicitly exclude equipment ownership and customer-prepayment financing. |
| 3–4 | Timing and direct prepayment arithmetic (3–4) | Show January dates and U, P, fee, own cash before shared calls. |
| 5–8 | Amortization arithmetic then schedule (5–8) | Show first two payments by hand, then complete time-zero-through-maturity table. |
| 9–12 | Three comparisons and explorer (9–12) | Show total cost, PV, initial cash and buffer; save a baseline cumulative-cash chart, then show the live version with three controls. |
| 13–16 | Discount and interest experiments (13–16) | Compare 8% versus 4% discount and 12% versus 24% nominal loan rate; explain each result. |
| 17–18 | Financing fraction experiment (17–18) | Compare 0/80/100%; fee-free 100% still needs 14,124.83 at t=1. |
| 19–22 | Break-even and full cash schedule (19–22) | Direct K scaling before helper; reconcile both thresholds and all month-13 receipts. |
| 23 | Close (23) | State limitations, references, and switch explicitly to equipment-purchasing F2. |

All direct arithmetic precedes its packaged counterpart. One compact table and one main chart type; explorer controls update calculated outputs in one helper call with a static fallback. Keep experiments fixed independently of prior widget edits.

## Acceptance and implementation checks

Keep all approved 28 financing/education tests; run full suite and fresh kernel after fixes. Check math is actually typeset, live values change after edits, defaults are restored, and saved outputs agree with defaults. Confirm no double counting, fee timing, full repayment, trailing receipts, and longer maturities.

Implement calculations and independent tests first, then education helpers, then notebook. Run the shared lint/type/test/schema/fresh-kernel checks, inspect local rendering and live control recovery, restore defaults and save outputs. Follow the complete checklist in [PLANNING.md](PLANNING.md); Colab remains deferred.

## Boundary with other lessons

F1 owns simple amortizing prepayment debt. Notebook 2 owns timing/PV basics. Customer-prepayment bridges belong to F2; debt sizing to F4; distributions to F9. Retain the separate nominal loan versus effective PV rate convention.

## Sources and attribution

Use the shared source ledger: AWS payment choices; CFPB amortization and interest/fees. All financing terms are invented. No collateral or loan-availability claim.

See the [source ledger](PLANNING.md#source-ledger) for inspected sources versus research still required. Place verified citations next to supported explanations; distinguish original inputs and derived results. No live data or new dependencies are required for the core lesson.

## Completed validation

- Full suite: 245 tests passed, including 28 financing and financing-presentation tests.
- Ruff lint and formatting checks on `src`, `tests`, `scripts`, and `notebooks`; strict mypy passed.
- Notebook schema and fresh-kernel execution passed; baseline and experiment outputs saved.
- Local Jupyter verified typeset formulas, timing and results tables, the cumulative-cash plot, live control updates, invalid-edit recovery, and restored defaults. Widget-free fallback is covered by tests.
- Existing Python 3.10.11 environment reused without new dependencies. Colab remains explicitly unverified.
