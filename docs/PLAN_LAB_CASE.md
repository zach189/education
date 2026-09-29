# Case study: can a training lab support a USD 500m GPU loan?

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](../notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

User-requested supplemental notebook: `notebooks/case_lab_gpu_financing.ipynb`.
This is not C1 and does not change the numbered curriculum. Read alongside F1,
F3, F4 and F8; the canonical roadmap remains `notebooks/README.md`.

## Scope and provenance

Use the supplied private discussion only as an unverified case prompt: USD 1bn
purchase, 50% advance and a 1.5% fee on debt. Anonymize counterparties. All other
inputs are explicit hypothetical assumptions. Do not repeat fundraising,
lender appetite, IG status or CoreWeave facility terms as verified facts.

Decision: minimum committed external capacity versus retained training capacity.
Monthly deterministic cash model: equipment ownership at time zero, external
cash settlement at month-end, explicit deployment delay and lost customer
payments, costs for training too, level-payment debt from F1 or an interest-only
balloon, a locked reserve funded separately, and retained operating surpluses.
No bridge, hedge pricing, lender recommendation or real transaction valuation.

## Ownership and presentation

`lab_financing` composes F1 loan schedules and F4 coverage/sizing conventions;
only case-specific capacity/cash integration and simple liquidation stress are
new. Rendering and independent optional controls live in `education`.
Show direct arithmetic, a sources-and-uses diagram, capacity stack, CFADS versus
debt service, rate/share heatmap, debt/liquidation curves, and downside bars.
A compact decision table reports off-take threshold, training capacity, modeled
loan limit, funding beyond equipment equity and stressed collateral recovery.

## Acceptance

Test independent cash examples, conservation of capacity/principal, delayed
operations, lost receipts, terminal balloon, nonfinite/type/range rejection,
funding retention and collateral assumptions; test charts headlessly. Validate
notebook schema and syntax only. No cell execution, saved generated outputs or
live presentation acceptance in this pass. Keep readable worked results in prose.

## Verification result

- 18 direct calculation/presentation tests passed; one additional notebook schema
  and syntax-only test passed. No notebook cell execution.
- Ruff lint/format passed for all 91 checked files; strict mypy passed (25 modules).
- Headless figures rendered; funding diagram and coverage heatmap visually inspected.
- Broader suite: 700 passed, 7 execution tests deliberately deselected, 5 failures
  in untouched F3/F4/F6/F7/F8 static tests that require empty outputs despite their
  existing saved outputs. Preserved those notebooks and tests.
- Execution, saved notebook plots and live widget presentation remain deferred.


## Ready presentation update — 2026-09-29

See the [Ready notebook review](READY_NOTEBOOK_REVIEW.md) for updated chart/control behavior, package boundaries, fresh-kernel outputs, automated checks, and live-check limitations. This update supersedes the historical execution deferrals above.
