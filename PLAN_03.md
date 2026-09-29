# Notebook 3: From Rental Quotes to an Implied Forward Curve

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status: implemented locally.** The [notebook](notebooks/03_rental_quotes_to_implied_forward_curve.ipynb) follows the [canonical roadmap](notebooks/README.md). Its next lesson is **Notebook 4 / M1: The Tenor Trade: Buying Long, Selling Short**, the first market-risk lesson. Forwards and swaps follow as M2; remaining market-risk lessons run through M7. Keep three shared foundation lessons, with financing accessible after Notebook 2. Notebook 4 is not implemented by this task.

## Learning experience and defaults

A 10–15-minute core lesson for readers who know basic Python and have studied compute economics, cash-flow timing, and present value. Use one independent rental menu, one overlap diagram, one interactive step chart, and a compact reconstruction table. Discounting and the post's numerical reproduction are optional extensions.

The business question is: **We can rent capacity cheaply by committing for several years, but our customers may buy shorter periods. What do the supplier's package prices imply about those future periods?** Do not assume inferred rates are available downstream selling prices or calculate resale profit yet.

Before arithmetic, contrast a forward quote offered today for a specified future period with an implied block rate allocated from overlapping same-start rental packages. No supplier necessarily offers the block separately. Market curves can also contain inferred or interpolated points. Use “implied block rate” consistently for computed outputs.

Independent hypothetical menu: 12 months at USD 6.00/GPU-hour; 36 at 5.00; 60 at 4.40. Continue the capacity reseller with 10 GPUs and 720 delivery hours per GPU per modeled month. GPU specifications, quantity, location, service, and start date match. All reserved hours are purchased; utilization does not reduce supplier commitments. This is rental capacity, not hardware ownership.

Every package charges its quoted flat rate throughout. The block allocation does not revise its invoices. With constant capacity and equal monthly hours, those factors cancel in the rate calculation.

## Core arithmetic and interpretation

Let R(b) be the flat whole-contract rate through month b. The block covers service months a+1 through b, delivery time [a,b):

\[
F(a,b)=\frac{bR(b)-aR(a)}{b-a},\qquad
\frac{NbhR(b)-NahR(a)}{N(b-a)h}=\frac{bR(b)-aR(a)}{b-a}.
\]

Handle the first block separately as the shortest quote; do not invent R(0). The main blocks are 6.00 / 4.50 / 3.50. Show direct arithmetic before calling shared functions:

- (36 × 5 − 12 × 6) / 24 = 4.50.
- (60 × 4.40 − 36 × 5) / 24 = 3.50.
- Reconstruct 36 months: (12 × 6 + 24 × 4.5) / 36 = 5.00.
- Reconstruct 60 months: (12 × 6 + 24 × 4.5 + 24 × 3.5) / 60 = 4.40.

The main chart uses delivery boundaries 0, 12, 36, 60 and USD/GPU-hour. Caption: **“Implied block rates; flat within each block assumed.”** No smoothing. A short static comparison shows flat 4.50 versus 3.50 in year 2 and 5.50 in year 3: both average 4.50 undiscounted, but months 13–15 differ. Do not claim those alternative shapes also preserve discounted totals.

Fixed experiments:

1. Raise the middle quote 5.00 → 5.20: blocks become 6.00 / 4.80 / 3.20. The unchanged five-year total links adjacent allocations.
2. Set every quote to 5.00: all implied blocks are 5.00.
3. Set the five-year quote to 3.00, then 2.80: the final block is zero, then −0.50.

Retain economically unusual outputs. Nonpositive blocks may reflect whole-package commitment discounts rather than erroneous quotes; they establish neither separately available free capacity nor executable arbitrage. Investigate comparable terms and actual transaction opportunities.

Missing quotes remain absent. Without a 36-month quote, return one months-13–60 block at 4.00; do not manufacture intermediate boundaries or marks. Display missing standard tenors as “Not quoted.”

## Cell-by-cell specification

Alternate Markdown and executable code by combining an experiment's explanation with the following introduction. Keep predictions optional and answers visible. Every experiment's next Markdown cell explains its result.

| Cell | Type | Content |
|---:|---|---|
| 1 | Markdown | Business question, goals, quoted versus inferred distinction, and reseller relevance. |
| 2 | Code | Editable main menu, GPU count, hours, and package table. |
| 3 | Markdown | Same-start contracts; contract length versus delivery period. |
| 4 | Code | Three overlapping delivery bars. |
| 5 | Markdown | First-year subtraction and unit cancellation. |
| 6 | Code | Direct block arithmetic with first block handled separately. |
| 7 | Markdown | General identity, Ornn citation, reconstruction explanation. |
| 8 | Code | Shared inference, direct reconstruction, compact comparison table. |
| 9 | Markdown | Static monthly-shape example and explorer instructions/fallback. |
| 10 | Interactive code | Three-price explorer, table, and step chart with saved static outputs. |
| 11 | Markdown | Predict the middle-quote experiment. |
| 12 | Code | Baseline and raised-middle blocks. |
| 13 | Markdown | Explain linked changes; introduce equal quotes. |
| 14 | Code | Flat-quote experiment. |
| 15 | Markdown | Explain flat blocks; introduce nonpositive blocks. |
| 16 | Code | Zero and negative final blocks. |
| 17 | Markdown | Interpret discounts, core takeaway, and optional discounted extension. |
| 18 | Optional code | Direct weighted block, shared calculations at 0/12/24%, package-PV reconstruction. |
| 19 | Markdown | Unchanged quotes/changed allocation; introduce source reproduction. |
| 20 | Optional code | Source menu and continuous-rate reproduction. |
| 21 | Markdown | Interpretation, references, limitations, and exact tenor-trade transition. |

Core content is complete without executing cells 18–20. End with:

> If longer commitments offer a lower hourly rate, what happens when we buy a long contract and resell the capacity in shorter blocks—and what risks do we retain?

## Optional discounting and source example

Reuse Notebook 2's effective annual convention and `discount_factor`. Assume month-end payments t_m=m and matching payment dates/delivery hours across overlapping months. Hours h_m are per GPU; factors D are dimensionless:

\[
D(t_m)=(1+r)^{-t_m/12},\quad W(a,b)=\sum_{m=a+1}^{b}h_mD(t_m),
\quad F_D(a,b)=\frac{R(b)W(0,b)-R(a)W(0,a)}{W(a,b)}.
\]

Discounting changes allocation weights, not quoted rates. Reconstruct every package PV in USD per GPU:

\[
R(T)W(0,T)=\sum_{\text{blocks through }T}F_D(a,b)W(a,b).
\]

| Effective annual rate | Months 1–12 | Months 13–36 | Months 37–60 |
|---|---:|---:|---:|
| 0% | 6.0000 | 4.5000 | 3.5000 |
| 12% | 6.0000 | 4.4083 | 3.2020 |
| 24% | 6.0000 | 4.3136 | 2.8442 |

Zero discounting recovers the undiscounted construction under the same hours. Do not use this formula unchanged for different package payment structures, such as upfront versus monthly. Discounting does not independently remove commercial, credit, or commitment discounts.

The optional source menu is 6.25 / 4.85 / 4.15 for 12 / 36 / 60 months, giving undiscounted blocks 6.25 / 4.15 / 3.10. Convert 10% continuous via `expm1(0.10)` (about 10.5171% effective annual): discounted blocks are approximately 6.25 / 4.0377 / 2.7990. Ten percent effective annual is different. Keep source reproduction readable, with assertions in tests only.

## Shared components

`liquid_compute.forward_curves` provides frozen, annotated records:

- `RentalQuote(term_months: int, rental_usd_per_gpu_hour: float)`.
- `ImpliedRentalBlock(start_month_offset: int, end_month_offset: int, implied_usd_per_gpu_hour: float)`.

```python
def imply_rental_blocks(
    quotes: Sequence[RentalQuote],
    *,
    delivery_hours_per_gpu: Sequence[float],
    payment_discount_factors: Sequence[float] | None = None,
) -> tuple[ImpliedRentalBlock, ...]: ...


def reconstruct_rental_quotes(
    blocks: Sequence[ImpliedRentalBlock],
    *,
    delivery_hours_per_gpu: Sequence[float],
    payment_discount_factors: Sequence[float] | None = None,
) -> tuple[RentalQuote, ...]: ...
```

Array index zero means service month 1, unlike the time-zero cash-flow sequence in `present_value_usd`. Omitted discount factors mean ones. Validate nonempty inputs, record types, positive increasing integer tenors excluding bool, positive finite source quotes/hours, exact array lengths, and finite factors in (0,1]. Reject unsorted/duplicate tenors, nonfinite arithmetic, overflow, and zero effective weights. Reconstruction requires contiguous positive-length blocks starting at zero and permits signed finite rates and reconstructed outputs. Never clip negative calculated blocks.

Optional rendering remains in `liquid_compute.education`: package and block tables, reconstruction table, overlap diagram, and independent explorer. Render precomputed values; do not hide business arithmetic in plotting code. Preserve exact control initialization, clear invalid states and recover, and display a complete static fallback without widgets. Explorer table and chart use ordinary notebook outputs updated by display handles, preserving the baseline for book-like reading. No new dependencies or environment.

## Sources

- [Ornn methodology](https://data.ornn.com/docs/forward-curves): undiscounted package unbundling, missing marks, and embedded commercial discounts. Cite near the identity and limitations. Its publication policy excludes nonpositive stretches; our lesson retains them for teaching.
- [Eugene Ye's post](https://wafer.substack.com/p/lets-talk-about-trading-compute): optional numerical menu, discounted extension, and flat-within-block assumption. The web reader failed, but the relevant post content was inspected through the browser during planning.
- [CME curve methodology](https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457224064/OTC%2BIRS%2BCurves): the opening qualification about inferred/interpolated market-curve points.

Main inputs, experiments, and alternate shapes are independent hypothetical teaching examples, not market data. Exclude options, stochastic simulation, curve fitting, and financing structures.

## Acceptance and validation

Implementation order: calculations/tests → display helpers → notebook → fresh-kernel execution and local visual checks → documentation alignment.

- Worked examples, all package reconstructions, and source reproduction match expected results.
- Tests cover weighted PV reconstruction, zero rate, unequal hours, scale cancellation, missing tenors, and signed outputs separately from invalid inputs.
- Validate types, bools, finite values, tenor/boundary order, factors, weights, and arithmetic failures.
- Explorer tests cover exact initialization, independent instances, invalid-edit recovery, missing tenors, negative rendering, and widget-free outputs.
- Check direct notebook arithmetic and alternating cell structure; no diagnostic assertions appear in lesson cells.
- Run Ruff, formatting checks, strict mypy, pytest, and the existing fresh-kernel validator with the Notebook 3 path. Keep Notebook 1 as the validator default.
- Inspect saved formulas, tables, interval labels, chart annotations, and local interactive updates. Preserve baseline outputs.
- Reuse Python 3.10.11 `.venv`. Standard `.ipynb`, no absolute paths or live APIs, and editable fallbacks preserve portability. Colab setup and hosted execution remain deferred.
- Keep roadmap IDs and prerequisite references consistent with Notebook 4 as M1 and former market-risk lessons shifted to M2–M7; do not implement Notebook 4 here.

### Completed verification

- All 217 tests passed, including both existing lessons and the new calculation/explorer checks. The three explorer/lesson checks passed again during visual review.
- Ruff lint/format checks and strict mypy passed. Notebook 3 passed schema validation and fresh-kernel execution with baseline outputs saved.
- Local Jupyter review verified rendered formulas/tables and live middle-quote and negative-block updates. Corrected a clipped overlap label and placed negative chart annotations below their steps.
- Local documentation links resolve; original chat history is preserved. Colab verification remains deferred.
