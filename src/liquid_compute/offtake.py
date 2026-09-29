"""Explicit hypothetical receipt conditions, credits, and renewal scenarios."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .cashflows import _integer
from .economics import _finite_number
from .financing import LoanCashFlow, _nonnegative, _total


@dataclass(frozen=True)
class OfftakeTerms:
    """USD billing per service month; lag in whole months, credits by service month.

    Acceptance, when required, releases all accrued billings. Cancellation
    removes later billings, not already delivered service or supplier costs.
    Frozen records are validated when used by build_offtake_receipts.
    """

    monthly_payment_usd: float
    service_months: int
    payment_lag_months: int = 0
    acceptance_required: bool = False
    cancellation_after_month: int | None = None
    credits_usd: tuple[float, ...] = ()


@dataclass(frozen=True)
class OfftakeRow:
    """USD flows at monthly boundaries including zero; unpaid is due less cash."""

    month_offset: int
    billings_usd: float
    credits_usd: float
    newly_due_usd: float
    receipts_usd: float
    unpaid_due_usd: float
    conditional_balance_usd: float
    reason: str


def build_offtake_receipts(
    terms: OfftakeTerms,
    *,
    acceptance_month: int | None = None,
    collection_month_by_service_month: Mapping[int, int | None] | None = None,
) -> tuple[OfftakeRow, ...]:
    """Separate billings, due obligations and cash; extend through late receipts.

    Arrays start at t=0. A None collection override means uncollected through
    the horizon. Without overrides, collect when due. For an acceptance
    condition, due=max(service month+lag, acceptance month); None acceptance
    leaves all amounts conditional. Acceptance must occur within delivered
    service; delayed cash can occur later. Credits reduce that service bill.
    Finite nonnegative USD, integer months, boolean flags are required.
    Wrong types raise TypeError; invalid ranges/chronology/overflow ValueError.
    """
    if not isinstance(terms, OfftakeTerms):
        raise TypeError("terms must be OfftakeTerms")
    amount = _nonnegative("monthly_payment_usd", terms.monthly_payment_usd)
    n = _integer("service_months", terms.service_months, minimum=1)
    lag = _integer("payment_lag_months", terms.payment_lag_months)
    if not isinstance(terms.acceptance_required, bool):
        raise TypeError("acceptance_required must be bool")
    end = (
        n
        if terms.cancellation_after_month is None
        else _integer("cancellation_after_month", terms.cancellation_after_month)
    )
    if end > n:
        raise ValueError("cancellation boundary exceeds service term")
    if acceptance_month is not None:
        _integer("acceptance_month", acceptance_month, minimum=1)
        if not terms.acceptance_required or acceptance_month > end:
            raise ValueError("acceptance must be required and within delivered service")
    credits = terms.credits_usd or (0.0,) * n
    if len(credits) != n:
        raise ValueError("credits must be empty or have one amount per service month")
    for t, credit in enumerate(credits, 1):
        if _nonnegative("credit_usd", credit) > amount or (t > end and credit):
            raise ValueError("credit exceeds delivered bill")
    overrides = dict(collection_month_by_service_month or {})
    for service, collected in overrides.items():
        if not 1 <= _integer("service month", service, minimum=1) <= end:
            raise ValueError("collection override requires delivered service")
        if collected is not None:
            _integer("collection month", collected, minimum=1)
    due: dict[int, list[float]] = {}
    receipts: dict[int, list[float]] = {}
    for service in range(1, end + 1):
        if terms.acceptance_required and acceptance_month is None:
            if overrides.get(service) is not None:
                raise ValueError("cannot collect before acceptance condition is met")
            continue
        due_month = max(service + lag, acceptance_month or 0)
        cash_month = overrides.get(service, due_month)
        net = amount - credits[service - 1]
        due.setdefault(due_month, []).append(net)
        if cash_month is not None:
            if cash_month < due_month:
                raise ValueError("collection cannot precede due month")
            receipts.setdefault(cash_month, []).append(net)
    horizon = max(n + lag, max(due, default=0), max(receipts, default=0))
    rows: list[OfftakeRow] = []
    unpaid = conditional = 0.0
    for t in range(horizon + 1):
        billing = amount if 1 <= t <= end else 0.0
        credit = credits[t - 1] if 1 <= t <= end else 0.0
        owed = _total(due.get(t, []))
        cash = _total(receipts.get(t, []))
        unpaid = _total([unpaid, owed, -cash])
        conditional = _total([conditional, billing, -credit, -owed])
        reason = (
            "cancelled future billing"
            if end < t <= n
            else "delivered service"
            if billing
            else "settlement boundary"
        )
        rows.append(
            OfftakeRow(t, billing, credit, owed, cash, unpaid, conditional, reason)
        )
    return tuple(rows)


def cash_available_for_debt_service_usd(
    receipts_usd: Sequence[float], operating_payments_usd: Sequence[float]
) -> tuple[float, ...]:
    """Same-index receipt minus operating cash, USD; equal-length arrays required.

    Caller includes all operating costs required by its definition. This lesson
    excludes taxes, debt, reserve transfers and owner cash. Negative CFADS is
    valid. Inputs are finite nonnegative cash components, excluding bool.
    """
    if len(receipts_usd) != len(operating_payments_usd):
        raise ValueError("cash arrays must have the same horizon and indexing")
    return tuple(
        _finite_number(
            "CFADS", _nonnegative("receipts", r) - _nonnegative("operating payments", p)
        )
        for r, p in zip(receipts_usd, operating_payments_usd)
    )


@dataclass(frozen=True)
class RenewalReceiptRow:
    """Monthly USD cash; contracted and assumed renewal kept separate, t=0 included."""

    month_offset: int
    contracted_receipts_usd: float
    assumed_renewal_receipts_usd: float
    total_receipts_usd: float


def build_renewal_receipt_scenarios(
    *,
    contracted_monthly_usd: float,
    contract_months: int,
    obligation_months: int,
    renewal_gap_months: int,
    renewal_monthly_usd: float,
) -> tuple[RenewalReceiptRow, ...]:
    """Contract runs 1..expiry, renewal starts expiry+gap+1 through obligations.

    Zero renewal price represents no renewal; no receipt beyond the supplied
    obligation horizon. Monetary inputs finite nonnegative, integer months,
    contract term positive and no longer than obligations; gap >=0. Wrong
    types/bools raise TypeError; invalid ranges/overflow raise ValueError.
    """
    amount = _nonnegative("contracted_monthly_usd", contracted_monthly_usd)
    renewal = _nonnegative("renewal_monthly_usd", renewal_monthly_usd)
    term = _integer("contract_months", contract_months, minimum=1)
    horizon = _integer("obligation_months", obligation_months, minimum=1)
    gap = _integer("renewal_gap_months", renewal_gap_months)
    if term > horizon:
        raise ValueError("obligation horizon cannot truncate contracted receipts")
    # Reuse F3's unconditional collection layer; renewal is separately labeled.
    contract = build_offtake_receipts(OfftakeTerms(amount, term))
    rows = []
    for t in range(horizon + 1):
        contracted = contract[t].receipts_usd if t <= term else 0.0
        assumed = renewal if t > term + gap else 0.0
        rows.append(
            RenewalReceiptRow(t, contracted, assumed, _total([contracted, assumed]))
        )
    return tuple(rows)


@dataclass(frozen=True)
class RenewalExposureSummary:
    """Debt at contract expiry and operational liquidity, excluding initial loan use."""

    debt_at_expiry_usd: float
    uncovered_obligation_months: int
    post_expiry_drawdown_usd: float
    required_initial_cash_buffer_usd: float


def renewal_exposure_summary(
    *,
    net_cash_after_debt_usd: Sequence[float],
    loan_schedule: Sequence["LoanCashFlow"],
    contract_months: int,
) -> RenewalExposureSummary:
    """Retain earlier cash; report expiry-relative drawdown AND whole-path buffer.

    Cash includes t=0 and all supplier/debt obligations; initial loan proceeds
    committed elsewhere are not free cash. Loan rows must be a complete F1
    schedule; cash horizon cannot truncate them or contract expiry. Nominal USD,
    no discounting. Validate finite cash and integer boundaries.
    """
    from .cashflows import maximum_funding_requirement_usd
    from .financing import LoanCashFlow, _validate_rows

    _validate_rows(loan_schedule, LoanCashFlow)
    cash = tuple(_finite_number("net cash", c) for c in net_cash_after_debt_usd)
    expiry = _integer("contract_months", contract_months, minimum=1)
    if len(cash) <= expiry or len(cash) < len(loan_schedule):
        raise ValueError("cash horizon must include expiry and every loan payment")
    debt = (
        loan_schedule[expiry].closing_debt_usd if expiry < len(loan_schedule) else 0.0
    )
    return RenewalExposureSummary(
        debt,
        len(cash) - 1 - expiry,
        maximum_funding_requirement_usd(cash[expiry + 1 :]),
        maximum_funding_requirement_usd(cash),
    )
