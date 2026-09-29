# C1: Structure and Stress-test a Compute Transaction — implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Planned; not implemented. **Prerequisites:** 1–3, F1–F9 and M1–M7; electives only if used.
**Target notebook:** `notebooks/C1_structure_a_compute_transaction.ipynb` (a proposed path, not an available-notebook link).

Read the [canonical roadmap](notebooks/README.md), [shared planning conventions](PLANNING.md), and [project guidance](AGENTS.md). Foundation plans remain implementation records; this document specifies only the new lesson or unfinished work.

## Learning decision, assumptions, and worked example

All numeric contract terms and scenarios below are hypothetical teaching assumptions, not market quotes.

Capstone question: which structure serves the buyer while remaining fundable for the operator and repayable for the financier? Use an original GPU-owning project, explicitly separate from the foundation reseller. Ten GPUs; equipment cost 300,000, deposit 60,000 at t=0, delivery 180,000 at t=2, acceptance 60,000 at t=3. Customer service begins month 4 for 24 months. Capacity 7,200 hours/month, billed 75%, customer rate 4; monthly receipts 21,600 at month-end, cash operating cost 8,000. Site cost 2,000 monthly t=1…3. Rates/rights are hypothetical.

Compare three whole structures on identical service: A all-equity purchase/customer monthly; B 70% equipment term debt drawn in proportion to milestone payments at 10% nominal annual,24 monthly amortization after acceptance/customer monthly; C same 70% long-term debt plus a short 60,000 deposit bridge and customer prepayment 64,800 due when accepted order documented at t=1. In C, customer prepayment buys the first three service months, so remove those later receipts; remaining customer service unchanged. Term loan's 42,000 deposit reimbursement at t=1 and prepayment cash repay bridge (12% nominal ACT/365, assume 30 days,1% fee); excess cash is retained for milestones, not a second revenue receipt. A/B first term draw, when applicable, is at t=0; C explicitly delays deposit reimbursement to t=1. Make the financing distinction visible in the initial contract table.

Compare borrower liquidity, total borrowing cost, debt cover, buyer payment PV (12% effective), financier dated draws/receipts and unpaid exposure. Equipment resale 30,000 at service-end month 27 only because this project owns it; stress 0/60,000 and never also release the same value as collateral cash. Cash waterfall has reserve target one scheduled debt payment,50% sweep on residual cash after required reserve; F9 recomputes debt after sweeps. For structure comparisons show before-waterfall business cash and after-waterfall distributions separately.

Core deterministic stress set: acceptance+2 months (extend service horizon), customer payment+2 months, cancellation after 12 service months without relief from existing debt, and 30% lower renewal price only in a separately labeled post-contract extension. Optional appendix adds an M2 financial price hedge with explicit benchmark/quantity and M7 collateral; derivatives are not mandatory to understand base funding structures. No compound-option requirement or Monte Carlo.

## Reusable calculations and interfaces

Compose existing modules, adding only `transactions` frozen scenario/structure/result records and `compare_transaction_structures`. Adapters map day-based bridge events explicitly to month boundary 1 using 30/365 for interest, not pretending monthly PV accepts days. Keep source amounts traceable to one ledger; customer prepayment is revenue timing, not new service revenue, and bridge/term draws are financing. Results include buyer/operator/financier cash ledgers plus conservation reconciliation. Do not build a universal deal DSL or repeat existing calculators. Real transaction data requires separately supplied assumptions/access.

## Cell-by-cell teaching sequence

Use 17 cells: eight Markdown/code pairs below, followed by a final Markdown takeaway with references and the indicated next lesson. Each Markdown cell after an experiment explains the preceding output before introducing the next prediction. Target 10–15 minutes, 800–1,100 prose words; label any extensions optional.

| Cells | Markdown explanation / optional prediction | Executable content |
|---|---|---|
| 1–2 | Original deal and roles | State assets, delivery rights, payment conditions and who owes whom. |
| 3–4 | Three structure term sheets | Hold equipment/service fixed; show changed customer/financier payments. |
| 5–6 | One visible event calculation | 60,000 bridge fee 600 plus 30-day interest 591.78 and intended repayment sources. |
| 7–8 | Baseline comparison/explorer | Structure and stress dropdowns; cash timeline and compact three-party scorecard. |
| 9–10 | Experiment: deployment delay | Shift milestones and delivery receipts consistently; separate bridge conditions. |
| 11–12 | Experiment: customer late or cancelled | Late cash versus removed future obligations; report lender shortfall, not invented recovery. |
| 13–14 | Experiment: terminal recovery | Change actual resale only; trace debt payoff/reserve release/equity cash once. |
| 15–16 | Decision memo and limitations | State tradeoffs, no universal winner; optional hedge appendix, real deal requires actual documents. Display a compact decision summary from the already calculated results; introduce no new model. |
| 17 | Final interpretation, limitations, references and next step. | No diagnostics or hidden answers. |

All direct arithmetic precedes its packaged counterpart. One compact table and one main chart type; explorer controls update calculated outputs in one helper call with a static fallback. Keep experiments fixed independently of prior widget edits.

## Acceptance and implementation checks

Every event must balance across parties plus explicitly external supplier/OPEX cash; loan draws/repaid principal reconcile; prepayment replaces exactly three monthly receipts; initial bridge/term refinancing not double debt; extended delayed horizon; no distributions before debt/reserve rules; no fictitious collateral or contractual credit support. Compare no-financing case to direct procurement arithmetic and individual module outputs. Stress model must show unpaid amounts rather than silently borrowing.

Implement calculations and independent tests first, then education helpers, then notebook. Run the shared lint/type/test/schema/fresh-kernel checks, inspect local rendering and live control recovery, restore defaults and save outputs. Follow the complete checklist in [PLANNING.md](PLANNING.md); Colab remains deferred.

## Boundary with other lessons

C1 integrates previous lessons; it introduces no new payoff, debt-sizing, margin or waterfall method. Core aims 15 minutes via prepared structure cards and one selected stress; full contract/ledger inspection and hedge extension optional. Foundation 3/market track supply interpretation, not fictional executable prices. Do not re-create the source article fleet simulation.

## Sources and attribution

Reuse already verified lesson sources, citing original passages for any reused factual claims. All deal terms are original hypothetical assumptions. No real Liquid Compute deal, actual facility availability or observed resale value is asserted.

See the [source ledger](PLANNING.md#source-ledger) for inspected sources versus research still required. Place verified citations next to supported explanations; distinguish original inputs and derived results. No live data or new dependencies are required for the core lesson.
