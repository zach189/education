# E5: Historical Risk Measurement and the Observation Window — implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](../notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Created/tested; optional elective. Coherence reviewed; execution/live acceptance deferred by user instruction. **Prerequisites:** M3 and M4.
**Notebook:** [notebooks/E5_historical_risk_measurement.ipynb](../notebooks/E5_historical_risk_measurement.ipynb).

Read the [canonical roadmap](../notebooks/README.md), [shared planning conventions](PLANNING.md), and [project guidance](../AGENTS.md). Foundation plans remain implementation records; this document specifies only the new lesson or unfinished work.

## Learning decision, assumptions, and worked example

All numeric contract terms and scenarios below are hypothetical teaching assumptions, not market quotes.

Optional question: how sensitive are measured price changes to the observations selected? The core uses an embedded **synthetic observation history**, not market data: monthly prices[10,11,10,11,10,11,10,20]USD/GPU-hour. Describe it as an illustration of historical-measurement methods. Log changes x_t=ln(P_t/P_(t−1)); sample standard deviation uses n−1. Whole series has seven changes; six alternating ±ln(1.1) followed byln 2. Compare the pre-jump six-change window to the last three changes; report exact sample counts and selected dates.

Annualized monthly volatility=sqrt(12)·sample_sd only under the explicitly assumed regular monthly, comparable sampling convention; do not use 365 or 252. Do not equate a short-window estimate with future risk or M6's model volatility. A chart shows observations and highlighted window, not a fitted future curve.

Optional real-data appendix is gated on primary administrator data with dates, units, matching product definition, redistribution permission and a checked-in snapshot. If inaccessible, omit the appendix rather than invent history. Missing prices stay missing: no silent forward-fill or zero returns. Compute returns only across adjacent calendar months with both observations; state how many were omitted. A 10→20 jump can be a valid observation requiring context, not an automatic outlier to remove.

## Reusable calculations and interfaces

Add `risk_statistics` with `monthly_log_returns(observations)` retaining explicit month labels and missing markers, and `sample_volatility(returns, periods_per_year=None)` returning count, sample sd and optional annualized sd. Use Python statistics/math; no pandas dependency. Require positive finite nonmissing prices, sorted unique month indices and at least two valid returns for sample sd; return unavailable result/reason for insufficient history rather than zero risk. Any winsorization or imputation is outside core.

## Cell-by-cell teaching sequence

Use 17 cells: eight Markdown/code pairs below, followed by a final Markdown takeaway with references and the indicated next lesson. Each Markdown cell after an experiment explains the preceding output before introducing the next prediction. Target 10–15 minutes, 800–1,100 prose words; label any extensions optional.

| Cells | Markdown explanation / optional prediction | Executable content |
|---|---|---|
| 1–2 | Measurement question | Declare synthetic data, dates, units and product consistency. |
| 3–4 | Visible two returns | ln(11/10)andln(10/11); distinguish level from return. |
| 5–6 | Direct variance arithmetic | Mean, deviations, n−1 denominator before helper. |
| 7–8 | Explorer | Price history and selected window; controls start/end month. |
| 9–10 | Experiment: window length | Compare pre-jump and jump-containing windows; counts visible. |
| 11–12 | Experiment: missing observation | Remove one price; adjacent-month returns missing, not zero. |
| 13–14 | Experiment: annualization | Raw monthly versus sqrt 12 under stated convention; no forecasting claim. |
| 15–16 | Takeaway | Estimates depend on data decisions; optional real snapshot and C1 sensitivity only. Display a compact decision summary from the already calculated results; introduce no new model. |
| 17 | Final interpretation, limitations, references and next step. | No diagnostics or hidden answers. |

All direct arithmetic precedes its packaged counterpart. One compact table and one main chart type; explorer controls update calculated outputs in one helper call with a static fallback. Keep experiments fixed independently of prior widget edits.

## Acceptance and implementation checks

Test log-return signs, constant serieszero, independent sample-sd calculation, n−1 versus population denominator, correct sqrt 12, insufficient data unavailable, missing-calendar gaps not bridged, positive prices and sorted unique dates. Optional fixture must include provenance and units.

Implement calculations and independent tests first, then education helpers, then notebook. Run the shared lint/type/test/schema/fresh-kernel checks, inspect local rendering and live control recovery, restore defaults and save outputs. Follow the complete checklist in [PLANNING.md](PLANNING.md); Colab remains deferred.

## Boundary with other lessons

E5 measures sample variability. M4 uses chosen scenarios; M6 values under trading/model assumptions. Do not silently calibrate either from this short dataset or teach stochastic simulation here.

## Sources and attribution

NIST statistical handbook is a primary research target for sample standard deviation. For actual compute history inspect administrator methodology and licensing first; none of our synthetic observations are attributed to Ornn or the source post.

See the [source ledger](PLANNING.md#source-ledger) for inspected sources versus research still required. Place verified citations next to supported explanations; distinguish original inputs and derived results. No live data or new dependencies are required for the core lesson.

## Implementation and coherence review

Reviewed all eight subsections against E5 and M3/M4/M6 boundaries. Embedded January–August 2025 observations are consistently labeled synthetic, with unchanged product definition explicitly assumed. Direct log returns and n−1 sample variance precede helpers. Inclusive price-date windows include only returns whose two endpoints are selected. Missing April removes two adjacent-month changes and is never bridged/filled; sparse calendar gaps receive explicit missing markers. Plots highlight dates and report valid/omitted counts, with N/A for insufficient history. Annualization uses sqrt(12) only under declared regular sampling and time-scaling assumptions, including the covariance limitation. No future curve, model calibration or real-data appendix is added. NIST sample-SD definition was inspected and cited near the calculation.

44 targeted risk-statistics and market-presentation tests passed. Checks cover independent n−1 arithmetic, log signs, constant versus unavailable history, extreme positive ratios, missing calendars, input validation, exact chart dates/window counts, visible missing-price gaps, independent start/end controls, invalid-window recovery and static rendering without widgets. Notebook schema/AST checks, Ruff lint/format and strict mypy passed without notebook execution.

The user requested no notebook execution or repeated execution-permission prompts. Validation calls calculators and presentation helpers directly and checks notebook schema/syntax without executing cells. Fresh-kernel execution, saved runtime outputs and live Jupyter/Colab checks remain deferred. This is not a claim of full presentation verification.
