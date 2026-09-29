"""Dated synthetic/historical sample measurements, never forecasts or pricing inputs."""

from collections.abc import Sequence
from dataclasses import dataclass
from math import log, sqrt
from statistics import stdev

from .cashflows import _integer
from .economics import _finite_number, _positive_number


@dataclass(frozen=True)
class MonthlyPrice:
    """Serial calendar month (year*12 + month-1) and USD/GPU-hour or missing None."""

    month_index: int
    price_usd_per_gpu_hour: float | None


@dataclass(frozen=True)
class MonthlyLogReturn:
    """Adjacent calendar-month log change; None records a missing endpoint."""

    start_month: int
    end_month: int
    log_change: float | None
    missing_reason: str | None


@dataclass(frozen=True)
class SampleVolatility:
    """Dimensionless sample SD, optional annual scaling, and transparent counts."""

    count: int
    omitted_count: int
    sample_sd: float | None
    annualized_sd: float | None
    unavailable_reason: str | None


def monthly_log_returns(
    observations: Sequence[MonthlyPrice],
) -> tuple[MonthlyLogReturn, ...]:
    """Log(P_end/P_start) for every calendar pair within supplied endpoints.

    Strictly ascending unique nonnegative serial month indices (not YYYYMM).
    Nonmissing prices finite positive numbers excluding bool. Missing explicit
    prices and absent calendar months both remain missing; never bridge gaps,
    forward-fill, remove jumps or invent a zero return. Empty/singleton input
    yields no returns. Bad types raise TypeError, ranges/order ValueError.
    Product definition/units must be comparable; numeric checks cannot prove it.
    """
    prices: dict[int, float | None] = {}
    previous = -1
    for observation in observations:
        if not isinstance(observation, MonthlyPrice):
            raise TypeError("observations must contain MonthlyPrice records")
        month = _integer("month_index", observation.month_index)
        if month <= previous:
            raise ValueError("month indices must be unique and strictly ascending")
        price = observation.price_usd_per_gpu_hour
        prices[month] = (
            None if price is None else _positive_number("price_usd_per_gpu_hour", price)
        )
        previous = month
    if len(prices) < 2:
        return ()
    first, last = min(prices), max(prices)
    result = []
    for end in range(first + 1, last + 1):
        before, after = prices.get(end - 1), prices.get(end)
        if before is None or after is None:
            result.append(
                MonthlyLogReturn(end - 1, end, None, "missing adjacent-month price")
            )
        else:
            # Log difference avoids overflow/underflow in extreme positive ratios.
            change = _finite_number("log change", log(after) - log(before))
            result.append(MonthlyLogReturn(end - 1, end, change, None))
    return tuple(result)


def sample_volatility(
    returns: Sequence[float | None],
    *,
    periods_per_year: float | None = None,
) -> SampleVolatility:
    """Sample SD with n-1 denominator; omit only explicit None markers.

    Fewer than two valid returns yields unavailable (not zero). Values must be
    finite signed numbers excluding bool. Optional positive periods_per_year
    scales by its square root: caller must justify regular comparable sampling
    and time-scaling assumptions; monthly data uses 12, not 252/365. No estimate
    is automatically a forecast or calibration for an option model.
    """
    frequency = (
        None
        if periods_per_year is None
        else _positive_number("periods_per_year", periods_per_year)
    )
    valid = tuple(
        _finite_number("return", value) for value in returns if value is not None
    )
    omitted = len(returns) - len(valid)
    if len(valid) < 2:
        return SampleVolatility(
            len(valid), omitted, None, None, "at least two valid returns required"
        )
    try:
        sd = _finite_number("sample standard deviation", stdev(valid))
    except OverflowError as error:
        raise ValueError("sample standard deviation overflow") from error
    annual = (
        None
        if frequency is None
        else _finite_number("annualized standard deviation", sd * sqrt(frequency))
    )
    return SampleVolatility(len(valid), omitted, sd, annual, None)
