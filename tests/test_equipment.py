import pytest

from liquid_compute.equipment import (
    compare_purchase_lease_cash_flows,
    financed_equipment_exit,
    straight_line_book_values,
)
from liquid_compute.financing import build_amortizing_loan_schedule

BASE = dict(
    purchase_price_usd=300000,
    lease_payments_usd=(8000,) * 36,
    exit_month=36,
    resale_proceeds_usd=60000,
    has_resale_rights=True,
    annual_discount_rate=0.12,
)


def test_nominal_pv_and_no_lease_sale():
    result = compare_purchase_lease_cash_flows(**BASE)
    assert (
        result.purchase_nominal_cost_usd == 240000
        and result.lease_nominal_cost_usd == 288000
    )
    assert result.purchase_pv_cost_usd == pytest.approx(300000 - 60000 / 1.12**3)
    assert result.lease_pv_cost_usd == pytest.approx(
        sum(8000 / 1.12 ** (m / 12) for m in range(1, 37))
    )
    zero = compare_purchase_lease_cash_flows(**(BASE | dict(annual_discount_rate=0)))
    assert zero.purchase_pv_cost_usd == 240000
    assert result.lease_outflows_usd[-1] == 8000


def test_exit_after_payment_and_no_tail():
    result = financed_equipment_exit(
        purchase_price_usd=300000,
        loan_principal_usd=210000,
        nominal_annual_interest_rate=0.10,
        loan_term_months=48,
        sale_month=36,
        sale_proceeds_usd=20000,
    )
    loan = build_amortizing_loan_schedule(
        principal_usd=210000, nominal_annual_interest_rate=0.10, loan_term_months=48
    )
    assert len(result.owner_outflows_usd) == 37
    assert result.debt_payoff_usd == loan[36].closing_debt_usd
    assert result.equity_from_sale_usd < 0
    assert result.owner_outflows_usd[-1] == pytest.approx(
        loan[36].interest_usd
        + loan[36].principal_repayment_usd
        + loan[36].closing_debt_usd
        - 20000
    )
    no_debt = financed_equipment_exit(
        purchase_price_usd=300000,
        loan_principal_usd=0,
        nominal_annual_interest_rate=0,
        loan_term_months=48,
        sale_month=36,
        sale_proceeds_usd=60000,
    )
    assert no_debt.equity_from_sale_usd == 60000


def test_book_values_and_rights():
    book = straight_line_book_values(
        purchase_price_usd=300000,
        assumed_book_residual_usd=60000,
        useful_life_months=36,
    )
    assert book[0] == 300000 and book[-1] == 60000
    assert sum(a - b for a, b in zip(book, book[1:])) == pytest.approx(240000)
    with pytest.raises(ValueError):
        compare_purchase_lease_cash_flows(**(BASE | dict(has_resale_rights=False)))
    with pytest.raises(ValueError):
        compare_purchase_lease_cash_flows(**(BASE | dict(exit_month=35)))
    with pytest.raises(TypeError):
        compare_purchase_lease_cash_flows(**(BASE | dict(resale_proceeds_usd=True)))
