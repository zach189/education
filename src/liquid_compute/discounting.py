"""Valuations under a chosen effective annual rate, not contractual cash charges."""

from collections.abc import Sequence
from math import fsum
from typing import Literal

from .cashflows import _integer
from .economics import _finite_number


def discount_factor(*, annual_discount_rate: float, months: int) -> float:
    """Return (1+r)**(-months/12); rate is an effective annual fraction.

    Rate must be finite and nonnegative; months a nonnegative integer. Negative
    rates are outside this initial lesson's scope. Reject bools and wrong types
    with TypeError, invalid values/overflow with ValueError. Time zero returns 1.
    This chosen valuation rate does not create a borrowing expense.
    """
    rate = _finite_number("annual_discount_rate", annual_discount_rate)
    if rate < 0:
        raise ValueError("annual_discount_rate must be nonnegative")
    offset = _integer("months", months)
    try:
        return _finite_number("discount_factor", (1 + rate) ** (-offset / 12))
    except OverflowError as exc:
        raise ValueError("discount factor calculation must be finite") from exc


def present_value_usd(
    cash_flows_usd: Sequence[float], *, annual_discount_rate: float
) -> float:
    """Value signed USD flows at t=0; index t is months from commencement.

    Sequence must include a zero placeholder for any boundary without movement.
    Supplier payments may be supplied as positive costs for cost comparisons.
    Empty flows return zero, but the rate is still validated. All amounts must
    be finite int/float, excluding bool; validation matches discount_factor.
    """
    discount_factor(annual_discount_rate=annual_discount_rate, months=0)
    try:
        return _finite_number(
            "present_value_usd",
            fsum(
                _finite_number("cash_flow_usd", value)
                * discount_factor(annual_discount_rate=annual_discount_rate, months=t)
                for t, value in enumerate(cash_flows_usd)
            ),
        )
    except OverflowError as exc:
        raise ValueError("present_value_usd must be finite") from exc


def break_even_prepayment_discount_fraction(
    *,
    service_months: int,
    annual_discount_rate: float,
    payment_timing: Literal[
        "monthly_in_advance", "monthly_in_arrears"
    ] = "monthly_in_advance",
) -> float:
    """Discount equating t=0 prepayment to equal monthly payments.

    Advance payments run t=0,...,T-1; arrears payments run t=1,...,T.

    Positive service_months and nonnegative effective annual rate are required.
    Same delivery is assumed; delivery/credit risk and financing costs are absent.
    Because price cancels, return 1 - mean(discount factors), without needing a
    rental amount. Result is a fraction, not a percent. Validation follows the
    other functions; at zero rate the discount is zero. A single advance payment
    also has zero equivalent discount, but a single arrears payment need not.
    """
    months = _integer("service_months", service_months, minimum=1)
    if not isinstance(payment_timing, str):
        raise TypeError("payment_timing must be a string")
    if payment_timing not in ("monthly_in_advance", "monthly_in_arrears"):
        raise ValueError(
            "payment_timing must be monthly_in_advance or monthly_in_arrears"
        )
    payments = ([0.0] if payment_timing == "monthly_in_arrears" else []) + [
        1.0
    ] * months
    return (
        1
        - present_value_usd(payments, annual_discount_rate=annual_discount_rate)
        / months
    )
