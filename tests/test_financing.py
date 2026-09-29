from dataclasses import replace
from math import fsum

import pytest

from liquid_compute.cashflows import build_cash_flow_schedule
from liquid_compute.discounting import present_value_usd
from liquid_compute.financing import (
    build_amortizing_loan_schedule,
    combine_financing_cash_flows,
    compare_prepayment_financing,
    financed_prepayment_break_even_discount_fraction,
    net_procurement_outflows_usd,
    summarize_financing_cash_flows,
)

BASE = dict(
    monthly_revenue_usd=21600,
    base_monthly_rental_expense_usd=14400,
    service_months=12,
    customer_payment_lag_months=1,
    prepayment_discount_fraction=0.08,
    financed_fraction=0.8,
    nominal_annual_interest_rate=0.12,
    loan_term_months=12,
    origination_fee_fraction=0.02,
)


def loan(**changes):
    return build_amortizing_loan_schedule(
        **(
            dict(
                principal_usd=127180.8,
                nominal_annual_interest_rate=0.12,
                loan_term_months=12,
                origination_fee_fraction=0.02,
            )
            | changes
        )
    )


@pytest.mark.parametrize("rate", [0, 1e-14, 0.12, 0.24])
def test_amortization_and_rollforward(rate):
    rows = loan(nominal_annual_interest_rate=rate)
    assert rows[0].loan_draw_usd == 127180.8
    assert rows[0].fee_usd == pytest.approx(2543.616)
    assert rows[0].principal_repayment_usd == 0
    assert sum(r.fee_usd for r in rows[1:]) == 0
    assert sum(r.principal_repayment_usd for r in rows) == pytest.approx(127180.8)
    for r in rows:
        assert (
            r.opening_debt_usd + r.loan_draw_usd - r.principal_repayment_usd
            == pytest.approx(r.closing_debt_usd)
        )
    payments = [r.interest_usd + r.principal_repayment_usd for r in rows[1:]]
    assert payments == pytest.approx([payments[0]] * 12)
    assert rows[-1].closing_debt_usd == 0
    if rate == 0:
        assert payments[0] == pytest.approx(127180.8 / 12)
        assert sum(r.interest_usd for r in rows) == 0


def test_zero_loan():
    rows = loan(principal_usd=0)
    assert all(
        r.closing_debt_usd
        == r.loan_draw_usd
        == r.fee_usd
        == r.interest_usd
        == r.principal_repayment_usd
        == 0
        for r in rows
    )


def test_baseline_cost_cash_and_no_double_counting():
    alternatives = compare_prepayment_financing(**BASE)
    expected = [
        (172800, 0, 28800, 14400, 164140.68739311228),
        (158976, 0, 158976, 158976, 158976),
        (158976, 10961.136277709, 45638.676023142, 34338.816, 161931.366131566),
    ]
    for rows, (supplier, charges, buffer, initial, pv) in zip(
        alternatives.values(), expected
    ):
        s = summarize_financing_cash_flows(rows)
        assert s.supplier_cost_usd == pytest.approx(supplier)
        assert s.interest_usd + s.fees_usd == pytest.approx(charges)
        assert s.required_initial_cash_buffer_usd == pytest.approx(buffer)
        assert s.initial_own_cash_usd == pytest.approx(initial)
        costs = net_procurement_outflows_usd(rows)
        assert sum(costs) == pytest.approx(s.combined_cost_usd)
        assert present_value_usd(costs, annual_discount_rate=0.12) == pytest.approx(pv)
        assert [r.customer_receipts_usd for r in rows] == [0, 0] + [21600] * 12
        assert rows[-1].cumulative_cash_usd == pytest.approx(
            259200 - s.combined_cost_usd
        )
    borrowed = alternatives["Borrowed prepayment"]
    assert [r.cumulative_cash_usd for r in borrowed[:3]] == pytest.approx(
        [-34338.816, -45638.676023142, -35338.536046284]
    )
    assert borrowed[0].supplier_payments_usd == 158976
    assert sum(r.supplier_payments_usd for r in borrowed[1:]) == 0


def test_zero_full_financing_and_later_need():
    zero = compare_prepayment_financing(**(BASE | {"financed_fraction": 0}))
    assert zero["Own-cash prepayment"] == zero["Borrowed prepayment"]
    full = compare_prepayment_financing(
        **(BASE | {"financed_fraction": 1, "origination_fee_fraction": 0})
    )["Borrowed prepayment"]
    summary = summarize_financing_cash_flows(full)
    assert summary.initial_own_cash_usd == 0
    assert summary.required_initial_cash_buffer_usd == pytest.approx(14124.825028928)


def test_longer_loan_and_no_funding_deficit():
    rows = compare_prepayment_financing(**(BASE | {"loan_term_months": 24}))[
        "Borrowed prepayment"
    ]
    assert rows[-1].month_offset == 24
    assert rows[13].customer_receipts_usd == 21600
    assert sum(r.customer_receipts_usd for r in rows[14:]) == 0
    assert rows[-1].closing_debt_usd == 0
    rows = compare_prepayment_financing(
        **(
            BASE
            | {
                "customer_payment_lag_months": 0,
                "financed_fraction": 1,
                "origination_fee_fraction": 0,
            }
        )
    )["Borrowed prepayment"]
    assert summarize_financing_cash_flows(rows).required_initial_cash_buffer_usd == 0


@pytest.mark.parametrize(
    "measure,expected",
    [("undiscounted", 0.06450112387322193), ("present_value", 0.06744791939215322)],
)
def test_break_even_reconciles(measure, expected):
    terms = {
        k: BASE[k]
        for k in [
            "service_months",
            "loan_term_months",
            "financed_fraction",
            "nominal_annual_interest_rate",
            "origination_fee_fraction",
        ]
    }
    discount = financed_prepayment_break_even_discount_fraction(
        **terms, cost_measure=measure, annual_discount_rate=0.12
    )
    assert discount == pytest.approx(expected)
    alternatives = compare_prepayment_financing(
        **(BASE | {"prepayment_discount_fraction": discount})
    )
    rate = 0 if measure == "undiscounted" else 0.12
    values = [
        present_value_usd(
            net_procurement_outflows_usd(alternatives[name]), annual_discount_rate=rate
        )
        for name in ["Monthly", "Borrowed prepayment"]
    ]
    assert values[0] == pytest.approx(values[1])
    zero = [
        financed_prepayment_break_even_discount_fraction(
            **terms, cost_measure=m, annual_discount_rate=0
        )
        for m in ["undiscounted", "present_value"]
    ]
    assert zero[0] == pytest.approx(zero[1])


@pytest.mark.parametrize(
    "key,value,error",
    [
        ("principal_usd", True, TypeError),
        ("principal_usd", -1, ValueError),
        ("principal_usd", float("inf"), ValueError),
        ("nominal_annual_interest_rate", -1, ValueError),
        ("nominal_annual_interest_rate", "12", TypeError),
        ("origination_fee_fraction", 1, ValueError),
        ("origination_fee_fraction", float("nan"), ValueError),
        ("loan_term_months", 0, ValueError),
        ("loan_term_months", True, TypeError),
        ("loan_term_months", 12.0, TypeError),
    ],
)
def test_invalid_loan(key, value, error):
    with pytest.raises(error):
        loan(**{key: value})


@pytest.mark.parametrize(
    "changes",
    [
        {"financed_fraction": 1.1},
        {"financed_fraction": -1},
        {"prepayment_discount_fraction": 1},
    ],
)
def test_invalid_comparison(changes):
    with pytest.raises(ValueError):
        compare_prepayment_financing(**(BASE | changes))


def test_invalid_rows_and_overflow():
    contract = build_cash_flow_schedule(
        monthly_revenue_usd=1,
        base_monthly_rental_expense_usd=1,
        service_months=12,
        customer_payment_lag_months=0,
    )
    rows = loan()
    for bad in [
        (),
        rows[1:],
        (replace(rows[0], closing_debt_usd=9),) + rows[1:],
        rows[:-1],
    ]:
        with pytest.raises(ValueError):
            combine_financing_cash_flows(contract_schedule=contract, loan_schedule=bad)
    with pytest.raises(ValueError):
        loan(principal_usd=1e308, nominal_annual_interest_rate=1e308)
    result = compare_prepayment_financing(**BASE)["Monthly"]
    with pytest.raises(ValueError):
        summarize_financing_cash_flows(
            (replace(result[0], cumulative_cash_usd=99),) + result[1:]
        )
    with pytest.raises(ValueError):
        net_procurement_outflows_usd(
            (replace(result[0], interest_usd=float("nan")),) + result[1:]
        )


def test_discount_rate_only_affects_valuation():
    rows = compare_prepayment_financing(**BASE)["Borrowed prepayment"]
    before = summarize_financing_cash_flows(rows)
    costs = net_procurement_outflows_usd(rows)
    assert present_value_usd(costs, annual_discount_rate=0) == pytest.approx(
        fsum(costs)
    )
    assert present_value_usd(costs, annual_discount_rate=0.24) < present_value_usd(
        costs, annual_discount_rate=0.12
    )
    assert summarize_financing_cash_flows(rows) == before
