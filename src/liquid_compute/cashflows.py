"""Contractual monthly amounts and funding before financing, without valuation."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from .economics import _finite_number, _positive_number


def _integer(name: str, value: int, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer, excluding bool")
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return value


@dataclass(frozen=True)
class MonthlyCashFlow:
    """USD amounts at a month boundary, after netting simultaneous movements.

    Service amounts at t=m refer to service month m just completed; t=0 has no
    service amounts. Payments/receipts are positive amounts, net cash is signed,
    and cumulative cash starts from zero. No interest or financing is included.
    """

    month_offset: int
    service_revenue_usd: float
    service_rental_expense_usd: float
    customer_receipts_usd: float
    supplier_payments_usd: float
    net_cash_flow_usd: float
    cumulative_cash_usd: float


def build_cash_flow_schedule(
    *,
    monthly_revenue_usd: float,
    base_monthly_rental_expense_usd: float,
    service_months: int,
    customer_payment_lag_months: int,
    supplier_terms: Literal[
        "monthly_in_advance", "monthly_in_arrears", "upfront"
    ] = "monthly_in_advance",
    prepayment_discount_fraction: float = 0.0,
    customer_terms: Literal["monthly_in_arrears", "upfront"] = "monthly_in_arrears",
) -> tuple[MonthlyCashFlow, ...]:
    """Build t=0 through t=service_months+lag, including every trailing receipt.

    Monthly service m spans [m-1, m]. Supplier payments occur at m-1 (advance),
    m (arrears), or entirely at t=0 (upfront). Monthly customer receipts occur
    at m+lag. Customer upfront means all revenue is collected at t=0, cleared
    before any supplier payment at that boundary; lag must then be zero. This
    is a contractual teaching assumption, not an industry convention. Equal service
    expense allocation applies even for prepayment; only its price discount
    changes expense. Same-date cash is netted, excluding intraday funding needs.

    Revenue is finite and nonnegative USD/month; base rent is positive USD/month.
    Service months is a positive integer and lag is a nonnegative integer.
    Discount must be finite in [0,1), and zero for monthly terms. Reject bools,
    unsupported types (TypeError), invalid values and arithmetic overflow
    (ValueError). Assumes all amounts paid/collected, zero starting cash, no
    taxes, ancillary expenses, defaults, interest, or derivatives.
    """
    revenue = _finite_number("monthly_revenue_usd", monthly_revenue_usd)
    if revenue < 0:
        raise ValueError("monthly_revenue_usd must be nonnegative")
    rent = _positive_number(
        "base_monthly_rental_expense_usd", base_monthly_rental_expense_usd
    )
    months = _integer("service_months", service_months, minimum=1)
    lag = _integer("customer_payment_lag_months", customer_payment_lag_months)
    if not isinstance(supplier_terms, str):
        raise TypeError("supplier_terms must be a string")
    if supplier_terms not in ("monthly_in_advance", "monthly_in_arrears", "upfront"):
        raise ValueError(
            "supplier_terms must be monthly_in_advance, monthly_in_arrears, or upfront"
        )
    if not isinstance(customer_terms, str):
        raise TypeError("customer_terms must be a string")
    if customer_terms not in ("monthly_in_arrears", "upfront"):
        raise ValueError("customer_terms must be monthly_in_arrears or upfront")
    if customer_terms == "upfront" and lag != 0:
        raise ValueError(
            "upfront customer terms require zero customer_payment_lag_months"
        )
    discount = _finite_number(
        "prepayment_discount_fraction", prepayment_discount_fraction
    )
    if not 0 <= discount < 1:
        raise ValueError("prepayment_discount_fraction must be in [0, 1)")
    if supplier_terms != "upfront" and discount != 0:
        raise ValueError(
            "monthly supplier terms require zero prepayment_discount_fraction"
        )
    try:
        total_rent = _finite_number(
            "total_rental_expense_usd", rent * months * (1 - discount)
        )
        total_revenue = _finite_number("total_revenue_usd", revenue * months)
    except OverflowError as exc:
        raise ValueError("contract totals must be finite") from exc
    expense = total_rent / months
    balance = 0.0
    rows = []
    for t in range(months + lag + 1):
        delivered = 1 <= t <= months
        if customer_terms == "upfront":
            receipts = total_revenue if t == 0 else 0.0
        else:
            receipts = revenue if 1 + lag <= t <= months + lag else 0.0
        if supplier_terms == "monthly_in_advance":
            payments = rent if t < months else 0.0
        elif supplier_terms == "monthly_in_arrears":
            payments = rent if 1 <= t <= months else 0.0
        else:
            payments = total_rent if t == 0 else 0.0
        net = receipts - payments
        balance = _finite_number("cumulative_cash_usd", balance + net)
        rows.append(
            MonthlyCashFlow(
                t,
                revenue if delivered else 0.0,
                expense if delivered else 0.0,
                receipts,
                payments,
                net,
                balance,
            )
        )
    return tuple(rows)


def maximum_funding_requirement_usd(net_cash_flows_usd: Sequence[float]) -> float:
    """Return cash needed before financing from chronologically ordered USD flows.

    Includes opening balance zero; empty/all-positive flows require zero funding.
    Never discounts. Finite signed int/float amounts are accepted, excluding bool.
    Invalid types raise TypeError; nonfinite inputs or cumulative overflow raise
    ValueError. Movements sharing a timestamp must be netted by the caller first.
    """
    balance = minimum = 0.0
    for amount in net_cash_flows_usd:
        balance = _finite_number(
            "cumulative_cash_usd", balance + _finite_number("net_cash_flow_usd", amount)
        )
        minimum = min(minimum, balance)
    return max(0.0, -minimum)


@dataclass(frozen=True)
class CashFlowSummary:
    """Undiscounted USD service totals and maximum cash needed before financing."""

    service_revenue_usd: float
    service_rental_expense_usd: float
    contribution_profit_usd: float
    maximum_funding_requirement_usd: float


def summarize_cash_flow_schedule(
    schedule: Sequence[MonthlyCashFlow],
) -> CashFlowSummary:
    """Summarize rows returned by build_cash_flow_schedule, without discounting.

    Empty rows summarize to zero. Input rows must have consecutive month offsets
    starting at zero. Reject wrong types, nonfinite values, and total overflow.
    """
    from math import fsum

    for t, row in enumerate(schedule):
        if not isinstance(row, MonthlyCashFlow):
            raise TypeError("schedule must contain MonthlyCashFlow rows")
        if _integer("month_offset", row.month_offset) != t:
            raise ValueError("schedule must start at zero and have consecutive months")
    try:
        revenue = _finite_number(
            "service_revenue_usd",
            fsum(
                _finite_number("service_revenue_usd", r.service_revenue_usd)
                for r in schedule
            ),
        )
        expense = _finite_number(
            "service_rental_expense_usd",
            fsum(
                _finite_number(
                    "service_rental_expense_usd", r.service_rental_expense_usd
                )
                for r in schedule
            ),
        )
    except OverflowError as exc:
        raise ValueError("service totals must be finite") from exc
    return CashFlowSummary(
        revenue,
        expense,
        _finite_number("contribution_profit_usd", revenue - expense),
        maximum_funding_requirement_usd([r.net_cash_flow_usd for r in schedule]),
    )


def allocate_supplier_prepayment_usd(
    monthly_service_expense_usd: Sequence[float], *, prepayment_fraction: float
) -> tuple[float, ...]:
    """Re-time stated expenses: fraction of total at t=0, remainder each month-end.

    This explicit hypothetical pro-rata credit rule does not infer contract
    payment rights. The prepayment is part of, never additional to, total rent.
    Inputs start at service month 1; output includes t=0. Expenses are finite
    nonnegative USD, nonempty; fraction is finite in [0,1]. Reject wrong types
    (including bool) with TypeError; range/nonfinite/overflow with ValueError.
    No interest, discount, fees or change in recognized service expense.
    """
    from .financing import _fraction, _nonnegative, _total

    fraction = _fraction("prepayment_fraction", prepayment_fraction, inclusive=True)
    expenses = tuple(
        _nonnegative("monthly service expense USD", v)
        for v in monthly_service_expense_usd
    )
    if not expenses:
        raise ValueError("monthly service expenses must be nonempty")
    total = _total(expenses)
    return (total * fraction, *(v * (1 - fraction) for v in expenses))
