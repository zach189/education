"""Daily contractual OEM bridge cash flows; no valuation or assumed recovery."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, TypedDict

from .cashflows import _integer
from .economics import _finite_number
from .financing import _fraction, _nonnegative, _total


class BridgeInputs(TypedDict):
    """USD amounts, integer day offsets, and annual ACT/365 simple rate."""

    deposit_usd: float
    draw_usd: float
    prepayment_usd: float
    nominal_annual_interest_rate: float
    fee_fraction: float
    condition_met: bool
    documentation_day: int | None
    due_day: int | None
    receipt_day: int | None
    horizon_day: int
    refund_day: int | None
    refund_usd: float


@dataclass(frozen=True)
class BridgeEvent:
    """Signed cash in USD at a nonnegative day; same-day events are netted."""

    day_offset: int
    kind: str
    amount_usd: float


@dataclass(frozen=True)
class BridgeRow:
    """USD ledger at each event boundary; accrual is since the previous row."""

    day_offset: int
    opening_principal_usd: float
    draw_usd: float
    accrued_interest_usd: float
    principal_repayment_usd: float
    interest_payment_usd: float
    net_cash_usd: float
    cumulative_cash_usd: float
    remaining_principal_usd: float
    remaining_interest_usd: float


@dataclass(frozen=True)
class BridgeSchedule:
    """Event ledger and unpaid debt at the stated maturity/horizon, in USD."""

    events: tuple[BridgeEvent, ...]
    rows: tuple[BridgeRow, ...]
    outstanding_debt_usd: float
    customer_status: Literal["conditional", "owed, unreceived", "received"]


def event_cash_funding_requirement_usd(events: Sequence[BridgeEvent]) -> float:
    """Initial USD buffer needed, netting same-day cash including day zero.

    Include opening zero cash. No intraday ordering or unpaid-debt injection.
    Events must have integer nonnegative days, string kinds and finite signed
    amounts. Invalid types raise TypeError; ranges/overflow raise ValueError.
    """
    by_day: dict[int, list[float]] = {}
    for event in events:
        if not isinstance(event, BridgeEvent):
            raise TypeError("events must contain BridgeEvent records")
        day = _integer("day_offset", event.day_offset)
        if not isinstance(event.kind, str):
            raise TypeError("kind must be a string")
        by_day.setdefault(day, []).append(
            _finite_number("amount_usd", event.amount_usd)
        )
    cash = low = 0.0
    for day in sorted(by_day):
        cash = _total([cash, _total(by_day[day])])
        low = min(low, cash)
    return -low


def build_deposit_bridge_schedule(
    *,
    deposit_usd: float,
    draw_usd: float,
    prepayment_usd: float,
    nominal_annual_interest_rate: float,
    fee_fraction: float,
    condition_met: bool,
    documentation_day: int | None,
    due_day: int | None,
    receipt_day: int | None,
    horizon_day: int,
    refund_day: int | None = None,
    refund_usd: float = 0.0,
) -> BridgeSchedule:
    """Draw/pay deposit at day 0; sweep receipts to principal, then interest.

    Explicit hypothetical principal-first allocation makes refund principal
    loss visible. Interest is simple ACT/365 on unpaid principal, never on
    interest. Fee is draw * fee_fraction paid separately at day 0. Residual
    receipt cash is retained; no implicit equity, refinancing or maturity
    repayment. Horizon is maturity: subsequent events are not permitted.
    Documentation and due dates must both exist if condition_met is True;
    otherwise neither they nor customer receipt may exist. A receipt cannot
    precede its due date. None means absent, not day zero. Refund and customer
    receipt may coexist only if explicitly supplied; refund cannot exceed
    deposit. All amounts/rate are finite nonnegative numbers (not bool), fee
    fraction is [0,1], days nonnegative integers (not bool). Invalid types
    raise TypeError; ranges, chronology and calculated overflow ValueError.
    """
    deposit = _nonnegative("deposit_usd", deposit_usd)
    draw = _nonnegative("draw_usd", draw_usd)
    prepayment = _nonnegative("prepayment_usd", prepayment_usd)
    rate = _nonnegative("nominal_annual_interest_rate", nominal_annual_interest_rate)
    fee = _finite_number(
        "fee_usd", draw * _fraction("fee_fraction", fee_fraction, inclusive=True)
    )
    refund = _nonnegative("refund_usd", refund_usd)
    horizon = _integer("horizon_day", horizon_day)
    if not isinstance(condition_met, bool):
        raise TypeError("condition_met must be bool")
    for name, day in [
        ("documentation_day", documentation_day),
        ("due_day", due_day),
        ("receipt_day", receipt_day),
        ("refund_day", refund_day),
    ]:
        if day is not None and _integer(name, day) > horizon:
            raise ValueError(f"{name} must not exceed horizon_day")
    if condition_met:
        if documentation_day is None or due_day is None:
            raise ValueError("satisfied condition requires documentation and due dates")
        if documentation_day > due_day or (
            receipt_day is not None and receipt_day < due_day
        ):
            raise ValueError("require documentation <= due <= receipt")
    elif any(day is not None for day in (documentation_day, due_day, receipt_day)):
        raise ValueError(
            "unmet condition cannot have documentation, due or receipt dates"
        )
    if refund > deposit or (refund_day is None and refund != 0):
        raise ValueError("refund requires a date and cannot exceed deposit")
    days = sorted(
        {
            0,
            horizon,
            *(
                d
                for d in (documentation_day, due_day, receipt_day, refund_day)
                if d is not None
            ),
        }
    )
    events = [
        BridgeEvent(0, "draw", draw),
        BridgeEvent(0, "deposit", -deposit),
        BridgeEvent(0, "fee", -fee),
    ]
    principal = interest = cash = 0.0
    previous_day = 0
    rows: list[BridgeRow] = []
    for day in days:
        opening = principal
        accrued = _finite_number(
            "accrued interest",
            principal
            * rate
            * (_finite_number("elapsed days", day - previous_day) / 365),
        )
        interest = _total([interest, accrued])
        current_draw = draw if day == 0 else 0.0
        principal = _total([principal, current_draw])
        receipt = prepayment if day == receipt_day else 0.0
        recovery = refund if day == refund_day else 0.0
        available = _total([receipt, recovery])
        principal_paid = min(principal, available)
        interest_paid = min(interest, available - principal_paid)
        principal -= principal_paid
        interest -= interest_paid
        events.extend(
            [
                BridgeEvent(day, "customer receipt", receipt),
                BridgeEvent(day, "refund", recovery),
                BridgeEvent(day, "principal repayment", -principal_paid),
                BridgeEvent(day, "interest payment", -interest_paid),
            ]
        )
        net = _total(
            [
                current_draw,
                -deposit if day == 0 else 0,
                -fee if day == 0 else 0,
                available,
                -principal_paid,
                -interest_paid,
            ]
        )
        cash = _total([cash, net])
        rows.append(
            BridgeRow(
                day,
                opening,
                current_draw,
                accrued,
                principal_paid,
                interest_paid,
                net,
                cash,
                principal,
                interest,
            )
        )
        previous_day = day
    status: Literal["conditional", "owed, unreceived", "received"]
    status = (
        "conditional"
        if not condition_met
        else "received"
        if receipt_day is not None
        else "owed, unreceived"
    )
    return BridgeSchedule(
        tuple(events), tuple(rows), _total([principal, interest]), status
    )
