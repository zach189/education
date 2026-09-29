"""Conditional binomial valuation for an ideal tradable, non-dividend proxy.

Frictionless trading, shorting and equal borrowing/lending rates are assumed.
Values are per normalized proxy unit, never executable compute quotes.
"""

from dataclasses import dataclass
from typing import Literal

from .cashflows import _integer
from .economics import _finite_number
from .financing import _nonnegative
from .options import european_option_payoff_usd


@dataclass(frozen=True)
class BinomialTree:
    """Rows indexed by step, then number of up moves (down node first)."""

    prices_usd_per_unit: tuple[tuple[float, ...], ...]
    option_values_usd: tuple[tuple[float, ...], ...]
    pricing_up_weight: float
    step_growth_factor: float
    step_years: float


@dataclass(frozen=True)
class Replication:
    """Time-zero holdings and value for one normalized option unit."""

    delta_units: float
    cash_position_usd: float
    pricing_up_weight: float
    value_usd: float
    down_price_usd: float
    up_price_usd: float
    down_payoff_usd: float
    up_payoff_usd: float
    step_growth_factor: float


def _backward_values(
    terminal_values: tuple[float, ...], weight: float, growth: float
) -> tuple[tuple[float, ...], ...]:
    """Shared European recursion; E1 may reuse it for intermediate node claims."""
    rows = [terminal_values]
    while len(rows[-1]) > 1:
        previous = rows[-1]
        rows.append(
            tuple(
                _finite_number(
                    "backward value",
                    ((1 - weight) * previous[j] + weight * previous[j + 1]) / growth,
                )
                for j in range(len(previous) - 1)
            )
        )
    return tuple(reversed(rows))


def binomial_european_option_tree(
    *,
    kind: Literal["call", "put"],
    spot_usd_per_unit: float,
    strike_usd_per_unit: float,
    up_factor: float,
    down_factor: float,
    effective_annual_rate: float,
    step_years: float,
    steps: int,
) -> BinomialTree:
    """Recombining European tree with explicit horizon steps * step_years.

    Positive spot, factors and duration; 0 < down < growth < up strictly.
    Rate/strike nonnegative. Steps is a positive integer. No business probability
    input: pricing weight follows replication. M5 payoff is reused on one unit
    via an explicitly normalized proxy mapping, not actual physical GPU supply.
    Wrong types/bools raise TypeError; invalid bounds/nonfinite/overflow raise
    ValueError. Extreme inputs that lose distinguishable nodes are rejected.
    """
    spot = _nonnegative("spot_usd_per_unit", spot_usd_per_unit)
    strike = _nonnegative("strike_usd_per_unit", strike_usd_per_unit)
    up = _nonnegative("up_factor", up_factor)
    down = _nonnegative("down_factor", down_factor)
    rate = _nonnegative("effective_annual_rate", effective_annual_rate)
    duration = _nonnegative("step_years", step_years)
    count = _integer("steps", steps, minimum=1)
    if spot == 0 or duration == 0 or not 0 < down < up:
        raise ValueError(
            "require positive spot/duration and 0 < down_factor < up_factor"
        )
    try:
        growth = _finite_number("step growth", (1 + rate) ** duration)
    except OverflowError as error:
        raise ValueError("step growth overflow") from error
    if not down < growth < up:
        raise ValueError("no-arbitrage requires down_factor < growth < up_factor")
    weight = (growth - down) / (up - down)
    if not 0 < weight < 1:
        raise ValueError(
            "pricing weight is numerically indistinguishable from a boundary"
        )
    rows: list[tuple[float, ...]] = [(spot,)]
    for _ in range(count):
        previous = rows[-1]
        current = tuple(_finite_number("tree node", p * down) for p in previous) + (
            _finite_number("tree node", previous[-1] * up),
        )
        if current[0] <= 0 or any(a >= b for a, b in zip(current, current[1:])):
            raise ValueError("tree nodes must remain positive and distinguishable")
        rows.append(current)
    terminal = tuple(
        european_option_payoff_usd(
            kind=kind,
            settlement_price_usd_per_gpu_hour=price,
            strike_usd_per_gpu_hour=strike,
            covered_gpu_hours=1,
        )
        for price in rows[-1]
    )
    return BinomialTree(
        tuple(rows),
        _backward_values(terminal, weight, growth),
        weight,
        growth,
        duration,
    )


def binomial_european_option_value_usd(
    *,
    kind: Literal["call", "put"],
    spot_usd_per_unit: float,
    strike_usd_per_unit: float,
    up_factor: float,
    down_factor: float,
    effective_annual_rate: float,
    step_years: float,
    steps: int,
) -> float:
    """Root USD value per unit; assumptions/validation as the explicit tree API."""
    return binomial_european_option_tree(
        kind=kind,
        spot_usd_per_unit=spot_usd_per_unit,
        strike_usd_per_unit=strike_usd_per_unit,
        up_factor=up_factor,
        down_factor=down_factor,
        effective_annual_rate=effective_annual_rate,
        step_years=step_years,
        steps=steps,
    ).option_values_usd[0][0]


def one_step_replication(
    *,
    kind: Literal["call", "put"],
    spot_usd_per_unit: float,
    strike_usd_per_unit: float,
    up_factor: float,
    down_factor: float,
    effective_annual_rate: float,
    step_years: float,
) -> Replication:
    """Solve delta and cash reproducing both terminal payoffs, per proxy unit.

    Negative cash denotes borrowing; put delta may be negative. No clipping.
    Uses the tree's strict validation and effective annual compounding.
    """
    tree = binomial_european_option_tree(
        kind=kind,
        spot_usd_per_unit=spot_usd_per_unit,
        strike_usd_per_unit=strike_usd_per_unit,
        up_factor=up_factor,
        down_factor=down_factor,
        effective_annual_rate=effective_annual_rate,
        step_years=step_years,
        steps=1,
    )
    down, up = tree.prices_usd_per_unit[-1]
    vd, vu = tree.option_values_usd[-1]
    delta = _finite_number("delta", (vu - vd) / (up - down))
    cash = _finite_number(
        "cash position", (vd - delta * down) / tree.step_growth_factor
    )
    value = _finite_number("replicating value", delta * spot_usd_per_unit + cash)
    return Replication(
        delta,
        cash,
        tree.pricing_up_weight,
        value,
        down,
        up,
        vd,
        vu,
        tree.step_growth_factor,
    )


@dataclass(frozen=True)
class CompoundCallValue:
    """One intermediate purchase right on a two-step European call.

    Nodes ordered down/up. Exercise on strict positive surplus; at equality
    choose not to exercise (indifferent under the model). Node surplus is a
    valuation, not a cash receipt in a physically exercised purchase right.
    """

    underlying_tree: BinomialTree
    underlying_node_values_usd: tuple[float, ...]
    exercise_at_node: tuple[bool, ...]
    node_surplus_usd: tuple[float, ...]
    premium_usd: float
    immediate_call_value_usd: float
    exercise_fee_usd_per_unit: float


def compound_call_value(
    *,
    spot_usd_per_unit: float,
    strike_usd_per_unit: float,
    up_factor: float,
    down_factor: float,
    effective_annual_rate: float,
    step_years: float,
    exercise_fee_usd_per_unit: float,
) -> CompoundCallValue:
    """Value a purchase right at step 1 on a call expiring at step 2.

    Reuses M6 tree and backward recursion. Fee is finite nonnegative USD per
    normalized proxy unit, paid only upon exercise. All other validation and
    trading assumptions follow binomial_european_option_tree. This is exactly
    two equal-duration steps, not an American or multi-layer compound option.
    """
    fee = _nonnegative("exercise_fee_usd_per_unit", exercise_fee_usd_per_unit)
    tree = binomial_european_option_tree(
        kind="call",
        spot_usd_per_unit=spot_usd_per_unit,
        strike_usd_per_unit=strike_usd_per_unit,
        up_factor=up_factor,
        down_factor=down_factor,
        effective_annual_rate=effective_annual_rate,
        step_years=step_years,
        steps=2,
    )
    node_values = tree.option_values_usd[1]
    surplus = tuple(max(value - fee, 0.0) for value in node_values)
    premium = _backward_values(
        surplus, tree.pricing_up_weight, tree.step_growth_factor
    )[0][0]
    return CompoundCallValue(
        tree,
        node_values,
        tuple(value > fee for value in node_values),
        surplus,
        premium,
        tree.option_values_usd[0][0],
        fee,
    )
