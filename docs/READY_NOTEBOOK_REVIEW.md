# Ready notebook visualization and interaction review

Reviewed on 2026-09-29 against the [canonical roadmap](../notebooks/README.md). Ready/WIP membership is unchanged. Each Ready lesson retains editable assumptions, visible core arithmetic, explanations after worked examples, and saved static outputs.

| Ready lesson | Visual explanation | Interactive controls and review result |
|---|---|---|
| [1 — Compute economics](../notebooks/01_compute_business.ipynb) | Contribution versus utilization, break-even marker and current scenario. | Existing capacity, hours, prices and utilization controls already support the decision. Retained and rerun. |
| [2 — Cash-flow timing](../notebooks/02_cash_flows_through_time.ipynb) | Cumulative cash compares funding gaps; present-value chart separates payment timing from cost. | Existing supplier/customer terms, collection lag, discount and valuation-rate explorer retained and rerun. |
| [3 — Implied rental blocks](../notebooks/03_rental_quotes_to_implied_forward_curve.ipynb) | Same-start contract bars and labeled step chart make quoted packages distinct from inferred blocks. | Existing exact-value quote controls and invalid-input recovery retained and rerun. |
| [4 / M1 — Tenor trade](../notebooks/04_the_tenor_trade.ipynb) | Attributed tenor-price snapshot, contribution heatmap with break-even boundary, and monthly price/fill comparison. | Existing resale price, placement and selling-fee controls retained and rerun. |
| [M2 — Forwards and swaps](../notebooks/M2_forwards_and_swaps.ipynb) | New paired charts compare unhedged/hedged physical outcomes and signed hedge cash. Partial coverage leaves a slope; overhedging reverses it. | Package helper controls buyer/seller, physical hours, hedge hours and strike. Includes reset, invalid-input recovery and widget-free fallback. |
| [M5 — Calls and puts](../notebooks/M5_calls_and_puts.ipynb) | New charts separate gross payoff, payoff less premium, and protected/unprotected physical outcomes. Price grids include the strike exactly. | Package helper controls call/put, physical/covered hours, strike, premium and physical-minus-benchmark basis. Both parties buy protection; totals remain nominal cash, not valuations. |
| [M6 — Option valuation](../notebooks/M6_option_valuation.ipynb) | New recombining node diagram labels proxy prices and option values, showing terminal payoffs and backward valuation. | Controls kind, spot, strike, factors, rate and step duration. Readout shows one-step delta, cash position and value, and separately labels the two-step expiry/value. Invalid no-arbitrage inputs replace the chart rather than producing clipped weights. |
| [Compute lab case](../notebooks/case_lab_gpu_financing.ipynb) | Existing funding structure, capacity, cash/debt-service, coverage heatmap, collateral and stress charts retained. | Expanded explorer varies training, commitments, spot price and loan rate; switches cash/capacity/collateral views. Explicit output updates replace the prior output-context callback. Scenario and decision-table assembly now lives in package helpers. |

## Package boundary

`liquid_compute.education` owns chart assembly, labels, widget construction, callbacks, output replacement, input snapshots, reset behavior, and static fallbacks. A private shared figure explorer supports the four updated panels. It preserves exact input values, clears stale charts after invalid edits, and keeps instances independent. Optional display imports remain lazy; the calculation package gains no runtime dependencies.

Notebook cells retain the business assumptions and direct financial arithmetic. M2 and M5 retain their short financial schedule compositions to make cash signs and payment dates inspectable. The changes reuse the existing hedging, option payoff, tree valuation and lab calculators; no new pricing model or contractual assumption is introduced.

## Verification

- All eight Ready notebooks passed local fresh-kernel execution with outputs saved. The four changed lessons were refreshed again after the reset-button width adjustment.
- Full suite: **758 tests passed**. Ruff lint/format and strict mypy passed. The 18 new tests cover plotted financial values, exact strike placement, signed hedge cash, premium accounting, partial coverage, basis, tree labels, control independence, precision, reset, invalid-input recovery and widget-free fallbacks.
- Visually inspected foundation charts, the tenor heatmap, the lab coverage chart and the new forward, option and valuation figures.
- Local Jupyter smoke check for M5: changing covered hours from 7,200 to 3,600 visibly changed the protected-cost slope; a negative premium replaced the chart with an explanatory error; reset restored full coverage and the original premium/chart. Other updated controls were exercised directly in headless tests, not claimed as separately browser-tested.
- Hosted Colab interaction remains unverified. Static charts and editable cells remain available without live widget support.
