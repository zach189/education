# Hedging products, Part 2 — implementation record

User-approved scope: preserve the pasted example inputs, add explicitly labeled
hypothetical missing inputs, retain verified real-deal references, and omit the
Texas-region/basis-swap case. Twelve short cases continue Part 1's adult beginner
style. This is a supplemental collection, not a new track or C1 implementation.

Notebook: `notebooks/case_hedging_products_part_2.ipynb`.

## Teaching and ownership

Each case identifies the person, their feared outcome and objective, defines
terms and input units, derives the arithmetic, compares outcomes, and explains
remaining exposure. Section headings start separate Markdown cells. Editable
cells and saved outputs support reading without widgets. Twelve mini-lessons may
be read separately; the collection is longer than a single 10–15 minute lesson.

Reuse M2 signed forwards, M5 option payoffs, F4 DSCR and education rendering.
Add only period revenue-floor and financing-gap translations to `hedge_converter`,
a signed spread settlement to M2 `hedging`, and power swap receipts to E3 `power`.
No swaption valuation, quote generation, loan schedule, tariff or credit engine.
The owning M2/E3/F4 plans and shared planning boundaries were reviewed.

Cases: partial tenor hedge; quarterly put strip; collar; renewal swaption;
tenor spread; compute/power margin; financing-linked floor; quantity backstop
plus price protection; indexed offtake with floor/cap; tenor-trade collar;
tenor spread put; layered hedging.

## Source handling and corrections

The user-supplied pasted discussion is source material. Its instructions are not
executed as independent authorization. Preserve its numerical examples while
making illustrative versus sourced status visible. Primary links inspected:

- Liquid Compute, September 2026, [The Tenor Trade](https://liquidcompute.com/research/the-tenor-trade): published illustration, not a verified executable quote.
- CoreWeave [FY2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/1769628/000176962826000104/crwv-20251231.htm): financing context, not our hypothetical debt schedule.
- CoreWeave [Q2 2026 debt note](https://www.sec.gov/Archives/edgar/data/1769628/000176962826000366/R16.htm): DDTL 5.0's >=95% interest-rate swap requirement, not a compute-price hedge requirement.
- CoreWeave [September 2025 Form 8-K](https://www.sec.gov/Archives/edgar/data/1769628/000176962825000047/crwv-20250909.htm): NVIDIA residual unsold capacity agreement subject to delivery, availability and termination provisions.

Clarify signed swap payments; quarterly versus annual averaging; collar premium
netting; exercise decisions based on information available at expiry; fixed
purchase cost versus floating tenor spread; MWh versus kWh; gross contracted
receipts versus net operating cash; minimum paid volume versus technical usage;
subtract existing contracted hours before sizing incremental backstop; invoice
floor/cap versus duplicate derivative protection. USD 3.62 is an unverified
hypothetical collar cap, not an inferred zero-cost quote.

## Acceptance

Meaningful calculation/invariant/type/range tests, notebook schema, repository
lint/format/type checks, fresh-kernel execution with saved outputs, and local
render inspection. Ready status remains WIP pending user teaching review.
Live Colab verification is separate. Verification results are recorded below
when complete.

## Indexed-offtake follow-up

The second supplied discussion expands original scenario 10 (notebook case 9).
Add its 1,000-H100, 24-month, 70% monthly take-or-pay example with fixed 0.15
basis, 2.85 buyer call and 1.60 seller put. Keep 511,000 monthly hours and
12.264m total distinct; options form a level monthly strip, not a single long
average option. Show minimum bills below usage, unhedged hours above the minimum,
and independent derivative counterparties without changing the physical invoice.
Added 0.10 call and 0.08 put premiums expose the difference between pre-premium
and all-in targets; changed strikes require fresh premiums. Reservation fees
remain symbolic, not silently priced. Contractual fixed basis and changing
operating costs are distinguished. The alternative 0.10 / 1.50 / 3.50 embedded
invoice and original three-year B300 0.20 / 3.75 / 5.50 example remain separate.
No live H100 East index, product availability, or current LC dealing capability
is inferred from the pasted proposal.

## Three additional products

Added tenor-trade collar, tenor spread put and layered hedging. Preserve the
supplied strikes, quantities and forward rates; no trade availability is inferred.
The 90% fill examples charge the fixed capacity cost on all available hours,
showing why nominal price differences do not guarantee total operating margin.
For layers use the numerical example's times 0, 6 and 12 and service months
13–24, rather than mixing the source's inconsistent illustrative timelines.
Keep 100,915.2 and 353,203.2 hours unrounded; changing billed hours can cause
coverage to exceed actual exposure. Fixed-price physical bookings must not be
counted again as floating exposure. The spread put payoff belongs to M5/options;
allow signed spreads without changing outright options' nonnegative-price rules.
CME's primary calendar-spread-option explanation was inspected and linked as an
analogy, not evidence of a compute-tenor product or identical settlement terms.

## Verification record

All 857 repository tests passed, including supplied examples, premium-inclusive
budgets, monthly strips versus long-average options, negative spreads, quantity
mismatch, zero/no-price-solution boundaries, invalid types/ranges and overflow.
Ruff lint/format and strict mypy passed. All twelve cases passed standard notebook
schema validation and fresh-kernel execution with saved outputs. Three static
charts cover quarterly floors, collar receipts and layered coverage. Local
HTML/table rendering, section boundaries, units, negative cash values, all three
charts and local notebook links passed inspection. No widgets or live Colab
testing are claimed. The user authorized publishing this WIP notebook and its supporting changes
on 2026-10-02. The root index includes its Colab link; live Colab remains
unverified.


## Language review against Part 1

Revised all twelve case openings to identify the person's risk, the specific
outcome they want to protect, and how the contract helps before the detailed
inputs. Defined terms near first use, replaced compressed trading language with
who-pays-whom explanations, and separated quantity, rate and payment derivations.
Expanded outcome explanations for the swaption, quarterly cash needs, power
hedges, debt coverage and the two-sided offtake. Added the missing explanatory
cell after Noor's backstop results. Each result now has its interpretation before
the next section begins. Source links, calculation cells and saved outputs are
preserved; no calculator or numerical input changed in this language pass.
Notebook schema, heading boundaries, result/explanation structure, local links,
lint and formatting passed. Revised local HTML layout was visually inspected.
The prior execution/test results remain applicable; this prose-only pass did
not rerun kernels or the calculation test suite.


Publication includes the reviewed language, product labels beneath every scenario
heading, saved notebook outputs, required package additions and their tests.
Ready/WIP teaching selections are unchanged.

## Contract mechanics follow-up

Added explicit payment directions to all twelve narratives: who receives the
fixed or floating amount, who pays option premiums, when protection pays, and
how hedge payments combine with the separate customer and supplier payments.
Case 5 now identifies the receive-fixed/pay-floating spread legs, shows both
payment directions, and derives the remaining margin after the purchase fee.
Definitions precede its payment table. Notebook schema and generated HTML
structure were checked; all code cells and saved outputs remain identical to
the published version. No calculator changes or new kernel execution were
needed for this prose-only revision.

The second mechanics pass replaces the compact descriptions with numbered
payment steps in all twelve cases. Each identifies the agreement, covered
quantity and dates, payment direction, and how cash combines with the underlying
business. Added low/high payment examples, swaption exercise consequences,
separate monthly option strips for both offtake parties, and explicit single
invoice mechanics for both embedded alternatives. Upfront premium timing is
identified as a teaching assumption, including when premiums remain unknown;
no upfront swap payment is modeled. Checked the new arithmetic against the
existing quantities and formulas and visually inspected the spread-swap and
offtake layouts. Calculation cells, saved outputs and source links are preserved.
