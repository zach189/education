from pathlib import Path

import matplotlib
import nbformat
import pytest

matplotlib.use("Agg")

from liquid_compute.education import explore_rental_quotes, show_rental_quotes
from liquid_compute.forward_curves import RentalQuote

MENU = (RentalQuote(12, 6), RentalQuote(36, 5), RentalQuote(60, 4.4))


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


def test_controls_exact_initialization_independence_and_recovery(outputs):
    first = explore_rental_quotes(
        (RentalQuote(12, 6.0123), *MENU[1:]), delivery_hours_per_gpu=[720] * 60
    )
    first_table, first_chart = outputs[-2:]
    second = explore_rental_quotes(MENU, delivery_hours_per_gpu=[720] * 60)
    second_table = outputs[-2]
    assert first.children[0].value == 6.0123
    first.children[0].value = 6
    first.children[1].value = 5.2
    assert "4.8000" in first_table.item.data
    assert second.children[1].value == 5
    assert "4.5000" in second_table.item.data
    first.children[1].value = -1
    assert "Check the inputs" in first_table.item.data
    assert "restore" in first_chart.item.data
    first.children[1].value = 5
    first.children[2].value = 2.8
    assert "-0.5000" in first_table.item.data
    assert first_chart.item.axes[0].get_ylim()[0] < -0.5
    first.close()
    second.close()


def test_missing_quotes_and_widget_free_saved_figure(outputs, monkeypatch, capsys):
    import sys

    monkeypatch.setitem(sys.modules, "ipywidgets", None)
    sparse = (MENU[0], MENU[2])
    show_rental_quotes(sparse)
    assert "| 36 | Not quoted |" in outputs[-1].data
    assert explore_rental_quotes(sparse, delivery_hours_per_gpu=[720] * 60) is None
    assert "13–60" in outputs[-2].data
    assert list(outputs[-1].axes[0].get_xticks()) == [0, 12, 60]
    assert "edit the rental menu" in capsys.readouterr().out


def test_notebook_arithmetic_and_structure(outputs):
    n = nbformat.read(
        Path(__file__).resolve().parents[1]
        / "notebooks/03_rental_quotes_to_implied_forward_curve.ipynb",
        4,
    )
    n.cells = [c for c in n.cells if "colab-setup" not in c.metadata.get("tags", [])]
    assert len(n.cells) == 21
    assert all(
        c.cell_type == ("markdown" if i % 2 == 0 else "code")
        for i, c in enumerate(n.cells)
    )
    scope = {}
    for index in [1, 5, 7, 11, 17, 19]:
        exec(n.cells[index].source, scope)
    assert scope["years_two_three"] == pytest.approx(4.5)
    assert scope["years_four_five"] == pytest.approx(3.5)
    assert scope["reconstructed_rates"] == pytest.approx([6, 5, 4.4])
    assert scope["weighted_middle"] == pytest.approx(4.4083018867924535)
    for index in [12, 14, 16]:
        assert "What this shows" in n.cells[index].source
    assert "Optional" in n.cells[16].source
    assert "Optional" in n.cells[18].source
    assert n.cells[-1].source.endswith(
        "If longer commitments offer a lower hourly rate, what happens when we buy a long contract and resell the capacity in shorter blocks—and what risks do we retain?"
    )
    assert not any("assert " in c.source for c in n.cells if c.cell_type == "code")
    assert any(isinstance(x, Handle) for x in outputs) is False
