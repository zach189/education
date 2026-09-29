from dataclasses import replace

import pytest

from liquid_compute.collateral import Receivable, calculate_receivables_borrowing_base

POOL = (
    Receivable("A", 100000, 30),
    Receivable("B", 80000, 30),
    Receivable("C", 20000, 30),
)
TERMS = dict(
    maximum_age_days=60,
    concentration_fraction=0.4,
    advance_fraction=0.8,
    reserve_usd=10000,
    facility_limit_usd=150000,
    debt_usd=100000,
)


def test_worked_base_and_age_stress():
    result = calculate_receivables_borrowing_base(POOL, **TERMS)
    assert result.eligible_usd == 200000 and result.adjusted_eligible_usd == 180000
    assert result.borrowing_base_usd == 134000 and result.availability_usd == 34000
    aged = calculate_receivables_borrowing_base(
        (POOL[0], replace(POOL[1], age_days=61), POOL[2]), **TERMS
    )
    assert aged.eligible_usd == 120000 and aged.adjusted_eligible_usd == 68000
    assert aged.borrowing_base_usd == 44400 and aged.overadvance_usd == 55600
    assert aged.invoices[1].reason == "over age limit"


def test_aggregation_order_age_boundary_and_flags():
    split = (Receivable("A", 50000, 60), Receivable("A", 50000, 30), *POOL[1:])
    result = calculate_receivables_borrowing_base(split, **TERMS)
    reverse = calculate_receivables_borrowing_base(tuple(reversed(split)), **TERMS)
    assert result.borrowing_base_usd == reverse.borrowing_base_usd == 134000
    assert dict(result.customer_deductions_usd)["A"] == 20000
    excluded = calculate_receivables_borrowing_base(
        [Receivable("X", 100, 0, False, True)], **TERMS
    )
    assert excluded.eligible_usd == 0 and "conditional" in excluded.invoices[0].reason


def test_empty_reserve_floor_and_facility():
    empty = calculate_receivables_borrowing_base([], **TERMS)
    assert empty.borrowing_base_usd == 0 and empty.overadvance_usd == 100000
    large = calculate_receivables_borrowing_base(
        [replace(r, amount_usd=r.amount_usd * 10) for r in POOL], **TERMS
    )
    assert large.availability_usd == 50000


@pytest.mark.parametrize(
    "invoice,error",
    [
        (Receivable("A", True, 0), TypeError),
        (Receivable("A", 1, True), TypeError),
        (Receivable("A", float("inf"), 0), ValueError),
        (Receivable("", 1, 0), ValueError),
        (Receivable("A", 1, 0, 1), TypeError),
    ],
)
def test_invalid(invoice, error):
    with pytest.raises(error):
        calculate_receivables_borrowing_base([invoice], **TERMS)
