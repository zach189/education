"""Contractual cash-settled hedges and physical cash; no valuation or margin model."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

from .cashflows import _integer
from .economics import _finite_number
from .financing import _nonnegative, _total


@dataclass(frozen=True)
class Settlement:
    """Signed USD received by the named side at a positive month offset."""

    month_offset: int
    amount_usd: float


@dataclass(frozen=True)
class HedgedCashFlow:
    """Signed USD cash from the side's perspective; negative means cash paid."""

    month_offset: int
    physical_cash_usd: float
    hedge_cash_usd: float
    net_cash_usd: float
    cumulative_cash_usd: float


def _side_sign(side: Literal["buyer", "seller"]) -> float:
    if not isinstance(side, str):
        raise TypeError("side must be a string")
    if side not in ("buyer", "seller"):
        raise ValueError("side must be buyer or seller")
    return 1.0 if side == "buyer" else -1.0


def _months(months: Sequence[int]) -> tuple[int, ...]:
    result = tuple(_integer("month_offset", month, minimum=1) for month in months)
    if any(b <= a for a, b in zip(result, result[1:])):
        raise ValueError("months must be positive and strictly ascending")
    return result


def forward_settlements_usd(
    *,
    benchmark_usd_per_gpu_hour: Sequence[float],
    strike_usd_per_gpu_hour: float,
    hedge_gpu_hours: Sequence[float],
    settlement_months: Sequence[int],
    side: Literal["buyer", "seller"],
) -> tuple[Settlement, ...]:
    """Buyer receives H*(benchmark-strike); seller receives its negative.

    A strip settles at each explicit month. It does not deliver physical compute
    or imply a fair strike. No premium, collateral, fees or default modeled.
    Arrays are nonempty/equal length, months strictly ascending integers >0,
    rates/quantities finite nonnegative numbers excluding bool. Zero strike and
    quantity valid; signed settlements retained. Invalid types raise TypeError,
    invalid ranges/length/order/nonfinite/overflow ValueError.
    """
    sign = _side_sign(side)
    strike = _nonnegative("strike_usd_per_gpu_hour", strike_usd_per_gpu_hour)
    months = _months(settlement_months)
    if (
        not months
        or len(benchmark_usd_per_gpu_hour) != len(months)
        or len(hedge_gpu_hours) != len(months)
    ):
        raise ValueError("settlement arrays must be nonempty and equal length")
    return tuple(
        Settlement(
            month,
            _finite_number(
                "forward settlement",
                sign
                * _nonnegative("hedge_gpu_hours", hours)
                * (_nonnegative("benchmark_usd_per_gpu_hour", price) - strike),
            ),
        )
        for month, price, hours in zip(
            months, benchmark_usd_per_gpu_hour, hedge_gpu_hours
        )
    )


def combined_physical_and_hedge_cash_flows(
    *,
    physical_usd_per_gpu_hour: Sequence[float],
    physical_gpu_hours: Sequence[float],
    physical_payment_months: Sequence[int],
    settlements: Sequence[Settlement],
    side: Literal["buyer", "seller"],
) -> tuple[HedgedCashFlow, ...]:
    """Combine spot physical cash with already-signed settlements, dense t=0 onward.

    Buyer physical cost is negative, seller physical receipt positive. Settlement
    amounts must already represent this side: this function does not flip them.
    Physical arrays are nonempty/equal and months strictly ascending >0;
    settlement rows may be empty (unhedged) but otherwise strictly ascending >0.
    Extend to the final physical OR financial date; never net across dates.
    Finite nonnegative prices/hours, finite signed settlements, no bools.
    Type/range/overflow errors follow forward_settlements_usd.
    """
    sign = _side_sign(side)
    months = _months(physical_payment_months)
    if (
        not months
        or len(physical_usd_per_gpu_hour) != len(months)
        or len(physical_gpu_hours) != len(months)
    ):
        raise ValueError("physical arrays must be nonempty and equal length")
    physical = {
        month: _finite_number(
            "physical cash",
            -sign
            * _nonnegative("physical price", price)
            * _nonnegative("physical GPU-hours", hours),
        )
        for month, price, hours in zip(
            months, physical_usd_per_gpu_hour, physical_gpu_hours
        )
    }
    for row in settlements:
        if not isinstance(row, Settlement):
            raise TypeError("settlements must contain Settlement records")
    settlement_months = _months([r.month_offset for r in settlements])
    hedge = {
        month: _finite_number("settlement USD", row.amount_usd)
        for month, row in zip(settlement_months, settlements)
    }
    horizon = max(months[-1], max(settlement_months, default=0))
    cumulative = 0.0
    rows = []
    for month in range(horizon + 1):
        cash = physical.get(month, 0.0)
        settlement = hedge.get(month, 0.0)
        net = _total([cash, settlement])
        cumulative = _total([cumulative, net])
        rows.append(HedgedCashFlow(month, cash, settlement, net, cumulative))
    return tuple(rows)


@dataclass(frozen=True)
class BenchmarkMatch:
    """Declared contract attributes; equal labels do not prove economic matching."""

    unit: str
    provider: str
    region: str
    delivery_period: str
    service_specification: str
    delivery_hours: str


def compare_benchmark_attributes(
    physical: BenchmarkMatch, benchmark: BenchmarkMatch
) -> tuple[str, ...]:
    """List declared differences; require USD/GPU-hour price units for this model.

    Validate records and nonempty text. No inference of equivalent hardware,
    service quality, delivery hours, legal rights or index methodology.
    """
    for record in (physical, benchmark):
        if not isinstance(record, BenchmarkMatch):
            raise TypeError("attributes must be BenchmarkMatch records")
        for name in record.__dataclass_fields__:
            value = getattr(record, name)
            if not isinstance(value, str):
                raise TypeError("benchmark attributes must be strings")
            if not value.strip():
                raise ValueError("benchmark attributes must be nonempty")
        if record.unit != "USD/GPU-hour":
            raise ValueError(
                "convert prices and quantities to USD/GPU-hour and GPU-hours explicitly"
            )
    return tuple(
        name
        for name in physical.__dataclass_fields__
        if getattr(physical, name) != getattr(benchmark, name)
    )


@dataclass(frozen=True)
class BasisExposureRow:
    """Buyer USD cost decomposition; retain payment date and hedge date separately."""

    physical_payment_month: int
    settlement_month: int
    unhedged_cost_usd: float
    hedge_receipts_usd: float
    net_cost_usd: float
    basis_usd_per_gpu_hour: float
    unmatched_gpu_hours: float
    unmatched_benchmark_cost_usd: float
    basis_cost_usd: float
    strike_component_usd: float


@dataclass(frozen=True)
class BasisExposureSummary:
    """Nominal buyer costs, not time-zero PV or an automatic benchmark rating."""

    rows: tuple[BasisExposureRow, ...]
    cash_flows: tuple[HedgedCashFlow, ...]
    unhedged_cost_usd: float
    hedge_receipts_usd: float
    net_cost_usd: float


def basis_exposure_summary(
    *,
    actual_usd_per_gpu_hour: Sequence[float],
    physical_gpu_hours: Sequence[float],
    benchmark_usd_per_gpu_hour: Sequence[float],
    hedge_gpu_hours: Sequence[float],
    strike_usd_per_gpu_hour: float,
    physical_payment_months: Sequence[int],
    settlements: Sequence[Settlement],
) -> BasisExposureSummary:
    """Decompose Q*A-H*(B-K) = (Q-H)*B + Q*(A-B) + H*K.

    One paired physical/financial block per array entry; all nonempty, equal
    length. Monetary prices and quantities finite nonnegative, strike >=0.
    Settlement rows must match M2 BUYER settlements for the supplied B/H/K.
    Time basis is supplied in prices/declared attributes, never inferred from
    payment dates. Physical and hedge payment months may differ; dense cash
    extends through both. Signed basis, unmatched hours and net costs retained.
    Types/ranges/order/overflow are validated as in the M2 functions.
    """
    n = len(actual_usd_per_gpu_hour)
    if not n or any(
        len(v) != n
        for v in (
            physical_gpu_hours,
            benchmark_usd_per_gpu_hour,
            hedge_gpu_hours,
            physical_payment_months,
            settlements,
        )
    ):
        raise ValueError("paired basis arrays must be nonempty and equal length")
    for row in settlements:
        if not isinstance(row, Settlement):
            raise TypeError("settlements must contain Settlement records")
    expected = forward_settlements_usd(
        benchmark_usd_per_gpu_hour=benchmark_usd_per_gpu_hour,
        strike_usd_per_gpu_hour=strike_usd_per_gpu_hour,
        hedge_gpu_hours=hedge_gpu_hours,
        settlement_months=[r.month_offset for r in settlements],
        side="buyer",
    )
    from math import isclose

    for supplied, calculated in zip(settlements, expected):
        if not isclose(
            _finite_number("settlement", supplied.amount_usd),
            calculated.amount_usd,
            rel_tol=1e-12,
            abs_tol=1e-8,
        ):
            raise ValueError(
                "settlement does not match buyer benchmark, strike and hedge quantity"
            )
    flows = combined_physical_and_hedge_cash_flows(
        physical_usd_per_gpu_hour=actual_usd_per_gpu_hour,
        physical_gpu_hours=physical_gpu_hours,
        physical_payment_months=physical_payment_months,
        settlements=settlements,
        side="buyer",
    )
    rows = []
    for actual, quantity, benchmark, hedge, month, settlement in zip(
        actual_usd_per_gpu_hour,
        physical_gpu_hours,
        benchmark_usd_per_gpu_hour,
        hedge_gpu_hours,
        physical_payment_months,
        settlements,
    ):
        unhedged = _finite_number("physical cost", quantity * actual)
        basis = _finite_number("basis", actual - benchmark)
        unmatched = _finite_number("unmatched GPU-hours", quantity - hedge)
        quantity_component = _finite_number(
            "unmatched benchmark cost", unmatched * benchmark
        )
        basis_component = _finite_number("basis cost", quantity * basis)
        strike_component = _finite_number(
            "strike component", hedge * strike_usd_per_gpu_hour
        )
        cost = _total([unhedged, -settlement.amount_usd])
        _total([quantity_component, basis_component, strike_component])
        rows.append(
            BasisExposureRow(
                month,
                settlement.month_offset,
                unhedged,
                settlement.amount_usd,
                cost,
                basis,
                unmatched,
                quantity_component,
                basis_component,
                strike_component,
            )
        )
    return BasisExposureSummary(
        tuple(rows),
        flows,
        _total([r.unhedged_cost_usd for r in rows]),
        _total([r.hedge_receipts_usd for r in rows]),
        _total([r.net_cost_usd for r in rows]),
    )


@dataclass(frozen=True)
class BasisBudget:
    """Matched-quantity buyer costs in USD; positive deviation means over budget."""

    basis_usd_per_gpu_hour: float
    unhedged_cost_usd: float
    hedge_receipt_usd: float
    net_cost_usd: float
    budgeted_cost_usd: float
    budget_deviation_usd: float


def basis_budget_summary(
    *,
    actual_usd_per_gpu_hour: float,
    benchmark_usd_per_gpu_hour: float,
    strike_usd_per_gpu_hour: float,
    gpu_hours: float,
    budget_basis_usd_per_gpu_hour: float,
) -> BasisBudget:
    """One aligned monthly purchase/hedge: b=S-I, cost=Q*(K+b), deviation=Q*(b-b0).

    Reuses M2 buyer settlement. Quantity is identical on both legs and cash
    settles together; no timing, fees, collateral, default or valuation model.
    Prices, strike and GPU-hours must be finite nonnegative numbers; b0 is any
    finite signed planning assumption, not an observed or guaranteed spread.
    Signed net/budget costs are retained (a hedge receipt can exceed the bill).
    Bools/wrong types raise TypeError; nonfinite/range/overflow raise ValueError.
    Zero quantity is valid but does not bypass input validation.
    """
    actual = _nonnegative("actual_usd_per_gpu_hour", actual_usd_per_gpu_hour)
    index = _nonnegative("benchmark_usd_per_gpu_hour", benchmark_usd_per_gpu_hour)
    quantity = _nonnegative("gpu_hours", gpu_hours)
    strike = _nonnegative("strike_usd_per_gpu_hour", strike_usd_per_gpu_hour)
    assumed = _finite_number(
        "budget_basis_usd_per_gpu_hour", budget_basis_usd_per_gpu_hour
    )
    receipt = forward_settlements_usd(
        benchmark_usd_per_gpu_hour=[index],
        strike_usd_per_gpu_hour=strike,
        hedge_gpu_hours=[quantity],
        settlement_months=[1],
        side="buyer",
    )[0].amount_usd
    basis = _finite_number("basis", actual - index)
    unhedged = _finite_number("physical cost", quantity * actual)
    net = _total([unhedged, -receipt])
    budget = _finite_number("budgeted cost", quantity * _total([strike, assumed]))
    deviation = _finite_number("budget deviation", quantity * _total([basis, -assumed]))
    return BasisBudget(basis, unhedged, receipt, net, budget, deviation)


def benchmark_basis_deviations_usd(
    *,
    actual_prices: "Mapping[str, float]",
    benchmark_prices: "Mapping[str, float]",
    baseline_basis_usd_per_gpu_hour: float,
    gpu_hours: float,
) -> dict[str, float]:
    """Residual Q*((S-I)-baseline) by scenario, in physical mapping order.

    Price mappings use USD/GPU-hour and nonempty scenario names. Require exactly
    matching nonempty scenario sets; never zip by order, drop gaps or fill zero.
    Values must be finite nonnegative numbers, baseline finite signed, quantity
    finite nonnegative. Reject invalid types/ranges as basis_budget_summary does.
    No probabilities, estimated losses or statistical benchmark ranking.
    """
    if not isinstance(actual_prices, Mapping) or not isinstance(
        benchmark_prices, Mapping
    ):
        raise TypeError("prices must be scenario mappings")
    if any(not isinstance(k, str) for k in (*actual_prices, *benchmark_prices)):
        raise TypeError("scenario names must be strings")
    if any(not k.strip() for k in (*actual_prices, *benchmark_prices)):
        raise ValueError("scenario names must be nonempty")
    if not actual_prices or actual_prices.keys() != benchmark_prices.keys():
        raise ValueError("physical and benchmark scenarios must match exactly")
    return {
        name: basis_budget_summary(
            actual_usd_per_gpu_hour=actual,
            benchmark_usd_per_gpu_hour=benchmark_prices[name],
            strike_usd_per_gpu_hour=0,
            gpu_hours=gpu_hours,
            budget_basis_usd_per_gpu_hour=baseline_basis_usd_per_gpu_hour,
        ).budget_deviation_usd
        for name, actual in actual_prices.items()
    }
