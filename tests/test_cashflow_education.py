from pathlib import Path

import matplotlib
import nbformat
import pytest

matplotlib.use("Agg")

from liquid_compute.cashflows import build_cash_flow_schedule
from liquid_compute.education import (
    explore_payment_terms,
    plot_cumulative_cash,
    show_cash_flow_schedule,
    show_payment_comparison,
)

BASE = dict(
    monthly_revenue_usd=21600,
    base_monthly_rental_expense_usd=14400,
    service_months=12,
    customer_payment_lag_months=1,
)


@pytest.fixture
def displayed(monkeypatch):
    results = []
    monkeypatch.setattr("IPython.display.display", lambda item: results.append(item))
    monkeypatch.setattr("IPython.display.clear_output", lambda **kwargs: None)
    return results


def test_controls_precision_independence_and_recovery(displayed, capsys):
    one = explore_payment_terms(
        **BASE, annual_discount_rate=0.1234, prepayment_discount_fraction=0.0812
    )
    two = explore_payment_terms(
        **BASE, annual_discount_rate=0.12, prepayment_discount_fraction=0.08
    )
    assert one.children[2].value == 0.1234
    assert one.children[3].value == 0.0812
    one.children[1].value = 2
    assert two.children[1].value == 1
    assert "43,200.00" in displayed[-2].data
    one.children[2].value = -1
    assert "Check the inputs" in capsys.readouterr().out
    one.children[2].value = 0.24
    assert "156,876.06" in displayed[-2].data
    one.close()
    two.close()


def test_static_plot_and_missing_widgets(displayed, monkeypatch, capsys):
    import sys

    monkeypatch.setitem(sys.modules, "ipywidgets", None)
    rows = build_cash_flow_schedule(**BASE)
    show_cash_flow_schedule(rows)
    assert "| 13 |" in displayed[-1].data
    show_payment_comparison({"Monthly": rows}, annual_discount_rate=0.12)
    assert "28,800.00" in displayed[-1].data
    show_payment_comparison(
        {"Monthly": rows}, annual_discount_rate=0.12, include_supplier_pv=False
    )
    assert "PV of supplier payments" not in displayed[-1].data
    figure = plot_cumulative_cash({"Monthly": rows}, service_months=12)
    assert min(figure.axes[0].lines[0].get_ydata()) == -28800
    assert figure.axes[0].lines[0].get_ydata()[-1] == 86400
    assert (
        explore_payment_terms(
            **BASE, annual_discount_rate=0.12, prepayment_discount_fraction=0.08
        )
        is None
    )
    assert "edit the assumptions" in capsys.readouterr().out


def test_notebook_arithmetic_and_reading_structure(displayed):
    n = nbformat.read(
        Path(__file__).resolve().parents[1]
        / "notebooks/02_cash_flows_through_time.ipynb",
        4,
    )
    n.cells = [c for c in n.cells if "colab-setup" not in c.metadata.get("tags", [])]
    scope = {}
    for index in [1, 3, 13, 15]:
        exec(n.cells[index].source, scope)
    assert scope["balances_usd"] == [0, 7200, 14400]
    assert scope["early_funding_usd"] == 0
    assert scope["upfront_price_usd"] == 158976
    assert scope["allocated_monthly_expense_usd"] == 13248
    assert scope["upfront_contribution_usd"] == 100224
    assert scope["monthly_supplier_pv_usd"] == pytest.approx(162597.83025025515)
    for index in [7, 10, 21]:
        assert n.cells[index + 1].cell_type == "markdown"
        assert "What this shows" in n.cells[index + 1].source
    assert not any("assert " in c.source for c in n.cells if c.cell_type == "code")


def test_matched_controls_and_customer_prepayment(displayed, capsys):
    panel = explore_payment_terms(
        **(BASE | {"customer_payment_lag_months": 0}),
        annual_discount_rate=0.12,
        prepayment_discount_fraction=0.08,
        supplier_payment_timing="monthly_in_arrears",
    )
    assert panel.children[4].value == "monthly_in_arrears"
    assert "162,597.83" in displayed[-2].data
    panel.children[4].value = "monthly_in_advance"
    assert "14,400.00" in displayed[-2].data
    panel.children[5].value = "upfront"
    assert "259,200.00" in displayed[-2].data
    assert min(displayed[-1].axes[0].lines[0].get_ydata()) == 0
    panel.children[1].value = 1
    assert "require zero" in capsys.readouterr().out
    panel.children[1].value = 0
    assert min(displayed[-1].axes[0].lines[0].get_ydata()) == 0
    panel.close()


@pytest.mark.parametrize("rate", [0.0, 0.12])
def test_single_payment_plot_distinguishes_bill_from_valuation(displayed, rate):
    from liquid_compute.education import plot_payment_present_value

    figure = plot_payment_present_value(payment_usd=14400, annual_discount_rate=rate)
    actual, valued = figure.axes[0].lines
    assert list(actual.get_ydata()) == [14400] * 13
    assert valued.get_ydata()[0] == 14400
    assert valued.get_ydata()[-1] == pytest.approx(14400 / (1 + rate))
    assert list(valued.get_xdata()) == list(range(13))
