# M7: Hedge Collateral and Liquidity — implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](../notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Created; calculator, headless presentation and static notebook tests pass. Coherence review complete. Notebook execution/live acceptance deferred by user instruction. **Prerequisites:** M2, M3 and 2; M5 for optional option example.
**Notebook:** [notebooks/M7_hedge_collateral_liquidity.ipynb](../notebooks/M7_hedge_collateral_liquidity.ipynb).

Read the [canonical roadmap](../notebooks/README.md), [shared planning conventions](PLANNING.md), and [project guidance](../AGENTS.md). Foundation plans remain implementation records; this document specifies only the new lesson or unfinished work.

## Learning decision, assumptions, and worked example

All numeric contract terms and scenarios below are hypothetical teaching assumptions, not market quotes.

Question: can a hedge reduce final price exposure yet increase peak cash need? First teach a hypothetical futures-style short hedge for a supplier expecting to sell 7,200 GPU-hours at month 3. Entry futures price 5; marks at months 1/2/3 are 6/7/5 USD/GPU-hour. Short variation settlements are−7,200,−7,200,+14,400. Sum zero, but cumulative variation reaches−14,400. Assume initial margin 5,000 at t=0 held unchanged until returned at t=3 after final settlement; combined funding peak 19,400 before physical sales receipt. Initial margin is restricted cash returned, not a permanent expense; variation settlement is actual cash P&L.

Contrast a separate hypothetical OTC short forward on the same marks: value proxy Q(K−mark), posting collateral=max(0,−value−threshold), threshold 5,000, zero minimum transfer amount and no interest. Model only this party’s posting on negative value; positive value does not create received collateral. These are monthly snapshots, not daily settlement records. Required posted balances 2,200/9,400/0; changes are cash movements, not repeated expenses. At maturity return collateral and settle final forward payoff once. Variation settlement and collateral are different ledgers.

Keep marks hypothetical, identify simplified month snapshots as potentially understating daily peaks. Physical receipt at t=3 can be netted at that boundary; no default losses or exchange margin calibration.

## Reusable calculations and interfaces

Add `collateral_liquidity` with separate `futures_variation_cash_flows` and `otc_collateral_transfers`; typed results distinguish locked collateral balance, transfers/returns and derivative settlement. Reuse M2 payoff and cash funding helpers. Futures variation must telescope to total futures P&L; never add full terminal forward payoff again. OTC collateral is returned before/with separately recorded terminal settlement under the declared no-default arrangement. Do not add a generic shared margin algorithm obscuring these differences.

## Cell-by-cell teaching sequence

Use 17 cells: eight Markdown/code pairs below, followed by a final Markdown takeaway with references and the indicated next lesson. Each Markdown cell after an experiment explains the preceding output before introducing the next prediction. Target 10–15 minutes, 800–1,100 prose words; label any extensions optional.

| Cells | Markdown explanation / optional prediction | Executable content |
|---|---|---|
| 1–2 | Hedge versus cash need | Introduce short seller exposure, marked prices and eventual sale. |
| 3–4 | Direct futures variation | Show−7,200−7,200+14,400 and 19,400 peak including initial margin. |
| 5–6 | Full dated futures table | Restricted balance and settlement separately; return margin once. |
| 7–8 | Explorer | Cumulative funding; controls interim mark and initial margin. |
| 9–10 | Experiment: same endpoint different path | Compare flat 5 to 6/7/5; final result equal, liquidity different. |
| 11–12 | Experiment: OTC threshold | Separate illustrative OTC ledger, threshold 0 versus 5,000. |
| 13–14 | Experiment: delayed physical cash | Keep hedge settlement dates fixed, delay customer receipt. |
| 15–16 | Takeaway and capstone route | Include hedge funding in transaction liquidity; options/collateral electives remain optional. Display a compact decision summary from the already calculated results; introduce no new model. |
| 17 | Final interpretation, limitations, references and next step. | No diagnostics or hidden answers. |

All direct arithmetic precedes its packaged counterpart. One compact table and one main chart type; explorer controls update calculated outputs in one helper call with a static fallback. Keep experiments fixed independently of prior widget edits.

## Acceptance and implementation checks

Test variation telescoping, margin return, same final mark different peak, OTC transfers sum to zero after return, no double terminal payoff, threshold effects, long/short sign, no-margin path and extended customer lag.

Implement calculations and independent tests first, then education helpers, then notebook. Run the shared lint/type/test/schema/fresh-kernel checks, inspect local rendering and live control recovery, restore defaults and save outputs. Follow the complete checklist in [PLANNING.md](PLANNING.md); Colab remains deferred.

## Boundary with other lessons

M7 owns hedge-related liquidity, distinct from F6 collateral borrowing eligibility. It does not imply OTC contracts inherit exchange margin rules. E4 handles interest-rate hedge cash but reuses this module only if collateral is explicitly added.

## Sources and attribution

CME futures-margin materials inspected for performance-bond concept. Exact hypothetical margin/threshold amounts are not exchange requirements; primary contract/clearing specs required before a real-product example.

See the [source ledger](PLANNING.md#source-ledger) for inspected sources versus research still required. Place verified citations next to supported explanations; distinguish original inputs and derived results. No live data or new dependencies are required for the core lesson.

## Implementation and coherence review

Reviewed all eight subsection pairs and coherence with M2, M3, Notebook 2 and F6. Futures variation telescopes using M2 signed marked amounts; initial margin is a separate restricted-cash balance returned once. The OTC posting equation is explicitly a one-way posting obligation, clarifying the plan's previously ambiguous symmetry wording without changing its reference numbers. Collateral transfers are balance changes, with separate terminal settlement and no double payoff. The explorer holds endpoints fixed while changing interim price/margin. Flat-path and threshold experiments retain their different mechanics. Customer lag extends through month 5 and explicitly leaves the peak unchanged on this recovery path. Final summary introduces no new calculation; C1 remains planned and outside implementation scope. CME sources support only the general margin/settlement concepts, not the hypothetical amounts or compute-product availability.

430 repository tests passed, with seven pre-existing notebook-cell execution tests deselected. Direct M7 tests cover variation telescoping, long/short signs, initial-margin return, flat versus adverse interim paths, zero margin, OTC thresholds/transfers/terminal loss, sparse marks and invalid/overflow inputs. Headless presentation checks cover extended receipt dates, signed funding paths, precise margin initialization, independent interim-mark changes and invalid-edit recovery. Static notebook schema/AST checks, Ruff lint/format and strict mypy (19 source files) passed. No notebook cells were executed.

The user requested no notebook execution or repeated execution-permission prompts. Validation calls calculators and presentation helpers directly and checks notebook schema/syntax without executing cells. Fresh-kernel execution, saved runtime outputs and live Jupyter/Colab checks remain deferred. This is not a claim of full presentation verification.
