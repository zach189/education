import pytest

from liquid_compute.cashflows import (
    build_cash_flow_schedule,
    summarize_cash_flow_schedule,
)
from liquid_compute.discounting import (
    break_even_prepayment_discount_fraction,
    discount_factor,
    present_value_usd,
)


@pytest.mark.parametrize("rate", [0, 0.12, 0.24])
def test_time_zero_and_empty(rate):
    assert discount_factor(annual_discount_rate=rate, months=0) == 1
    assert present_value_usd([14400], annual_discount_rate=rate) == 14400
    assert present_value_usd([], annual_discount_rate=rate) == 0


def test_known_pvs_and_signed_amounts():
    assert discount_factor(annual_discount_rate=0.12, months=12) == pytest.approx(
        1 / 1.12
    )
    assert present_value_usd([0, 14400], annual_discount_rate=0.12) == pytest.approx(
        14264.645730379249
    )
    assert present_value_usd([14400] * 12, annual_discount_rate=0.12) == pytest.approx(
        164140.68739311228
    )
    assert present_value_usd([14400] * 12, annual_discount_rate=0.24) == pytest.approx(
        156876.0567960412
    )
    assert present_value_usd([-100, 110], annual_discount_rate=0) == 10
    assert present_value_usd([10, -20, 30], annual_discount_rate=0) == 20


@pytest.mark.parametrize("months", [1, 12, 24])
@pytest.mark.parametrize("rate", [0, 0.12, 0.24])
def test_equivalence(months, rate):
    discount = break_even_prepayment_discount_fraction(
        service_months=months, annual_discount_rate=rate
    )
    assert months * 14400 * (1 - discount) == pytest.approx(
        present_value_usd([14400] * months, annual_discount_rate=rate)
    )
    if months == 1 or rate == 0:
        assert discount == 0


def test_valuation_changes_no_contract_amounts():
    rows = build_cash_flow_schedule(
        monthly_revenue_usd=21600,
        base_monthly_rental_expense_usd=14400,
        service_months=12,
        customer_payment_lag_months=1,
    )
    before = summarize_cash_flow_schedule(rows)
    payments = [r.supplier_payments_usd for r in rows]
    assert present_value_usd(payments, annual_discount_rate=0.12) > 158976
    assert present_value_usd(payments, annual_discount_rate=0.24) < 158976
    assert summarize_cash_flow_schedule(rows) == before
    assert break_even_prepayment_discount_fraction(
        service_months=12, annual_discount_rate=0.12
    ) == pytest.approx(0.050111762771340995)
    assert break_even_prepayment_discount_fraction(
        service_months=12, annual_discount_rate=0.24
    ) == pytest.approx(0.09215244909698384)


@pytest.mark.parametrize(
    "rate,error",
    [
        (-0.01, ValueError),
        (float("inf"), ValueError),
        (float("nan"), ValueError),
        (True, TypeError),
        (".12", TypeError),
    ],
)
def test_bad_rates_including_empty(rate, error):
    with pytest.raises(error):
        discount_factor(annual_discount_rate=rate, months=0)
    with pytest.raises(error):
        present_value_usd([], annual_discount_rate=rate)
    with pytest.raises(error):
        break_even_prepayment_discount_fraction(
            service_months=12, annual_discount_rate=rate
        )


@pytest.mark.parametrize(
    "months,error", [(-1, ValueError), (1.5, TypeError), (True, TypeError)]
)
def test_bad_months(months, error):
    with pytest.raises(error):
        discount_factor(annual_discount_rate=0.12, months=months)
    with pytest.raises(error):
        break_even_prepayment_discount_fraction(
            service_months=months, annual_discount_rate=0.12
        )


@pytest.mark.parametrize(
    "value,error",
    [
        (float("nan"), ValueError),
        (float("inf"), ValueError),
        (True, TypeError),
        ("1", TypeError),
    ],
)
def test_bad_flows(value, error):
    with pytest.raises(error):
        present_value_usd([value], annual_discount_rate=0)


def test_overflow():
    with pytest.raises(ValueError):
        present_value_usd([1e308, 1e308], annual_discount_rate=0)
    with pytest.raises(ValueError):
        discount_factor(annual_discount_rate=0.12, months=10**400)


@pytest.mark.parametrize(
    "rate,pv,threshold",
    [
        (0.12, 162597.83025025515, 0.05904033419991228),
        (0.24, 154088.96002184766, 0.10828148135504823),
        (0, 172800, 0),
    ],
)
def test_month_end_valuation(rate, pv, threshold):
    value = present_value_usd([0] + [14400] * 12, annual_discount_rate=rate)
    discount = break_even_prepayment_discount_fraction(
        service_months=12,
        annual_discount_rate=rate,
        payment_timing="monthly_in_arrears",
    )
    assert value == pytest.approx(pv)
    assert discount == pytest.approx(threshold)
    assert 172800 * (1 - discount) == pytest.approx(value)


@pytest.mark.parametrize("timing,error", [(True, TypeError), ("upfront", ValueError)])
def test_invalid_regular_payment_timing(timing, error):
    with pytest.raises(error):
        break_even_prepayment_discount_fraction(
            service_months=12,
            annual_discount_rate=0.12,
            payment_timing=timing,
        )


def test_single_month_end_discount():
    assert break_even_prepayment_discount_fraction(
        service_months=1,
        annual_discount_rate=0.12,
        payment_timing="monthly_in_arrears",
    ) == pytest.approx(1 - 1.12 ** (-1 / 12))
