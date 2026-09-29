# E1: Compound Options and Staged Protection Purchases — implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Created/tested; optional elective. Coherence reviewed; execution/live acceptance deferred by user instruction. **Prerequisites:** M6 and 2.
**Notebook:** [notebooks/E1_compound_options.ipynb](notebooks/E1_compound_options.ipynb).

Read the [canonical roadmap](notebooks/README.md), [shared planning conventions](PLANNING.md), and [project guidance](AGENTS.md). Foundation plans remain implementation records; this document specifies only the new lesson or unfinished work.

## Learning decision, assumptions, and worked example

All numeric contract terms and scenarios below are hypothetical teaching assumptions, not market quotes.

Optional question: what is the value of paying now for the right to purchase protection later? Use M6's idealized proxy, not the article's customer story. S0=5, up 1.2/down 0.8 per one-year step, effective annual rate 5%, final strike 5 at t=2. At t=1 pay exercise feeX=0.5 per unit only if buying the underlying t=2 call is worthwhile. Compound call pays max(V_call(t=1)−X,0) at t=1 in valuation terms; actual cash is −X on exercise then the underlying call payoff at t=2. Initial compound premium is its model value, not zero.

Use M6 risk-neutral q=.625. Up node underlying-call value=(.625·2.2)/1.05=1.3095238; down node=0. Compound premium=.625·(1.3095238−.5)/1.05=0.4818594 per unit. Immediate underlying call model value=.7794785. Lower initial cash for staged protection is not free protection: it adds contingent exercise payment and can forgo protection on some paths.

Keep model value comparison separate from realized cash by path and from a business launch decision. A launch/no-launch flag may illustrate whether protection is useful, but it does not change financial exercise value unless a separate business-constrained exercise policy is clearly labeled. No multi-layer compound tree or American option.

## Reusable calculations and interfaces

Extend `option_valuation` with `compound_call_value` consuming the existing two-step tree and an intermediate exercise fee; return node option values, exercise policy and premium. Extend `options` with `staged_option_cash_flows` only for realized path cash. Preserve the two ledgers: valuation node max(V−X,0) is not an extra cash receipt. Reuse M6 recursion rather than reimplement pricing. Validate exercise occurs strictly before final expiry, nonnegative fee, valid tree and consistent dates.

## Cell-by-cell teaching sequence

Use 17 cells: eight Markdown/code pairs below, followed by a final Markdown takeaway with references and the indicated next lesson. Each Markdown cell after an experiment explains the preceding output before introducing the next prediction. Target 10–15 minutes, 800–1,100 prose words; label any extensions optional.

| Cells | Markdown explanation / optional prediction | Executable content |
|---|---|---|
| 1–2 | Staged protection decision | Contrast premium now, exercise purchase later, final payoff. |
| 3–4 | Visible underlying node values | Compute up/down call values from M6 terminal payoffs. |
| 5–6 | Direct compound valuation | max(V−.5,0), discounted expectation, then shared helper. |
| 7–8 | Explorer | Two-step cash/tree view; control exercise fee. |
| 9–10 | Experiment: fee rises | Lower initial compound value, more expensive/less frequent later exercise. |
| 11–12 | Experiment: fee zero | Compound becomes the underlying call under this model; verify equality. |
| 13–14 | Experiment: realized down path | No exercise, initial premium still lost; compare immediate protection. |
| 15–16 | Takeaway | Optional staged contract, not a prerequisite for C1; return to core track. Display a compact decision summary from the already calculated results; introduce no new model. |
| 17 | Final interpretation, limitations, references and next step. | No diagnostics or hidden answers. |

All direct arithmetic precedes its packaged counterpart. One compact table and one main chart type; explorer controls update calculated outputs in one helper call with a static fallback. Keep experiments fixed independently of prior widget edits.

## Acceptance and implementation checks

Test .4818594 premium, .7794785 underlying value, zero-fee equivalence, prohibit double counting node value as cash, never exercise when value below fee, terminal path cash and valid exercise dates. Business probability never replaces pricing weight.

Implement calculations and independent tests first, then education helpers, then notebook. Run the shared lint/type/test/schema/fresh-kernel checks, inspect local rendering and live control recovery, restore defaults and save outputs. Follow the complete checklist in [PLANNING.md](PLANNING.md); Colab remains deferred.

## Boundary with other lessons

E1 adds one intermediate protection-purchase decision to M6. It does not revisit basic call payoff or model a construction draw (F5). Compound options stay optional and are not the capstone’s organizing structure.

## Sources and attribution

Inspect original compound-option research (Geske) or an accessible primary derivation before attribution. The source post is optional context only, not the required scenario; disclose any inaccessible research gap instead of copying unsupported results.

See the [source ledger](PLANNING.md#source-ledger) for inspected sources versus research still required. Place verified citations next to supported explanations; distinguish original inputs and derived results. No live data or new dependencies are required for the core lesson.

## Implementation and coherence review

Reviewed all eight subsections against E1 and M6. The same two-step proxy tree and pricing weight produce underlying node values, exercise surplus and initial premium; no second tree engine or business-probability input exists. Actual path cash contains only initial premium, exercised purchase fee and final owned-call payoff. Equality chooses no exercise, with no economic difference in the model. Fee increase, zero-fee equivalence and down-first cancellation use independent inputs. Year/month mapping is explicit (1/12 and 2/24); all amounts are per normalized proxy unit, not inferred GPU-hours. No launch policy or financing draw is inserted. E1 stays optional with a return to M7 and transition to E2. The original Geske retrieval failed; the notebook discloses this and derives the binomial example directly. NYU's accessible author-written chapter supports compound-option terminology only, not a claimed reproduction of the continuous-time formula.

33 targeted compound-option and market-presentation tests passed. Independent checks cover reference premiums/node values, zero-fee equivalence, fee monotonicity, strict exercise policy, realized paths, pricing-weighted discounted cash conservation, invalid dates/types/ranges, no intermediate-value cash receipt, static schema/AST checks, chart dates and fee-control recovery. Ruff lint/format and strict mypy passed. No notebook cells were run.

The user requested no notebook execution or repeated execution-permission prompts. Validation calls calculators and presentation helpers directly and checks notebook schema/syntax without executing cells. Fresh-kernel execution, saved runtime outputs and live Jupyter/Colab checks remain deferred. This is not a claim of full presentation verification.
