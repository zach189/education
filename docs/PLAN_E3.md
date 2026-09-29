# E3: Power Costs and Compute Margins — implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](../notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Created/tested; optional elective. Coherence reviewed; execution/live acceptance deferred by user instruction. **Prerequisites:** 1 and 2.
**Notebook:** [notebooks/E3_power_costs_compute_margins.ipynb](../notebooks/E3_power_costs_compute_margins.ipynb).

Read the [canonical roadmap](../notebooks/README.md), [shared planning conventions](PLANNING.md), and [project guidance](../AGENTS.md). Foundation plans remain implementation records; this document specifies only the new lesson or unfinished work.

## Learning decision, assumptions, and worked example

All numeric contract terms and scenarios below are hypothetical teaching assumptions, not market quotes.

Optional question: who bears power costs, and when does an attractive compute price fail to cover them? Explicitly switch to an operator that pays its own electricity bill. Do not add power to the reseller's all-in rental cost without changing contract assumptions. Use 10 GPUs,720 hours/month, IT draw 0.7 kW per GPU, illustrative facility multiplier 1.2, delivered electricity 0.10 USD/kWh and fixed monthly power-service charge 200 USD. These are invented equipment/contract inputs, not hardware specifications.

IT energy=10·.7·720=5,040 kWh; facility energy=6,048 kWh; total energy bill=804.80. Revenue remains 21,600 with a separately specified 14,400 non-power operating cost; contribution after electricity=6,395.20. A synthetic wholesale energy component 0.06 USD/kWh yields 362.88, but it is not the delivered bill. Do not present that comparison as an actual tariff quote.

For technical load, interpolate IT draw from idle 0.2 kW to active 0.7 kW using a **technical active fraction**; do not equate this with 75% billed utilization. Facility multiplier fixed in core; optional discussion of its limits. Demand charges and nonlinear tariffs excluded, clearly stated.

## Reusable calculations and interfaces

Add `power` with `electricity_cost_usd(gpu_count, hours, it_kw_per_gpu, facility_multiplier, delivered_usd_per_kwh, fixed_charge_usd)` returning IT/facility kWh, energy cost and total bill. `average_it_kw_per_gpu` interpolates idle/active draw from technical fraction. Reuse economic revenue without importing rental cost that already includes electricity. Validate positive count/hours, nonnegative power/tariff, multiplier≥1 and active≥idle. Keep fractional units explicit; do not add a tariff database or live price fetch.

## Cell-by-cell teaching sequence

Use 17 cells: eight Markdown/code pairs below, followed by a final Markdown takeaway with references and the indicated next lesson. Each Markdown cell after an experiment explains the preceding output before introducing the next prediction. Target 10–15 minutes, 800–1,100 prose words; label any extensions optional.

| Cells | Markdown explanation / optional prediction | Executable content |
|---|---|---|
| 1–2 | Cost responsibility | Define the operator and electricity terms before adding a cost line. |
| 3–4 | Direct units arithmetic | kW×hours=kWh; facility multiplier and delivered price. |
| 5–6 | Contribution table | Revenue, non-power expense, energy, fixed charge and contribution. |
| 7–8 | Explorer | Contribution versus delivered tariff; controls power and tariff. |
| 9–10 | Experiment: electricity price | 0.10→0.20; energy-dependent cost doubles, fixed charge does not. |
| 11–12 | Experiment: technical load | Idle/active mix changes draw independently of billed usage. |
| 13–14 | Experiment: wholesale versus bill | Compare 0.06 energy component with declared delivered tariff; explain omitted components. |
| 15–16 | Takeaway | Power risk matters only to the party bearing it; optional capstone input. Display a compact decision summary from the already calculated results; introduce no new model. |
| 17 | Final interpretation, limitations, references and next step. | No diagnostics or hidden answers. |

All direct arithmetic precedes its packaged counterpart. One compact table and one main chart type; explorer controls update calculated outputs in one helper call with a static fallback. Keep experiments fixed independently of prior widget edits.

## Acceptance and implementation checks

Test 5,040/6,048 kWh and 804.80 bill, W/kW conversion in notebook explanation, zero draw/rate, multiplier 1, fixed charge behavior, independent technical/billed fractions, invalid units/ranges and no duplicate power expense.

Implement calculations and independent tests first, then education helpers, then notebook. Run the shared lint/type/test/schema/fresh-kernel checks, inspect local rendering and live control recovery, restore defaults and save outputs. Follow the complete checklist in [PLANNING.md](PLANNING.md); Colab remains deferred.

## Boundary with other lessons

E3 owns energy-cost decomposition. E6 owns useful-output productivity. Neither redefines rented capacity utilization from Notebook 1. No power hedge or PUE hardware benchmark in core.

## Sources and attribution

EIA delivered electricity pricing source inspected; use only to distinguish energy from full delivered charges. If calling the multiplier PUE, inspect the relevant primary definition and label our constant factor as illustrative.

See the [source ledger](PLANNING.md#source-ledger) for inspected sources versus research still required. Place verified citations next to supported explanations; distinguish original inputs and derived results. No live data or new dependencies are required for the core lesson.

## Implementation and coherence review

Reviewed all eight subsections against E3 and foundation conventions. The operator's separately paid electricity and non-power cost assumptions replace the reseller cost basis explicitly; only foundation revenue is reused, with no imported all-in rental expense. W-to-kW and kW-hours-to-kWh arithmetic precedes helpers. The fixed charge appears once and stays unchanged when the variable rate doubles. Technical active fraction changes average draw independently of billed utilization. The facility multiplier is illustrative, with no measured PUE or hardware-specification claim. The energy-only comparison is synthetic; inspected EIA text supports the delivered-cost distinction and cautions that average retail prices are not utility rates. Final summary reuses worked outcomes and keeps payment timing/financing and E6 productivity separate.

40 targeted power and market-presentation tests passed. Independent checks cover 5040/6048 kWh, the 804.80 bill and 6395.20 contribution, fixed-charge preservation, zero draw/rate, multiplier one, technical load, invalid units/types/ranges and overflow. Headless plot/control tests check tariff sensitivity, unchanged revenue and recovery from invalid draw. Static notebook schema/AST checks passed without executing cells. Ruff lint/format and strict mypy passed.

The user requested no notebook execution or repeated execution-permission prompts. Validation calls calculators and presentation helpers directly and checks notebook schema/syntax without executing cells. Fresh-kernel execution, saved runtime outputs and live Jupyter/Colab checks remain deferred. This is not a claim of full presentation verification.
