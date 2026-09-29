"""Headless market-lesson plots and static source checks; never execute cells."""

import ast
from pathlib import Path

import matplotlib
import nbformat
import pytest

matplotlib.use("Agg")

from liquid_compute.education import plot_finance_series
from liquid_compute.tenor_trade import build_reseller_commitment_scenario

ROOT = Path(__file__).resolve().parents[1]
PATHS = sorted(
    [
        *(ROOT / "notebooks").glob("04_*.ipynb"),
        *(ROOT / "notebooks").glob("M[2-7]_*.ipynb"),
        *(ROOT / "notebooks").glob("E[1-6]_*.ipynb"),
    ]
)


@pytest.mark.parametrize("path", PATHS, ids=lambda p: p.stem)
def test_static_market_notebook_structure(path):
    notebook = nbformat.read(path, 4)
    notebook.cells = [
        c for c in notebook.cells if "colab-setup" not in c.metadata.get("tags", [])
    ]
    nbformat.validate(notebook)
    assert len(notebook.cells) == 17
    prose = "\n".join(c.source for c in notebook.cells if c.cell_type == "markdown")
    assert 750 <= len(prose.split()) <= 1200
    assert "hypothetical" in prose.lower() and "Next" in prose
    assert not any(ord(c) < 32 and c not in "\n\t" for c in prose)
    assert "/Users/" not in str(notebook)
    for i, cell in enumerate(notebook.cells):
        assert cell.cell_type == ("markdown" if i % 2 == 0 else "code")
        if cell.cell_type == "code":
            tree = ast.parse(cell.source)
            compile(tree, str(path), "exec")  # Syntax only: no cell execution.
            # Saved outputs from reader execution are valid notebook content.
            # This test parses source only; it never executes a lesson cell.
            assert not any(isinstance(node, ast.Assert) for node in ast.walk(tree))


def test_tenor_plot_retains_supplier_tail_and_negative_cash():
    rows = build_reseller_commitment_scenario(
        purchased_gpu_hours=[7200] * 36,
        supplier_usd_per_gpu_hour=[5] * 36,
        billed_fractions=[0.75] * 12 + [0] * 24,
        customer_usd_per_gpu_hour=[8] * 36,
        customer_contracted=[True] * 12 + [False] * 24,
    )
    figure = plot_finance_series(
        {"Contract-only": [r.cumulative_cash_usd for r in rows]},
        title="Commitment mismatch",
        marker_month=12,
    )
    ax = figure.axes[0]
    assert list(ax.lines[0].get_xdata()) == list(range(37))
    assert ax.lines[0].get_ydata()[12] == 86400
    assert ax.lines[0].get_ydata()[-1] == -777600
    assert ax.get_ylabel() == "USD"
    assert ax.lines[1].get_xdata() == [12, 12]
    figure.canvas.draw()


def test_forward_cost_chart_uses_benchmark_axis_and_partial_coverage(monkeypatch):
    from liquid_compute.education import explore_finance_series
    from liquid_compute.hedging import forward_settlements_usd

    prices = (3, 5, 7)

    def calculate(values):
        return {
            "Net buyer cost": [
                7200 * p
                - forward_settlements_usd(
                    benchmark_usd_per_gpu_hour=[p],
                    strike_usd_per_gpu_hour=values["Strike"],
                    hedge_gpu_hours=[values["Hours"]],
                    settlement_months=[12],
                    side="buyer",
                )[0].amount_usd
                for p in prices
            ]
        }

    fig = plot_finance_series(
        calculate({"Strike": 5, "Hours": 3600}),
        title="Partial",
        xlabel="USD/GPU-hour",
        x_values=prices,
    )
    assert list(fig.axes[0].lines[0].get_xdata()) == [3, 5, 7]
    assert list(fig.axes[0].lines[0].get_ydata()) == [28800, 36000, 43200]
    fig.canvas.draw()
    monkeypatch.setattr("IPython.display.display", lambda item: None)
    panel = explore_finance_series(
        {"Strike": 5.12345, "Hours": 7200.0},
        calculate,
        title="Control",
        x_values=prices,
    )
    assert panel.children[0].value == 5.12345
    panel.children[1].value = -1
    assert len(panel.children[-1].outputs) == 1
    panel.children[1].value = 3600
    assert "image/png" in panel.children[-1].outputs[1]["data"]
    panel.close()
    with pytest.raises(ValueError):
        plot_finance_series({"USD": [1, 2]}, title="Bad axis", x_values=[3])


def test_basis_price_axis_retains_residual_cost():
    from liquid_compute.hedging import basis_exposure_summary, forward_settlements_usd

    basis_values = (-0.5, 0, 0.5)
    settlements = forward_settlements_usd(
        benchmark_usd_per_gpu_hour=[7],
        strike_usd_per_gpu_hour=5,
        hedge_gpu_hours=[7200],
        settlement_months=[12],
        side="buyer",
    )
    costs = [
        basis_exposure_summary(
            actual_usd_per_gpu_hour=[7 + b],
            physical_gpu_hours=[7200],
            benchmark_usd_per_gpu_hour=[7],
            hedge_gpu_hours=[7200],
            strike_usd_per_gpu_hour=5,
            physical_payment_months=[12],
            settlements=settlements,
        ).net_cost_usd
        for b in basis_values
    ]
    fig = plot_finance_series(
        {"Cost": costs},
        title="Basis exposure",
        xlabel="Basis (USD/GPU-hour)",
        x_values=basis_values,
    )
    assert list(fig.axes[0].lines[0].get_xdata()) == [-0.5, 0, 0.5]
    assert list(fig.axes[0].lines[0].get_ydata()) == [32400, 36000, 39600]
    fig.canvas.draw()


def test_operating_scenario_bars_show_economic_loss_and_delay_separately():
    from liquid_compute.scenarios import OperatingScenario, evaluate_reseller_scenarios

    rows = evaluate_reseller_scenarios(
        [
            OperatingScenario("Base", 8, 5400),
            OperatingScenario("Half demand", 8, 2700),
            OperatingScenario("Delay", 8, 5400, 1),
        ],
        purchased_gpu_hours=7200,
        supplier_usd_per_gpu_hour=5,
    )
    fig = plot_finance_series(
        {"Contribution": [r.total_contribution_usd for r in rows]},
        title="Scenarios",
        bar=True,
        x_tick_labels=[r.name for r in rows],
    )
    ax = fig.axes[0]
    assert [p.get_height() for p in ax.patches] == [7200, -14400, 7200]
    assert [t.get_text() for t in ax.get_xticklabels()] == [
        "Base",
        "Half demand",
        "Delay",
    ]
    assert rows[2].funding_requirement_usd == 36000
    fig.canvas.draw()


def test_option_chart_and_choice_control_recover_independently(monkeypatch):
    from liquid_compute.education import explore_finance_series
    from liquid_compute.options import option_cash_flows

    seen = []

    def calculate(values):
        seen.append(dict(values))
        kind = values["Option"]
        amounts = []
        for price in (3, 5, 7):
            cash = option_cash_flows(
                kind=kind,
                settlement_price_usd_per_gpu_hour=price,
                strike_usd_per_gpu_hour=values["Strike"],
                covered_gpu_hours=7200,
                premium_usd_per_gpu_hour=values["Premium"],
                expiry_month=12,
            )
            option_total = sum(row.net_cash_usd for row in cash)
            amounts.append(
                7200 * price + (-option_total if kind == "call" else option_total)
            )
        return {"Nominal physical outcome": amounts}

    inputs = {"Option": "call", "Strike": 5.0, "Premium": 0.4}
    figure = plot_finance_series(
        calculate(inputs),
        title="Options",
        x_values=(3, 5, 7),
        xlabel="Benchmark (USD/GPU-hour)",
    )
    assert list(figure.axes[0].lines[0].get_ydata()) == [24480, 38880, 38880]
    figure.canvas.draw()
    monkeypatch.setattr("IPython.display.display", lambda item: None)
    panel = explore_finance_series(
        inputs,
        calculate,
        title="Options",
        x_values=(3, 5, 7),
        choices={"Option": ("call", "put")},
    )
    inputs["Option"] = "put"
    assert panel.children[0].value == "call"
    panel.children[0].value = "put"
    panel.children[2].value = 0.3
    assert seen[-1] == {"Option": "put", "Strike": 5.0, "Premium": 0.3}
    assert calculate(seen[-1])["Nominal physical outcome"] == [33840, 33840, 48240]
    panel.children[1].value = -1
    assert len(panel.children[-1].outputs) == 1
    panel.children[1].value = 5
    assert "image/png" in panel.children[-1].outputs[1]["data"]
    panel.close()
    for choices in ({"Option": ()}, {"Option": ("other",)}, {"Missing": ("call",)}):
        with pytest.raises(ValueError):
            explore_finance_series(
                inputs, calculate, title="Bad choice", choices=choices
            )


def test_proxy_tree_chart_and_invalid_model_recovery(monkeypatch):
    from liquid_compute.education import explore_finance_series
    from liquid_compute.option_valuation import binomial_european_option_tree

    def branches(values):
        tree = binomial_european_option_tree(
            kind="call",
            spot_usd_per_unit=5,
            strike_usd_per_unit=5,
            up_factor=values["Up"],
            down_factor=0.8,
            effective_annual_rate=0.05,
            step_years=1,
            steps=2,
        )
        p = tree.prices_usd_per_unit
        return {
            "Down/up": [p[0][0], p[1][0], p[2][1]],
            "Up/down": [p[0][0], p[1][1], p[2][1]],
        }

    figure = plot_finance_series(
        branches({"Up": 1.2}),
        title="Recombination",
        xlabel="Years",
        ylabel="USD per proxy unit",
        x_values=(0, 1, 2),
    )
    assert figure.axes[0].get_ylabel() == "USD per proxy unit"
    assert list(figure.axes[0].lines[0].get_ydata()) == pytest.approx([5, 4, 4.8])
    assert list(figure.axes[0].lines[1].get_ydata()) == pytest.approx([5, 6, 4.8])
    figure.canvas.draw()
    monkeypatch.setattr("IPython.display.display", lambda item: None)
    panel = explore_finance_series(
        {"Up": 1.2},
        branches,
        title="Model",
        x_values=(0, 1, 2),
        ylabel="USD per proxy unit",
    )
    assert (
        "USD per proxy unit" in panel.children[-1].outputs[0]["data"]["text/markdown"]
    )
    panel.children[0].value = 1.02
    assert "no-arbitrage" in panel.children[-1].outputs[0]["data"]["text/markdown"]
    panel.children[0].value = 1.4
    assert "image/png" in panel.children[-1].outputs[1]["data"]
    panel.close()


def test_hedge_liquidity_chart_retains_customer_lag_and_funding_peak():
    from itertools import accumulate

    from liquid_compute.cashflows import maximum_funding_requirement_usd
    from liquid_compute.collateral_liquidity import futures_variation_cash_flows

    rows = futures_variation_cash_flows(
        entry_usd_per_gpu_hour=5,
        marks_usd_per_gpu_hour=[6, 7, 5],
        hedge_gpu_hours=7200,
        mark_months=[1, 2, 3],
        side="seller",
        initial_margin_usd=5000,
    )
    cash = [r.net_cash_usd for r in rows] + [0, 36000]
    assert cash == [-5000, -7200, -7200, 19400, 0, 36000]
    assert maximum_funding_requirement_usd(cash) == 19400
    figure = plot_finance_series(
        {"Delayed receipt": list(accumulate(cash))}, title="Hedge and sale cash"
    )
    assert list(figure.axes[0].lines[0].get_xdata()) == [0, 1, 2, 3, 4, 5]
    assert list(figure.axes[0].lines[0].get_ydata()) == [
        -5000,
        -12200,
        -19400,
        0,
        0,
        36000,
    ]
    figure.canvas.draw()


def test_margin_explorer_changes_peak_without_changing_endpoint(monkeypatch):
    from liquid_compute.collateral_liquidity import futures_variation_cash_flows
    from liquid_compute.education import explore_finance_series

    calculated = []

    def calculate(values):
        rows = futures_variation_cash_flows(
            entry_usd_per_gpu_hour=5,
            marks_usd_per_gpu_hour=[6, values["Mark"], 5],
            hedge_gpu_hours=7200,
            mark_months=[1, 2, 3],
            side="seller",
            initial_margin_usd=values["Margin"],
        )
        cash = [r.cumulative_cash_usd for r in rows]
        calculated.append(cash)
        return {"Hedge cash": cash}

    monkeypatch.setattr("IPython.display.display", lambda item: None)
    panel = explore_finance_series(
        {"Mark": 7.0, "Margin": 5000.125}, calculate, title="Funding"
    )
    assert panel.children[1].value == 5000.125
    assert min(calculated[-1]) == -19400.125
    panel.children[0].value = 8
    assert min(calculated[-1]) == -26600.125
    assert calculated[-1][-1] == 0
    panel.children[1].value = -1
    assert len(panel.children[-1].outputs) == 1
    panel.children[1].value = 0
    assert min(calculated[-1]) == -21600
    assert "image/png" in panel.children[-1].outputs[1]["data"]
    panel.close()


def test_staged_cash_chart_and_fee_control_use_real_cash(monkeypatch):
    from liquid_compute.education import explore_finance_series
    from liquid_compute.option_valuation import compound_call_value
    from liquid_compute.options import staged_option_cash_flows

    seen = []

    def calculate(values):
        result = compound_call_value(
            spot_usd_per_unit=5,
            strike_usd_per_unit=5,
            up_factor=1.2,
            down_factor=0.8,
            effective_annual_rate=0.05,
            step_years=1,
            exercise_fee_usd_per_unit=values["Fee"],
        )
        rows = staged_option_cash_flows(
            premium_usd=result.premium_usd,
            exercise_fee_usd=values["Fee"],
            exercise_month=12,
            expiry_month=24,
            exercised=result.exercise_at_node[1],
            settlement_price_usd_per_unit=7.2,
            strike_usd_per_unit=5,
        )
        cash = [r.net_cash_usd for r in rows]
        seen.append(cash)
        return {"Realized cash": cash}

    figure = plot_finance_series(calculate({"Fee": 0.5}), title="Staged cash")
    cash = list(figure.axes[0].lines[0].get_ydata())
    assert cash[0] == pytest.approx(-0.48185941043)
    assert cash[12] == -0.5
    assert cash[24] == pytest.approx(2.2)
    assert sum(c != 0 for c in cash) == 3
    figure.canvas.draw()
    monkeypatch.setattr("IPython.display.display", lambda item: None)
    panel = explore_finance_series({"Fee": 0.5}, calculate, title="Staged")
    panel.children[0].value = 2
    assert all(c == 0 for c in seen[-1])
    panel.children[0].value = -1
    assert len(panel.children[-1].outputs) == 1
    panel.children[0].value = 0.5
    assert "image/png" in panel.children[-1].outputs[1]["data"]
    panel.close()


def test_revenue_share_plot_retains_payer_loss_and_fraction_controls(monkeypatch):
    from liquid_compute.education import explore_finance_series
    from liquid_compute.revenue_sharing import delivered_hour_revenue_share

    seen = []

    def calculate(values):
        rows = [
            delivered_hour_revenue_share(
                delivered_gpu_hours=7200,
                reference_usd_per_gpu_hour=p,
                guarantee_usd_per_gpu_hour=values["Guarantee"],
                supplier_upside_fraction=values["Share"],
            )
            for p in (3, 5, 7)
        ]
        seen.append(rows)
        return {
            "Supplier": [r.supplier_receipts_usd for r in rows],
            "Counterparty": [r.counterparty_net_usd for r in rows],
        }

    figure = plot_finance_series(
        calculate({"Guarantee": 4, "Share": 0.5}),
        title="Sharing",
        x_values=(3, 5, 7),
        xlabel="USD/GPU-hour",
    )
    assert list(figure.axes[0].lines[0].get_ydata()) == [28800, 32400, 39600]
    assert list(figure.axes[0].lines[1].get_ydata()) == [-7200, 3600, 10800]
    figure.canvas.draw()
    monkeypatch.setattr("IPython.display.display", lambda item: None)
    panel = explore_finance_series(
        {"Guarantee": 4.0, "Share": 0.5}, calculate, title="Sharing", x_values=(3, 5, 7)
    )
    panel.children[1].value = 1
    assert seen[-1][-1].supplier_receipts_usd == 50400
    panel.children[1].value = 1.1
    assert len(panel.children[-1].outputs) == 1
    panel.children[1].value = 0
    assert seen[-1][-1].supplier_receipts_usd == 28800
    assert "image/png" in panel.children[-1].outputs[1]["data"]
    panel.close()


def test_power_plot_and_draw_control_keep_revenue_fixed(monkeypatch):
    from liquid_compute.education import explore_finance_series
    from liquid_compute.power import electricity_cost_usd

    observed = []

    def calculate(values):
        profits = [
            21600
            - 14400
            - electricity_cost_usd(
                gpu_count=10,
                hours=720,
                it_kw_per_gpu=values["Draw"],
                facility_multiplier=1.2,
                delivered_usd_per_kwh=p,
                fixed_charge_usd=200,
            ).total_bill_usd
            for p in (0.1, 0.2)
        ]
        observed.append(profits)
        return {"Contribution": profits}

    figure = plot_finance_series(
        calculate({"Draw": 0.7}), title="Power", xlabel="USD/kWh", x_values=(0.1, 0.2)
    )
    assert list(figure.axes[0].lines[0].get_ydata()) == pytest.approx([6395.2, 5790.4])
    figure.canvas.draw()
    monkeypatch.setattr("IPython.display.display", lambda item: None)
    panel = explore_finance_series(
        {"Draw": 0.7}, calculate, title="Power", x_values=(0.1, 0.2)
    )
    panel.children[0].value = 0.45
    assert observed[-1] == pytest.approx([6611.2, 6222.4])
    panel.children[0].value = -1
    assert len(panel.children[-1].outputs) == 1
    panel.children[0].value = 0
    assert observed[-1] == [7000, 7000]
    assert "image/png" in panel.children[-1].outputs[1]["data"]
    panel.close()


def test_rate_hedge_chart_and_partial_control(monkeypatch):
    from liquid_compute.education import explore_finance_series
    from liquid_compute.floating_rates import (
        fixed_pay_swap_settlements_usd,
        floating_loan_interest_usd,
    )

    seen = []

    def calculate(values):
        if not 0 <= values["Fraction"] <= 1:
            raise ValueError("Fraction must be in [0,1]")
        combined = []
        for ref in (0.04, 0.08):
            args = dict(
                reference_rates=[ref] * 12,
                year_fractions=[1 / 12] * 12,
                payment_months=list(range(1, 13)),
            )
            loan = floating_loan_interest_usd(
                opening_principal_usd=[1e6] * 12, spread=0.03, **args
            )
            swap = fixed_pay_swap_settlements_usd(
                notional_usd=[1e6 * values["Fraction"]] * 12,
                fixed_rate=values["Fixed"],
                **args,
            )
            combined.append(
                sum(a.outflow_usd + b.outflow_usd for a, b in zip(loan, swap))
            )
        seen.append(combined)
        return {"Combined charges": combined}

    figure = plot_finance_series(
        calculate({"Fraction": 1, "Fixed": 0.05}),
        title="Rate hedge",
        x_values=(0.04, 0.08),
    )
    assert list(figure.axes[0].lines[0].get_ydata()) == pytest.approx([80000, 80000])
    figure.canvas.draw()
    monkeypatch.setattr("IPython.display.display", lambda item: None)
    panel = explore_finance_series(
        {"Fraction": 1.0, "Fixed": 0.05},
        calculate,
        title="Rate hedge",
        x_values=(0.04, 0.08),
    )
    panel.children[0].value = 0.5
    assert seen[-1] == pytest.approx([75000, 95000])
    panel.children[1].value = -0.01
    assert len(panel.children[-1].outputs) == 1
    panel.children[1].value = 0.05
    assert "image/png" in panel.children[-1].outputs[1]["data"]
    panel.close()


def test_observation_window_dates_gaps_counts_and_controls(monkeypatch):
    import math

    from liquid_compute.education import (
        explore_observation_window,
        plot_observation_window,
    )
    from liquid_compute.risk_statistics import MonthlyPrice

    january = 2025 * 12
    rows = [
        MonthlyPrice(january + i, p)
        for i, p in enumerate([10, 11, 10, 11, 10, 11, 10, 20])
    ]
    figure = plot_observation_window(rows, start_month=january, end_month=january + 6)
    ax = figure.axes[0]
    assert "n=6, omitted=0" in ax.get_title()
    assert "0.104407" in ax.get_title()
    assert ax.get_ylabel() == "USD/GPU-hour"
    assert ax.get_xticklabels()[0].get_text() == "2025-01"
    assert len(ax.patches) == 1
    figure.canvas.draw()
    missing = rows[:3] + rows[4:]
    gap_figure = plot_observation_window(
        missing, start_month=january, end_month=january + 7
    )
    assert math.isnan(gap_figure.axes[0].lines[0].get_ydata()[3])
    assert "n=5, omitted=2" in gap_figure.axes[0].get_title()
    gap_figure.canvas.draw()
    single = plot_observation_window(rows, start_month=january, end_month=january)
    assert "N/A (insufficient history)" in single.axes[0].get_title()
    monkeypatch.setattr("IPython.display.display", lambda item: None)
    panel = explore_observation_window(rows, start_month=january, end_month=january + 6)
    rows.clear()  # The panel owns an immutable snapshot.
    panel.children[0].value = january + 7
    assert "Check the window" in panel.children[-1].outputs[0]["data"]["text/markdown"]
    panel.children[1].value = january + 7
    assert "image/png" in panel.children[-1].outputs[0]["data"]
    panel.children[0].value = january + 4
    assert "image/png" in panel.children[-1].outputs[0]["data"]
    panel.close()


def test_observation_window_static_fallback_without_widgets(monkeypatch):
    import sys

    from liquid_compute.education import explore_observation_window
    from liquid_compute.risk_statistics import MonthlyPrice

    displayed = []
    monkeypatch.setattr("IPython.display.display", displayed.append)
    monkeypatch.setitem(sys.modules, "ipywidgets", None)
    result = explore_observation_window(
        [MonthlyPrice(0, 10), MonthlyPrice(1, 11)], start_month=0, end_month=1
    )
    assert result is None
    assert len(displayed) == 1
    assert "N/A" in displayed[0].axes[0].get_title()


def test_useful_output_chart_units_zero_tasks_and_controls(monkeypatch):
    from liquid_compute.education import explore_workload_mix, plot_workload_comparison
    from liquid_compute.workload_costs import useful_output_costs

    def costs(counts):
        return useful_output_costs(
            task_counts=counts,
            gpu_hours_per_task={"light": 0.005, "heavy": 0.02},
            usd_per_gpu_hour=4,
        )

    baseline = costs({"light": 8000, "heavy": 2000})
    changed = costs({"light": 5000, "heavy": 5000})
    zero = costs({"light": 0, "heavy": 0})
    figure = plot_workload_comparison(
        {"Base": baseline, "Changed": changed, "Zero": zero}
    )
    assert [p.get_height() for p in figure.axes[0].patches] == [320, 500, 0]
    assert [p.get_height() for p in figure.axes[1].patches][:2] == [0.032, 0.05]
    assert figure.axes[0].get_ylabel() == "Total spend (USD)"
    assert figure.axes[1].get_ylabel() == "USD per useful task"
    assert figure.axes[1].texts[0].get_text() == "N/A: zero tasks"
    figure.canvas.draw()
    monkeypatch.setattr("IPython.display.display", lambda item: None)
    panel = explore_workload_mix(
        task_count=10000,
        heavy_fraction=0.2,
        light_gpu_hours_per_task=0.005,
        heavy_gpu_hours_per_task=0.02,
        usd_per_gpu_hour=4,
    )
    panel.children[1].value = 0.5
    readout = panel.children[-1].outputs[0]["data"]["text/markdown"]
    assert "500.00" in readout and "0.050000" in readout
    panel.children[0].value = 0
    assert "N/A (zero tasks)" in panel.children[-1].outputs[0]["data"]["text/markdown"]
    panel.children[1].value = 1.01
    assert len(panel.children[-1].outputs) == 1
    panel.children[1].value = 0.2
    assert "image/png" in panel.children[-1].outputs[1]["data"]
    panel.close()


def test_workload_explorer_static_fallback(monkeypatch):
    import sys

    from liquid_compute.education import explore_workload_mix

    displayed = []
    monkeypatch.setattr("IPython.display.display", displayed.append)
    monkeypatch.setitem(sys.modules, "ipywidgets", None)
    panel = explore_workload_mix(
        task_count=10000,
        heavy_fraction=0.2,
        light_gpu_hours_per_task=0.005,
        heavy_gpu_hours_per_task=0.02,
        usd_per_gpu_hour=4,
    )
    assert panel is None
    assert len(displayed[0].axes) == 2


EXPECTED_TRACK_FILES = {
    "M1": "04_the_tenor_trade.ipynb",
    "M2": "M2_forwards_and_swaps.ipynb",
    "M3": "M3_benchmark_basis_risk.ipynb",
    "M4": "M4_price_quantity_scenarios.ipynb",
    "M5": "M5_calls_and_puts.ipynb",
    "M6": "M6_option_valuation.ipynb",
    "M7": "M7_hedge_collateral_liquidity.ipynb",
    "E1": "E1_compound_options.ipynb",
    "E2": "E2_minimum_revenue_shared_upside.ipynb",
    "E3": "E3_power_costs_compute_margins.ipynb",
    "E4": "E4_floating_rate_financing.ipynb",
    "E5": "E5_historical_risk_measurement.ipynb",
    "E6": "E6_cost_per_useful_output.ipynb",
}


def test_complete_market_elective_inventory_and_document_links():
    import re

    assert {p.name for p in PATHS} == set(EXPECTED_TRACK_FILES.values())
    roadmap = (ROOT / "notebooks/README.md").read_text()
    docs = [
        ROOT / "README.md",
        ROOT / "notebooks/README.md",
        ROOT / "PLANNING.md",
        ROOT / "MARKET_ELECTIVES_REVIEW.md",
    ]
    for lesson, filename in EXPECTED_TRACK_FILES.items():
        assert f"]({filename})" in roadmap
        plan = ROOT / ("PLAN_04.md" if lesson == "M1" else f"PLAN_{lesson}.md")
        record = plan.read_text()
        assert "## Implementation and coherence review" in record
        assert "deferred" in record
        docs.append(plan)
    for path in docs:
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if "://" not in target and not target.startswith("#"):
                assert (path.parent / target.split("#")[0]).exists(), (path, target)


@pytest.mark.parametrize("path", PATHS, ids=lambda p: p.stem)
def test_static_package_imports_and_direct_call_keywords(path):
    """Inspect AST and package signatures only; never execute notebook code."""
    import importlib
    import inspect

    notebook = nbformat.read(path, 4)
    notebook.cells = [
        c for c in notebook.cells if "colab-setup" not in c.metadata.get("tags", [])
    ]
    imports = {}
    trees = [ast.parse(c.source) for c in notebook.cells if c.cell_type == "code"]
    for tree in trees:
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module
                and node.module.startswith("liquid_compute")
            ):
                module = importlib.import_module(node.module)
                for alias in node.names:
                    imports[alias.asname or alias.name] = getattr(module, alias.name)
    for tree in trees:
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in imports
            ):
                signature = inspect.signature(imports[node.func.id])
                accepts_arbitrary = any(
                    p.kind == inspect.Parameter.VAR_KEYWORD
                    for p in signature.parameters.values()
                )
                if not accepts_arbitrary:
                    assert all(
                        kw.arg is None or kw.arg in signature.parameters
                        for kw in node.keywords
                    ), node.func.id
