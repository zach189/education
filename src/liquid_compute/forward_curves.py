"""Allocate rental package costs to implied blocks, not executable forward quotes."""

from collections.abc import Sequence
from dataclasses import dataclass
from math import fsum

from .cashflows import _integer
from .economics import _finite_number, _positive_number


@dataclass(frozen=True)
class RentalQuote:
    """Flat USD/GPU-hour package rate from commencement through term_months.

    Data carrier: inference validates positive source quotes. Reconstruction may
    return signed rates when supplied arbitrary signed block allocations.
    """

    term_months: int
    rental_usd_per_gpu_hour: float


@dataclass(frozen=True)
class ImpliedRentalBlock:
    """USD/GPU-hour allocation for months start+1 through end; may be signed.

    Delivery spans [start_month_offset, end_month_offset). A flat monthly shape
    within this interval is an additional assumption, not separately identified.
    """

    start_month_offset: int
    end_month_offset: int
    implied_usd_per_gpu_hour: float


def _sum(values: Sequence[float]) -> float:
    try:
        return _finite_number("weighted total", fsum(values))
    except OverflowError as exc:
        raise ValueError("weighted total must be finite") from exc


def _weights(
    months: int, hours: Sequence[float], factors: Sequence[float] | None
) -> tuple[float, ...]:
    if len(hours) != months or (factors is not None and len(factors) != months):
        raise ValueError("weight arrays must have exactly the final tenor's length")
    result = []
    for i, value in enumerate(hours):
        h = _positive_number("delivery_hours_per_gpu", value)
        d = (
            1.0
            if factors is None
            else _positive_number("payment_discount_factor", factors[i])
        )
        if d > 1:
            raise ValueError("payment_discount_factors must be in (0, 1]")
        result.append(_positive_number("effective monthly weight", h * d))
    return tuple(result)


def imply_rental_blocks(
    quotes: Sequence[RentalQuote],
    *,
    delivery_hours_per_gpu: Sequence[float],
    payment_discount_factors: Sequence[float] | None = None,
) -> tuple[ImpliedRentalBlock, ...]:
    """Subtract overlapping weighted package costs and divide by block weights.

    Quotes must be nonempty, positive finite rates with strictly increasing
    positive integer tenors. All packages start together with matching capacity,
    service, and payment dates/hours in overlapping months. Array index zero is
    service month 1 (unlike the time-zero cash array in present_value_usd).
    Hours are positive per GPU; factors are finite in (0,1], defaulting to one.
    Arrays cover exactly the final tenor. Missing quotes must be omitted, never
    filled or interpolated. Returns the actual wider block between known tenors.

    Nonpositive implied rates are valid economic results, not arbitrage claims.
    Reject bools/wrong types with TypeError, invalid ranges/order, nonfinite
    arithmetic and zero effective weights with ValueError. Does not change quotes
    or remove commercial discounts; not valid unchanged for mixed payment terms.
    """
    if not quotes:
        raise ValueError("at least one rental quote is required")
    previous = 0
    for q in quotes:
        if not isinstance(q, RentalQuote):
            raise TypeError("quotes must contain RentalQuote records")
        end = _integer("term_months", q.term_months, minimum=1)
        if end <= previous:
            raise ValueError("tenors must be strictly increasing")
        _positive_number("rental_usd_per_gpu_hour", q.rental_usd_per_gpu_hour)
        previous = end
    weights = _weights(previous, delivery_hours_per_gpu, payment_discount_factors)
    start = 0
    previous_cost = 0.0
    blocks = []
    for q in quotes:
        cost = _finite_number(
            "package weighted cost",
            q.rental_usd_per_gpu_hour * _sum(weights[: q.term_months]),
        )
        block_weight = _positive_number(
            "block weight", _sum(weights[start : q.term_months])
        )
        rate = _finite_number(
            "implied_usd_per_gpu_hour", (cost - previous_cost) / block_weight
        )
        blocks.append(ImpliedRentalBlock(start, q.term_months, rate))
        start, previous_cost = q.term_months, cost
    return tuple(blocks)


def reconstruct_rental_quotes(
    blocks: Sequence[ImpliedRentalBlock],
    *,
    delivery_hours_per_gpu: Sequence[float],
    payment_discount_factors: Sequence[float] | None = None,
) -> tuple[RentalQuote, ...]:
    """Recover package rates at block endpoints using the same monthly weights.

    Blocks must be nonempty, contiguous from zero, with integer positive lengths
    and finite signed rates. Weight units/indexing and exceptions match inference.
    Arbitrary signed allocations can produce signed reconstructed package rates.
    Multiplying each returned rate by its cumulative weight recovers package USD
    per GPU (present value when discounted). No forecast or offer is implied.
    """
    if not blocks:
        raise ValueError("at least one block is required")
    previous = 0
    for b in blocks:
        if not isinstance(b, ImpliedRentalBlock):
            raise TypeError("blocks must contain ImpliedRentalBlock records")
        start = _integer("start_month_offset", b.start_month_offset)
        end = _integer("end_month_offset", b.end_month_offset, minimum=1)
        if start != previous or end <= start:
            raise ValueError(
                "blocks must be contiguous from zero with positive lengths"
            )
        _finite_number("implied_usd_per_gpu_hour", b.implied_usd_per_gpu_hour)
        previous = end
    weights = _weights(previous, delivery_hours_per_gpu, payment_discount_factors)
    costs = []
    quotes = []
    for b in blocks:
        weight = _positive_number(
            "block weight", _sum(weights[b.start_month_offset : b.end_month_offset])
        )
        costs.append(
            _finite_number("block weighted cost", b.implied_usd_per_gpu_hour * weight)
        )
        rate = _finite_number(
            "reconstructed rate", _sum(costs) / _sum(weights[: b.end_month_offset])
        )
        quotes.append(RentalQuote(b.end_month_offset, rate))
    return tuple(quotes)
