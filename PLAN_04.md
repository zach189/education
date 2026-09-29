# M1: The Tenor Trade: Buying Long, Selling Short

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Revised source, calculations and presentation checks complete; fresh-kernel execution passed and outputs saved. Live Jupyter interaction and hosted Colab acceptance remain unverified. **Prerequisite:** Foundations 1–3.
**Notebook:** [04_the_tenor_trade.ipynb](notebooks/04_the_tenor_trade.ipynb).

The [canonical roadmap](notebooks/README.md) controls status. The [planning index](PLANNING.md) controls calculation ownership. This specification supersedes the prior fully contracted first-year/two-year-tail lesson, which changed the article's underlying trade. Existing tail APIs and regression tests remain compatible for other callers.

## Decision and source distinction

What does a lower long-term rental rate pay a capacity reseller to take on? Buy 36 months and sell separately each month, without an assumed profitable contracted first year.

The opening chart/table reproduce the actual published Figure 1 observations in [Liquid Compute's The Tenor Trade](https://liquidcompute.com/research/the-tenor-trade), September 2026, inspected September 28: B300 on demand 5.97, 1M 5.30, 6M 5.15, 12M 5.05, 24M 4.60, 36M 4.25 USD/GPU-hour. These are attributed reported observations, not a live feed or independently verified executable offers. Differences versus 36M are 1.72, 1.05, 0.90, 0.80, 0.35 and zero. Use endpoint arithmetic rather than the source chart's approximate spread annotation.

This is a rental **term-price curve**, not forward quotes for different future delivery dates. On demand is a separate category, not a zero-month forward. No interpolation or inference across unspecified payment/service terms. [Ornn's methodology](https://data.ornn.com/docs/forward-curves) supports the term-price/implied-block distinction. The separate hypothetical 12M/36M menu of 6/5 implies a 4.50 years-2–3 allocation under equal monthly weights; it does not create an offer or replace the 5/hour supplier bill.

## Independent main example

10 GPUs × 720 monthly hours, 36-month rental rights at USD 5/hour. Initial resale USD 6/hour; every month must find buyers. Resale rights, upstream delivery and payment performance are assumed. No hardware ownership or resale proceeds. Initial fees zero, adjustable; no overhead, tax or borrowing costs. Fill means booked paid hours, not technical GPU utilization.

- At full fill: USD 43,200 monthly revenue minus USD 36,000 service expense = USD 7,200 monthly gross; USD 86,400 annual if repeated.
- Contribution H[fP(1−c)−C]; break-even fill C/[P(1−c)]. At 6/hour: 83.33%; at 5.50: 90.91%; below cost, required fill exceeds 100%.
- Annual scenarios at 6/hour and 100%/90%/80% fill: 86,400/34,560/−17,280. At 5.50 and 90%: −4,320. There is no first-year surplus credited against later obligations.
- Explicit 36-month synthetic prices and fill weaken together then recover. No historical dataset, forecast, simulated probabilities or estimated correlation. Compare resale price with revenue per purchased hour and fixed cost.
- 30% upfront payment: USD 388,800 at signing plus USD 25,200 at each of 36 month-ends = USD 1,296,000 total rent. The hypothetical pro-rata credit rule is stated. Service expense remains USD 36,000/month; never double-count the deposit. Customers and fees settle at each month-end. Peak funding reuses the cashflows module.
- M2 preview: one-third seller hedge (2,400 hours) at hypothetical 5.50. With full fill, index 3/6/8 produces combined monthly contribution −8,400/6,000/15,600. At index 6 and 70% fill the fixed hedge pays −1,200, leaving combined contribution −6,960. No real hedge availability or financing advance rate is inferred.

## Teaching and reusable components

Seventeen alternating cells, approximately 1,150 prose words, 10–15 minutes. Sequence: sourced tenor curve and spreads; direct monthly trade; annual fill grid and controls; 36-month re-let path; prepayment cash; partial seller hedge; fill stress; implied-versus-quoted distinction; takeaways and M2/F1 transitions. Results have adjacent interpretations; baseline charts are saved before widgets. Editable cells remain available.

Reuse `build_reseller_commitment_scenario` for monthly operating economics, `tenor_tail_outcome` with zero initial contracted revenue for annual hurdles, `forward_settlements_usd` for the seller hedge, and `imply_rental_blocks` for the separate hypothetical allocation. No duplicate financial engine.

Add `allocate_supplier_prepayment_usd` to the cashflows owner: nonempty finite nonnegative monthly expenses, finite fraction in [0,1], output includes time zero and preserves total nominal rent. Wrong types/bools, invalid ranges, nonfinite values and overflow are rejected. New `plot_tenor_price_snapshot` renders supplied quotes and gaps with source/date supplied by the notebook. Existing heatmap/explorer accept a reporting-period label so the annual display does not claim a 36-month horizon. Prior default behavior remains available.

## Implementation and coherence review

The new lesson preserves the article's recurring resale exposure, upfront capital requirement, price/fill interaction and partial-hedge mechanism while retaining an independent main scenario. The source-specific price snapshot is explicitly cited and separated from that scenario. It no longer assumes a profitable contracted first year or treats a whole-deal tail hurdle as the recurring fill threshold. It does not endorse the article's broad claims about unhedgeable risks or automatic financing benefits. Existing library APIs/tests are retained for downstream reuse.

## Validation

- Focused regression: **122 passed**, covering tenor snapshots, cash allocation, annual hurdles, monthly placement, seller settlement, existing heatmap controls and static notebook structure.
- Full allowed regression: **687 passed, 7 deselected**. Only unrelated pre-existing notebook-cell execution tests were excluded; M1 execution was performed separately with the existing validator.
- Ruff lint and format passed across source/tests/scripts/notebooks; strict mypy passed for all 24 package files. Existing Python 3.10 environment and dependencies reused.
- M1 passed schema validation and fresh-kernel execution twice, including the final presentation fixes; all eight code cells have saved results. No errors. The sourced price curve, annual heatmap and synthetic path chart were visually inspected. A clipped price-gap label and duplicate static heatmap display were fixed.
- Synthetic annual contributions are 54,972 / −128,916 / −13,212 USD, totaling −87,156. The explicit prepayment cash schedule reconciles to that total and requires USD 388,800 peak funding before financing.
- The user's earlier M1 execution authorization applies to this revision only. Other lessons' scope is unchanged. Live Jupyter interaction is not newly verified; hosted Colab remains deferred. Saved figures and editable-cell fallbacks are available.

## Superseded revision history

The preceding M1 revision used a contracted 12-month customer at USD 8 and a two-year renewal tail, with fees and whole-deal break-even. It passed 617 headless/static tests and later user-authorized fresh-kernel execution. Those values and saved outputs described the old lesson, not this revision. Its calculator regression tests remain useful compatibility tests.
