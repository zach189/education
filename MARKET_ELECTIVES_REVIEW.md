# Market-risk and elective implementation review

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

This records completion of the **source creation, individual coherence review and non-executing verification** requested for M1–M7 and E1–E6. The [canonical roadmap](notebooks/README.md) owns availability and prerequisites; [PLANNING.md](PLANNING.md) owns shared conventions and calculation boundaries. C1 remains planned and has no notebook implementation.

The user explicitly prohibited running notebooks. No cells were executed directly or indirectly during this pass. Fresh-kernel execution, saved runtime outputs, live Jupyter rendering/interactions and hosted Colab checks remain deferred. Passing headless rendering tests does not claim those checks were performed. Worked values and interpretations are included in Markdown so the lessons remain readable without their runtime outputs.

A subsequent [plain-language review](PLAIN_LANGUAGE_REVIEW.md) rewrote F1–F9 and M1–M7 explanations without changing code or outputs. Word counts and test totals below record the earlier implementation pass.

## Subsection coverage and coherence

Each notebook has 17 alternating cells: eight teaching/code pairs followed by interpretation, limitations and next step. Each has a decision and role, hypothetical inputs, visible arithmetic, corresponding reusable calculations, an independent explorer with editable fallback, fixed experiments with following interpretations, and a final summary that reuses existing results. Individual plans retain detailed post-implementation reviews.

| Lesson / record | Required subsections and experiments verified | Boundary with prior lessons |
|---|---|---|
| [M1](PLAN_04.md) | Revised: full first-year placement; capacity timeline; fee-adjusted contribution; full commitment and break-even hurdles; renewal, lower-price and placement-gap scenarios; interactive heatmap; three worked prediction exercises. | Actual supplier invoices remain distinct from implied blocks. Placement differs from technical utilization. No hardware proceeds or debt; gap counted once. See the updated M1 record. |
| [M2](PLAN_M2.md) | Physical versus financial contract; direct buyer payoff; price table; coverage explorer; seller sign; dated swap strip; half coverage; matching summary. | M1 operating exposure and M2 financial settlement remain separate. Same-date physical cash is combined once. |
| [M3](PLAN_M3.md) | Metadata mismatch; direct residual; shared settlement; basis/quantity explorer; provider basis; delivery-period basis; under/overhedging; checklist. | Reuses M2 signs and retains negative unmatched quantities; metadata comparison does not certify economic equivalence. |
| [M4](PLAN_M4.md) | Reseller scenario; direct fixed-cost economics; timing table; price/demand explorer; cancellation; separate overhedged buyer; delayed delivery; unweighted summary. | M1 contractual economics reused. Buyer cancellation does not cancel its financial hedge; delay retains supplier timing. |
| [M5](PLAN_M5.md) | Buyer cap/supplier floor; direct call/put; premium dates; strike/premium/call-put explorer; higher premium; half coverage; basis mismatch; payoff-versus-value summary. | M2 physical combination reused. Premium is paid once at inception; nominal totals are not PVs. |
| [M6](PLAN_M6.md) | Proxy assumptions; terminal payoffs; delta and cash replication; one/two-step tree and explorer; business probabilities; wider states; invalid tree; liquidity transition. | M5 payoff reused. Pricing weight is not a forecast. Two one-year steps change maturity to two years; no compute tradability is asserted. |
| [M7](PLAN_M7.md) | Short hedge; direct variation; restricted-cash ledger; interim-price/margin explorer; same endpoint/different path; separate OTC thresholds; delayed physical cash; funding summary. | M2 settlement reused. Futures variation is not paid twice; OTC posting is not expense. F6 lending collateral is a separate topic. |
| [E1](PLAN_E1.md) | Staged decision; underlying node values; compound value; fee explorer and realized cash; higher fee; zero fee; down-first path; optional return. | M6 tree/recursion reused. Node surplus is a value, not another cash receipt. No business-launch policy is inserted. |
| [E2](PLAN_E2.md) | Named guarantee payer; direct allocation; four contracts; guarantee/share explorer; participation endpoints; higher guarantee; per-hour versus fixed-total quantity terms; summary. | M5 payoff algebra reused; no fair-premium claim. This is bilateral revenue allocation, not F9's capital waterfall. |
| [E3](PLAN_E3.md) | Operator responsibility; W/kW/kWh arithmetic; contribution table; power/rate explorer; higher tariff; technical load; energy-only versus bill; summary. | Only foundation revenue is reused. No all-in rental expense is imported; technical load is independent of billed utilization. |
| [E4](PLAN_E4.md) | Interest-only debt terms; monthly arithmetic; dated charges/principal; rate/coverage explorer; higher reference; half hedge; loan-only floor; summary. | M2 difference engine adapted with explicit units/signs. Principal is separate and repaid once. F1 amortization and M7 collateral remain distinct. |
| [E5](PLAN_E5.md) | Synthetic dates/units; log changes; n−1 variance; highlighted window controls; pre-jump/recent windows; missing price; annualization assumptions; measurement summary. | Missing calendar pairs stay missing. Business scenarios and pricing inputs are not inferred. No actual market data is claimed. |
| [E6](PLAN_E6.md) | Customer/useful-task unit; direct spend/efficiency; weighted mix; demand/share explorer; efficiency only; volume growth; ordered mix decomposition; budget/unit-cost summary. | Consumed hours differ from committed rent. Useful outputs differ from tokens, billing utilization and power draw. No hardware or quality benchmark is asserted. |

## Calculation and source checks

- Pure typed modules contain the calculation logic. Presentation dependencies remain optional and lazy; `pyproject.toml` has no runtime dependencies and targets the existing Python 3.10 environment.
- Independent examples, invalid types/ranges/nonfinite values, overflow, boundaries, dates, signed losses, conservation and relevant zero cases are covered in calculation tests. Plot tests call these calculators and rendering helpers directly, then inspect chart values/labels and render canvases.
- Common explorers snapshot inputs. Tests cover initial precision, state independence, invalid-edit replacement/recovery and widget-free rendering. E5 additionally checks highlighted date windows and missing-price gaps; E6 checks separate units and N/A at zero tasks.
- Source ledger gates were inspected before claims were added: CME for general settlement/margin/basis concepts; OIC for option payoff terminology; MIT's authored derivation for replication; EIA for delivered electricity versus energy components; New York Fed for the SOFR definition only; NIST for sample standard deviation.
- The original Geske paper could not be retrieved. E1 discloses this and derives its finite-tree example from M6 rather than claiming a reproduction of the continuous-time formula. NYU's authored chapter supports terminology only.
- All quantities, prices, rates, premiums, thresholds, equipment loads, probabilities and observations in the worked examples remain hypothetical. Optional real-data/real-performance appendices are omitted because they are not required and their provenance gates have not been satisfied.

## Verification scope

The test suite statically checks the exact thirteen-file inventory, notebook schema/17-cell structure, syntax, imported package symbols and direct-call keyword signatures. It checks local README/plan links and review records. These are structural checks, not a substitute for the per-subsection reviews above or eventual kernel execution.

Final checks: **561 tests passed, seven execution tests deselected**; Ruff lint and formatting passed across source, tests, scripts and notebooks; strict mypy passed for all 24 source files. All thirteen requested notebooks are present, with 17 cells each and 788–909 prose words. The seven pre-existing tests that execute notebook arithmetic are deliberately excluded using `-k 'not notebook_arithmetic and not visible_arithmetic'`; all other tests remain enabled. The source-writing scripts create notebook JSON only and do not evaluate notebook cells.

## Subsequent M3 revision

The original M3 subsection inventory above is superseded by the [focused basis-risk revision](PLAN_M3.md). The user explicitly authorized M3 execution: its fresh-kernel check passed and baseline outputs are saved. Quantity/time mismatch experiments were removed from M3 teaching while existing reusable APIs remain intact. See the [canonical roadmap](notebooks/README.md) for current per-lesson verification; the historical no-run audit above remains a record of its original pass.

## Subsequent M1 article-alignment revision

The [current M1 record](PLAN_04.md) supersedes the earlier subsection inventory: the lesson now shows the attributed published tenor-price curve and models 36 repeated monthly sales, fill break-even, upfront cash and a partial seller hedge. The prior contracted-first-year framing was removed. See the [canonical roadmap](notebooks/README.md) for current validation.
