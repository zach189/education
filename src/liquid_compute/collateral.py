"""Hypothetical receivables eligibility and pre-concentration-denominator cap."""

from collections.abc import Sequence
from dataclasses import dataclass

from .cashflows import _integer
from .financing import _fraction, _nonnegative, _total


@dataclass(frozen=True)
class Receivable:
    """Issued invoice USD and age in days; no future offtake or hardware value."""

    customer_id: str
    amount_usd: float
    age_days: int
    unconditional: bool = True
    disputed: bool = False


@dataclass(frozen=True)
class InvoiceEligibility:
    """Original invoice, eligible USD before concentration, and exclusion reason."""

    invoice: Receivable
    eligible_usd: float
    reason: str


@dataclass(frozen=True)
class BorrowingBaseResult:
    """Snapshot USD amounts; availability is credit capacity, never cash drawn."""

    invoices: tuple[InvoiceEligibility, ...]
    customer_deductions_usd: tuple[tuple[str, float], ...]
    eligible_usd: float
    adjusted_eligible_usd: float
    gross_advance_usd: float
    reserve_usd: float
    borrowing_base_usd: float
    facility_limit_usd: float
    debt_usd: float
    availability_usd: float
    overadvance_usd: float


def calculate_receivables_borrowing_base(
    invoices: Sequence[Receivable],
    *,
    maximum_age_days: int,
    concentration_fraction: float,
    advance_fraction: float,
    reserve_usd: float,
    facility_limit_usd: float,
    debt_usd: float,
) -> BorrowingBaseResult:
    """Exclude conditional/disputed/over-age invoices, aggregate customer caps.

    Cap each customer at concentration_fraction * total eligible BEFORE any
    concentration deduction. Advance against the adjusted pool, deduct reserve
    with a zero floor, apply facility ceiling, subtract existing debt. Report
    overadvance separately. Cutoff age is inclusive. Assume security/assignment
    rights have separately been established; this function makes no legal test.
    Amounts nonnegative finite, fractions [0,1], ages integer >=0, flags bool;
    invalid types raise TypeError; ranges/nonfinite/overflow raise ValueError.
    """
    age = _integer("maximum_age_days", maximum_age_days)
    concentration = _fraction(
        "concentration_fraction", concentration_fraction, inclusive=True
    )
    advance = _fraction("advance_fraction", advance_fraction, inclusive=True)
    reserve = _nonnegative("reserve_usd", reserve_usd)
    limit = _nonnegative("facility_limit_usd", facility_limit_usd)
    debt = _nonnegative("debt_usd", debt_usd)
    rows = []
    customers: dict[str, list[float]] = {}
    for invoice in invoices:
        if not isinstance(invoice, Receivable):
            raise TypeError("invoices must contain Receivable records")
        if not isinstance(invoice.customer_id, str):
            raise TypeError("customer_id must be a string")
        if not invoice.customer_id.strip():
            raise ValueError("customer_id must be nonempty")
        amount = _nonnegative("invoice amount", invoice.amount_usd)
        days = _integer("age_days", invoice.age_days)
        if not isinstance(invoice.unconditional, bool) or not isinstance(
            invoice.disputed, bool
        ):
            raise TypeError("invoice flags must be bool")
        reasons = []
        if not invoice.unconditional:
            reasons.append("conditional")
        if invoice.disputed:
            reasons.append("disputed")
        if days > age:
            reasons.append("over age limit")
        eligible = 0.0 if reasons else amount
        rows.append(
            InvoiceEligibility(invoice, eligible, ", ".join(reasons) or "eligible")
        )
        customers.setdefault(invoice.customer_id, []).append(eligible)
    totals = {key: _total(values) for key, values in customers.items()}
    eligible_total = _total(list(totals.values()))
    cap = eligible_total * concentration
    deductions = tuple(
        (key, max(0, value - cap)) for key, value in sorted(totals.items())
    )
    adjusted = _total([min(value, cap) for value in totals.values()])
    gross = adjusted * advance
    base = max(0, gross - reserve)
    permitted = min(limit, base)
    return BorrowingBaseResult(
        tuple(rows),
        deductions,
        eligible_total,
        adjusted,
        gross,
        reserve,
        base,
        limit,
        debt,
        max(0, permitted - debt),
        max(0, debt - permitted),
    )
