"""Direct helper checks only: never execute educational notebook cells."""

from dataclasses import replace

import matplotlib
import pytest

from liquid_compute.lab_financing import (
    LabInputs,
    liquidation_stress,
    minimum_contract_fraction,
    model_lab,
)

matplotlib.use("Agg")


def test_independent_baseline_and_conservation():
    p = LabInputs()
    r = model_lab(p)
    row = r.months[0]
    assert row.external_receipts_usd == pytest.approx(39_398_400)
    assert row.operating_cost_usd == pytest.approx(14_819_520)
    assert row.cfads_usd == pytest.approx(24_578_880)
    payment = 500e6 * (0.17 / 12) / (1 - (1 + 0.17 / 12) ** -60)
    assert row.debt_service_usd == pytest.approx(payment)
    assert r.fee_usd == 7.5e6
    assert r.reserve_usd == pytest.approx(3 * payment)
    assert r.operating_buffer_usd == 0
    assert sum(x.principal_repayment_usd for x in r.loan) == pytest.approx(500e6)
    for m in r.months:
        assert sum(
            (
                m.training_gpu_hours,
                m.contracted_gpu_hours,
                m.spot_gpu_hours,
                m.unsold_gpu_hours,
            )
        ) == pytest.approx(21_888_000)


def test_threshold_and_capacity_are_binding():
    p = LabInputs()
    threshold = minimum_contract_fraction(p)
    assert threshold == pytest.approx(0.24693083736829813)
    assert model_lab(
        replace(p, contracted_fraction=threshold)
    ).minimum_dscr == pytest.approx(1.25)
    r = model_lab(p)
    sized = model_lab(
        replace(p, advance_fraction=r.supportable_loan_usd / p.equipment_usd)
    )
    assert sized.minimum_dscr == pytest.approx(1.25)
    assert (
        minimum_contract_fraction(
            replace(p, training_fraction=0.9, contracted_fraction=0.1)
        )
        is None
    )


def test_delay_needs_cash_and_support_is_not_cfads():
    p = replace(LabInputs(), deployment_delay_months=6)
    r = model_lab(p)
    assert r.operating_buffer_usd == pytest.approx(
        6 * (3e6 + r.months[0].debt_service_usd)
    )
    assert r.supportable_loan_usd == 0
    assert minimum_contract_fraction(p) is None
    supported = model_lab(replace(p, support_cash_usd=10e6))
    assert supported.uncovered_cash_usd == pytest.approx(r.operating_buffer_usd - 10e6)
    assert supported.minimum_dscr == r.minimum_dscr
    assert all(m.training_gpu_hours == 0 for m in r.months[:6])


def test_retained_surpluses_cover_later_losses_but_not_coverage():
    p = replace(LabInputs(), interruption_months=3)
    r = model_lab(p)
    assert r.minimum_dscr < 0
    assert r.operating_buffer_usd == 0
    assert r.months[12].external_receipts_usd == pytest.approx(4_377_600)
    assert r.months[15].external_receipts_usd == r.months[0].external_receipts_usd


def test_balloon_is_counted_and_zero_rate_zero_debt_work():
    r = model_lab(replace(LabInputs(), repayment="balloon"))
    assert r.months[-1].debt_service_usd == pytest.approx(500e6 + 500e6 * 0.17 / 12)
    assert r.months[-2].closing_debt_usd == 500e6
    assert r.months[-1].closing_debt_usd == 0
    assert r.minimum_dscr < 0.05
    zero = model_lab(replace(LabInputs(), repayment="balloon", nominal_annual_rate=0))
    assert zero.months[-1].debt_service_usd == 500e6
    assert model_lab(replace(LabInputs(), advance_fraction=0)).minimum_dscr is None


def test_collateral_age_delay_costs_and_claim():
    p = replace(LabInputs(), repayment="balloon")
    sale, claim, recovery = liquidation_stress(p, default_month=24)
    assert sale == pytest.approx(1e9 * 0.65**2.5 * 0.75 * 0.9)
    assert claim == pytest.approx(500e6 * 1.085)
    assert recovery == min(sale, claim)
    assert liquidation_stress(p, default_month=60)[2] == 0
    with pytest.raises(ValueError):
        liquidation_stress(p, default_month=61)


@pytest.mark.parametrize(
    "field,value,error",
    [
        ("gpu_count", True, TypeError),
        ("term_months", 1.5, TypeError),
        ("spot_usd_per_gpu_hour", float("nan"), ValueError),
        ("equipment_usd", float("inf"), ValueError),
        ("training_fraction", 1.1, ValueError),
        ("training_fraction", 0.8, ValueError),
        ("minimum_dscr", 0.9, ValueError),
        ("support_cash_usd", -1, ValueError),
        ("repayment", "other", ValueError),
        ("hours_per_month", "720", TypeError),
        ("contract_usd_per_gpu_hour", 1e308, ValueError),
    ],
)
def test_invalid_inputs(field, value, error):
    with pytest.raises(error):
        model_lab(replace(LabInputs(), **{field: value}))


def test_all_plot_views_and_independent_control():
    from liquid_compute.education import (
        lab_training_explorer,
        plot_lab_case,
        plot_lab_scenarios,
    )

    p = replace(LabInputs(), training_fraction=0.401234)
    for view in ("structure", "capacity", "cash", "coverage", "collateral"):
        fig = plot_lab_case(p, view=view)
        fig.canvas.draw()
        assert fig.axes[0].get_title()
    fig = plot_lab_scenarios(
        {"Base": p, "Delayed": replace(p, deployment_delay_months=6)}
    )
    fig.canvas.draw()
    control = lab_training_explorer(p)
    assert control.children[0].value == p.training_fraction
    control.children[0].value = 0.9
    control.children[0].value = 0.4
    assert p.training_fraction == 0.401234


def test_notebook_schema_and_syntax_only():
    import ast
    from pathlib import Path

    import nbformat

    path = Path(__file__).parents[1] / "notebooks/case_lab_gpu_financing.ipynb"
    notebook = nbformat.read(path, as_version=4)
    notebook.cells = [
        c for c in notebook.cells if "colab-setup" not in c.metadata.get("tags", [])
    ]
    nbformat.validate(notebook)
    for cell in notebook.cells:
        if cell.cell_type == "code":
            ast.parse(cell.source)
            assert not any(o.output_type == "error" for o in cell.outputs)
    prose = "\n".join(c.source for c in notebook.cells if c.cell_type == "markdown")
    assert "unverified" in prose
    assert "hypothetical" in prose
