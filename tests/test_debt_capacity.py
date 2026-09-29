import pytest

from liquid_compute.financing import (
    build_amortizing_loan_schedule,
    debt_service_coverage,
    level_payment_debt_capacity_usd,
    shape_debt_service,
)

BASE = dict(cfads_usd=[8000] * 12, minimum_dscr=1.25, nominal_annual_interest_rate=0.12)


def test_flat_capacity_and_roll_forward():
    expected = 6400 * (1 - 1.01**-12) / 0.01
    level = level_payment_debt_capacity_usd(**BASE)
    shaped = shape_debt_service(**BASE)
    assert level == pytest.approx(expected)
    assert shaped.capacity_usd == pytest.approx(level)
    assert sum(r.principal_repayment_usd for r in shaped.rows) == pytest.approx(level)
    assert shaped.rows[-1].closing_debt_usd == 0
    assert shaped.minimum_defined_dscr == pytest.approx(1.25)
    loan = build_amortizing_loan_schedule(
        principal_usd=level, nominal_annual_interest_rate=0.12, loan_term_months=12
    )
    assert all(
        r.interest_usd + r.principal_repayment_usd == pytest.approx(6400)
        for r in loan[1:]
    )


def test_uneven_feasible_and_weak_infeasible():
    inputs = BASE | dict(cfads_usd=[4000] * 6 + [12000] * 6)
    result = shape_debt_service(**inputs)
    assert result.feasible
    assert result.capacity_usd > level_payment_debt_capacity_usd(**inputs)
    assert sum(
        (r.interest_usd + r.principal_repayment_usd) / 1.01**r.month_offset
        for r in result.rows
    ) == pytest.approx(result.capacity_usd)
    weak = shape_debt_service(**(BASE | dict(cfads_usd=[0] + [8000] * 11)))
    assert not weak.feasible and weak.capacity_usd == 0 and weak.rows == ()


def test_zero_rate_coverage_monotonicity():
    assert (
        level_payment_debt_capacity_usd(**(BASE | dict(nominal_annual_interest_rate=0)))
        == 76800
    )
    assert level_payment_debt_capacity_usd(
        **(BASE | dict(minimum_dscr=1.5))
    ) < level_payment_debt_capacity_usd(**BASE)
    assert level_payment_debt_capacity_usd(
        **(BASE | dict(nominal_annual_interest_rate=0.24))
    ) < level_payment_debt_capacity_usd(**BASE)
    assert debt_service_coverage(cfads_usd=-100, debt_service_usd=20) == -5
    assert debt_service_coverage(cfads_usd=0, debt_service_usd=0) is None
    assert (
        shape_debt_service(**(BASE | dict(cfads_usd=[0] * 12))).minimum_defined_dscr
        is None
    )


@pytest.mark.parametrize(
    "changes,error",
    [
        (dict(cfads_usd=[]), ValueError),
        (dict(cfads_usd=[-1]), ValueError),
        (dict(cfads_usd=[True]), TypeError),
        (dict(minimum_dscr=0.9), ValueError),
        (dict(nominal_annual_interest_rate=float("inf")), ValueError),
    ],
)
def test_invalid(changes, error):
    with pytest.raises(error):
        level_payment_debt_capacity_usd(**(BASE | changes))
    with pytest.raises(error):
        shape_debt_service(**(BASE | changes))
