import pytest

from liquid_compute.floating_rates import (
    fixed_pay_swap_settlements_usd,
    floating_loan_interest_usd,
)

DATES = dict(year_fractions=[1 / 12] * 12, payment_months=list(range(1, 13)))


def values(references, notional=1e6, floor=0):
    loan = floating_loan_interest_usd(
        opening_principal_usd=[1e6] * 12,
        reference_rates=references,
        spread=0.03,
        reference_floor=floor,
        **DATES,
    )
    swap = fixed_pay_swap_settlements_usd(
        notional_usd=[notional] * 12,
        reference_rates=references,
        fixed_rate=0.05,
        **DATES,
    )
    return loan, swap


def test_baseline_high_reference_partial_and_no_hedge():
    loan, swap = values([0.04] * 6 + [0.06] * 6)
    assert sum(r.outflow_usd for r in loan) == pytest.approx(80000)
    assert sum(r.outflow_usd for r in swap) == pytest.approx(0, abs=1e-10)
    for notional, hedge_total, combined in (
        (1e6, -30000, 80000),
        (5e5, -15000, 95000),
        (0, 0, 110000),
    ):
        loan, swap = values([0.08] * 12, notional)
        assert sum(r.outflow_usd for r in loan) == pytest.approx(110000)
        assert sum(r.outflow_usd for r in swap) == pytest.approx(hedge_total)
        assert sum(
            a.outflow_usd + b.outflow_usd for a, b in zip(loan, swap)
        ) == pytest.approx(combined)


def test_floor_mismatch_and_separate_principal():
    loan, swap = values([0.04] * 12, floor=0.05)
    assert sum(r.outflow_usd for r in loan) == pytest.approx(80000)
    assert sum(r.outflow_usd for r in swap) == pytest.approx(10000)
    principal_payments = [0] * 11 + [1e6]
    total = sum(
        a.outflow_usd + b.outflow_usd + principal
        for a, b, principal in zip(loan, swap, principal_payments)
    )
    assert total == pytest.approx(1090000)
    assert sum(principal_payments) == 1e6


def test_zero_rate_and_explicit_unequal_accruals_and_dates():
    zero = floating_loan_interest_usd(
        opening_principal_usd=[100],
        reference_rates=[0],
        spread=0,
        year_fractions=[0.25],
        payment_months=[3],
    )
    assert zero[0].outflow_usd == 0
    loan = floating_loan_interest_usd(
        opening_principal_usd=[100, 50],
        reference_rates=[0.1, 0.2],
        spread=0,
        year_fractions=[0.25, 0.5],
        payment_months=[3, 9],
    )
    assert [(r.payment_month, r.outflow_usd) for r in loan] == [(3, 2.5), (9, 5)]


@pytest.mark.parametrize(
    "changes,error",
    [
        ({"reference_rates": []}, ValueError),
        ({"reference_rates": [-1]}, ValueError),
        ({"year_fractions": [0]}, ValueError),
        ({"payment_months": [0]}, ValueError),
        ({"payment_months": [True]}, TypeError),
        ({"reference_rates": [True]}, TypeError),
        ({"reference_rates": [float("inf")]}, ValueError),
        ({"year_fractions": [1e308]}, ValueError),
    ],
)
def test_period_validation(changes, error):
    args = (
        dict(reference_rates=[0.04], year_fractions=[1 / 12], payment_months=[1])
        | changes
    )
    with pytest.raises(error):
        floating_loan_interest_usd(opening_principal_usd=[1e6], spread=0.03, **args)
    with pytest.raises(error):
        fixed_pay_swap_settlements_usd(notional_usd=[1e6], fixed_rate=0.05, **args)


def test_spread_floor_fixed_validation_and_dates():
    args = dict(reference_rates=[0.04], year_fractions=[1 / 12], payment_months=[1])
    for field in ("spread", "reference_floor"):
        with pytest.raises(ValueError):
            floating_loan_interest_usd(
                opening_principal_usd=[100], **args, **({"spread": 0.03} | {field: -1})
            )
    with pytest.raises(ValueError):
        fixed_pay_swap_settlements_usd(notional_usd=[100], fixed_rate=-0.01, **args)
    with pytest.raises(ValueError):
        fixed_pay_swap_settlements_usd(
            notional_usd=[100, 100],
            fixed_rate=0.05,
            reference_rates=[0.04, 0.04],
            year_fractions=[0.1, 0.1],
            payment_months=[1, 1],
        )
