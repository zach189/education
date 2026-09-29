import pytest

from liquid_compute.cashflows import maximum_funding_requirement_usd
from liquid_compute.offtake import (
    OfftakeTerms,
    build_offtake_receipts,
    cash_available_for_debt_service_usd,
)


def test_acceptance_catchup_and_cancellation():
    rows = build_offtake_receipts(
        OfftakeTerms(20000, 12, acceptance_required=True), acceptance_month=3
    )
    assert [r.receipts_usd for r in rows[:4]] == [0, 0, 0, 60000]
    cf = cash_available_for_debt_service_usd(
        [r.receipts_usd for r in rows], [0] + [12000] * 12
    )
    assert maximum_funding_requirement_usd(cf) == 24000
    assert sum(cf) == 96000
    cancelled = build_offtake_receipts(
        OfftakeTerms(20000, 12, cancellation_after_month=6)
    )
    assert sum(r.billings_usd for r in cancelled) == 120000
    assert (
        sum(
            cash_available_for_debt_service_usd(
                [r.receipts_usd for r in cancelled], [0] + [12000] * 12
            )
        )
        == -24000
    )


def test_owed_conditional_credit_and_late_cash():
    terms = OfftakeTerms(20000, 12)
    late = build_offtake_receipts(terms, collection_month_by_service_month={7: 14})
    assert (
        len(late) == 15
        and late[7].unpaid_due_usd == 20000
        and late[14].unpaid_due_usd == 0
    )
    assert sum(r.receipts_usd for r in late) == 240000
    unpaid = build_offtake_receipts(terms, collection_month_by_service_month={7: None})
    assert unpaid[-1].unpaid_due_usd == 20000
    conditional = build_offtake_receipts(
        OfftakeTerms(20000, 12, acceptance_required=True)
    )
    assert conditional[-1].conditional_balance_usd == 240000
    assert conditional[-1].unpaid_due_usd == 0
    credit = build_offtake_receipts(
        OfftakeTerms(20000, 12, credits_usd=(0, 0, 0, 4000) + (0,) * 8)
    )
    assert credit[4].receipts_usd == 16000
    assert sum(r.receipts_usd for r in credit) == 236000


@pytest.mark.parametrize(
    "terms,extra,error",
    [
        (OfftakeTerms(True, 12), {}, TypeError),
        (OfftakeTerms(-1, 12), {}, ValueError),
        (OfftakeTerms(float("inf"), 12), {}, ValueError),
        (OfftakeTerms(1, True), {}, TypeError),
        (OfftakeTerms(1, 12, credits_usd=(2,) * 12), {}, ValueError),
        (OfftakeTerms(1, 12, cancellation_after_month=13), {}, ValueError),
        (
            OfftakeTerms(1, 12, acceptance_required=True),
            {"collection_month_by_service_month": {1: 2}},
            ValueError,
        ),
        (
            OfftakeTerms(1, 12),
            {"collection_month_by_service_month": {2: 1}},
            ValueError,
        ),
        (
            OfftakeTerms(1, 12, acceptance_required=True, cancellation_after_month=6),
            {"acceptance_month": 7},
            ValueError,
        ),
    ],
)
def test_invalid(terms, extra, error):
    with pytest.raises(error):
        build_offtake_receipts(terms, **extra)


def test_zero_and_bounds():
    assert sum(r.receipts_usd for r in build_offtake_receipts(OfftakeTerms(0, 1))) == 0
    with pytest.raises(ValueError):
        cash_available_for_debt_service_usd([1], [])
    with pytest.raises(TypeError):
        cash_available_for_debt_service_usd([True], [1])
