from dataclasses import FrozenInstanceError

import pytest

from liquid_compute.cashflows import (
    build_cash_flow_schedule,
    maximum_funding_requirement_usd,
    summarize_cash_flow_schedule,
)

BASE = dict(
    monthly_revenue_usd=21600,
    base_monthly_rental_expense_usd=14400,
    service_months=12,
    customer_payment_lag_months=1,
)


def test_baseline_and_prepaid_allocation():
    monthly = build_cash_flow_schedule(**BASE)
    upfront = build_cash_flow_schedule(
        **BASE, supplier_terms="upfront", prepayment_discount_fraction=0.08
    )
    assert [r.cumulative_cash_usd for r in monthly[:3]] == [-14400, -28800, -21600]
    assert monthly[0].service_rental_expense_usd == 0
    assert upfront[0].service_rental_expense_usd == 0
    assert upfront[0].supplier_payments_usd == 158976
    assert all(r.service_rental_expense_usd == 13248 for r in upfront[1:13])
    assert all(r.supplier_payments_usd == 0 for r in upfront[1:])
    for schedule, rent, profit, funding in [
        (monthly, 172800, 86400, 28800),
        (upfront, 158976, 100224, 158976),
    ]:
        summary = summarize_cash_flow_schedule(schedule)
        assert summary.service_revenue_usd == 259200
        assert summary.service_rental_expense_usd == rent
        assert summary.contribution_profit_usd == profit
        assert summary.maximum_funding_requirement_usd == funding
        assert schedule[-1].cumulative_cash_usd == profit
        assert sum(r.customer_receipts_usd for r in schedule) == 259200


@pytest.mark.parametrize(
    "lag,funding", [(0, 14400), (1, 28800), (2, 43200), (15, 172800)]
)
def test_all_receipts_and_timing_only(lag, funding):
    monthly = build_cash_flow_schedule(**(BASE | {"customer_payment_lag_months": lag}))
    upfront = build_cash_flow_schedule(
        **(BASE | {"customer_payment_lag_months": lag}), supplier_terms="upfront"
    )
    assert [r.month_offset for r in monthly if r.customer_receipts_usd] == list(
        range(1 + lag, 13 + lag)
    )
    assert len(monthly) == 13 + lag
    assert monthly[-1].customer_receipts_usd == 21600
    assert monthly[-1].service_revenue_usd == (21600 if lag == 0 else 0)
    assert (
        summarize_cash_flow_schedule(monthly).maximum_funding_requirement_usd == funding
    )
    assert (
        summarize_cash_flow_schedule(upfront).maximum_funding_requirement_usd == 172800
    )
    assert summarize_cash_flow_schedule(monthly).contribution_profit_usd == 86400
    assert monthly[-1].cumulative_cash_usd == upfront[-1].cumulative_cash_usd == 86400


@pytest.mark.parametrize(
    "flows,funding",
    [
        ([], 0),
        ([1, 2, 3], 0),
        ([-10, 20, -30], 20),
        ([20, -5, -10], 0),
        ([-10, -10, 30], 20),
    ],
)
def test_funding_includes_opening_zero(flows, funding):
    assert maximum_funding_requirement_usd(flows) == funding


def test_zero_revenue_and_single_month():
    zero = build_cash_flow_schedule(**(BASE | {"monthly_revenue_usd": 0}))
    assert summarize_cash_flow_schedule(zero).maximum_funding_requirement_usd == 172800
    one = build_cash_flow_schedule(
        **(BASE | {"service_months": 1, "customer_payment_lag_months": 0})
    )
    assert len(one) == 2
    assert one[0].supplier_payments_usd == 14400
    assert one[1].supplier_payments_usd == 0
    assert one[1].customer_receipts_usd == 21600
    with pytest.raises(FrozenInstanceError):
        one[0].month_offset = 4


@pytest.mark.parametrize(
    "name,value,error",
    [
        ("monthly_revenue_usd", -1, ValueError),
        ("monthly_revenue_usd", True, TypeError),
        ("base_monthly_rental_expense_usd", 0, ValueError),
        ("base_monthly_rental_expense_usd", float("inf"), ValueError),
        ("service_months", 0, ValueError),
        ("service_months", 1.5, TypeError),
        ("service_months", True, TypeError),
        ("customer_payment_lag_months", -1, ValueError),
        ("customer_payment_lag_months", 0.5, TypeError),
        ("supplier_terms", "later", ValueError),
        ("supplier_terms", False, TypeError),
        (
            "prepayment_discount_fraction",
            0.1,
            ValueError,
        ),  # cannot discount monthly terms
        ("monthly_revenue_usd", float("nan"), ValueError),
        ("monthly_revenue_usd", "21600", TypeError),
    ],
)
def test_bad_schedule_inputs(name, value, error):
    with pytest.raises(error):
        build_cash_flow_schedule(**(BASE | {name: value}))


@pytest.mark.parametrize(
    "discount,error",
    [
        (-0.1, ValueError),
        (1, ValueError),
        (float("nan"), ValueError),
        (float("inf"), ValueError),
        (True, TypeError),
        (".1", TypeError),
    ],
)
def test_invalid_prepaid_discounts(discount, error):
    with pytest.raises(error):
        build_cash_flow_schedule(
            **BASE, supplier_terms="upfront", prepayment_discount_fraction=discount
        )


@pytest.mark.parametrize(
    "value,error",
    [
        (True, TypeError),
        ("2", TypeError),
        (float("nan"), ValueError),
        (float("inf"), ValueError),
    ],
)
def test_funding_validation(value, error):
    with pytest.raises(error):
        maximum_funding_requirement_usd([value])


def test_overflow_and_empty_summary():
    with pytest.raises(ValueError):
        build_cash_flow_schedule(**(BASE | {"monthly_revenue_usd": 1e308}))
    with pytest.raises(ValueError):
        build_cash_flow_schedule(**(BASE | {"base_monthly_rental_expense_usd": 1e308}))
    with pytest.raises(ValueError):
        maximum_funding_requirement_usd([-1e308, -1e308])
    assert summarize_cash_flow_schedule([]).contribution_profit_usd == 0


@pytest.mark.parametrize(
    "supplier,customer,lag,funding",
    [
        ("monthly_in_arrears", "monthly_in_arrears", 0, 0),
        ("monthly_in_advance", "monthly_in_arrears", 0, 14400),
        ("monthly_in_advance", "monthly_in_arrears", 1, 28800),
        ("monthly_in_advance", "upfront", 0, 0),
    ],
)
def test_payment_arrangements(supplier, customer, lag, funding):
    rows = build_cash_flow_schedule(
        monthly_revenue_usd=21600,
        base_monthly_rental_expense_usd=14400,
        service_months=12,
        customer_payment_lag_months=lag,
        supplier_terms=supplier,
        customer_terms=customer,
    )
    assert (
        maximum_funding_requirement_usd([r.net_cash_flow_usd for r in rows]) == funding
    )
    assert rows[-1].cumulative_cash_usd == 86400
    assert (
        sum(r.service_revenue_usd - r.service_rental_expense_usd for r in rows) == 86400
    )
    assert rows[0].service_revenue_usd == rows[0].service_rental_expense_usd == 0
    if supplier == "monthly_in_arrears":
        assert [r.month_offset for r in rows if r.supplier_payments_usd] == list(
            range(1, 13)
        )
    if customer == "upfront":
        assert rows[0].customer_receipts_usd == 259200
        assert all(r.customer_receipts_usd == 0 for r in rows[1:])


@pytest.mark.parametrize(
    "extra,error",
    [
        ({"customer_terms": True}, TypeError),
        ({"customer_terms": "unknown"}, ValueError),
        ({"customer_terms": "upfront", "customer_payment_lag_months": 1}, ValueError),
        (
            {
                "supplier_terms": "monthly_in_arrears",
                "prepayment_discount_fraction": 0.08,
            },
            ValueError,
        ),
    ],
)
def test_new_terms_validation(extra, error):
    inputs = dict(
        monthly_revenue_usd=21600,
        base_monthly_rental_expense_usd=14400,
        service_months=12,
        customer_payment_lag_months=0,
    )
    inputs.update(extra)
    with pytest.raises(error):
        build_cash_flow_schedule(**inputs)


def test_zero_funding_displays_without_negative_sign():
    assert f"{maximum_funding_requirement_usd([0, 7200]):.2f}" == "0.00"
