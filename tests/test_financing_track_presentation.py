"""Headless helper tests and static notebook checks; never execute lesson cells."""

import ast
import sys
from pathlib import Path

import matplotlib
import nbformat
import pytest

matplotlib.use("Agg")

from liquid_compute.education import plot_finance_series, show_finance_table

ROOT = Path(__file__).resolve().parents[1]


def test_plot_labels_signed_values_and_expiry_marker():
    fig = plot_finance_series(
        {"Stress": [0, 100, -50], "Base": [0, 100, 200]},
        title="Cumulative cash",
        marker_month=1,
    )
    ax = fig.axes[0]
    assert list(ax.lines[0].get_ydata()) == [0, 100, -50]
    assert list(ax.lines[0].get_xdata()) == [0, 1, 2]
    assert ax.get_ylabel() == "USD"
    assert "Month offset" in ax.get_xlabel()
    assert ax.get_title() == "Cumulative cash"
    assert any(line.get_label() == "Contract expires" for line in ax.lines)
    fig.canvas.draw()


def test_stacked_plot_and_snapshot_axis():
    stacked = plot_finance_series(
        {"Interest": [0, 1000, 955], "Principal": [0, 4500, 6000]},
        title="Uses",
        stacked=True,
    )
    assert len(stacked.axes[0].collections) == 2
    assert [t.get_text() for t in stacked.axes[0].legend_.get_texts()] == [
        "Interest",
        "Principal",
    ]
    stacked.canvas.draw()
    snap = plot_finance_series(
        {"Base": [200000, 180000, 144000, 134000]},
        title="Eligibility",
        xlabel="Calculation step",
    )
    assert snap.axes[0].get_xlabel() == "Calculation step"


def test_table_units_na_and_negative_values_without_widgets(monkeypatch):
    captured = []
    monkeypatch.setattr("IPython.display.display", lambda item: captured.append(item))
    monkeypatch.setitem(sys.modules, "ipywidgets", None)
    show_finance_table(["Case", "Cash (USD)", "DSCR"], [["Loss", -24000, None]])
    assert "-24,000.00" in captured[0].data and "N/A" in captured[0].data
    fig = plot_finance_series({"Loss": [0, -24000]}, title="Loss")
    fig.canvas.draw()


@pytest.mark.parametrize(
    "values", [{}, {"A": []}, {"A": [1], "B": [1, 2]}, {"A": [float("nan")]}]
)
def test_invalid_chart_data(values):
    with pytest.raises(ValueError):
        plot_finance_series(values, title="invalid")


@pytest.mark.parametrize(
    "path", sorted((ROOT / "notebooks").glob("F[2-9]_*.ipynb")), ids=lambda p: p.stem
)
def test_financing_track_static_format_and_teaching_structure(path):
    notebook = nbformat.read(path, 4)
    notebook.cells = [
        c for c in notebook.cells if "colab-setup" not in c.metadata.get("tags", [])
    ]
    nbformat.validate(notebook)
    assert len(notebook.cells) == 17
    prose = "\n".join(c.source for c in notebook.cells if c.cell_type == "markdown")
    assert "hypothetical" in prose.lower()
    assert "USD" in prose and "Next" in prose
    assert not any(ord(c) < 32 and c not in "\n\t" for c in prose)
    assert "/Users/" not in str(notebook)
    words = len(prose.split())
    assert 750 <= words <= 1200
    for i, cell in enumerate(notebook.cells):
        assert cell.cell_type == ("markdown" if i % 2 == 0 else "code")
        if cell.cell_type == "code":
            tree = ast.parse(cell.source)
            assert not any(isinstance(node, ast.Assert) for node in ast.walk(tree))
            compile(tree, str(path), "exec")  # Compile only; do not run notebook code.
    assert not any(
        output.output_type == "error"
        for cell in notebook.cells
        if cell.cell_type == "code"
        for output in cell.outputs
    )


def test_generic_explorer_exact_values_independence_and_recovery(monkeypatch):
    from liquid_compute.education import explore_finance_series
    from liquid_compute.financing import level_payment_debt_capacity_usd

    monkeypatch.setattr("IPython.display.display", lambda item: None)

    def calculate(values):
        capacity = level_payment_debt_capacity_usd(
            cfads_usd=[8000] * 12,
            minimum_dscr=values["DSCR"],
            nominal_annual_interest_rate=values["Rate"],
        )
        return {"Capacity": (capacity, 0)}

    original = {"DSCR": 1.251234, "Rate": 0.12}
    first = explore_finance_series(original, calculate, title="Capacity")
    second = explore_finance_series(original, calculate, title="Capacity")
    assert first.children[0].value == 1.251234
    before = first.children[-1].outputs[1]["data"]["image/png"]
    first.children[0].value = 1.5
    assert first.children[-1].outputs[1]["data"]["image/png"] != before
    assert second.children[0].value == original["DSCR"] == 1.251234
    first.children[0].value = 0.5
    assert len(first.children[-1].outputs) == 1
    assert "Check the inputs" in first.children[-1].outputs[0]["data"]["text/markdown"]
    first.children[0].value = 1.25
    assert len(first.children[-1].outputs) == 2
    first.close()
    second.close()


def test_generic_explorer_widget_free(monkeypatch, capsys):
    from liquid_compute.education import explore_finance_series

    captured = []
    monkeypatch.setattr("IPython.display.display", lambda item: captured.append(item))
    monkeypatch.setitem(sys.modules, "ipywidgets", None)
    assert (
        explore_finance_series(
            {"USD": 123.4567}, lambda v: {"Cash": [0, v["USD"]]}, title="Fallback"
        )
        is None
    )
    assert list(captured[0].axes[0].lines[0].get_ydata()) == [0, 123.4567]
    assert "edit the assumptions" in capsys.readouterr().out


def test_actual_calculator_series_render_without_kernel():
    from itertools import accumulate

    from liquid_compute.collateral import (
        Receivable,
        calculate_receivables_borrowing_base,
    )
    from liquid_compute.deployment import build_deployment_funding_schedule
    from liquid_compute.equipment import compare_purchase_lease_cash_flows
    from liquid_compute.financing import shape_debt_service
    from liquid_compute.offtake import (
        OfftakeTerms,
        build_offtake_receipts,
        build_renewal_receipt_scenarios,
    )
    from liquid_compute.waterfalls import build_cash_waterfall

    receipts = build_offtake_receipts(
        OfftakeTerms(20000, 12, acceptance_required=True), acceptance_month=3
    )
    debt = shape_debt_service(
        cfads_usd=[8000] * 12, minimum_dscr=1.25, nominal_annual_interest_rate=0.12
    )
    deployment = build_deployment_funding_schedule(
        milestone_months=(0, 3, 4),
        milestone_payments_usd=(200000, 600000, 200000),
        operating_start_month=5,
        operating_receipts_usd=[110000] * 12,
        operating_costs_usd=[15000] * 12,
        monthly_site_cost_usd=5000,
        draw_strategy="staged",
        debt_fraction=0.8,
        nominal_annual_interest_rate=0.12,
        repayment_term_months=12,
    )
    collateral = calculate_receivables_borrowing_base(
        [
            Receivable("A", 100000, 30),
            Receivable("B", 80000, 30),
            Receivable("C", 20000, 30),
        ],
        maximum_age_days=60,
        concentration_fraction=0.4,
        advance_fraction=0.8,
        reserve_usd=10000,
        facility_limit_usd=150000,
        debt_usd=100000,
    )
    renewal = build_renewal_receipt_scenarios(
        contracted_monthly_usd=20000,
        contract_months=12,
        obligation_months=24,
        renewal_gap_months=3,
        renewal_monthly_usd=17000,
    )
    equipment = compare_purchase_lease_cash_flows(
        purchase_price_usd=300000,
        lease_payments_usd=[8000] * 36,
        exit_month=36,
        resale_proceeds_usd=60000,
        has_resale_rights=True,
        annual_discount_rate=0.12,
    )
    waterfall = build_cash_waterfall(
        cash_after_operations_usd=[10000, 10000, 3000] + [10000] * 22,
        initial_debt_usd=100000,
        nominal_annual_interest_rate=0.12,
        scheduled_principal_usd=[4000] * 25,
        opening_reserve_usd=2000,
        reserve_target_usd=6000,
        sweep_fraction=0.5,
    )
    cases = {
        "F3": tuple(
            accumulate(
                r.receipts_usd - (12000 if r.month_offset else 0) for r in receipts
            )
        ),
        "F4": tuple(r.closing_debt_usd for r in debt.rows),
        "F5": tuple(r.cumulative_cash_usd for r in deployment),
        "F6": (
            collateral.eligible_usd,
            collateral.adjusted_eligible_usd,
            collateral.gross_advance_usd,
            collateral.borrowing_base_usd,
            collateral.availability_usd,
        ),
        "F7": tuple(r.total_receipts_usd for r in renewal),
        "F8": tuple(accumulate(-v for v in equipment.purchase_outflows_usd)),
        "F9": (0,) + tuple(r.distribution_usd for r in waterfall),
    }
    assert min(cases["F3"]) == -24000
    assert min(cases["F5"]) == pytest.approx(-231200)
    assert cases["F6"][-1] == 34000
    assert cases["F7"][13:16] == (0, 0, 0)
    assert cases["F8"][-1] == -240000
    assert cases["F9"][1] == 500
    for name, values in cases.items():
        figure = plot_finance_series({name: values}, title=name)
        assert tuple(figure.axes[0].lines[0].get_ydata()) == values
        assert len(figure.axes[0].lines[0].get_xdata()) == len(values)
        figure.canvas.draw()
