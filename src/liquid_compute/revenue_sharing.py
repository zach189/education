"""Hypothetical bilateral revenue allocation, not valuation or a debt waterfall."""

from dataclasses import dataclass

from .economics import _finite_number
from .financing import _fraction, _nonnegative, _total


@dataclass(frozen=True)
class RevenueShare:
    """USD allocations; counterparty net may be negative when funding a guarantee."""

    reference_revenue_usd: float
    guaranteed_revenue_usd: float
    supplier_receipts_usd: float
    counterparty_net_usd: float


def minimum_revenue_share_usd(
    *,
    reference_revenue_usd: float,
    guaranteed_revenue_usd: float,
    supplier_upside_fraction: float,
) -> RevenueShare:
    """Supplier gets G + alpha*max(R-G,0); counterparty retains R minus payout.

    R/G finite nonnegative USD; alpha in [0,1]. This is a specified commercial
    promise, with no separate premium, discounting, default or collateral.
    Negative counterparty net is a required contribution, never clipped away.
    Invalid types/bools raise TypeError; range/nonfinite/overflow ValueError.
    """
    revenue = _nonnegative("reference_revenue_usd", reference_revenue_usd)
    guarantee = _nonnegative("guaranteed_revenue_usd", guaranteed_revenue_usd)
    fraction = _fraction(
        "supplier_upside_fraction", supplier_upside_fraction, inclusive=True
    )
    supplier = _total([guarantee, fraction * max(revenue - guarantee, 0)])
    counterparty = _finite_number("counterparty net", revenue - supplier)
    return RevenueShare(revenue, guarantee, supplier, counterparty)


def delivered_hour_revenue_share(
    *,
    delivered_gpu_hours: float,
    reference_usd_per_gpu_hour: float,
    guarantee_usd_per_gpu_hour: float,
    supplier_upside_fraction: float,
) -> RevenueShare:
    """Convert delivered hours to R and G under a per-delivered-hour guarantee.

    Hours and rates finite nonnegative; zero hours implies zero R/G/payout.
    For a fixed-total guarantee, use minimum_revenue_share_usd explicitly instead.
    Quantity is delivered service, not promised capacity or technical utilization.
    """
    hours = _nonnegative("delivered_gpu_hours", delivered_gpu_hours)
    rate = _nonnegative("reference_usd_per_gpu_hour", reference_usd_per_gpu_hour)
    guarantee_rate = _nonnegative(
        "guarantee_usd_per_gpu_hour", guarantee_usd_per_gpu_hour
    )
    return minimum_revenue_share_usd(
        reference_revenue_usd=_finite_number("reference revenue", hours * rate),
        guaranteed_revenue_usd=_finite_number(
            "guaranteed revenue", hours * guarantee_rate
        ),
        supplier_upside_fraction=supplier_upside_fraction,
    )
