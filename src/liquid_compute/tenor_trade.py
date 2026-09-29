"""Unfinanced reseller commitments; quoted invoices are not implied block rates."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .economics import _finite_number
from .financing import _fraction, _nonnegative, _total


@dataclass(frozen=True)
class ResellerCommitmentRow:
    """USD/GPU-hour rates and USD cash at monthly boundaries, including t=0.

    customer_contracted labels the receipt assumption, not legal enforceability.
    Purchased hours must be paid even when billed hours are zero. No debt,
    physical hardware resale, taxes, overhead or discounting is included.
    Selling fees apply only to actual revenue; billed hours are booked and
    paid hours, not technical processor utilization.
    """

    month_offset: int
    purchased_gpu_hours: float
    billed_gpu_hours: float
    supplier_usd_per_gpu_hour: float
    customer_usd_per_gpu_hour: float
    customer_contracted: bool
    supplier_cash_usd: float
    customer_cash_usd: float
    contribution_usd: float
    cumulative_cash_usd: float
    selling_cost_usd: float = 0.0

    @property
    def sold_gpu_hours(self) -> float:
        """Booked hours paid by customers, regardless of technical usage."""
        return self.billed_gpu_hours

    @property
    def unplaced_gpu_hours(self) -> float:
        """Purchased hours without a paying customer; no inventory carryover."""
        return self.purchased_gpu_hours - self.billed_gpu_hours


def build_reseller_commitment_scenario(
    *,
    purchased_gpu_hours: Sequence[float],
    supplier_usd_per_gpu_hour: Sequence[float],
    billed_fractions: Sequence[float],
    customer_usd_per_gpu_hour: Sequence[float],
    customer_contracted: Sequence[bool],
    selling_fee_fraction: float = 0.0,
) -> tuple[ResellerCommitmentRow, ...]:
    """Build same-month-end cash from explicit monthly terms, no t=0 inputs.

    All input arrays start at service month 1 and have the same positive length.
    Hours and rates are finite nonnegative numbers excluding bool; fractions
    are in [0,1], contract flags bool. Zero hours/rates are supported for explicit
    zero-service periods. Contracted flags do not manufacture receipts: callers
    must supply zero billed usage when modeling contract-only later cash.
    billed_fractions measures placement, not technical utilization. The scalar
    selling fee is in [0,1] and applies to all realized customer revenue.
    Wrong types raise TypeError; ranges, lengths and overflow raise ValueError.
    """
    fee = _fraction("selling_fee_fraction", selling_fee_fraction, inclusive=True)
    n = len(purchased_gpu_hours)
    if not n or any(
        len(values) != n
        for values in (
            supplier_usd_per_gpu_hour,
            billed_fractions,
            customer_usd_per_gpu_hour,
            customer_contracted,
        )
    ):
        raise ValueError("monthly arrays must be nonempty and equal length")
    rows = [ResellerCommitmentRow(0, 0, 0, 0, 0, False, 0, 0, 0, 0)]
    cash = 0.0
    for t, (hours, supplier, fraction, customer, contracted) in enumerate(
        zip(
            purchased_gpu_hours,
            supplier_usd_per_gpu_hour,
            billed_fractions,
            customer_usd_per_gpu_hour,
            customer_contracted,
        ),
        1,
    ):
        hours = _nonnegative("purchased_gpu_hours", hours)
        supplier = _nonnegative("supplier_usd_per_gpu_hour", supplier)
        fraction = _fraction("billed_fraction", fraction, inclusive=True)
        customer = _nonnegative("customer_usd_per_gpu_hour", customer)
        if not isinstance(contracted, bool):
            raise TypeError("customer_contracted entries must be bool")
        billed = _finite_number("billed GPU-hours", hours * fraction)
        expense = _finite_number("supplier cash", hours * supplier)
        revenue = _finite_number("customer cash", billed * customer)
        selling_cost = _finite_number("selling cost", revenue * fee)
        contribution = _finite_number("contribution", revenue - selling_cost - expense)
        cash = _total([cash, contribution])
        rows.append(
            ResellerCommitmentRow(
                t,
                hours,
                billed,
                supplier,
                customer,
                contracted,
                expense,
                revenue,
                contribution,
                cash,
                selling_cost,
            )
        )
    return tuple(rows)


def compare_tenor_strategies(
    *,
    supplier_rate_scenarios: Mapping[str, Sequence[float]],
    purchased_gpu_hours: Sequence[float],
    billed_fractions: Sequence[float],
    customer_usd_per_gpu_hour: Sequence[float],
    customer_contracted: Sequence[bool],
) -> dict[str, tuple[ResellerCommitmentRow, ...]]:
    """Compare caller-supplied supplier paths, not forecasts from implied quotes.

    Names are nonempty strings; at least one scenario is required. Cash input
    units/ranges/indexing match build_reseller_commitment_scenario.
    """
    if not supplier_rate_scenarios:
        raise ValueError("at least one supplier scenario is required")
    result = {}
    for name, rates in supplier_rate_scenarios.items():
        if not isinstance(name, str):
            raise TypeError("scenario names must be strings")
        if not name.strip():
            raise ValueError("scenario names must be nonempty")
        result[name] = build_reseller_commitment_scenario(
            purchased_gpu_hours=purchased_gpu_hours,
            supplier_usd_per_gpu_hour=rates,
            billed_fractions=billed_fractions,
            customer_usd_per_gpu_hour=customer_usd_per_gpu_hour,
            customer_contracted=customer_contracted,
        )
    return result


@dataclass(frozen=True)
class TenorTailOutcome:
    """Whole-deal USD contribution and conditional tail break-even requirements.

    A None hurdle means no finite solution at the chosen price/placement.
    Required placement may exceed 1; placement_attainable explicitly flags it.
    If contracted net revenue already covers costs, both hurdles are zero.
    """

    tail_revenue_usd: float
    selling_cost_usd: float
    contribution_usd: float
    required_tail_revenue_usd: float | None
    break_even_resale_usd_per_gpu_hour: float | None
    break_even_placement_fraction: float | None
    placement_attainable: bool
    costs_already_recovered: bool


def tenor_tail_outcome(
    *,
    upstream_commitment_usd: float,
    contracted_revenue_usd: float,
    tail_available_gpu_hours: float,
    future_resale_usd_per_gpu_hour: float,
    placement_fraction: float,
    selling_fee_fraction: float,
) -> TenorTailOutcome:
    """Evaluate an average-price tail after a separately contracted first period.

    Costs/revenue/hours/prices must be finite nonnegative numbers; placement and
    fee are in [0,1]. Bools and nonnumeric values are rejected. Selling fees
    apply to contracted AND future sales. No overhead, financing or hardware
    proceeds are included. This is contractual/scenario arithmetic, not PV.

    Tail hours include every remaining purchased hour. If a gap is excluded
    from those hours instead, placement must refer only to the remaining active
    hours: never also apply a gap-adjusted fraction. Upstream commitment always
    includes the gap. Monthly schedules model gaps with explicit zero placement.

    Zero price, placement, hours and a 100% fee are valid economic scenarios.
    An undefined required price/placement returns None rather than infinity;
    a finite placement above 1 remains visible as unattainable. Overflow raises
    ValueError. If initial net sales cover cost, a zero hurdle means no further
    revenue is needed, not that a positive existing surplus becomes zero.
    """
    cost = _nonnegative("upstream_commitment_usd", upstream_commitment_usd)
    initial = _nonnegative("contracted_revenue_usd", contracted_revenue_usd)
    hours = _nonnegative("tail_available_gpu_hours", tail_available_gpu_hours)
    price = _nonnegative(
        "future_resale_usd_per_gpu_hour", future_resale_usd_per_gpu_hour
    )
    placement = _fraction("placement_fraction", placement_fraction, inclusive=True)
    fee = _fraction("selling_fee_fraction", selling_fee_fraction, inclusive=True)
    tail_revenue = _finite_number("tail revenue", hours * placement * price)
    revenue = _total([initial, tail_revenue])
    selling_cost = _finite_number("selling costs", revenue * fee)
    contribution = _total([revenue, -selling_cost, -cost])
    remaining_cost = max(0.0, _total([cost, -initial * (1 - fee)]))
    recovered = remaining_cost == 0
    required_revenue = (
        0.0
        if recovered
        else None
        if fee == 1
        else _finite_number("required tail revenue", remaining_cost / (1 - fee))
    )

    def hurdle(denominator: float) -> float | None:
        if recovered:
            return 0.0
        if denominator == 0 or required_revenue is None:
            return None
        return _finite_number("break-even hurdle", required_revenue / denominator)

    required_price = hurdle(_finite_number("placed hours", hours * placement))
    required_placement = hurdle(_finite_number("full-placement revenue", hours * price))
    return TenorTailOutcome(
        tail_revenue,
        selling_cost,
        contribution,
        required_revenue,
        required_price,
        required_placement,
        required_placement is not None and required_placement <= 1,
        recovered,
    )
