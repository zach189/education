import pytest

from liquid_compute.option_valuation import compound_call_value
from liquid_compute.options import staged_option_cash_flows

MODEL = dict(
    spot_usd_per_unit=5,
    strike_usd_per_unit=5,
    up_factor=1.2,
    down_factor=0.8,
    effective_annual_rate=0.05,
    step_years=1,
)


def test_reference_value_and_node_exercise():
    result = compound_call_value(**MODEL, exercise_fee_usd_per_unit=0.5)
    assert result.underlying_node_values_usd == pytest.approx((0, 1.30952380952))
    assert result.exercise_at_node == (False, True)
    assert result.premium_usd == pytest.approx(0.48185941043)
    assert result.immediate_call_value_usd == pytest.approx(0.77947845805)
    assert result.premium_usd == pytest.approx(0.625 * (1.30952380952 - 0.5) / 1.05)


def test_zero_fee_equivalence_and_fee_monotonicity():
    results = [
        compound_call_value(**MODEL, exercise_fee_usd_per_unit=fee)
        for fee in (0, 0.5, 1, 2)
    ]
    assert results[0].premium_usd == results[0].immediate_call_value_usd
    assert all(a.premium_usd >= b.premium_usd for a, b in zip(results, results[1:]))
    assert results[-1].premium_usd == 0
    assert results[-1].exercise_at_node == (False, False)
    fee = results[0].underlying_node_values_usd[1]
    assert compound_call_value(
        **MODEL, exercise_fee_usd_per_unit=fee
    ).exercise_at_node == (False, False)


@pytest.mark.parametrize(
    "up_moves,exercised", [(2, True), (1, True), (1, False), (0, False)]
)
def test_realized_paths_do_not_pay_node_surplus_as_cash(up_moves, exercised):
    result = compound_call_value(**MODEL, exercise_fee_usd_per_unit=0.5)
    price = result.underlying_tree.prices_usd_per_unit[2][up_moves]
    rows = staged_option_cash_flows(
        premium_usd=result.premium_usd,
        exercise_fee_usd=0.5,
        exercise_month=12,
        expiry_month=24,
        exercised=exercised,
        settlement_price_usd_per_unit=price,
        strike_usd_per_unit=5,
    )
    assert len(rows) == 25
    assert rows[0].net_cash_usd == -result.premium_usd
    assert rows[12].net_cash_usd == (-0.5 if exercised else 0)
    assert rows[-1].net_cash_usd == pytest.approx(max(price - 5, 0) if exercised else 0)
    assert all(r.net_cash_usd == 0 for r in rows[1:12] + rows[13:24])
    assert sum(r.net_cash_usd for r in rows) == pytest.approx(
        -result.premium_usd + (-0.5 + max(price - 5, 0) if exercised else 0)
    )


def test_pricing_weighted_discounted_path_cash_is_zero():
    result = compound_call_value(**MODEL, exercise_fee_usd_per_unit=0.5)
    q = result.underlying_tree.pricing_up_weight
    expected_pv = -result.premium_usd - q * 0.5 / 1.05 + q * q * 2.2 / 1.05**2
    assert expected_pv == pytest.approx(0, abs=1e-14)


@pytest.mark.parametrize(
    "fee,error", [(-1, ValueError), (True, TypeError), (float("nan"), ValueError)]
)
def test_invalid_exercise_fee(fee, error):
    with pytest.raises(error):
        compound_call_value(**MODEL, exercise_fee_usd_per_unit=fee)


@pytest.mark.parametrize(
    "changes,error",
    [
        ({"exercise_month": 0}, ValueError),
        ({"exercise_month": 24}, ValueError),
        ({"exercise_month": True}, TypeError),
        ({"exercised": 1}, TypeError),
        ({"premium_usd": -1}, ValueError),
        ({"exercise_fee_usd": float("inf")}, ValueError),
    ],
)
def test_invalid_realized_cash(changes, error):
    args = dict(
        premium_usd=0.5,
        exercise_fee_usd=0.5,
        exercise_month=12,
        expiry_month=24,
        exercised=False,
        settlement_price_usd_per_unit=4.8,
        strike_usd_per_unit=5,
    )
    with pytest.raises(error):
        staged_option_cash_flows(**(args | changes))
