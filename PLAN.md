# Notebook 1 implementation plan

> Status update (2026-09-29): all existing notebooks now have saved outputs from successful local fresh-kernel execution, with Colab setup cells and links. Earlier execution deferrals below are historical. Live Colab interaction remains unverified. See the [canonical roadmap](notebooks/README.md) for Ready/WIP status and prerequisites. C1 remains planned.

## Curriculum context

This is the implementation record for foundation Notebook 1; its settled calculations remain unchanged. The [canonical roadmap](notebooks/README.md) now organizes an independent Liquid Compute curriculum into a shared foundation, financing and market-risk tracks, electives, and an original transaction capstone. Financing can begin after Notebook 2; Notebook 3 prepares readers for Notebook 4 / M1, the tenor trade. See [PLAN_03.md](PLAN_03.md) for the third foundation lesson.

Working title: **The Compute Business: Capacity, Utilization, and Profit**.

Status: notebook 1 implemented locally. Package tests, lint, formatting, type checking, fresh-kernel execution, and local browser interaction checks passed. Colab work is deferred until the series is complete, per the user’s instruction. Project-wide requirements are in `AGENTS.md`. This plan includes the accepted presentation refactor: calculation functions remain dependency-free, while optional rendering helpers live in `liquid_compute.education`. Notebooks retain visible arithmetic and teaching content. Configuration lives in `pyproject.toml`.

## Learning experience

Create a 10–15 minute lesson for readers comfortable with basic Python but new to compute financing. Follow one operator that rents GPUs at a fixed price and bills a customer for consumed GPU-hours. Readers calculate the business economics by hand in code, then use a reusable function to explore assumptions.

Learning goals: translate capacity into purchased and billed GPU-hours; calculate revenue, expense, and contribution profit; derive break-even utilization; explain why a positive selling/rental price spread does not guarantee profit.

All rented hours incur expense, including unused hours. Assume identical GPUs, full availability, and all consumed hours billed. Exclude resale, usage beyond capacity, ancillary operating expenses, taxes, financing, and derivatives. Billed utilization is not hardware processor activity.

Call revenue minus rental expense **contribution profit**, a simplified contribution margin before excluded costs. Explain that this is the lesson's defined measure, not the conventional revenue-minus-variable-costs definition: the committed rental expense is fixed as utilization changes. Distinguish dollar profit from percentage margin.

## Hypothetical example and equations

These are teaching assumptions, not market quotes:

| Input | Default | Unit |
| --- | ---: | --- |
| `gpu_count` | 10 | GPUs |
| `hours_per_month` | 720 | hours per GPU in a 30-day illustrative month |
| `rental_usd_per_gpu_hour` | 2.00 | USD per purchased GPU-hour |
| `customer_usd_per_gpu_hour` | 4.00 | USD per billed GPU-hour |
| `utilization_fraction` | 0.75 | billed / purchased GPU-hours |

For N GPUs, H hours, rental rate c, customer rate p, and utilization u:

- Purchased GPU-hours Q = N × H.
- Billed GPU-hours B = Q × u; unused GPU-hours = Q − B.
- Revenue R = B × p; rental expense C = Q × c.
- Contribution profit P = R − C = N × H × (u × p − c).
- Break-even utilization = c / p.
- Contribution margin fraction = P / R when R > 0; otherwise undefined. Multiply by 100 only for percentage display.

Defaults yield 7,200 purchased, 5,400 billed, and 1,800 unused GPU-hours; $21,600 revenue; $14,400 rental expense; $7,200 contribution profit; 33.33% margin; and 50% break-even. Round only for display.

## Reusable package and interfaces

Use a `src/liquid_compute/` package with an `economics.py` module and explicit calculation exports from `__init__.py`. Calculations use only the standard library. The separate `education.py` module lazily imports optional display dependencies when helpers are called; it is not imported from `__init__.py`.

Implement only two public pure calculation functions initially:

```python
def break_even_utilization_fraction(
    *, rental_usd_per_gpu_hour: float, customer_usd_per_gpu_hour: float
) -> float: ...

def compute_monthly_economics(
    *, gpu_count: int, hours_per_month: float,
    rental_usd_per_gpu_hour: float, customer_usd_per_gpu_hour: float,
    utilization_fraction: float,
) -> MonthlyEconomics: ...
```

Use a frozen, fully annotated `MonthlyEconomics` dataclass with float fields `purchased_gpu_hours`, `billed_gpu_hours`, `unused_gpu_hours`, `revenue_usd`, `rental_expense_usd`, `contribution_profit_usd`, `break_even_utilization_fraction`, and `contribution_margin_fraction: float | None`. Docstrings identify the one-month period, unit conventions, assumptions, return values, and exceptions. Do not introduce an input dataclass or a general valuation interface yet.

Validate `gpu_count` as a positive Python integer, excluding bool. Other inputs accept Python int/float values, excluding bool, and must be finite. Hours and both prices must be positive; utilization must lie in [0, 1]. Wrong types raise `TypeError`; invalid values raise `ValueError`. Guard nonfinite calculated results from numeric overflow with `ValueError`. Type annotations do not enforce units; document that callers supply the declared units.

Break-even above 1 is a valid result, not an input error. Zero revenue produces `None` for the margin, displayed as N/A. Zero-price or zero-capacity contracts are outside this first lesson's domain and receive clear validation errors.

These functions calculate amounts implied by hypothetical contract terms and realized billed utilization. They do not discount cash flows, forecast demand, determine payment dates, or estimate fair value. Later lessons can add distinct cash-flow and valuation modules when actually needed.

## Presentation helpers

`liquid_compute.education` provides `show_monthly_results(result) -> None`, `plot_profit_by_utilization(**five_named_inputs) -> Figure`, and `explore_monthly_economics(**five_named_inputs) -> VBox | None`. Both latter functions have explicit, fully annotated keyword-only inputs matching `compute_monthly_economics`. The explorer owns its controls, chart, and table and preserves the exact initial utilization fraction. Static display does not require widgets. All optional imports are deferred to function calls.

Move direct-versus-package consistency checks into tests. Keep all diagnostic assertions and automated boundary checks in the test suite, outside the educational notebook. Experiments use computed results and retain their saved outputs, per the user’s preference for reading like a book. Prediction prompts are optional. Baseline table and chart outputs also remain saved.

## Cell-by-cell notebook outline

Keep prose around 700–900 words, excluding references. Notebook presentation cells call the helpers directly; the longer rendering mechanics live in the education module.

| Cell | Type | Purpose |
| --- | --- | --- |
| 1 | Markdown | Title, estimated time, context, goals, setup pointer, exclusions, and AWS citation for an example of charges on unused reserved capacity. |
| 2 | Code | Imports and five labeled editable assumptions. No automatic installation or external data fetch. |
| 3 | Markdown | Define GPUs versus GPU-hours, billed utilization, and the 30 × 24 hours convention. Show the small worked example. |
| 4 | Code | Direct, visible arithmetic for hours, revenue, expense, profit, margin, and break-even. No packaged calculation call yet. |
| 5 | Markdown | Explain profit versus percentage margin and the lesson-specific contribution terminology. Introduce the reusable function as the same arithmetic with validation. |
| 6 | Code | Call `compute_monthly_economics` using the assumptions; show a compact Markdown results table with explicit units. |
| 7 | Markdown | Derive break-even from revenue = expense; explain why rates alone do not determine profit. Cite the break-even source. |
| 8 | Code | One helper call displaying the static chart: profit versus utilization over 0–100%, zero-profit line, current point, and feasible break-even marker. |
| 9 | Markdown | Explain controls and fallback: edit assumptions and rerun subsequent cells. Widget values do not overwrite baseline assumptions. |
| 10 | Interactive code | One helper call displaying an independent explorer with controls, chart, and results together. |
| 11 | Markdown | Predict: does the positive $4 versus $2 spread still produce profit at 25% utilization? |
| 12 | Code | Independent scenario inputs; display computed results and retain saved outputs for reading. |
| 13 | Markdown | Explain why billing only 25% of rented hours loses money despite a positive price spread. |
| 14 | Markdown | Predict: double GPUs while holding utilization at 75%. Does break-even change? State that billed demand doubles under this assumption. |
| 15 | Code | Compare 10 and 20 GPUs: profit doubles to $14,400; break-even and margin percentage are unchanged. |
| 16 | Markdown | Explain why scaling at fixed utilization changes dollar amounts but not margin or break-even; emphasize the demand assumption. |
| 17 | Markdown | Predict: can full utilization rescue $5 rental against $4 customer pricing? |
| 18 | Code | Show 125% break-even and a $7,200 loss at full utilization. |
| 19 | Markdown | Explain the full-utilization loss, infeasible 125% threshold, and need to change prices or terms. |
| 20 | Markdown | Takeaway, limitations, and linked references. Finish with the next problem: a profitable contract may require cash before the customer pays; how much funding is needed, and for how long? |

The chart uses 101 utilization points, clear axis units, and labels that do not depend on color. Keep the x-axis within 0–100%; annotate break-even above 100% as infeasible rather than extending capacity. Use Python lists rather than importing NumPy directly.

Use a fraction-valued floating-point utilization slider, displaying percentages and preserving the exact initial fraction. Dragging moves in one-percentage-point steps. Other controls accept numeric edits and show runtime validation errors. Disable continuous slider updates, close replaced figures, and replace stale outputs with a corrective message on invalid input. A missing widget import gives a short fallback message; the static chart and editable cells still work. Do not rely on detecting frontend rendering failures automatically.

## Sources and claims

- [AWS Capacity Reservation pricing and billing](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/capacity-reservations-pricing-billing.html): supports a specific industry example of charges on unused reserved capacity. Do not generalize to all GPU rental contracts.
- [OpenStax break-even analysis](https://openstax.org/books/principles-managerial-accounting/pages/3-2-calculate-a-break-even-point-in-units-and-dollars): supports revenue equaling modeled costs at break-even and the effect of sales volume on recovery of committed costs.
- [OpenStax contribution margin](https://openstax.org/books/principles-managerial-accounting/pages/3-1-explain-contribution-margin-and-calculate-contribution-margin-per-unit-contribution-margin-ratio-and-total-contribution-margin): supports the conventional terminology and distinction between dollar contribution and a ratio.
- [Jupyter Widgets installation](https://ipywidgets.readthedocs.io/en/stable/user_install.html): supports setup and frontend troubleshooting guidance.

These sources were inspected during planning. Put citations beside the relevant explanations and in a short references list. Arithmetic and explicitly hypothetical inputs do not require citations. Colab widget compatibility will be verified after the series is complete; it is not an acceptance requirement for notebook 1 now.

## Files, tooling, and implementation order

Planned structure:

```text
AGENTS.md
PLAN.md
README.md
pyproject.toml
src/liquid_compute/__init__.py
src/liquid_compute/economics.py
src/liquid_compute/education.py
scripts/validate_notebook.py
notebooks/01_compute_business.ipynb
tests/test_economics.py
tests/test_education.py
```

Use setuptools packaging, project name `liquid-compute`, Python >=3.10, and a `py.typed` marker included in package data. Fully annotate public functions and configure mypy strict checking for `src/liquid_compute`; use pytest for calculations and Ruff for package, tests, and notebook code. Configure Ruff for Python 3.10 with E4/E7/E9/F/I/UP rules and its formatter. Keep documentation examples compatible with Python 3.10 rather than newer-only type syntax.

Declare no runtime dependencies. Add a `notebook` optional dependency group containing matplotlib, ipywidgets, IPython, ipykernel, and JupyterLab; add a `dev` group containing pytest, Ruff, mypy, nbformat, and nbclient. All are missing from the current environment. Install with the existing `.venv` interpreter using an editable install of `.[notebook,dev]`. Set compatible dependency ranges based on versions verified in Python 3.10, and record tested versions in README. Do not create a competing requirements file.

1. Configure packaging and tools; install into the existing `.venv` only.
2. Implement the two functions, immutable result dataclass, runtime validation, and meaningful pytest tests.
3. Build the lesson with visible arithmetic first, then packaged calls; keep displayed content in the notebook and rendering mechanics in the education module.
4. Run Ruff, mypy, pytest, notebook format validation, and fresh-kernel execution using the existing environment's Python kernel.
5. Inspect local Jupyter display and widget updates. Save baseline outputs so the lesson remains readable without widgets.
6. A wheel has been built with the existing environment. Defer the following Colab setup documentation until the series is complete: upload that wheel, install it into the Colab runtime, then upload/run the same notebook. This removes the need for a published package or a hard-coded repository URL. The notebook must not embed a local path, duplicate the package as a fallback, or depend on external data. Explain that Colab provides a separate hosted runtime; do not create another local virtual environment.
7. Defer Colab setup and smoke testing until the series is complete. Document local launch, fallback, tests, and the tested tool versions in README. A wheel was already built locally, but hosted execution has not been verified.

## Acceptance checklist

- [x] Existing `.venv` reused; package installs and imports outside the repository working directory without `sys.path` modifications.
- [x] Pure, fully annotated, documented calculation functions with explicit units; optional education helpers do not add runtime dependencies or eager presentation imports.
- [x] Visible notebook arithmetic matches packaged outputs before rounding.
- [x] Default scenario matches all expected values listed above.
- [x] Zero utilization: $0 revenue, -$14,400 profit, and undefined percentage margin.
- [x] Full utilization: $14,400 profit; 50% utilization: approximately zero profit.
- [x] Equal prices give 100% break-even; $5/$4 pricing gives 125% break-even and losses across feasible utilization.
- [x] Purchased hours equal billed plus unused hours; rental expense stays fixed when only utilization changes.
- [x] Doubling capacity at constant utilization doubles monetary amounts without changing break-even or percentage margin.
- [x] Parameterized tests cover invalid types, bool, NaN/infinity, zero/negative capacity/hours/prices, out-of-range utilization, and numeric overflow.
- [x] Ruff, mypy, pytest, notebook format validation, and fresh-kernel execution pass. Tests assert independent expected values and contractual invariants, not a copy of the implementation.
- [x] Local widget changes agree with direct function calls; editable-cell fallback remains complete. Colab is explicitly deferred.
- [x] No absolute paths or external data dependencies in the lesson; setup instructions explain the reusable package requirement.
- [x] Lesson is designed for 10–15 minutes; assumptions, units, sourced claims, model limitations, and cash-flow timing transition are present. Actual learner timing has not been measured.
