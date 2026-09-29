import pytest

from liquid_compute.hedging import Settlement, combined_physical_and_hedge_cash_flows
from liquid_compute.options import european_option_payoff_usd, option_cash_flows

BASE = dict(strike_usd_per_gpu_hour=5, covered_gpu_hours=7200)


@pytest.mark.parametrize(
    "kind,price,payoff",
    [
        ("call", 3, 0),
        ("call", 5, 0),
        ("call", 7, 14400),
        ("put", 3, 14400),
        ("put", 5, 0),
        ("put", 7, 0),
    ],
)
def test_gross_payoff(kind, price, payoff):
    assert (
        european_option_payoff_usd(
            kind=kind, settlement_price_usd_per_gpu_hour=price, **BASE
        )
        == payoff
    )


def test_holder_writer_cash_and_premium_once():
    args = dict(
        kind="call",
        settlement_price_usd_per_gpu_hour=7,
        premium_usd_per_gpu_hour=0.4,
        expiry_month=12,
        **BASE,
    )
    long = option_cash_flows(**args)
    short = option_cash_flows(**args, position="short")
    assert long[0].premium_cash_usd == -2880
    assert long[-1].payoff_cash_usd == 14400
    assert sum(r.net_cash_usd for r in long) == 11520
    assert all(a.net_cash_usd == -b.net_cash_usd for a, b in zip(long, short))
    assert all(r.net_cash_usd == 0 for r in long[1:12])


def test_matched_caps_floors_partial_and_basis():
    for price, call_cost, put_receipt in [
        (3, 24480, 33840),
        (5, 38880, 33840),
        (7, 38880, 48240),
    ]:
        call = option_cash_flows(
            kind="call",
            settlement_price_usd_per_gpu_hour=price,
            premium_usd_per_gpu_hour=0.4,
            expiry_month=12,
            **BASE,
        )
        put = option_cash_flows(
            kind="put",
            settlement_price_usd_per_gpu_hour=price,
            premium_usd_per_gpu_hour=0.3,
            expiry_month=12,
            **BASE,
        )
        buyer = combined_physical_and_hedge_cash_flows(
            physical_usd_per_gpu_hour=[price],
            physical_gpu_hours=[7200],
            physical_payment_months=[12],
            settlements=[Settlement(12, call[-1].payoff_cash_usd)],
            side="buyer",
        )
        assert -buyer[-1].net_cash_usd - call[0].premium_cash_usd == call_cost
        assert 7200 * price + sum(r.net_cash_usd for r in put) == put_receipt
    half = option_cash_flows(
        kind="call",
        settlement_price_usd_per_gpu_hour=7,
        strike_usd_per_gpu_hour=5,
        covered_gpu_hours=3600,
        premium_usd_per_gpu_hour=0.4,
        expiry_month=12,
    )
    assert 7200 * 7 - sum(r.net_cash_usd for r in half) == 44640
    assert 7200 * 7.5 - 14400 + 2880 == 42480


def test_zero_boundaries_and_invalid_values():
    assert (
        european_option_payoff_usd(
            kind="call",
            settlement_price_usd_per_gpu_hour=7,
            strike_usd_per_gpu_hour=0,
            covered_gpu_hours=1,
        )
        == 7
    )
    zero = option_cash_flows(
        kind="put",
        settlement_price_usd_per_gpu_hour=3,
        strike_usd_per_gpu_hour=5,
        covered_gpu_hours=0,
        premium_usd_per_gpu_hour=0,
        expiry_month=1,
    )
    assert all(r.net_cash_usd == 0 for r in zero)
    for value, error in [
        (True, TypeError),
        (-1, ValueError),
        (float("nan"), ValueError),
    ]:
        with pytest.raises(error):
            european_option_payoff_usd(
                kind="call", settlement_price_usd_per_gpu_hour=value, **BASE
            )
    with pytest.raises(ValueError):
        european_option_payoff_usd(
            kind="call", settlement_price_usd_per_gpu_hour=1e308, **BASE
        )
    with pytest.raises(ValueError):
        european_option_payoff_usd(
            kind="other", settlement_price_usd_per_gpu_hour=7, **BASE
        )
    with pytest.raises(TypeError):
        option_cash_flows(
            kind="call",
            settlement_price_usd_per_gpu_hour=7,
            premium_usd_per_gpu_hour=0.4,
            expiry_month=True,
            **BASE,
        )
