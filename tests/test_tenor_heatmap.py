"""Inspect actual plot data and widget callbacks, without running notebook cells."""

import sys

import matplotlib
import pytest

matplotlib.use("Agg")
from liquid_compute.education import (
    explore_tenor_trade,
    plot_tenor_capacity,
    plot_tenor_heatmap,
)
from liquid_compute.tenor_trade import (
    build_reseller_commitment_scenario,
    tenor_tail_outcome,
)

INPUTS = dict(
    upstream_commitment_usd=1296000,
    contracted_revenue_usd=691200,
    tail_available_gpu_hours=172800,
    future_resale_usd_per_gpu_hour=6.5,
    placement_fraction=0.9,
    selling_fee_fraction=0.05,
)


def test_heatmap_data_marker_boundary_and_units():
    fig = plot_tenor_heatmap(**INPUTS)
    ax = fig.axes[0]
    grid = ax.collections[0].get_array().reshape(41, 49)
    assert grid[0, 0] == -639360
    assert grid[36, 26] == pytest.approx(320976)
    assert ax.collections[1].get_offsets()[0].tolist() == [6.5, 0.9]
    boundary = ax.lines[0]
    for p, f in zip(boundary.get_xdata(), boundary.get_ydata()):
        assert tenor_tail_outcome(
            **(
                INPUTS
                | dict(
                    future_resale_usd_per_gpu_hour=float(p), placement_fraction=float(f)
                )
            )
        ).contribution_usd == pytest.approx(0, abs=1e-8)
    assert "USD/GPU-hour" in ax.get_xlabel()
    assert "fraction" in ax.get_ylabel()
    assert "USD" in fig.axes[1].get_ylabel()
    fig.canvas.draw()


@pytest.mark.parametrize(
    "change,message",
    [
        (dict(selling_fee_fraction=1), "No break-even"),
        (dict(upstream_commitment_usd=500000), "already covers"),
    ],
)
def test_no_fake_boundary(change, message):
    fig = plot_tenor_heatmap(**(INPUTS | change))
    assert not fig.axes[0].lines
    assert message in fig.axes[0].texts[0].get_text()
    fig.canvas.draw()


def test_timeline_preserves_capacity_and_unplaced_period():
    rows = build_reseller_commitment_scenario(
        purchased_gpu_hours=[7200] * 36,
        supplier_usd_per_gpu_hour=[5] * 36,
        billed_fractions=[1] * 12 + [0] * 24,
        customer_usd_per_gpu_hour=[8] * 12 + [0] * 24,
        customer_contracted=[True] * 12 + [False] * 24,
    )
    fig = plot_tenor_capacity(rows)
    ax = fig.axes[0]
    assert list(ax.lines[0].get_ydata()) == [7200] * 36
    assert [p.get_height() for p in ax.containers[0]] == [7200] * 12 + [0] * 24
    assert [p.get_height() for p in ax.containers[2]] == [0] * 12 + [7200] * 24
    assert ax.get_ylabel() == "GPU-hours per month"
    fig.canvas.draw()


def test_controls_exact_independent_update_and_recover(monkeypatch):
    monkeypatch.setattr("IPython.display.display", lambda x: None)
    first = explore_tenor_trade(
        **(INPUTS | dict(future_resale_usd_per_gpu_hour=6.512345))
    )
    second = explore_tenor_trade(**INPUTS)
    assert first.children[0].value == 6.512345
    before = first.children[-1].outputs[1]["data"]["image/png"]
    first.children[0].value = 4
    assert before != first.children[-1].outputs[1]["data"]["image/png"]
    assert "48,384" in first.children[-1].outputs[0]["data"]["text/markdown"]
    assert second.children[0].value == 6.5
    first.children[1].value = 0
    assert (
        "No finite solution" in first.children[-1].outputs[0]["data"]["text/markdown"]
    )
    first.children[1].value = 1.1
    assert len(first.children[-1].outputs) == 1
    assert "Check the inputs" in first.children[-1].outputs[0]["data"]["text/markdown"]
    first.children[1].value = 0.9
    first.children[2].value = 1
    assert len(first.children[-1].outputs) == 2
    assert (
        "No finite solution" in first.children[-1].outputs[0]["data"]["text/markdown"]
    )
    first.children[2].value = 0.05
    assert len(first.children[-1].outputs) == 2
    first.close()
    second.close()


def test_static_fallback(monkeypatch, capsys):
    rendered = []
    monkeypatch.setattr("IPython.display.display", rendered.append)
    monkeypatch.setitem(sys.modules, "ipywidgets", None)
    assert explore_tenor_trade(**INPUTS) is None
    assert len(rendered) == 1
    assert "320,976" in rendered[0].axes[0].get_title()
    assert "edit the price" in capsys.readouterr().out
