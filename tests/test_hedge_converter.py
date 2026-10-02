"""Independent source reconciliation and business invariants for hedge sizing."""

import pytest

from liquid_compute.hedge_converter import (
    buyer_hedge_terms,
    lender_hedge_terms,
    lessor_hedge_terms,
    operator_hedge_terms,
)
from liquid_compute.options import european_option_payoff_usd


def lender(**changes):
    inputs = dict(
        contract_usd_per_gpu_hour=2.5,
        prepaid_usd=10_000_000,
        advance_fraction=0.8,
        remarketing_fee_fraction=0.1,
    )
    return lender_hedge_terms(**(inputs | changes))


def lessor(**changes):
    inputs = dict(
        gpu_count=512,
        residual_usd_per_gpu=8000,
        relet_months=12,
        utilization_fraction=0.7,
        opex_usd_per_billed_gpu_hour=0.4,
    )
    return lessor_hedge_terms(**(inputs | changes))


def test_source_workbook_values():
    a, b = lender(), lessor()
    c = operator_hedge_terms(
        gpu_count=1024,
        months=12,
        utilization_fraction=0.8,
        breakeven_usd_per_gpu_hour=1.95,
    )
    d = buyer_hedge_terms(gpu_count=256, months=12, budget_usd_per_gpu_hour=3)
    assert [a.kind, b.kind, c.kind, d.kind] == ["put", "put", "put", "call"]
    assert [x.strike_usd_per_gpu_hour for x in (a, b, c, d)] == pytest.approx(
        [2.222222222222222, 1.704631441617743, 1.95, 3]
    )
    assert [x.notional_gpu_hours for x in (a, b, c, d)] == pytest.approx(
        [3_600_000, 3_139_584, 7_176_192, 2_242_560]
    )
    assert b.strike_usd_per_gpu_hour * b.notional_gpu_hours == pytest.approx(
        5_351_833.6
    )


@pytest.mark.parametrize("price", [0, 1.8, 2.222222222222222, 4])
def test_lender_offsets_principal_shortfall_only_when_matched(price):
    terms = lender()
    payoff = european_option_payoff_usd(
        kind=terms.kind,
        settlement_price_usd_per_gpu_hour=price,
        strike_usd_per_gpu_hour=terms.strike_usd_per_gpu_hour,
        covered_gpu_hours=terms.notional_gpu_hours,
    )
    assert payoff == pytest.approx(max(8_000_000 - price * 3_600_000, 0), abs=1e-8)


def test_lessor_target_and_quantity_scaling():
    terms = lessor()
    assert (
        terms.strike_usd_per_gpu_hour - 0.4
    ) * terms.notional_gpu_hours == pytest.approx(4_096_000)
    doubled = lessor(gpu_count=1024)
    assert doubled.strike_usd_per_gpu_hour == terms.strike_usd_per_gpu_hour
    assert doubled.notional_gpu_hours == 2 * terms.notional_gpu_hours
    assert (
        lessor(utilization_fraction=0.35).strike_usd_per_gpu_hour
        > terms.strike_usd_per_gpu_hour
    )


def test_zero_and_full_boundaries():
    assert lender(advance_fraction=0).strike_usd_per_gpu_hour == 0
    assert lender(prepaid_usd=0).notional_gpu_hours == 0
    assert (
        lender(advance_fraction=1, remarketing_fee_fraction=0).strike_usd_per_gpu_hour
        == 2.5
    )
    assert lessor(gpu_count=0).notional_gpu_hours == 0
    assert (
        operator_hedge_terms(
            gpu_count=1, months=1, utilization_fraction=0, breakeven_usd_per_gpu_hour=0
        ).notional_gpu_hours
        == 0
    )
    assert (
        buyer_hedge_terms(
            gpu_count=1, months=1, budget_usd_per_gpu_hour=0, hours_per_gpu_month=720
        ).notional_gpu_hours
        == 720
    )


@pytest.mark.parametrize(
    "key,value,error",
    [
        ("contract_usd_per_gpu_hour", 0, ValueError),
        ("contract_usd_per_gpu_hour", True, TypeError),
        ("prepaid_usd", "100", TypeError),
        ("prepaid_usd", -1, ValueError),
        ("advance_fraction", 1.01, ValueError),
        ("advance_fraction", float("nan"), ValueError),
        ("remarketing_fee_fraction", 1, ValueError),
        ("remarketing_fee_fraction", -0.1, ValueError),
        ("prepaid_usd", float("inf"), ValueError),
        ("contract_usd_per_gpu_hour", 1e-308, ValueError),
    ],
)
def test_invalid_lender(key, value, error):
    with pytest.raises(error):
        lender(**{key: value})


@pytest.mark.parametrize(
    "key,value,error",
    [
        ("gpu_count", True, TypeError),
        ("gpu_count", 1.2, TypeError),
        ("gpu_count", -1, ValueError),
        ("relet_months", 0, ValueError),
        ("relet_months", 1.5, TypeError),
        ("utilization_fraction", 0, ValueError),
        ("utilization_fraction", 1.1, ValueError),
        ("residual_usd_per_gpu", -1, ValueError),
        ("opex_usd_per_billed_gpu_hour", float("nan"), ValueError),
        ("hours_per_gpu_month", 0, ValueError),
        ("hours_per_gpu_month", 1e308, ValueError),
    ],
)
def test_invalid_lessor(key, value, error):
    with pytest.raises(error):
        lessor(**{key: value})


def test_operator_and_buyer_reject_invalid_inputs():
    for changes in ({"gpu_count": 10**400}, {"months": 10**400}):
        with pytest.raises(ValueError):
            buyer_hedge_terms(
                **(dict(gpu_count=1, months=1, budget_usd_per_gpu_hour=1) | changes)
            )
    with pytest.raises(ValueError):
        operator_hedge_terms(
            gpu_count=1,
            months=1,
            utilization_fraction=1.1,
            breakeven_usd_per_gpu_hour=1,
        )
    with pytest.raises(TypeError):
        buyer_hedge_terms(gpu_count=1, months=True, budget_usd_per_gpu_hour=1)
    with pytest.raises(ValueError):
        buyer_hedge_terms(gpu_count=1, months=1, budget_usd_per_gpu_hour=-1)
