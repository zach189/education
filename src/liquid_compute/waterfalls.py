"""Explicit hypothetical debt/reserve/equity priority, with no implicit funding."""

from collections.abc import Sequence
from dataclasses import dataclass

from .economics import _finite_number
from .financing import _fraction, _nonnegative, _total


@dataclass(frozen=True)
class WaterfallState:
    """USD balances. Debt includes unpaid principal; interest never capitalizes."""

    debt_usd: float
    reserve_usd: float = 0.0
    unrestricted_cash_usd: float = 0.0
    interest_arrears_usd: float = 0.0
    principal_arrears_usd: float = 0.0
    operating_arrears_usd: float = 0.0


@dataclass(frozen=True)
class WaterfallRow:
    """One period's USD allocation, followed by complete closing balances."""

    opening: WaterfallState
    cash_available_usd: float
    operating_shortfall_usd: float
    current_interest_usd: float
    current_principal_due_usd: float
    operating_paid_usd: float
    interest_paid_usd: float
    principal_paid_usd: float
    reserve_draw_usd: float
    reserve_topup_usd: float
    reserve_release_usd: float
    sweep_usd: float
    distribution_usd: float
    closing: WaterfallState


def _state(state: WaterfallState) -> None:
    if not isinstance(state, WaterfallState):
        raise TypeError("state must be WaterfallState")
    for name in state.__dataclass_fields__:
        _nonnegative(name, getattr(state, name))
    if state.principal_arrears_usd > state.debt_usd:
        raise ValueError("unpaid principal cannot exceed outstanding debt")


def allocate_period_cash(
    *,
    state: WaterfallState,
    cash_available_usd: float,
    scheduled_interest_usd: float,
    scheduled_principal_usd: float,
    reserve_target_usd: float,
    sweep_fraction: float,
    distribution_locked: bool = False,
    operating_shortfall_usd: float = 0.0,
) -> WaterfallRow:
    """Pay operating shortage, interest, principal, reserve, sweep, then equity.

    Use unrestricted cash then reserve for shortages. Old interest/principal
    arrears precede current amounts within each class. Principal arrears remain
    in debt and accrue ordinary principal interest; interest arrears do not.
    Reserve releases only after debt and all unpaid amounts are zero. A lock
    retains excess unrestricted cash, not a fictitious payout. No new equity.
    cash_available is AFTER operating costs; if negative pass zero and its
    magnitude as operating_shortfall (cannot both be positive). Components are
    finite nonnegative USD; sweep [0,1], lock bool. Invalid types raise TypeError;
    invalid ranges, contradictory states or arithmetic overflow ValueError.
    """
    _state(state)
    available = _nonnegative("cash_available_usd", cash_available_usd)
    shortfall = _nonnegative("operating_shortfall_usd", operating_shortfall_usd)
    interest = _nonnegative("scheduled_interest_usd", scheduled_interest_usd)
    principal = _nonnegative("scheduled_principal_usd", scheduled_principal_usd)
    target = _nonnegative("reserve_target_usd", reserve_target_usd)
    fraction = _fraction("sweep_fraction", sweep_fraction, inclusive=True)
    if not isinstance(distribution_locked, bool):
        raise TypeError("distribution_locked must be bool")
    if available and shortfall:
        raise ValueError(
            "cash after operations and operating shortfall cannot both be positive"
        )
    if state.debt_usd == 0 and (interest or principal):
        raise ValueError("no current debt service is due on zero debt")
    principal = min(principal, max(0, state.debt_usd - state.principal_arrears_usd))
    cash = _total([state.unrestricted_cash_usd, available])
    reserve = state.reserve_usd
    drawn = 0.0

    def pay(due: float) -> float:
        nonlocal cash, reserve, drawn
        from_cash = min(cash, due)
        cash -= from_cash
        from_reserve = min(reserve, due - from_cash)
        reserve -= from_reserve
        drawn = _total([drawn, from_reserve])
        return _total([from_cash, from_reserve])

    operating_due = _total([state.operating_arrears_usd, shortfall])
    operating_paid = pay(operating_due)
    unpaid_operating = max(0, operating_due - operating_paid)
    interest_due = _total([state.interest_arrears_usd, interest])
    interest_paid = pay(interest_due)
    unpaid_interest = max(0, interest_due - interest_paid)
    principal_due = _total([state.principal_arrears_usd, principal])
    principal_paid = pay(principal_due)
    unpaid_principal = max(0, principal_due - principal_paid)
    debt = max(0, state.debt_usd - principal_paid)
    arrears = _total([unpaid_operating, unpaid_interest, unpaid_principal])
    topup = sweep = release = distribution = 0.0
    if arrears == 0:
        if debt > 0:
            topup = min(cash, max(0, target - reserve))
            reserve = _total([reserve, topup])
            cash -= topup
            sweep = min(debt, cash * fraction)
            cash -= sweep
            debt -= sweep
        if debt == 0:
            release = reserve
            reserve = 0.0
            cash = _total([cash, release])
        if not distribution_locked:
            distribution = cash
            cash = 0.0
    closing = WaterfallState(
        debt, reserve, cash, unpaid_interest, unpaid_principal, unpaid_operating
    )
    return WaterfallRow(
        state,
        available,
        shortfall,
        interest,
        principal,
        operating_paid,
        interest_paid,
        principal_paid,
        drawn,
        topup,
        release,
        sweep,
        distribution,
        closing,
    )


def build_cash_waterfall(
    *,
    cash_after_operations_usd: Sequence[float],
    initial_debt_usd: float,
    nominal_annual_interest_rate: float,
    scheduled_principal_usd: Sequence[float],
    opening_reserve_usd: float,
    reserve_target_usd: float,
    sweep_fraction: float,
    distribution_locks: Sequence[bool] | None = None,
) -> tuple[WaterfallRow, ...]:
    """Iterate service-month arrays (month 1 first), recomputing opening-debt interest.

    Signed finite operating cash is adapted to the explicit shortage input.
    No time-zero row; opening reserve must be funded separately by the caller.
    Principal schedule is capped by debt less prior principal arrears. Retain
    unpaid balances at horizon; no automatic terminal distribution or refinance.
    """
    cash = tuple(
        _finite_number("cash after operations", v) for v in cash_after_operations_usd
    )
    principal = tuple(
        _nonnegative("scheduled principal", v) for v in scheduled_principal_usd
    )
    if not cash or len(cash) != len(principal):
        raise ValueError(
            "cash and principal schedules must be nonempty with matching lengths"
        )
    locks = (
        tuple(distribution_locks)
        if distribution_locks is not None
        else (False,) * len(cash)
    )
    if len(locks) != len(cash):
        raise ValueError("one distribution lock required per period")
    state = WaterfallState(
        _nonnegative("initial_debt_usd", initial_debt_usd),
        _nonnegative("opening_reserve_usd", opening_reserve_usd),
    )
    rate = (
        _nonnegative("nominal_annual_interest_rate", nominal_annual_interest_rate) / 12
    )
    rows = []
    for current, scheduled, locked in zip(cash, principal, locks):
        row = allocate_period_cash(
            state=state,
            cash_available_usd=max(0, current),
            operating_shortfall_usd=max(0, -current),
            scheduled_interest_usd=_finite_number("interest", state.debt_usd * rate),
            scheduled_principal_usd=min(
                scheduled, max(0, state.debt_usd - state.principal_arrears_usd)
            ),
            reserve_target_usd=reserve_target_usd,
            sweep_fraction=sweep_fraction,
            distribution_locked=locked,
        )
        rows.append(row)
        state = row.closing
    return tuple(rows)


@dataclass(frozen=True)
class EquityReturnSummary:
    """Undiscounted USD and multiple of invested capital; never an annual return."""

    invested_usd: float
    returned_usd: float
    net_gain_usd: float
    moic: float | None


def equity_return_summary(
    *,
    equity_investments_usd: Sequence[float],
    equity_distributions_usd: Sequence[float],
) -> EquityReturnSummary:
    """Sum finite nonnegative actual contributions/distributions; zero invested N/A."""
    invested = _total(
        [_nonnegative("equity investment", v) for v in equity_investments_usd]
    )
    returned = _total(
        [_nonnegative("equity distribution", v) for v in equity_distributions_usd]
    )
    return EquityReturnSummary(
        invested,
        returned,
        _finite_number("net gain", returned - invested),
        None if invested == 0 else _finite_number("MOIC", returned / invested),
    )
