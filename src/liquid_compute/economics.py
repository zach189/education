"""Monthly contract economics, without payment timing or model-based valuations."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class MonthlyEconomics:
    """One modeled month's amounts; USD, GPU-hours, and dimensionless fractions.

    Contribution profit is revenue less the entire committed rental expense,
    before ancillary costs, taxes, and financing. This is a lesson-specific
    contribution measure, not conventional revenue less variable costs.
    Margin is profit / revenue, or None when revenue is zero. Break-even can
    exceed one: such utilization cannot be achieved within rented capacity.
    """

    purchased_gpu_hours: float
    billed_gpu_hours: float
    unused_gpu_hours: float
    revenue_usd: float
    rental_expense_usd: float
    contribution_profit_usd: float
    break_even_utilization_fraction: float
    contribution_margin_fraction: float | None


def _finite_number(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be an int or float, excluding bool")
    try:
        number = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} must be representable as a finite float") from exc
    if not isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def _positive_number(name: str, value: float) -> float:
    number = _finite_number(name, value)
    if number <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return number


def break_even_utilization_fraction(
    *, rental_usd_per_gpu_hour: float, customer_usd_per_gpu_hour: float
) -> float:
    """Return billed/purchased GPU-hours needed to cover the full rental bill.

    Both prices must be finite, strictly positive Python int/float values
    (not bool), in USD per GPU-hour. All rented hours are paid, while only
    billed hours earn revenue. The ratio is independent of positive capacity.
    Values above 1 are valid but infeasible within the rented capacity.

    Raises TypeError for unsupported types and ValueError for invalid ranges,
    nonfinite inputs, or overflow. Callers must supply the stated units.
    This is a contractual break-even calculation, not a valuation or forecast.
    """
    rental = _positive_number("rental_usd_per_gpu_hour", rental_usd_per_gpu_hour)
    customer = _positive_number("customer_usd_per_gpu_hour", customer_usd_per_gpu_hour)
    return _finite_number("break_even_utilization_fraction", rental / customer)


def compute_monthly_economics(
    *,
    gpu_count: int,
    hours_per_month: float,
    rental_usd_per_gpu_hour: float,
    customer_usd_per_gpu_hour: float,
    utilization_fraction: float,
) -> MonthlyEconomics:
    """Calculate one month's purchased/billed hours and contract economics.

    gpu_count is a positive Python integer (not bool). hours_per_month is
    positive hours available per rented GPU in the modeled month. Both prices
    are positive USD/GPU-hour rates. utilization_fraction is billed/purchased
    hours in [0, 1], not processor activity. Non-count inputs accept finite
    Python int/float values, excluding bool; callers must supply these units.

    Assume identical, fully available GPUs; pay for all rented hours and bill
    every consumed hour. Exclude resale, excess demand, ancillary operating
    costs, taxes, financing, and derivatives. Results are contractual amounts,
    not dated cash flows or fair values. No intermediate rounding is applied.

    Return MonthlyEconomics; margin is None if revenue is zero. Raise TypeError
    for wrong types and ValueError for invalid ranges, nonfinite inputs, or
    calculated overflow. Zero capacity, hours, and prices are outside scope.
    """
    if isinstance(gpu_count, bool) or not isinstance(gpu_count, int):
        raise TypeError("gpu_count must be a positive integer, excluding bool")
    if gpu_count <= 0:
        raise ValueError("gpu_count must be greater than zero")
    count = _finite_number("gpu_count", gpu_count)
    hours = _positive_number("hours_per_month", hours_per_month)
    rental = _positive_number("rental_usd_per_gpu_hour", rental_usd_per_gpu_hour)
    customer = _positive_number("customer_usd_per_gpu_hour", customer_usd_per_gpu_hour)
    utilization = _finite_number("utilization_fraction", utilization_fraction)
    if not 0 <= utilization <= 1:
        raise ValueError("utilization_fraction must be between 0 and 1 inclusive")

    purchased = _finite_number("purchased_gpu_hours", count * hours)
    billed = _finite_number("billed_gpu_hours", purchased * utilization)
    unused = purchased - billed
    revenue = _finite_number("revenue_usd", billed * customer)
    expense = _finite_number("rental_expense_usd", purchased * rental)
    profit = _finite_number("contribution_profit_usd", revenue - expense)
    margin = (
        _finite_number("contribution_margin_fraction", profit / revenue)
        if revenue > 0
        else None
    )
    break_even = break_even_utilization_fraction(
        rental_usd_per_gpu_hour=rental, customer_usd_per_gpu_hour=customer
    )
    return MonthlyEconomics(
        purchased_gpu_hours=purchased,
        billed_gpu_hours=billed,
        unused_gpu_hours=unused,
        revenue_usd=revenue,
        rental_expense_usd=expense,
        contribution_profit_usd=profit,
        break_even_utilization_fraction=break_even,
        contribution_margin_fraction=margin,
    )
