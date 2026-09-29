import pytest

from liquid_compute.hedging import (
    Settlement,
    combined_physical_and_hedge_cash_flows,
    forward_settlements_usd,
)


def settle(prices, hours=None, side="buyer", months=None):
    return forward_settlements_usd(
        benchmark_usd_per_gpu_hour=prices,
        strike_usd_per_gpu_hour=5,
        hedge_gpu_hours=[7200] * len(prices) if hours is None else hours,
        settlement_months=list(range(12, 12 + len(prices)))
        if months is None
        else months,
        side=side,
    )


def test_buyer_seller_zero_sum_and_exact_lock():
    for price, payoff in [(3, -14400), (5, 0), (7, 14400)]:
        buyer = settle([price])
        seller = settle([price], side="seller")
        assert buyer[0].amount_usd == payoff == -seller[0].amount_usd
        for side, settlements, expected in [
            ("buyer", buyer, -36000),
            ("seller", seller, 36000),
        ]:
            rows = combined_physical_and_hedge_cash_flows(
                physical_usd_per_gpu_hour=[price],
                physical_gpu_hours=[7200],
                physical_payment_months=[12],
                settlements=settlements,
                side=side,
            )
            assert len(rows) == 13 and rows[12].net_cash_usd == expected
            assert rows[12].physical_cash_usd + rows[12].hedge_cash_usd == expected
            assert all(r.net_cash_usd == 0 for r in rows[:12])


def test_strip_preserves_dates_even_when_total_is_zero():
    strip = settle([3, 5, 7])
    assert strip == (Settlement(12, -14400), Settlement(13, 0), Settlement(14, 14400))
    assert sum(r.amount_usd for r in strip) == 0
    rows = combined_physical_and_hedge_cash_flows(
        physical_usd_per_gpu_hour=[3, 5, 7],
        physical_gpu_hours=[7200] * 3,
        physical_payment_months=[12, 13, 14],
        settlements=strip,
        side="buyer",
    )
    assert rows[-1].cumulative_cash_usd == -108000
    assert all(r.net_cash_usd == -36000 for r in rows[12:])


def test_zero_partial_and_different_cash_dates():
    assert settle([7], hours=[0])[0].amount_usd == 0
    assert settle([7], hours=[3600])[0].amount_usd == 7200
    rows = combined_physical_and_hedge_cash_flows(
        physical_usd_per_gpu_hour=[7],
        physical_gpu_hours=[7200],
        physical_payment_months=[13],
        settlements=settle([7]),
        side="buyer",
    )
    assert rows[12].net_cash_usd == 14400 and rows[13].net_cash_usd == -50400
    assert rows[-1].cumulative_cash_usd == -36000
    unhedged = combined_physical_and_hedge_cash_flows(
        physical_usd_per_gpu_hour=[3],
        physical_gpu_hours=[0],
        physical_payment_months=[12],
        settlements=settle([3]),
        side="buyer",
    )
    assert unhedged[-1].net_cash_usd == -14400  # Hedge survives canceled physical need.


@pytest.mark.parametrize(
    "args,error",
    [
        ({"benchmark_usd_per_gpu_hour": []}, ValueError),
        ({"hedge_gpu_hours": [1, 2]}, ValueError),
        ({"settlement_months": [0]}, ValueError),
        ({"settlement_months": [True]}, TypeError),
        ({"side": "long"}, ValueError),
        ({"side": 1}, TypeError),
        ({"strike_usd_per_gpu_hour": True}, TypeError),
        ({"benchmark_usd_per_gpu_hour": [float("inf")]}, ValueError),
        ({"hedge_gpu_hours": [-1]}, ValueError),
        ({"hedge_gpu_hours": [1e308]}, ValueError),
    ],
)
def test_invalid(args, error):
    base = dict(
        benchmark_usd_per_gpu_hour=[7],
        strike_usd_per_gpu_hour=5,
        hedge_gpu_hours=[7200],
        settlement_months=[12],
        side="buyer",
    )
    with pytest.raises(error):
        forward_settlements_usd(**(base | args))


def test_order_and_malformed_settlements():
    with pytest.raises(ValueError):
        settle([3, 7], months=[12, 12])
    with pytest.raises(ValueError):
        settle([3, 7], months=[13, 12])
    base = dict(
        physical_usd_per_gpu_hour=[7],
        physical_gpu_hours=[7200],
        physical_payment_months=[12],
        side="buyer",
    )
    with pytest.raises(TypeError):
        combined_physical_and_hedge_cash_flows(**base, settlements=[(12, 1)])
    with pytest.raises(ValueError):
        combined_physical_and_hedge_cash_flows(
            **base, settlements=[Settlement(12, float("nan"))]
        )
