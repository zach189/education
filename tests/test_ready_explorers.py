"""Financial chart data and independent interactive behavior for Ready lessons."""

import sys
from dataclasses import replace

import matplotlib
import pytest

matplotlib.use("Agg")

from liquid_compute.education import (
    explore_forward_hedge,
    explore_option_protection,
    explore_option_valuation,
    lab_training_explorer,
    plot_forward_hedge,
    plot_lab_case,
    plot_option_protection,
    plot_option_tree,
    show_lab_decision_summary,
    show_lab_scenario_comparison,
)
from liquid_compute.lab_financing import LabInputs
from liquid_compute.option_valuation import binomial_european_option_tree


def test_lab_cash_breakdown_and_target_without_phantom_shortfall():
    fig = plot_lab_case(LabInputs(), view="cash")
    waterfall, timeline = fig.axes
    assert [bar.get_height() for bar in waterfall.patches] == pytest.approx(
        [39.3984, -14.81952, 24.57888, -12.4262878836, 12.1525921164]
    )
    assert list(timeline.lines[0].get_ydata()) == pytest.approx([12.1525921164] * 60)
    assert list(timeline.lines[1].get_ydata()) == pytest.approx([3.1065719709] * 60)
    assert "shortfall" not in " ".join(timeline.get_legend_handles_labels()[1]).lower()


def test_lab_cash_shortfall_and_weakest_month_for_balloon():
    fig = plot_lab_case(replace(LabInputs(), repayment="balloon"), view="cash")
    waterfall, timeline = fig.axes
    assert "Month 60" in waterfall.get_title()
    assert waterfall.patches[-1].get_height() == pytest.approx(-482.5044533333)
    assert "Monthly shortfall" in timeline.get_legend_handles_labels()[1]
    assert timeline.lines[0].get_ydata()[-1] < 0
    # Even a single shortfall at maturity must have a visible bar.
    assert any(bar.get_height() < 0 for bar in timeline.patches)


def test_lab_cash_target_breach_is_distinct_from_payment_shortfall():
    fig = plot_lab_case(replace(LabInputs(), contracted_fraction=0.22), view="cash")
    timeline = fig.axes[1]
    margin = timeline.lines[0].get_ydata()[0]
    target = timeline.lines[1].get_ydata()[0]
    assert 0 < margin < target
    assert "Monthly shortfall" not in timeline.get_legend_handles_labels()[1]


def test_lab_cash_without_debt_has_no_coverage_ratio():
    fig = plot_lab_case(replace(LabInputs(), advance_fraction=0), view="cash")
    assert "No debt payments" in fig.axes[1].get_title()
    assert all(value == 0 for value in fig.axes[1].lines[1].get_ydata())


FORWARD = dict(
    physical_gpu_hours=7200, hedge_gpu_hours=7200, strike_usd_per_gpu_hour=5.0
)
OPTION = dict(
    kind="call",
    physical_gpu_hours=7200,
    covered_gpu_hours=7200,
    strike_usd_per_gpu_hour=5.0,
    premium_usd_per_gpu_hour=0.4,
)
MODEL = dict(
    kind="call",
    spot_usd_per_unit=5.0,
    strike_usd_per_unit=5.0,
    up_factor=1.2,
    down_factor=0.8,
    effective_annual_rate=0.05,
    step_years=1.0,
)


def at(line, price):
    return list(line.get_ydata())[list(line.get_xdata()).index(price)]


@pytest.mark.parametrize("side,receipt", [("buyer", 14400), ("seller", -14400)])
def test_forward_chart_separates_physical_and_signed_hedge(side, receipt):
    fig = plot_forward_hedge(**FORWARD, side=side)
    assert at(fig.axes[0].lines[0], 7) == 50400
    assert at(fig.axes[0].lines[1], 7) == 36000
    assert at(fig.axes[1].lines[0], 7) == receipt
    partial = plot_forward_hedge(**(FORWARD | {"hedge_gpu_hours": 3600}), side=side)
    assert at(partial.axes[0].lines[1], 7) == 43200
    over = plot_forward_hedge(**(FORWARD | {"hedge_gpu_hours": 14400}), side=side)
    assert at(over.axes[0].lines[1], 7) == 21600
    fig.canvas.draw()


def test_option_chart_distinguishes_gross_net_and_business_cost():
    fig = plot_option_protection(**OPTION)
    assert at(fig.axes[0].lines[0], 7) == 14400
    assert at(fig.axes[0].lines[1], 3) == -2880
    assert at(fig.axes[1].lines[1], 7) == 38880
    assert at(fig.axes[1].lines[1], 3) == 24480
    partial = plot_option_protection(**(OPTION | {"covered_gpu_hours": 3600}))
    assert at(partial.axes[1].lines[1], 7) == 44640
    basis = plot_option_protection(**OPTION, basis_usd_per_gpu_hour=0.5)
    assert at(basis.axes[1].lines[1], 7) == 42480
    put = plot_option_protection(
        **(OPTION | {"kind": "put", "premium_usd_per_gpu_hour": 0.3})
    )
    assert at(put.axes[1].lines[1], 3) == 33840
    fig.canvas.draw()


def test_option_grid_contains_exact_kink_and_valid_physical_prices():
    fig = plot_option_protection(
        **(OPTION | {"strike_usd_per_gpu_hour": 5.123456}), basis_usd_per_gpu_hour=-0.5
    )
    assert 5.123456 in fig.axes[0].lines[0].get_xdata()
    assert min(fig.axes[1].lines[0].get_ydata()) == 0


def test_tree_nodes_show_backward_values_and_explicit_expiry():
    tree = binomial_european_option_tree(**MODEL, steps=2)
    fig = plot_option_tree(tree)
    labels = [t.get_text() for t in fig.axes[0].texts]
    assert len(labels) == 6
    assert labels[0] == "Proxy USD 5.00\nOption USD 0.7795"
    assert labels[-1] == "Proxy USD 7.20\nOption USD 2.2000"
    assert list(fig.axes[0].get_xticks()) == [0, 1, 2]
    fig.canvas.draw()


@pytest.fixture
def captured(monkeypatch):
    values = []
    monkeypatch.setattr("IPython.display.display", values.append)
    return values


def markdown(panel):
    return panel.children[-1].outputs[0]["data"]["text/markdown"]


@pytest.mark.parametrize(
    "factory,kwargs,key,bad",
    [
        (explore_forward_hedge, FORWARD, "Hedge GPU-hours", -1),
        (explore_option_protection, OPTION, "Premium USD/covered hour", -1),
        (explore_option_valuation, MODEL, "Up factor", 1.02),
    ],
)
def test_controls_recover_reset_and_preserve_independence(
    captured, factory, kwargs, key, bad
):
    a = factory(**kwargs)
    b = factory(**kwargs)
    controls = {c.description: c for c in a.children[:-2]}
    original = controls[key].value
    baseline = markdown(a)
    controls[key].value = bad
    assert "Check the inputs" in markdown(a)
    assert len(a.children[-1].outputs) == 1  # Remove stale chart on invalid input.
    assert "Check the inputs" not in markdown(b)
    a.children[-2].click()
    assert controls[key].value == original
    assert markdown(a) == baseline
    assert "image/png" in a.children[-1].outputs[1]["data"]
    a.close()
    b.close()


def test_precision_and_effective_widget_changes(captured):
    panel = explore_option_protection(
        **(OPTION | {"strike_usd_per_gpu_hour": 5.123456})
    )
    controls = {c.description: c for c in panel.children[:-2]}
    assert controls["Strike USD/GPU-hour"].value == 5.123456
    original = panel.children[-1].outputs[1]["data"]["image/png"]
    controls["Covered GPU-hours"].value = 3600
    assert panel.children[-1].outputs[1]["data"]["image/png"] != original
    controls["Option"].value = "put"
    assert "Check the inputs" not in markdown(panel)
    panel.close()


def test_lab_output_updates_and_allocation_error_recovery(captured):
    base = replace(LabInputs(), training_fraction=0.401234)
    panel = lab_training_explorer(base)
    controls = {c.description: c for c in panel.children[:-2]}
    assert controls["Training share"].value == 0.401234
    controls["Training share"].value = 0.9
    assert "Check the inputs" in markdown(panel)
    controls["Committed share"].value = 0.1
    assert "Minimum DSCR" in markdown(panel)
    controls["View"].value = "capacity"
    assert "image/png" in panel.children[-1].outputs[1]["data"]
    panel.children[-2].click()
    assert controls["Training share"].value == base.training_fraction
    assert controls["Committed share"].value == base.contracted_fraction
    assert base.training_fraction == 0.401234
    panel.close()


@pytest.mark.parametrize(
    "factory,kwargs",
    [
        (explore_forward_hedge, FORWARD),
        (explore_option_protection, OPTION),
        (explore_option_valuation, MODEL),
    ],
)
def test_static_fallback_without_widgets(captured, monkeypatch, factory, kwargs):
    monkeypatch.setitem(sys.modules, "ipywidgets", None)
    assert factory(**kwargs) is None
    assert len(captured) == 2
    captured[-1].canvas.draw()


def test_lab_static_fallback_and_packaged_tables(captured, monkeypatch):
    monkeypatch.setitem(sys.modules, "ipywidgets", None)
    assert lab_training_explorer(LabInputs()) is None
    show_lab_decision_summary(LabInputs())
    assert "24.69%" in captured[-1].data
    show_lab_scenario_comparison({"Base": LabInputs()})
    assert "60.8%" in captured[-1].data
    assert "1.98×" in captured[-1].data


@pytest.mark.parametrize("bad", [True, "5", float("nan"), float("inf")])
def test_explorer_rejects_invalid_initial_numeric_types(captured, bad):
    with pytest.raises((TypeError, ValueError)):
        explore_option_protection(**(OPTION | {"strike_usd_per_gpu_hour": bad}))
