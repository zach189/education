import pytest

from liquid_compute.financing import build_amortizing_loan_schedule
from liquid_compute.offtake import (
    build_renewal_receipt_scenarios,
    renewal_exposure_summary,
)

BASE = dict(
    contracted_monthly_usd=20000,
    contract_months=12,
    obligation_months=24,
    renewal_gap_months=3,
    renewal_monthly_usd=17000,
)


def test_receipt_boundaries_and_retained_cash():
    rows = build_renewal_receipt_scenarios(**BASE)
    assert [r.total_receipts_usd for r in rows[12:17]] == [20000, 0, 0, 0, 17000]
    assert sum(r.contracted_receipts_usd for r in rows) == 240000
    assert sum(r.assumed_renewal_receipts_usd for r in rows) == 153000
    loan = build_amortizing_loan_schedule(
        principal_usd=120000, nominal_annual_interest_rate=0.12, loan_term_months=24
    )
    service = loan[1].interest_usd + loan[1].principal_repayment_usd
    cash = [0] + [
        r.total_receipts_usd
        - 12000
        - loan[r.month_offset].interest_usd
        - loan[r.month_offset].principal_repayment_usd
        for r in rows[1:]
    ]
    result = renewal_exposure_summary(
        net_cash_after_debt_usd=cash, loan_schedule=loan, contract_months=12
    )
    assert result.debt_at_expiry_usd == loan[12].closing_debt_usd
    # Lower-price renewal remains slightly negative after debt, so the full
    # expiry-relative drawdown also includes months 16..24.
    expected = 3 * (12000 + service) + 9 * max(0, service - 5000)
    assert result.post_expiry_drawdown_usd == pytest.approx(expected)
    assert result.required_initial_cash_buffer_usd == pytest.approx(
        max(0, expected - 12 * (8000 - service))
    )


def test_contract_only_and_shorter_debt():
    rows = build_renewal_receipt_scenarios(**(BASE | dict(renewal_monthly_usd=0)))
    assert all(r.total_receipts_usd == 0 for r in rows[13:])
    short = build_amortizing_loan_schedule(
        principal_usd=120000, nominal_annual_interest_rate=0.12, loan_term_months=12
    )
    result = renewal_exposure_summary(
        net_cash_after_debt_usd=[0] * 25, loan_schedule=short, contract_months=12
    )
    assert result.debt_at_expiry_usd == 0 and result.uncovered_obligation_months == 12
    with pytest.raises(ValueError):
        build_renewal_receipt_scenarios(**(BASE | dict(obligation_months=11)))
    with pytest.raises(TypeError):
        build_renewal_receipt_scenarios(**(BASE | dict(renewal_gap_months=True)))
