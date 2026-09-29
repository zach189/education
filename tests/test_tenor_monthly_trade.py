"""Price snapshots, repeated monthly sales and prepayment; no notebook execution."""

import matplotlib
import pytest

matplotlib.use("Agg")
from liquid_compute.cashflows import (
    allocate_supplier_prepayment_usd,
    maximum_funding_requirement_usd,
)
from liquid_compute.education import plot_tenor_heatmap, plot_tenor_price_snapshot
from liquid_compute.forward_curves import RentalQuote
from liquid_compute.hedging import forward_settlements_usd
from liquid_compute.tenor_trade import (
    build_reseller_commitment_scenario,
    tenor_tail_outcome,
)


def test_reported_tenor_prices_and_spreads_not_future_dates():
    quotes = [
        RentalQuote(t, p)
        for t, p in [(1, 5.30), (6, 5.15), (12, 5.05), (24, 4.60), (36, 4.25)]
    ]
    fig = plot_tenor_price_snapshot(
        quotes, on_demand_usd_per_gpu_hour=5.97, source_label="Article snapshot"
    )
    assert list(fig.axes[0].lines[0].get_ydata()) == [
        5.97,
        5.30,
        5.15,
        5.05,
        4.60,
        4.25,
    ]
    assert [p.get_height() for p in fig.axes[1].patches] == pytest.approx(
        [1.72, 1.05, 0.90, 0.80, 0.35, 0]
    )
    assert [t.get_text() for t in fig.axes[0].get_xticklabels()] == [
        "On\ndemand",
        "1M",
        "6M",
        "12M",
        "24M",
        "36M",
    ]
    assert "not future dates" in fig.axes[0].get_xlabel()
    fig.canvas.draw()


@pytest.mark.parametrize(
    "quotes,error",
    [
        ([], ValueError),
        ([RentalQuote(3, 5), RentalQuote(1, 6)], ValueError),
        ([RentalQuote(True, 5)], TypeError),
        ([RentalQuote(1, float("nan"))], ValueError),
        ([None], TypeError),
    ],
)
def test_curve_rejects_invalid_snapshots(quotes, error):
    with pytest.raises(error):
        plot_tenor_price_snapshot(
            quotes, on_demand_usd_per_gpu_hour=6, source_label="Snapshot"
        )


@pytest.mark.parametrize("fraction", [0, 0.3, 1])
def test_prepayment_is_part_of_rent_not_additional_cost(fraction):
    payments = allocate_supplier_prepayment_usd(
        [36000] * 36, prepayment_fraction=fraction
    )
    assert len(payments) == 37
    assert payments[0] == pytest.approx(1296000 * fraction)
    assert payments[1:] == pytest.approx([36000 * (1 - fraction)] * 36)
    assert sum(payments) == pytest.approx(1296000)
    cash = [-payments[0]] + [43200 - p for p in payments[1:]]
    assert sum(cash) == pytest.approx(259200)
    assert maximum_funding_requirement_usd(cash) == pytest.approx(payments[0])


def test_varying_service_expenses_receive_proportional_prepayment_credit():
    assert allocate_supplier_prepayment_usd(
        [100, 200, 0], prepayment_fraction=0.3
    ) == pytest.approx([90, 70, 140, 0])


@pytest.mark.parametrize(
    "expenses,fraction,error",
    [
        ([], 0, ValueError),
        ([True], 0, TypeError),
        ([-1], 0, ValueError),
        ([float("inf")], 0, ValueError),
        ([1e308, 1e308], 0, ValueError),
        ([1], True, TypeError),
        ([1], -0.1, ValueError),
        ([1], 1.1, ValueError),
        ([1], float("nan"), ValueError),
        ([1], "0.3", TypeError),
    ],
)
def test_prepayment_validation(expenses, fraction, error):
    with pytest.raises(error):
        allocate_supplier_prepayment_usd(expenses, prepayment_fraction=fraction)


def annual(price=6, fill=1, fee=0):
    return tenor_tail_outcome(
        upstream_commitment_usd=432000,
        contracted_revenue_usd=0,
        tail_available_gpu_hours=86400,
        future_resale_usd_per_gpu_hour=price,
        placement_fraction=fill,
        selling_fee_fraction=fee,
    )


def test_monthly_reletting_has_no_contracted_first_year_cushion():
    assert [annual(6, f).contribution_usd for f in (1, 0.9, 0.8)] == pytest.approx(
        [86400, 34560, -17280]
    )
    assert annual(5.5, 0.9).contribution_usd == pytest.approx(-4320)
    assert annual().break_even_placement_fraction == pytest.approx(5 / 6)
    assert annual(5.5).break_even_placement_fraction == pytest.approx(5 / 5.5)
    assert annual(4.5).break_even_placement_fraction > 1
    assert annual(6, fee=0.05).break_even_placement_fraction == pytest.approx(
        5 / (6 * 0.95)
    )
    rows = build_reseller_commitment_scenario(
        purchased_gpu_hours=[7200] * 36,
        supplier_usd_per_gpu_hour=[5] * 36,
        billed_fractions=[0.8] * 36,
        customer_usd_per_gpu_hour=[6] * 36,
        customer_contracted=[False] * 36,
    )
    assert all(not r.customer_contracted for r in rows)
    assert rows[-1].cumulative_cash_usd == pytest.approx(-51840)
    assert sum(r.unplaced_gpu_hours for r in rows) == pytest.approx(51840)


def test_partial_seller_hedge_and_fill_gap():
    settlements = forward_settlements_usd(
        benchmark_usd_per_gpu_hour=[3, 6, 8],
        strike_usd_per_gpu_hour=5.5,
        hedge_gpu_hours=[2400] * 3,
        settlement_months=[1, 2, 3],
        side="seller",
    )
    assert [r.amount_usd for r in settlements] == [6000, -1200, -6000]
    assert [7200 * (p - 5) + r.amount_usd for p, r in zip([3, 6, 8], settlements)] == [
        -8400,
        6000,
        15600,
    ]
    assert 7200 * 0.7 * 6 - 36000 + settlements[1].amount_usd == pytest.approx(-6960)


def test_annual_grid_labels_and_zero_initial_revenue():
    fig = plot_tenor_heatmap(
        upstream_commitment_usd=432000,
        contracted_revenue_usd=0,
        tail_available_gpu_hours=86400,
        future_resale_usd_per_gpu_hour=6,
        placement_fraction=1,
        selling_fee_fraction=0,
        period_label="Annual",
    )
    assert "Annual contribution" in fig.axes[0].get_title()
    assert "Annual contribution" in fig.axes[1].get_ylabel()
    assert fig.axes[0].collections[0].get_array().reshape(41, 49)[0, 0] == -432000
    fig.canvas.draw()
