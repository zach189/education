"""Separate futures settlement and hypothetical one-way OTC posting ledgers."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from .economics import _finite_number
from .financing import _nonnegative, _total
from .hedging import forward_settlements_usd


@dataclass(frozen=True)
class HedgeLiquidityRow:
    """Signed cash to hedge holder; restricted balance is positive USD posted.

    Balance is measured after transfers at that boundary. All posted cash is
    returned at expiry; no interest, default or fees. Net cash excludes physical
    receipts, which callers combine at their own explicit dates.
    """

    month_offset: int
    derivative_settlement_usd: float
    collateral_transfer_usd: float
    restricted_balance_usd: float
    net_cash_usd: float
    cumulative_cash_usd: float


def futures_variation_cash_flows(
    *,
    entry_usd_per_gpu_hour: float,
    marks_usd_per_gpu_hour: Sequence[float],
    hedge_gpu_hours: float,
    mark_months: Sequence[int],
    side: Literal["buyer", "seller"],
    initial_margin_usd: float,
) -> tuple[HedgeLiquidityRow, ...]:
    """Settle each change in marked value, plus fixed initial margin at t=0.

    Buyer means long and seller short. Marks are nonnegative; months positive,
    strictly ascending, nonempty, same length as marks. Last mark is expiry.
    Margin is nonnegative and returned at expiry after the final variation.
    Dense monthly rows net same-boundary cash. Variation telescopes to M2's
    endpoint settlement: do NOT add that endpoint amount again. Monthly marks
    can miss intra-month liquidity peaks. Initial margin is never P&L.
    M2 validation: wrong types/bools TypeError; range/nonfinite/overflow ValueError.
    """
    margin = _nonnegative("initial_margin_usd", initial_margin_usd)
    # M2 amounts here are cumulative P&L at each mark, not repeated payments.
    marked = forward_settlements_usd(
        benchmark_usd_per_gpu_hour=marks_usd_per_gpu_hour,
        strike_usd_per_gpu_hour=entry_usd_per_gpu_hour,
        hedge_gpu_hours=[hedge_gpu_hours] * len(mark_months),
        settlement_months=mark_months,
        side=side,
    )
    movements = {}
    prior = 0.0
    for mark in marked:
        movements[mark.month_offset] = _finite_number(
            "variation settlement", mark.amount_usd - prior
        )
        prior = mark.amount_usd
    expiry = marked[-1].month_offset
    rows = []
    cumulative = 0.0
    for month in range(expiry + 1):
        transfer = -margin if month == 0 else margin if month == expiry else 0.0
        settlement = movements.get(month, 0.0)
        net = _total([transfer, settlement])
        cumulative = _total([cumulative, net])
        rows.append(
            HedgeLiquidityRow(
                month,
                settlement,
                transfer,
                margin if month < expiry else 0.0,
                net,
                cumulative,
            )
        )
    return tuple(rows)


def otc_collateral_transfers(
    *,
    entry_usd_per_gpu_hour: float,
    marks_usd_per_gpu_hour: Sequence[float],
    hedge_gpu_hours: float,
    mark_months: Sequence[int],
    side: Literal["buyer", "seller"],
    threshold_usd: float,
) -> tuple[HedgeLiquidityRow, ...]:
    """One-way posting for negative undiscounted value proxy Q*(mark-entry).

    Sign is long/buyer or short/seller per M2. Before expiry required posted cash
    is max(0, -value_proxy-threshold). Positive values trigger no receipt from
    the counterparty: this ledger models only this party's posting obligation.
    Transfers are balance differences, not derivative P&L. At final mark return
    all collateral and record M2's terminal settlement once. No post-and-return
    round trip at expiry, MTA, interest, discounting or default. Threshold finite
    nonnegative; remaining inputs follow futures/M2 validation. Dense monthly
    same-boundary netting may understate actual intraday cash requirements.
    """
    threshold = _nonnegative("threshold_usd", threshold_usd)
    marked = forward_settlements_usd(
        benchmark_usd_per_gpu_hour=marks_usd_per_gpu_hour,
        strike_usd_per_gpu_hour=entry_usd_per_gpu_hour,
        hedge_gpu_hours=[hedge_gpu_hours] * len(mark_months),
        settlement_months=mark_months,
        side=side,
    )
    values = {row.month_offset: row.amount_usd for row in marked}
    expiry = marked[-1].month_offset
    balance = cumulative = 0.0
    rows = []
    for month in range(expiry + 1):
        required = balance
        if month == expiry:
            required = 0.0
        elif month in values:
            required = max(0.0, -values[month] - threshold)
        transfer = _finite_number("collateral transfer", balance - required)
        settlement = values[month] if month == expiry else 0.0
        net = _total([transfer, settlement])
        cumulative = _total([cumulative, net])
        rows.append(
            HedgeLiquidityRow(month, settlement, transfer, required, net, cumulative)
        )
        balance = required
    return tuple(rows)
