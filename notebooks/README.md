# Liquid Compute curriculum roadmap

This is the canonical roadmap for an independent **compute-finance curriculum and reusable calculator library**. Its organizing question is:

> What decision does Liquid Compute need to help a buyer, operator, or financier make?

The shared foundation leads into named tracks: **Financing a deal (F)**, **Managing market risk (M)**, **Electives (E)**, and an original **Capstone (C1)**. Financing is the development priority. It can begin after Notebook 2; Notebook 3 is the prerequisite for the market-risk track, not a barrier to studying financing. Track IDs are curriculum identifiers, not promises of existing notebook files.

All 26 existing notebooks passed fresh-kernel execution locally on 2026-09-29, with outputs saved. Each includes a Colab setup cell to install the package from GitHub. Live Colab interaction remains unverified. The capstone is still planned. See the [Colab notebook index](../README.md), [implementation plans](../PLANNING.md), and [historical conversation](../chat.md).

## Ready and WIP

**Ready:** notebooks 1–4 (Notebook 4 is M1), M5 calls and puts, M6 option valuation, and E1 compound options. **WIP:** F1–F9, M2–M4, M7, E2–E6, and the [lab financing case](case_lab_gpu_financing.ipynb). C1 remains planned. These release labels reflect the user's selected teaching readiness, independently of successful execution. All existing lessons have saved results; pending live presentation checks are not claimed as complete.

## Audience and teaching conventions

F1–F9 and M1–M7 have completed a [language review](../PLAIN_LANGUAGE_REVIEW.md) for adult readers new to compute finance: direct business examples, clear definitions and explanations after each worked result. The tone is professional and accessible, without child-oriented analogies. That prose-only pass preserved code and saved outputs; later lesson revisions and execution/live-presentation status are tracked individually below.

Readers know basic Python but are new to compute financing and derivatives. Aim for 10–15 minutes per lesson, one business decision, visible arithmetic before packaged calculations, editable inputs, a compact results table, and a main chart. Start with a few understandable scenarios before simulations. Predictions are optional; worked answers remain visible. Follow experiments with Markdown explaining the results, and end with a question or route to the next relevant lesson.

Save outputs for reading like a book. Keep explanations and arithmetic in notebooks, stable calculations in `liquid_compute`, and repeated rendering and widget mechanics in `liquid_compute.education`. Controls are optional; editable cells provide a fallback. Tests and diagnostic assertions belong outside the lessons.

Distinguish contractual obligations, cash settlement, accounting/service amounts, model-dependent valuations, and hypothetical scenarios. Use explicit units and primary-source citations. A chosen valuation rate is not an automatic borrowing charge, and a financial hedge does not guarantee physical capacity.

## Two business models

- **Capacity reseller:** rents GPU capacity and sells compute. It does not thereby own GPUs, hardware collateral, or hardware resale proceeds. Use this model for the existing foundation and contract-financing examples.
- **GPU-owning operator/project:** purchases or leases equipment and contracts for customer demand. Introduce this model explicitly in the OEM bridge, deployment, and equipment-financing lessons. At the deposit stage, identify the actual deposit, refund, and contractual rights; do not assume equipment has been delivered or is already available as collateral. Lease rights and ownership also remain distinct.

Start the foundation with the existing hypothetical 10 GPUs, 720 hours per month, USD 2 rental and USD 4 customer price per GPU-hour, and 75% billed utilization. Later lessons may introduce independent, clearly labeled scenarios. Never quietly transfer ownership, security rights, or commercial terms between businesses.

## Shared foundation

| ID and lesson | Decision and main experiment | Reusable calculation | Prerequisites | Status |
|---|---|---|---|---|
| **1. [Compute economics](01_compute_business.ipynb)** | Can the capacity reseller earn a contribution? Change utilization, capacity, and the price spread. | Purchased/billed GPU-hours, contribution, margin, break-even utilization. | Basic Python. | Implemented locally. |
| **2. [Cash-flow timing and present value](02_cash_flows_through_time.ipynb)** | When does cash become available, and what does paying early change? Compare matched payments, funding gaps, customer prepayment, and supplier prepayment. | Dated cash flows, maximum funding, discount factors, PV, break-even supplier discount. | 1. | Implemented locally. |
| **3. [Rental quotes and implied curves](03_rental_quotes_to_implied_forward_curve.ipynb)** | What future block averages reconcile different-length contracts? Unbundle, reconstruct, change quotes, and add discounting. | Implied blocks with explicit boundaries and weighted reconstruction. | 2. | Implemented locally; see [implementation plan](../PLAN_03.md). |

Notebook 3 distinguishes whole-contract quotes, implied future blocks, and assumed monthly allocations before the math. Its independent main menu is USD **6.00 / 5.00 / 4.40 per GPU-hour** for **12 / 36 / 60 months**, giving undiscounted blocks **6.00 / 4.50 / 3.50**. Attribute Ornn's method; retain Eugene Ye's menu and continuous-rate example only in an optional cited appendix. Its transition leads to **Notebook 4 / M1: The Tenor Trade: Buying Long, Selling Short**, while **F1** is already accessible after Notebook 2. Discounting and the source reproduction are optional extensions; the core uses one menu, one overlap diagram, and one interactive block chart.

## Financing a deal — priority track

These lessons replace the former three financing extensions. Read in the listed order for the complete track; the prerequisite column also supports focused entry.

| ID and lesson | Decision and main experiment | Prospective reusable calculation | Prerequisites | Status |
|---|---|---|---|---|
| **F1. Financing a compute prepayment** | Does a supplier discount cover financing costs? Compare monthly purchasing, own-cash prepayment and a fixed amortizing loan; vary discount, interest and financed fraction. | Funding-source cash schedules, all-in financing cost, required equity. | 2. | Implemented locally. [Notebook](F1_financing_a_compute_prepayment.ipynb) · [Record](../PLAN_F1.md). |
| **F2. Bridging an OEM deposit to customer prepayment** | How do we fund the order-triggered gap? Delay the customer payment, leave conditions unmet, or change deposit refunds. | Event-dated bridge draws, interest/fees, repayment, and remaining equity need. | F1; introduce the equipment-purchasing project. | Created; calculation/plot tests and coherence review complete. Fresh-kernel execution passed; outputs saved. Live presentation review pending. [Notebook](F2_oem_deposit_bridge.ipynb) · [Record](../PLAN_F2.md). |
| **F3. What makes an offtake financeable?** | Why can equal headline revenues support different financing? Vary minimum commitments, cancellation rights, payment conditions, reliability, and service credits. | Scenario-dependent receipts and cash available for debt service under explicit contract terms. | 2 and F1. | Created; calculation/plot tests and coherence review complete. Fresh-kernel execution passed; outputs saved. Live presentation review pending. [Notebook](F3_offtake_financeability.ipynb) · [Record](../PLAN_F3.md). |
| **F4. How much debt can the deal support?** | What debt can dependable cash flows repay? Compare level payments with payments shaped around available cash. | Debt-service coverage, repayment schedules, debt capacity under stated constraints. | F1 and F3. | Created; calculation/plot tests and coherence review complete. Fresh-kernel execution passed; outputs saved. Live presentation review pending. [Notebook](F4_debt_capacity.ipynb) · [Record](../PLAN_F4.md). |
| **F5. Deployment delays and staged funding** | What if equipment arrives or is accepted late? Compare drawing all debt immediately with staged draws. | Deployment-event cash schedules, accrued interest, incremental equity and liquidity needs. | F2 and F4. | Created; calculation/plot tests and coherence review complete. Fresh-kernel execution passed; outputs saved. Live presentation review pending. [Notebook](F5_deployment_and_staged_funding.ipynb) · [Record](../PLAN_F5.md). |
| **F6. Receivables and collateral** | How much financing is available today? Stress overdue invoices, concentrations, advance rates, and reserves. | Eligible borrowing base and available credit; distinguish capacity from cash drawn. | F3 and F4. | Created; calculation/plot tests and coherence review complete. Fresh-kernel execution passed; outputs saved. Live presentation review pending. [Notebook](F6_receivables_and_collateral.ipynb) · [Record](../PLAN_F6.md). |
| **F7. Renewal risk and maturity mismatch** | What happens when obligations outlast customer commitments? Change renewal prices, replacement demand, and downtime. | Contracted versus renewal-dependent cash flows, debt coverage, and funding shortfalls. | F3 and F4. | Created; calculation/plot tests and coherence review complete. Fresh-kernel execution passed; outputs saved. Live presentation review pending. [Notebook](F7_renewal_and_maturity_mismatch.ipynb) · [Record](../PLAN_F7.md). |
| **F8. GPU ownership, leasing, and residual value** | How dependent is a purchase or lease on hardware's later value? Stress resale proceeds against debt outstanding. | Purchase/lease cash-flow comparison, residual-value sensitivity, debt shortfall at exit. | 2 and F4; explicitly use the equipment project. | Created; calculation/plot tests and coherence review complete. Fresh-kernel execution passed; outputs saved. Live presentation review pending. [Notebook](F8_ownership_leasing_residual_value.ipynb) · [Record](../PLAN_F8.md). |
| **F9. Waterfalls, reserves, and investor returns** | Who gets paid first and who absorbs losses? Introduce reserves, cash sweeps, and distribution restrictions. | Ordered cash allocation, debt/equity distributions, reserve balances, investor returns. | F4 and F7; F6/F8 when collateral or equipment exit is included. | Created; calculation/plot tests and coherence review complete. Fresh-kernel execution passed; outputs saved. Live presentation review pending. [Notebook](F9_waterfalls_reserves_returns.ipynb) · [Record](../PLAN_F9.md). |

### Verification scope for F2–F9

At the user's request, this implementation pass does **not** run notebook kernels or live Jupyter checks. Calculations, chart data/labels, widget independence/recovery and fallback behavior are tested directly; notebook schema, syntax and teaching structure are checked without executing cells. F2 has saved outputs from its initial execution before this request, but later edits are not execution-verified. F3–F9 intentionally have no saved runtime outputs yet. Worked interpretations remain in Markdown. These lessons are created and tested, not fully presentation-verified. See each implementation record and [PLANNING.md](../PLANNING.md).

### F2: the OEM deposit bridge

Use this explicit event sequence:

**Signed offtake → OEM deposit required → accepted order documented → customer prepayment becomes due → cash received → bridge repaid.**

An OEM is the equipment manufacturer. The project needs cash to place an order, but its customer pays only after the accepted order is documented. The intended bridge repayment source is that customer prepayment, not years of operating revenue. Model the deposit amount/date, payment conditions, expected receipt date, existing cash, interest, fees, and any remaining shortfall.

A payment that is already owed but arrives late differs from one that never becomes due because a condition remains unmet. A signed offtake alone is not an unconditional receivable. Treat refund rights, recoveries, and cancellation outcomes as explicit scenario terms, not automatic repayment guarantees.

**F2 funds the order-triggered gap. F5 funds the longer period through delivery, acceptance, and operating revenue.** Do not collapse them into one generic funding example.

## Managing market risk

| ID and lesson | Decision and main experiment | Prospective reusable calculation | Prerequisites | Status |
|---|---|---|---|---|
| **M1. The Tenor Trade: Buying Long, Selling Short (Notebook 4)** | What does the tenor price gap compensate us for? See the published B300 tenor-price snapshot, then stress 36 monthly resale decisions, fill, prepayment and a partial hedge. | Monthly placement economics, recurring fill hurdle, prepayment cash allocation and existing seller settlement. | 3. | Revised/tested; fresh-kernel execution passed and outputs saved; static figures inspected. Live UI/Colab unverified. [Notebook](04_the_tenor_trade.ipynb) · [Record](../PLAN_04.md). |
| **M2. Forwards and swaps** | How can buyers and sellers lock a price? Compare fixed/floating business cash flows and a financial settlement across price scenarios. | Forward/swap settlement and combined buyer cost or seller receipts. | M1. | Created/tested; coherence reviewed. Fresh-kernel execution passed; outputs saved. Live presentation review pending. [Notebook](M2_forwards_and_swaps.ipynb) · [Record](../PLAN_M2.md). |
| **M3. Basis Risk: When the Index Isn’t Your Price** | What remains when the supplier price differs from the index? Hold quantities/dates equal; stress regional basis around a budget and compare synthetic benchmarks. | Matched-quantity cost, budget deviation and aligned benchmark residuals. | M2. | Created/tested; fresh-kernel execution passed, outputs saved. Live widget updates unverified (local connection issue); Live Colab unverified. [Notebook](M3_benchmark_basis_risk.ipynb) · [Record](../PLAN_M3.md). |
| **M4. Price and quantity uncertainty** | What if price, demand, or delivery differs from expectations? Model cancellation, unused capacity, renewal gaps, and delays in a few scenarios first. | Scenario cash flows and weighted business outcomes under explicit assumptions. | M3. | Created/tested; coherence reviewed. Fresh-kernel execution passed; outputs saved. Live presentation review pending. [Notebook](M4_price_quantity_scenarios.ipynb) · [Record](../PLAN_M4.md). |
| **M5. Calls and puts** | How can a buyer cap cost or a supplier protect revenue? Change strikes, premiums, and coverage. | Call/put payoffs and combined physical-plus-financial outcomes. | M4. | Created/tested; coherence reviewed. Fresh-kernel execution passed; outputs saved. Live presentation review pending. [Notebook](M5_calls_and_puts.ipynb) · [Record](../PLAN_M5.md). |
| **M6. Option valuation** | What assumptions produce a model price? Work through replication before changing volatility or strike. | Small-tree valuation with explicit trading assumptions and pricing weights. | M5 and 2. | Created/tested; coherence reviewed. Fresh-kernel execution passed; outputs saved. Live presentation review pending. [Notebook](M6_option_valuation.ipynb) · [Record](../PLAN_M6.md). |
| **M7. Hedge collateral and liquidity** | Can protection create an early cash crunch? Move collateral payments ahead of offsetting business receipts. | Collateral and settlement cash schedules with liquidity requirements. | M2, M3, and 2; M5 for option examples. | Created/tested; coherence reviewed. Fresh-kernel execution passed; outputs saved. Live presentation review pending. [Notebook](M7_hedge_collateral_liquidity.ipynb) · [Record](../PLAN_M7.md). |

Teach futures margin first in M7, then specify any hypothetical OTC collateral arrangement separately. Do not imply that all forwards or swaps share exchange margin rules. Across the track, separate physical delivery from cash settlement, business-outcome probabilities from pricing weights, and model values from executable quotes.

## Advanced electives

| ID and lesson | Decision and main experiment | Prospective reusable calculation | Prerequisites | Status |
|---|---|---|---|---|
| **E1. Compound options and staged protection purchases** | When is paying for a later protection decision useful? Compare immediate purchase, staged purchase, and cancellation. | Staged option payoffs, exercise payments, and valuation under explicit assumptions. | M6 and 2. | Created/tested; optional. Fresh-kernel execution passed; outputs saved. Live presentation review pending. [Notebook](E1_compound_options.ipynb) · [Record](../PLAN_E1.md). |
| **E2. Minimum revenue with shared upside** | How should buyer and supplier share price risk? Compare fixed, floating, and minimum-plus-participation terms. | Contract payout and upside-participation schedules. | M5. | Created/tested; optional. Fresh-kernel execution passed; outputs saved. Live presentation review pending. [Notebook](E2_minimum_revenue_shared_upside.ipynb) · [Record](../PLAN_E2.md). |
| **E3. Power costs and compute margins** | Can stable rental prices coexist with shrinking margins? Change electricity costs and power consumption. | Power cost per GPU-hour and contribution sensitivity; identify who bears the power bill. | 1 and 2. | Created/tested; optional. Fresh-kernel execution passed; outputs saved. Live presentation review pending. [Notebook](E3_power_costs_compute_margins.ipynb) · [Record](../PLAN_E3.md). |
| **E4. Floating-rate financing and interest-rate hedging** | How does a rate change affect debt cost? Compare an unhedged loan with a specified fixed-rate hedge. | Floating debt charges, hedge settlements, and combined financing cash flows. | F4 and M2. | Created/tested; optional. Fresh-kernel execution passed; outputs saved. Live presentation review pending. [Notebook](E4_floating_rate_financing.ipynb) · [Record](../PLAN_E4.md). |
| **E5. Historical risk measurement** | How sensitive is measured risk to the data window? Vary observations, lookbacks, and missing-data assumptions. | Return/volatility estimates with explicit sampling conventions. | M3 and M4. | Created/tested; optional. Fresh-kernel execution passed; outputs saved. Live presentation review pending. [Notebook](E5_historical_risk_measurement.ipynb) · [Record](../PLAN_E5.md). |
| **E6. Cost per useful output** | Can the unit cost fall while the total bill rises? Change workload intensity, volume, and mix separately. | Unit-cost and total-spend decomposition. | 1. | Created/tested; optional. Fresh-kernel execution passed; outputs saved. Live presentation review pending. [Notebook](E6_cost_per_useful_output.ipynb) · [Record](../PLAN_E6.md). |

Later data exercises may use sourced datasets, but live APIs and credentials are not prerequisites for the foundation. Keep market rented-capacity utilization, technical GPU utilization, and a customer's billed usage distinct. Wholesale power prices are not a complete delivered electricity bill.

## C1: Structure and stress-test a compute transaction — planned

[Implementation plan](../PLAN_C1.md).

**Decision:** Which transaction structure meets the buyer's needs while remaining fundable for the operator and acceptable to the financier?

**Experiment:** Compare a small set of original structures on the same hypothetical transaction and stress customer delays/cancellation, deployment, renewal, price, and residual value where relevant. Show buyer obligations, operator contribution and liquidity, and financier repayment and losses. Specify asset ownership and rights before introducing collateral or exit proceeds.

**Prospective reusable calculation:** Compose the lesson calculators into a transaction comparison and stress report, with traceable inputs and no new universal deal framework.

**Prerequisites:** Foundations 1–3, F1–F9, and M1–M7; electives only when the chosen structure uses them. Begin with hand-built scenarios; simulation is optional later. This replaces the earlier article-shaped five-year purchasing simulation. It is not an extension of the article's customer story or compound-option example.

Start with an original hypothetical deal. A real Liquid Compute transaction requires separately supplied assumptions and appropriate data access; no actual transaction or terms are presumed here.

## Sources and development boundaries

External sources support concepts and methods; they do not supply the curriculum's organizing story. Attribute [Ornn's package-unbundling methodology](https://data.ornn.com/docs/forward-curves) and [Eugene Ye's example](https://wafer.substack.com/p/lets-talk-about-trading-compute) where used. Do not present implied blocks as executable quotes or pure forecasts, and do not claim discounting removes commercial concessions embedded in package quotes.

The imported direction discussion mentions CoreWeave disclosures, OCC lending guidance, World Bank project-finance material, CME education, Ornn data, and shipping profit-sharing examples. Treat these as **research leads**, not verified current facility terms or ready-to-use model assumptions. Inspect primary documents when developing each lesson, cite claims nearby, and distinguish sourced practice from hypothetical adaptations.

For all track plans, calculation ownership, source research gates and the coherence review, see [PLANNING.md](../PLANNING.md).

See the [project README](../README.md) for setup and checks, [AGENTS.md](../AGENTS.md) for engineering conventions, and the individual foundation plans: [1](../PLAN.md), [2](../PLAN_02.md), and [3](../PLAN_03.md). Extend the typed package only as a lesson needs a stable calculation. Reuse the existing Python 3.10 environment. Colab setup and verification remain deferred until the series is complete.

## Supplemental deal case study

[Can a training lab support a USD 500 million GPU loan?](case_lab_gpu_financing.ipynb)
explores an anonymized, unverified user-supplied deal prompt with explicit hypothetical
operating and financing assumptions. Includes a funding diagram, five plots,
training-allocation control, repayment comparison, downside cases and decision table.
Read alongside F1, F4 and F8. This is separate from the numbered curriculum; C1
remains planned. Source/calculator and headless checks are complete; notebook
execution, saved plot outputs and live presentation checks are deferred.
See the [case specification](../PLAN_LAB_CASE.md).
