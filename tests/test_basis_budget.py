import sys

import matplotlib
import pytest

matplotlib.use("Agg")

from liquid_compute.education import (
    basis_budget_series,
    explore_basis_budget,
    plot_finance_series,
)
from liquid_compute.hedging import (
    basis_budget_summary,
    benchmark_basis_deviations_usd,
)

BASE = dict(
    actual_usd_per_gpu_hour=7.5,
    benchmark_usd_per_gpu_hour=7.0,
    strike_usd_per_gpu_hour=5.0,
    gpu_hours=7200.0,
    budget_basis_usd_per_gpu_hour=0.5,
)


def test_independent_cash_amounts_and_widening():
    r = basis_budget_summary(**BASE)
    assert (r.unhedged_cost_usd, r.hedge_receipt_usd, r.net_cost_usd) == (
        54000,
        14400,
        39600,
    )
    assert r.budgeted_cost_usd == 39600
    assert r.budget_deviation_usd == 0
    wider = basis_budget_summary(**(BASE | {"actual_usd_per_gpu_hour": 8.5}))
    assert wider.net_cost_usd - r.net_cost_usd == 7200
    assert wider.budget_deviation_usd == 7200
    negative = basis_budget_summary(**(BASE | {"actual_usd_per_gpu_hour": 4.5}))
    assert negative.basis_usd_per_gpu_hour == -2.5
    assert negative.net_cost_usd == 18000
    assert negative.budget_deviation_usd == -21600


@pytest.mark.parametrize(
    "index,basis", [(0, 0), (3, 0), (7, 0), (3, 0.5), (7, 0.5), (7, -7)]
)
@pytest.mark.parametrize("quantity", [0, 7200])
def test_matched_cost_identity_and_budget_reconciliation(index, basis, quantity):
    r = basis_budget_summary(
        **(
            BASE
            | dict(
                actual_usd_per_gpu_hour=index + basis,
                benchmark_usd_per_gpu_hour=index,
                gpu_hours=quantity,
            )
        )
    )
    assert r.net_cost_usd == quantity * (5 + basis)
    assert r.net_cost_usd == r.unhedged_cost_usd - r.hedge_receipt_usd
    assert r.net_cost_usd - r.budgeted_cost_usd == r.budget_deviation_usd
    if quantity == 0:
        assert r.unhedged_cost_usd == r.hedge_receipt_usd == r.budget_deviation_usd == 0


@pytest.mark.parametrize("field", BASE)
@pytest.mark.parametrize(
    "value,error",
    [
        (True, TypeError),
        ("7", TypeError),
        (None, TypeError),
        (float("nan"), ValueError),
        (float("inf"), ValueError),
    ],
)
def test_invalid_scalar_inputs(field, value, error):
    with pytest.raises(error):
        basis_budget_summary(**(BASE | {field: value}))


@pytest.mark.parametrize(
    "field", [k for k in BASE if k != "budget_basis_usd_per_gpu_hour"]
)
def test_negative_prices_or_quantity(field):
    with pytest.raises(ValueError):
        basis_budget_summary(**(BASE | {field: -1}))


def test_signed_budget_and_overflow():
    r = basis_budget_summary(**(BASE | {"budget_basis_usd_per_gpu_hour": -1}))
    assert r.budgeted_cost_usd == 28800
    for changes in [dict(gpu_hours=1e308), dict(budget_basis_usd_per_gpu_hour=1e308)]:
        with pytest.raises(ValueError):
            basis_budget_summary(**(BASE | changes))


def test_candidates_align_by_scenario_not_insertion_order():
    actual = dict(base=5.5, together=7.5, wider=8.5, falls=4.5)
    a = dict(falls=7, wider=7, together=7, base=5)
    b = dict(wider=8.1, base=5.3, falls=4.4, together=7.2)
    for prices, baseline, expected in [
        (a, 0.5, [0, 0, 7200, -21600]),
        (b, 0.2, [0, 720, 1440, -720]),
    ]:
        result = benchmark_basis_deviations_usd(
            actual_prices=actual,
            benchmark_prices=prices,
            baseline_basis_usd_per_gpu_hour=baseline,
            gpu_hours=7200,
        )
        assert list(result) == list(actual)
        assert list(result.values()) == pytest.approx(expected, abs=1e-8)
    for prices in [dict(base=5), a | dict(extra=7), {}]:
        with pytest.raises(ValueError, match="match exactly"):
            benchmark_basis_deviations_usd(
                actual_prices=actual,
                benchmark_prices=prices,
                baseline_basis_usd_per_gpu_hour=0.5,
                gpu_hours=7200,
            )
    for missing, error in [(None, TypeError), (float("nan"), ValueError)]:
        with pytest.raises(error):
            benchmark_basis_deviations_usd(
                actual_prices=actual,
                benchmark_prices=a | dict(wider=missing),
                baseline_basis_usd_per_gpu_hour=0.5,
                gpu_hours=7200,
            )


CHART = dict(
    settlement_index_usd_per_gpu_hour=7.0,
    realized_basis_usd_per_gpu_hour=0.5,
    budget_basis_usd_per_gpu_hour=0.5,
    gpu_hours=7200.0,
    strike_usd_per_gpu_hour=5.0,
)


def test_plot_and_index_cancellation():
    initial = basis_budget_series(**CHART)
    moved = basis_budget_series(**(CHART | dict(settlement_index_usd_per_gpu_hour=8)))
    assert initial["Hedged cost"] == moved["Hedged cost"] == (39600,)
    assert moved["Unhedged cost"] == (61200,)
    assert moved["Budget deviation"] == (0,)
    fig = plot_finance_series(
        initial, title="Basis", bar=True, x_tick_labels=["Selected scenario"]
    )
    assert [p.get_height() for p in fig.axes[0].patches] == [54000, 39600, 0]
    fig.canvas.draw()
    for changes in [
        dict(realized_basis_usd_per_gpu_hour=-8),
        dict(settlement_index_usd_per_gpu_hour=-1),
    ]:
        with pytest.raises(ValueError):
            basis_budget_series(**(CHART | changes))


def test_controls_precision_independence_and_recovery(monkeypatch):
    monkeypatch.setattr("IPython.display.display", lambda item: None)
    panel = explore_basis_budget(
        **(CHART | dict(budget_basis_usd_per_gpu_hour=0.512345))
    )
    second = explore_basis_budget(**CHART)
    assert panel.children[2].value == 0.512345
    panel.children[1].value = -8
    assert len(panel.children[-1].outputs) == 1
    assert "Check the inputs" in panel.children[-1].outputs[0]["data"]["text/markdown"]
    panel.children[1].value = -2.5
    assert "image/png" in panel.children[-1].outputs[1]["data"]
    assert "18,000.00" in panel.children[-1].outputs[0]["data"]["text/markdown"]
    assert second.children[1].value == 0.5
    panel.children[2].value = -2.5
    assert (
        "Budget deviation | 0.00"
        in panel.children[-1].outputs[0]["data"]["text/markdown"]
    )
    panel.close()
    second.close()


def test_widget_free_fallback(monkeypatch):
    displayed = []
    monkeypatch.setattr("IPython.display.display", displayed.append)
    monkeypatch.setitem(sys.modules, "ipywidgets", None)
    assert explore_basis_budget(**CHART) is None
    assert [p.get_height() for p in displayed[0].axes[0].patches] == [54000, 39600, 0]
