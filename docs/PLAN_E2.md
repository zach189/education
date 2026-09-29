# E2: Minimum Revenue with Shared Upside — implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](../notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

**Status:** Created/tested; optional elective. Coherence reviewed; execution/live acceptance deferred by user instruction. **Prerequisites:** M5.
**Notebook:** [notebooks/E2_minimum_revenue_shared_upside.ipynb](../notebooks/E2_minimum_revenue_shared_upside.ipynb).

Read the [canonical roadmap](../notebooks/README.md), [shared planning conventions](PLANNING.md), and [project guidance](../AGENTS.md). Foundation plans remain implementation records; this document specifies only the new lesson or unfinished work.

## Learning decision, assumptions, and worked example

All numeric contract terms and scenarios below are hypothetical teaching assumptions, not market quotes.

Optional question: how can a buyer and compute supplier divide downside protection and upside? One period,7,200 GPU-hours, reference revenue R=Q·S. Compare spot receiptsR, fixed receiptsQ·5, and a hypothetical guarantee with upside sharing: supplier receiptG+alpha·max(R−G,0), whereG=Q·4 and alpha=.5. At S=3,5,7 supplier receipts 28,800/32,400/39,600. Counterparty's net payoff=R−supplier receipt, so it funds the downside and retains some upside.

This is an assumed bilateral revenue agreement, not an automatically enforceable minimum price or free put. The payer promises the guarantee; no separate premium in baseline because the commercial concession is retained upside, not a claim of fair economic equivalence. Show payoff algebra supplier G+alpha·call_on_R(G); contrast with full floor max(R, G). Settlement month 12, same delivered quantity in core; no collateral, defaults or valuation.

Experiment with alpha 0/0.5/1, guarantee rate 3/4/5, and lower delivered quantity. For quantity experiment explicitly keep guarantee specified as per-delivered-hour unless the user selects the separate fixed-total guarantee example; compare the obligations without silently changing terms.

## Reusable calculations and interfaces

Add `revenue_sharing` with `minimum_revenue_share_usd(reference_revenue_usd, guaranteed_revenue_usd, supplier_upside_fraction)` returning supplier/counterparty allocation. A small wrapper converts explicit delivered hours and guarantee rate to totalG. Reuse M5 payoff for optional decomposition, not pricing. Accept finite nonnegativeR/G and alpha[0,1]; counterparty payout may be negative. No separate waterfall priority or counterparty credit model.

## Cell-by-cell teaching sequence

Use 17 cells: eight Markdown/code pairs below, followed by a final Markdown takeaway with references and the indicated next lesson. Each Markdown cell after an experiment explains the preceding output before introducing the next prediction. Target 10–15 minutes, 800–1,100 prose words; label any extensions optional.

| Cells | Markdown explanation / optional prediction | Executable content |
|---|---|---|
| 1–2 | Commercial sharing decision | Name who guarantees, who receives, and which upside is surrendered. |
| 3–4 | Direct allocation | Work S=3 and 7 and reconcile supplier plus counterparty toR. |
| 5–6 | Contract comparison table | Spot, fixed, full floor and shared-upside receipts. |
| 7–8 | Explorer | Receipt-versus-price chart; controls guarantee and upside share. |
| 9–10 | Experiment: upside fraction | 0/0.5/1 interpolates fixed guarantee to full floor. |
| 11–12 | Experiment: higher guarantee | Shows greater payer downside, not guaranteed fair trade. |
| 13–14 | Experiment: delivered quantity | Separate per-hour guarantee from a fixed-total commitment. |
| 15–16 | Takeaway | A payoff allocation is not a valuation; optional C1 structure only. Display a compact decision summary from the already calculated results; introduce no new model. |
| 17 | Final interpretation, limitations, references and next step. | No diagnostics or hidden answers. |

All direct arithmetic precedes its packaged counterpart. One compact table and one main chart type; explorer controls update calculated outputs in one helper call with a static fallback. Keep experiments fixed independently of prior widget edits.

## Acceptance and implementation checks

Test reference values, conservation supplier+counterparty=R, signed downside payer cash, alpha endpoints, zero quantity and distinct fixed-total/per-hour guarantee. Do not label guarantee market value without a pricing model.

Implement calculations and independent tests first, then education helpers, then notebook. Run the shared lint/type/test/schema/fresh-kernel checks, inspect local rendering and live control recovery, restore defaults and save outputs. Follow the complete checklist in [PLANNING.md](PLANNING.md); Colab remains deferred.

## Boundary with other lessons

E2 concerns bilateral operating revenue sharing. F9 concerns priority among expenses/debt/reserves/equity. M5 teaches floor payoffs; E2 reuses them but does not repeat call/put premium lessons.

## Sources and attribution

OIC payoff concepts as background. Any shipping or compute profit-sharing commercial example requires inspected primary agreement; no such facility terms are assumed in this original model.

See the [source ledger](PLANNING.md#source-ledger) for inspected sources versus research still required. Place verified citations next to supported explanations; distinguish original inputs and derived results. No live data or new dependencies are required for the core lesson.

## Implementation and coherence review

Reviewed all eight subsections against the spec and M5/F9 boundaries. Names the guarantee payer and supplier, shows direct low/high-state conservation before helpers, and distinguishes a fixed USD 5/hour comparator from alpha=0 at the USD 4/hour guarantee. Full floor and shared participation remain separate agreements. M5 payoff decomposition explicitly uses one normalized revenue claim, not an asserted GPU-hour option quote. Alpha endpoints, higher guarantees and lower delivery are independently calculated; per-delivered-hour versus unconditional fixed-total terms remain explicit, including zero delivery. Counterparty losses are retained in tables and charts. No fair-premium, creditworthiness or capital-structure waterfall claim is added; final summary only reuses baseline results.

471 repository tests passed, with seven pre-existing notebook-cell execution tests deselected. E2 tests cover independent reference allocations, conservation, signed payer loss, alpha endpoints, distinct quantity guarantees, invalid inputs and overflow. Headless chart/control checks retain negative values, react to share endpoints and recover from invalid fractions; notebook schema/AST checks passed without execution. Ruff lint/format and strict mypy passed for 20 source files.

The user requested no notebook execution or repeated execution-permission prompts. Validation calls calculators and presentation helpers directly and checks notebook schema/syntax without executing cells. Fresh-kernel execution, saved runtime outputs and live Jupyter/Colab checks remain deferred. This is not a claim of full presentation verification.
