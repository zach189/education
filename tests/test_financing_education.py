import ast
import sys
from pathlib import Path

import matplotlib
import nbformat
import pytest

matplotlib.use("Agg")
from liquid_compute.education import (
    explore_prepayment_financing,
    show_financing_schedule,
)
from liquid_compute.financing import compare_prepayment_financing

BASE = dict(
    monthly_revenue_usd=21600,
    base_monthly_rental_expense_usd=14400,
    service_months=12,
    customer_payment_lag_months=1,
    prepayment_discount_fraction=0.08,
    financed_fraction=0.8,
    nominal_annual_interest_rate=0.12,
    loan_term_months=12,
    origination_fee_fraction=0.02,
)


class Handle:
    def __init__(self, item):
        self.item = item

    def update(self, item):
        self.item = item


@pytest.fixture
def outputs(monkeypatch):
    captured = []

    def display(item, **kwargs):
        if kwargs.get("display_id"):
            handle = Handle(item)
            captured.append(handle)
            return handle
        captured.append(item)

    monkeypatch.setattr("IPython.display.display", display)
    return captured


def test_explorer_precision_independence_recovery(outputs):
    first = explore_prepayment_financing(
        BASE | {"prepayment_discount_fraction": 0.081234}, annual_discount_rate=0.12
    )
    live = first.children[-1]
    second = explore_prepayment_financing(BASE, annual_discount_rate=0.12)
    assert first.children[0].value == 0.081234
    first.children[0].value = 0.08
    assert "45,638.68" in live.outputs[0]["data"]["text/markdown"]
    first.children[2].value = 1
    assert second.children[2].value == 0.8
    assert "3,179.52" in live.outputs[0]["data"]["text/markdown"]
    assert "45,638.68" in second.children[-1].outputs[0]["data"]["text/markdown"]
    assert "image/png" in live.outputs[1]["data"]
    first.children[2].value = 1.1
    assert "Check the inputs" in live.outputs[0]["data"]["text/markdown"]
    assert len(live.outputs) == 1  # No stale chart after invalid inputs.
    first.children[2].value = 0.8
    assert "45,638.68" in live.outputs[0]["data"]["text/markdown"]
    assert len(live.outputs) == 2
    first.close()
    second.close()


def test_fallback_and_full_schedule(outputs, monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "ipywidgets", None)
    assert explore_prepayment_financing(BASE, annual_discount_rate=0.12) is None
    assert "edit the assumptions" in capsys.readouterr().out
    assert "161,931.37" in outputs[-2].data
    rows = compare_prepayment_financing(**BASE)["Borrowed prepayment"]
    show_financing_schedule(rows)
    assert "| 13 |" in outputs[-1].data
    assert "Outstanding debt" in outputs[-1].data


def test_notebook_arithmetic_and_structure(outputs, monkeypatch):
    monkeypatch.setitem(sys.modules, "ipywidgets", None)
    path = (
        Path(__file__).resolve().parents[1]
        / "notebooks/F1_financing_a_compute_prepayment.ipynb"
    )
    notebook = nbformat.read(path, 4)
    notebook.cells = [
        c for c in notebook.cells if "colab-setup" not in c.metadata.get("tags", [])
    ]
    nbformat.validate(notebook)
    assert len(notebook.cells) == 23
    assert "principal" in notebook.cells[4].source
    assert "interest" in notebook.cells[4].source
    assert "\t" not in notebook.cells[4].source
    assert "plot_financing_cash" in notebook.cells[9].source
    scope = {}
    for i, cell in enumerate(notebook.cells):
        assert cell.cell_type == ("markdown" if i % 2 == 0 else "code")
        if cell.cell_type == "code":
            assert not any(
                isinstance(n, ast.Assert) for n in ast.walk(ast.parse(cell.source))
            )
            exec(cell.source, scope)
    assert scope["supplier_savings_usd"] == 13824
    assert scope["monthly_payment_usd"] == pytest.approx(11299.860023142)
    assert scope["cash_t1"] == pytest.approx(-45638.676023142)
    assert "smaller price cut saves" in notebook.cells[14].source
    assert "bigger loan rate" in notebook.cells[16].source
    assert "More borrowing" in notebook.cells[18].source
    assert "F2" in notebook.cells[-1].source
