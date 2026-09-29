from dataclasses import FrozenInstanceError

import pytest

from liquid_compute.bridge_financing import (
    BridgeEvent,
    build_deposit_bridge_schedule,
    event_cash_funding_requirement_usd,
)

BASE = dict(
    deposit_usd=200000,
    draw_usd=200000,
    prepayment_usd=250000,
    nominal_annual_interest_rate=0.12,
    fee_fraction=0.01,
    condition_met=True,
    documentation_day=10,
    due_day=15,
    receipt_day=20,
    horizon_day=60,
)


def test_base_cash_and_interest():
    result = build_deposit_bridge_schedule(**BASE)
    assert sum(r.accrued_interest_usd for r in result.rows) == pytest.approx(
        200000 * 0.12 * 20 / 365
    )
    assert sum(r.principal_repayment_usd for r in result.rows) == 200000
    assert result.rows[-1].cumulative_cash_usd == pytest.approx(46684.93150685)
    assert result.outstanding_debt_usd == 0
    assert event_cash_funding_requirement_usd(result.events) == 2000
    assert result.customer_status == "received"
    with pytest.raises(FrozenInstanceError):
        result.outstanding_debt_usd = 2


def test_delay_unmet_and_unreceived_are_distinct():
    late = build_deposit_bridge_schedule(**(BASE | dict(receipt_day=50)))
    assert sum(r.interest_payment_usd for r in late.rows) == pytest.approx(
        3287.67123288
    )
    owed = build_deposit_bridge_schedule(**(BASE | dict(receipt_day=None)))
    unmet = build_deposit_bridge_schedule(
        **(
            BASE
            | dict(
                condition_met=False,
                documentation_day=None,
                due_day=None,
                receipt_day=None,
            )
        )
    )
    assert owed.customer_status == "owed, unreceived"
    assert unmet.customer_status == "conditional"
    assert (
        owed.outstanding_debt_usd
        == unmet.outstanding_debt_usd
        == pytest.approx(203945.20547945)
    )


def test_refund_partial_principal_and_horizon_interest():
    result = build_deposit_bridge_schedule(
        **(
            BASE
            | dict(
                condition_met=False,
                documentation_day=None,
                due_day=None,
                receipt_day=None,
                refund_day=30,
                refund_usd=160000,
            )
        )
    )
    at_refund = next(r for r in result.rows if r.day_offset == 30)
    assert at_refund.remaining_principal_usd == 40000
    assert at_refund.remaining_interest_usd == pytest.approx(1972.60273973)
    assert result.outstanding_debt_usd == pytest.approx(42367.12328767)
    assert sum(e.amount_usd for e in result.events) == pytest.approx(
        result.rows[-1].cumulative_cash_usd
    )
    assert (
        sum(r.principal_repayment_usd for r in result.rows)
        + result.rows[-1].remaining_principal_usd
        == 200000
    )


@pytest.mark.parametrize(
    "changes",
    [
        dict(nominal_annual_interest_rate=0),
        dict(documentation_day=0, due_day=0, receipt_day=0),
    ],
)
def test_zero_interest_or_same_day_payoff(changes):
    result = build_deposit_bridge_schedule(**(BASE | changes))
    assert sum(r.accrued_interest_usd for r in result.rows) == 0
    assert result.outstanding_debt_usd == 0


def test_no_draw_and_zero_receipt():
    result = build_deposit_bridge_schedule(**(BASE | dict(draw_usd=0)))
    assert result.outstanding_debt_usd == 0
    assert event_cash_funding_requirement_usd(result.events) == 200000
    zero = build_deposit_bridge_schedule(**(BASE | dict(prepayment_usd=0)))
    assert zero.outstanding_debt_usd == pytest.approx(203945.20547945)


@pytest.mark.parametrize(
    "changes,error",
    [
        (dict(receipt_day=9), ValueError),
        (dict(due_day=9), ValueError),
        (dict(condition_met=False), ValueError),
        (dict(condition_met=1), TypeError),
        (dict(receipt_day=True), TypeError),
        (dict(receipt_day=20.1), TypeError),
        (dict(receipt_day=61), ValueError),
        (dict(deposit_usd=-1), ValueError),
        (dict(draw_usd=True), TypeError),
        (dict(draw_usd="2"), TypeError),
        (dict(draw_usd=float("inf")), ValueError),
        (dict(fee_fraction=1.1), ValueError),
        (dict(refund_usd=1), ValueError),
        (dict(refund_day=30, refund_usd=200001), ValueError),
        (dict(nominal_annual_interest_rate=float("nan")), ValueError),
        (dict(draw_usd=1e308, nominal_annual_interest_rate=1e308), ValueError),
    ],
)
def test_invalid_inputs(changes, error):
    with pytest.raises(error):
        build_deposit_bridge_schedule(**(BASE | changes))


def test_funding_nets_unordered_same_day_events_and_includes_opening_zero():
    events = [
        BridgeEvent(1, "pay", -120),
        BridgeEvent(0, "receipt", 100),
        BridgeEvent(1, "draw", 30),
    ]
    assert event_cash_funding_requirement_usd(events) == 0
    assert event_cash_funding_requirement_usd([BridgeEvent(0, "pay", -100)]) == 100
    with pytest.raises(ValueError):
        event_cash_funding_requirement_usd([BridgeEvent(0, "bad", float("nan"))])
