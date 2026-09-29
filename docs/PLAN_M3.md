# M3: Basis Risk: When the Index Isn’t Your Price

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](../notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Revised source, calculators and tests complete; fresh-kernel execution passed and outputs saved. Local rendered tables and chart inspected; live widget updates remain unverified due to the local Jupyter connection issue described below. **Prerequisite:** M2.
**Notebook:** [notebooks/M3_benchmark_basis_risk.ipynb](../notebooks/M3_benchmark_basis_risk.ipynb).

The [canonical roadmap](../notebooks/README.md) controls lesson status; [PLANNING.md](PLANNING.md) controls shared calculation ownership. The user's attached M3 request supersedes this lesson's earlier provider/time/quantity experiment outline and explicitly authorizes M3 execution. Other lessons retain their own verification scope. Colab verification remains deferred.

## Learning decision and scope

What happens when an index hedge pays correctly but the supplier price moves differently? Retain M2's buyer, 7,200 GPU-hours, USD 5/GPU-hour strike and month-12 payment. Equal purchased/hedged quantities, identical settlement dates and performance by counterparties isolate benchmark mismatch. Region is the sole main contract difference. No fees, margin, financing, regression, options or probability model.

Define basis as actual minus index. Show Q*S − Q*(I−K) = Q*(K+b), budget Q*(K+b0), and deviation Q*(b−b0) directly before reusable calls. The budget spread is a planning assumption, not an observed or guaranteed spread. Signed negative basis and favorable deviations remain visible.

## Teaching sequence and worked values

Seventeen alternating cells, approximately 966 prose words, target 10–15 minutes:

1. M2 perfect-match recap: USD 50,400 bill less USD 14,400 receipt = USD 36,000.
2. Budget a 0.50 regional premium: USD 54,000 bill less USD 14,400 = USD 39,600; zero budget deviation.
3. Common rise: index/supplier 5/5.50 to 7/7.50; net cost remains USD 39,600.
4. Widening: index/supplier 7/8.50; net USD 46,800, deviation +USD 7,200.
5. Supplier falls while index rises: 7/4.50; net USD 18,000, deviation −USD 21,600.
6. Static saved chart plus optional independent index/realized-basis/budget-basis controls; fixed quantity and strike. S=I+b must remain nonnegative. Editable assumptions provide fallback.
7. Aligned synthetic candidate benchmarks with stated baseline spreads 0.50/0.20. Deviations A: 0/0/7,200/−21,600; B: 0/720/1,440/−720. No probabilities, expected-loss label or statistically optimal benchmark claim.
8. Qualitative GPU specification, region, service terms, observation method and averaging-period comparison. Takeaways and exact requested transition question to M4.

Each result is followed by a short interpretation. Boundaries explain usage-weighted bills versus time averages, changing relationships, correlation versus one-for-one adequacy, and available hedge terms versus an index or capacity guarantee.

## Reusable calculations

Keep existing `basis_exposure_summary` and metadata interfaces compatible for downstream lessons. `basis_budget_summary` adds a typed frozen result for matched-quantity costs and budget deviation, reusing M2's `forward_settlements_usd`. `benchmark_basis_deviations_usd` aligns mappings by scenario name and rejects unequal sets and missing/nonfinite values. No silent zero fill or ordinal zip. Prices and quantities are finite nonnegative; budget spreads are finite signed; wrong types/bools and arithmetic overflow are rejected.

`basis_budget_series` and `explore_basis_budget` live in `liquid_compute.education`, reuse the existing chart/widget machinery, preserve input precision, own their inputs and replace invalid-price results with a recovery message. No runtime dependencies or environment were added.

## Sources and attribution

Inspected [CME basis in grains](https://www.cmegroup.com/education/courses/introduction-to-grains-and-oilseeds/learn-about-basis-grains), [Ornn price index](https://data.ornn.com/docs/price-index) and [Ornn forward curves](https://data.ornn.com/docs/forward-curves) for this revision. Citations sit near claims and in a short references section. Commodity concepts remain analogies; Ornn methodology does not establish actual hedge availability or validate the synthetic comparisons. No external data dependency or provider history is introduced.

## Implementation and coherence review

The revised lesson isolates uncertain changes in basis rather than treating every nonzero spread as a surprise loss. All primary experiments use equal quantities and aligned dates. Quantity mismatch moves to M4 and liquidity remains M7. Existing broader decomposition functions/tests remain available without exposing those extensions in this lesson.

Validation: **113 focused tests passed**; full headless/static regression run **664 passed, 7 deselected** (only unrelated pre-existing notebook-cell execution tests excluded). Ruff lint/format and strict mypy passed. Python 3.10.11 and the existing editable environment were reused. M3 alone passed fresh-kernel execution, including a second run after formatting dollar output; all eight code cells have saved results. Tables reconcile to direct arithmetic, and the saved chart was visually inspected. Schema/static structure and package-call checks passed. Tests cover zero basis, constant spread, exact budget, dollar widening, negative basis, zero quantity, signed net costs, independent cash reconciliation, overflow, scenario alignment/gaps, chart values, control precision/independence, invalid-input recovery and widget-free fallback.

Local Jupyter rendered formulas, tables, baseline charts and controls. A restart/rerun and reload were attempted, but browser-side edits did not reliably update displayed values; the browser logged a lost connection and missing widget models. Defaults were restored. Live interaction acceptance is therefore unverified, not passed; direct Python widget-observer tests (including invalid-price recovery) pass. The saved static chart and editable-cell fallback remain available. Hosted Colab execution remains unverified and deferred until the series is complete.
