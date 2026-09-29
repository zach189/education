"""Presentation regressions: preserve financial inputs and optional dependencies."""

import os
import subprocess
import sys
from pathlib import Path

import matplotlib
import nbformat
import pytest

matplotlib.use("Agg")

from liquid_compute import compute_monthly_economics
from liquid_compute.education import (
    explore_monthly_economics,
    plot_profit_by_utilization,
    show_monthly_results,
)

BASE = dict(
    gpu_count=10,
    hours_per_month=720,
    rental_usd_per_gpu_hour=2.0,
    customer_usd_per_gpu_hour=4.0,
    utilization_fraction=0.75,
)


@pytest.fixture
def displayed(monkeypatch):
    captured = []
    monkeypatch.setattr("IPython.display.display", lambda value: captured.append(value))
    monkeypatch.setattr("IPython.display.clear_output", lambda **kwargs: None)
    return captured


def test_fractional_initialization_and_control_updates(displayed):
    panel = explore_monthly_economics(**(BASE | {"utilization_fraction": 0.504}))
    assert panel.children[4].value == 0.504
    assert "115.20" in displayed[-1].data
    # Changing a price must retain the exact usage chosen in editable assumptions.
    panel.children[2].value = 3
    assert panel.children[4].value == 0.504
    assert "-7,084.80" in displayed[-1].data
    panel.children[4].value = 0
    assert "N/A (zero revenue)" in displayed[-1].data
    assert "-21,600.00" in displayed[-1].data
    panel.close()


def test_explorers_are_independent(displayed):
    first = explore_monthly_economics(**BASE)
    second = explore_monthly_economics(**(BASE | {"gpu_count": 20}))
    first.children[4].value = 0.5
    assert second.children[4].value == 0.75
    assert second.children[0].value == 20
    assert "0.00" in displayed[-1].data
    first.close()
    second.close()


def test_invalid_edit_and_recovery(displayed, capsys):
    panel = explore_monthly_economics(**BASE)
    panel.children[2].value = 0
    assert (
        "rental_usd_per_gpu_hour must be greater than zero" in capsys.readouterr().out
    )
    panel.children[2].value = 5
    panel.children[4].value = 1
    assert "125.00%" in displayed[-1].data
    assert "-7,200.00" in displayed[-1].data
    panel.close()


def test_plot_values_and_infeasible_threshold(displayed):
    import matplotlib.pyplot as plt

    baseline = plot_profit_by_utilization(**BASE)
    ax = baseline.axes[0]
    assert ax.get_xlim() == (0, 100)
    assert list(ax.lines[0].get_ydata())[:1] == [-14400]
    assert ax.lines[0].get_ydata()[50] == 0
    assert ax.lines[0].get_ydata()[-1] == 14400
    infeasible = plot_profit_by_utilization(**(BASE | {"rental_usd_per_gpu_hour": 5}))
    assert "125.00%" in infeasible.axes[0].texts[0].get_text()
    assert infeasible.axes[0].get_xlim() == (0, 100)
    assert plt.get_fignums() == []


def test_missing_widgets_preserves_static_fallback(monkeypatch, displayed, capsys):
    monkeypatch.setitem(sys.modules, "ipywidgets", None)
    result = compute_monthly_economics(**BASE)
    show_monthly_results(result)
    assert "7,200.00" in displayed[-1].data
    assert plot_profit_by_utilization(**BASE).axes
    assert explore_monthly_economics(**BASE) is None
    assert "edit the assumptions cell" in capsys.readouterr().out


def test_imports_do_not_require_optional_dependencies():
    root = Path(__file__).resolve().parents[1]
    environment = os.environ | {"PYTHONPATH": str(root / "src")}
    subprocess.run(
        [
            sys.executable,
            "-S",
            "-c",
            "import sys; import liquid_compute; import liquid_compute.education; "
            "assert not any(name in sys.modules for name in ('IPython', 'matplotlib', 'ipywidgets'))",
        ],
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize("usage", [0, 0.504, 0.75, 1])
def test_visible_arithmetic_matches_package(usage, displayed):
    root = Path(__file__).resolve().parents[1]
    notebook = nbformat.read(root / "notebooks/01_compute_business.ipynb", 4)
    notebook.cells = [
        c for c in notebook.cells if "colab-setup" not in c.metadata.get("tags", [])
    ]
    scope = {}
    exec(notebook.cells[1].source, scope)
    scope["utilization_fraction"] = usage
    exec(notebook.cells[3].source, scope)
    exec(notebook.cells[5].source, scope)
    result = scope["result"]
    for name in [
        "purchased_gpu_hours",
        "billed_gpu_hours",
        "unused_gpu_hours",
        "revenue_usd",
        "rental_expense_usd",
        "contribution_profit_usd",
        "contribution_margin_fraction",
    ]:
        assert (
            scope[name] == pytest.approx(getattr(result, name))
            if scope[name] is not None
            else getattr(result, name) is None
        )
    assert scope["break_even_fraction"] == result.break_even_utilization_fraction
