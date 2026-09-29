import pytest

from liquid_compute.option_valuation import (
    binomial_european_option_tree,
    binomial_european_option_value_usd,
    one_step_replication,
)

BASE = dict(
    spot_usd_per_unit=5,
    strike_usd_per_unit=5,
    up_factor=1.2,
    down_factor=0.8,
    effective_annual_rate=0.05,
    step_years=1,
)


@pytest.mark.parametrize("kind", ["call", "put"])
def test_replication_both_states_and_pricing_equivalence(kind):
    row = one_step_replication(kind=kind, **BASE)
    for price, payoff in (
        (row.down_price_usd, row.down_payoff_usd),
        (row.up_price_usd, row.up_payoff_usd),
    ):
        assert row.delta_units * price + row.cash_position_usd * 1.05 == pytest.approx(
            payoff
        )
    assert row.pricing_up_weight == pytest.approx(0.625)
    assert row.value_usd == pytest.approx(
        (0.625 * row.up_payoff_usd + 0.375 * row.down_payoff_usd) / 1.05
    )
    if kind == "call":
        assert row.delta_units == 0.5
        assert row.cash_position_usd == pytest.approx(-1.90476190476)
        assert row.value_usd == pytest.approx(0.595238095238)


def test_two_year_tree_terminal_payoff_and_hand_recursion():
    tree = binomial_european_option_tree(kind="call", steps=2, **BASE)
    assert tree.prices_usd_per_unit[-1] == pytest.approx((3.2, 4.8, 7.2))
    assert tree.option_values_usd[-1] == pytest.approx((0, 0, 2.2))
    up_value = 0.625 * 2.2 / 1.05
    assert tree.option_values_usd[1] == pytest.approx((0, up_value))
    assert tree.option_values_usd[0][0] == pytest.approx(0.625 * up_value / 1.05)
    assert tree.option_values_usd[0][0] == pytest.approx(0.77947845805)


@pytest.mark.parametrize("steps", [1, 2, 5])
def test_model_call_put_parity(steps):
    call = binomial_european_option_value_usd(kind="call", steps=steps, **BASE)
    put = binomial_european_option_value_usd(kind="put", steps=steps, **BASE)
    assert call - put == pytest.approx(5 - 5 / 1.05**steps)


@pytest.mark.parametrize(
    "changes,error",
    [
        ({"up_factor": 0.8}, ValueError),
        ({"down_factor": 1.05}, ValueError),
        ({"up_factor": 1.05}, ValueError),
        ({"effective_annual_rate": -0.01}, ValueError),
        ({"spot_usd_per_unit": 0}, ValueError),
        ({"strike_usd_per_unit": True}, TypeError),
        ({"step_years": 0}, ValueError),
        ({"step_years": float("inf")}, ValueError),
        ({"up_factor": "1.2"}, TypeError),
        ({"effective_annual_rate": 1e308, "step_years": 2}, ValueError),
        ({"spot_usd_per_unit": 1e308, "up_factor": 2}, ValueError),
    ],
)
def test_invalid_tree_inputs(changes, error):
    with pytest.raises(error):
        binomial_european_option_tree(kind="call", steps=2, **(BASE | changes))


@pytest.mark.parametrize(
    "steps,error", [(0, ValueError), (True, TypeError), (1.5, TypeError)]
)
def test_invalid_step_count(steps, error):
    with pytest.raises(error):
        binomial_european_option_tree(kind="call", steps=steps, **BASE)
