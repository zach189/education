# E6: Cost per Useful Output, Workload Intensity, and Mix — implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Created/tested; optional elective. Coherence reviewed; execution/live acceptance deferred by user instruction. **Prerequisites:** 1.
**Notebook:** [notebooks/E6_cost_per_useful_output.ipynb](notebooks/E6_cost_per_useful_output.ipynb).

Read the [canonical roadmap](notebooks/README.md), [shared planning conventions](PLANNING.md), and [project guidance](AGENTS.md). Foundation plans remain implementation records; this document specifies only the new lesson or unfinished work.

## Learning decision, assumptions, and worked example

All numeric contract terms and scenarios below are hypothetical teaching assumptions, not market quotes.

Optional question: can unit cost improve while total spend grows? Use a customer buying consumed GPU-hours at 4 USD/hour, not the reseller's reserved-rent model. Define one useful output as a task that meets a fixed quality criterion; do not equate it with a token, technical utilization or revenue. Baseline 10,000 tasks,0.01 GPU-hours/task, total 100 hours, spend 400 USD, unit 0.04 USD/task. Efficiency improves to 0.008 hours/task while demand grows 50% to 15,000 tasks:120 hours,480 USD,0.032 USD/task. Unit cost falls 20%, total spend rises 20%.

Add two workloads under the same quality definitions: light 0.005 hours/task and heavy 0.02, baseline mix 80% light/20% heavy. Weighted intensity 0.008, so 10,000 tasks cost 320. Mix shifts 50/50:0.0125 hours/task, cost 500. Use a sequential exact decomposition with fixed order volume→mix→intensity→price. Changes depend on attribution order; total reconciliation does not. Keep capacity ceilings, failed attempts, power and financing outside core; optionally count retries only with an explicit useful-output definition.

## Reusable calculations and interfaces

Add `workload_costs` with `useful_output_costs(task_counts, gpu_hours_per_task, usd_per_gpu_hour)` returning useful tasks, consumedGPU-hours, total cost and USD/task (None for zero tasks). `decompose_workload_spend` applies the documented ordered replacements to two aligned workload mappings and reports contributions plus reconciliation. Validate stable category identities, nonnegative counts/intensities/rates, finite products; reject overlapping categories. Fractions if used must sum to 1, but core API uses explicit counts to avoid ambiguous normalization.

## Cell-by-cell teaching sequence

Use 17 cells: eight Markdown/code pairs below, followed by a final Markdown takeaway with references and the indicated next lesson. Each Markdown cell after an experiment explains the preceding output before introducing the next prediction. Target 10–15 minutes, 800–1,100 prose words; label any extensions optional.

| Cells | Markdown explanation / optional prediction | Executable content |
|---|---|---|
| 1–2 | Business question and output unit | Name customer role and constant quality criterion. |
| 3–4 | Direct baseline and efficiency arithmetic | 400→480 whileunit 0.04→0.032. |
| 5–6 | Workload mix table | Two categories, consumed hours and weighted unit costs. |
| 7–8 | Explorer | Total cost and unit-cost comparison; controls demand and heavy-workload share. |
| 9–10 | Experiment: efficiency only | Hold volume/mix fixed; isolate lower hours per task. |
| 11–12 | Experiment: more demand | Apply 1.5 volume with 0.8 intensity; explain higher spend. |
| 13–14 | Experiment: mix shift | 80/20→50/50; perform ordered spend decomposition. |
| 15–16 | Takeaway | Cheap compute per task and a lower total bill are different goals; optional C1 demand lens. Display a compact decision summary from the already calculated results; introduce no new model. |
| 17 | Final interpretation, limitations, references and next step. | No diagnostics or hidden answers. |

All direct arithmetic precedes its packaged counterpart. One compact table and one main chart type; explorer controls update calculated outputs in one helper call with a static fallback. Keep experiments fixed independently of prior widget edits.

## Acceptance and implementation checks

Test 400/480 and 320/500 examples, weighted totals not average of category unit prices, zero tasks N/A, decomposition exact reconciliation, unchanged inputs all-zero contributions, invalid/overlapping categories and dimension consistency.

Implement calculations and independent tests first, then education helpers, then notebook. Run the shared lint/type/test/schema/fresh-kernel checks, inspect local rendering and live control recovery, restore defaults and save outputs. Follow the complete checklist in [PLANNING.md](PLANNING.md); Colab remains deferred.

## Boundary with other lessons

E6 owns workload/productivity units. Notebook 1 owns billed utilization and reseller profit; E3 owns energy. No hardware benchmark, model quality claim or dollars-per-token claim without controlled data.

## Sources and attribution

No external source needed for invented arithmetic. If including real performance comparisons, require original benchmark methodology, hardware/software configuration and quality criterion; inspect MLCommons primary material first.

See the [source ledger](PLANNING.md#source-ledger) for inspected sources versus research still required. Place verified citations next to supported explanations; distinguish original inputs and derived results. No live data or new dependencies are required for the core lesson.

## Implementation and coherence review

Reviewed all eight subsections against E6 and Notebook 1/E3 boundaries. The customer buys consumed hours, with fixed useful-task quality and disjoint category counts; no reserved-rent, token, technical-load or benchmark claim is inferred. Direct 400-to-480 arithmetic precedes helpers. Weighted 80/20 versus 50/50 mix yields 320 versus 500. Charts separate USD from USD/task and show zero-task unit cost as N/A. Demand/mix controls retain a frozen baseline and valid complementary shares. Efficiency-only, growth and mix-shift experiments use independent inputs. Spend decomposition follows volume, mix, intensity, price in that order and reports reconciliation; its zero-volume convention is documented in the reusable API. Small unit costs/intensities retain explicit display precision. The last summary introduces no new model and C1 remains unimplemented.

46 targeted workload and market-presentation tests passed. Independent calculations cover the 400/480 and 320/500 references, weighted allocation, all four ordered effects, unchanged/zero-volume cases, category/type/range validation and overflow. Headless plotting tests check separate axes, N/A at zero tasks, demand/mix control changes, invalid-input recovery and widget-free rendering. Static notebook schema/AST checks, Ruff lint/format and strict mypy passed. Final inventory/signature/link checks are included in the subsequent cross-track audit.

The user requested no notebook execution or repeated execution-permission prompts. Validation calls calculators and presentation helpers directly and checks notebook schema/syntax without executing cells. Fresh-kernel execution, saved runtime outputs and live Jupyter/Colab checks remain deferred. This is not a claim of full presentation verification.
