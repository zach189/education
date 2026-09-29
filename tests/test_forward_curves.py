from dataclasses import FrozenInstanceError
from math import expm1, fsum

import pytest

from liquid_compute.discounting import discount_factor
from liquid_compute.forward_curves import (
    ImpliedRentalBlock,
    RentalQuote,
    imply_rental_blocks,
    reconstruct_rental_quotes,
)

MENU = (RentalQuote(12, 6), RentalQuote(36, 5), RentalQuote(60, 4.4))
HOURS = [720.0] * 60


def rates(blocks):
    return [b.implied_usd_per_gpu_hour for b in blocks]


def test_baseline_and_missing_tenor():
    blocks = imply_rental_blocks(MENU, delivery_hours_per_gpu=HOURS)
    assert rates(blocks) == pytest.approx([6, 4.5, 3.5])
    assert reconstruct_rental_quotes(blocks, delivery_hours_per_gpu=HOURS) == MENU
    wider = imply_rental_blocks([MENU[0], MENU[2]], delivery_hours_per_gpu=HOURS)
    assert [(b.start_month_offset, b.end_month_offset) for b in wider] == [
        (0, 12),
        (12, 60),
    ]
    assert rates(wider) == pytest.approx([6, 4])
    with pytest.raises(FrozenInstanceError):
        blocks[0].end_month_offset = 20


@pytest.mark.parametrize(
    "prices,expected",
    [
        ([6, 5.2, 4.4], [6, 4.8, 3.2]),
        ([5, 5, 5], [5, 5, 5]),
        ([6, 5, 3], [6, 4.5, 0]),
        ([6, 5, 2.8], [6, 4.5, -0.5]),
    ],
)
def test_experiments(prices, expected):
    quotes = tuple(RentalQuote(t, p) for t, p in zip([12, 36, 60], prices))
    blocks = imply_rental_blocks(quotes, delivery_hours_per_gpu=HOURS)
    assert rates(blocks) == pytest.approx(expected)
    assert [
        q.rental_usd_per_gpu_hour
        for q in reconstruct_rental_quotes(blocks, delivery_hours_per_gpu=HOURS)
    ] == pytest.approx(prices)


@pytest.mark.parametrize(
    "rate,expected",
    [
        (0, [6, 4.5, 3.5]),
        (0.12, [6, 4.4083018867924535, 3.202024332075472]),
        (0.24, [6, 4.313571428571428, 2.844168457142861]),
    ],
)
def test_discounted_examples_and_pv(rate, expected):
    factors = [
        discount_factor(annual_discount_rate=rate, months=m) for m in range(1, 61)
    ]
    blocks = imply_rental_blocks(
        MENU, delivery_hours_per_gpu=HOURS, payment_discount_factors=factors
    )
    assert rates(blocks) == pytest.approx(expected)
    for q in MENU:
        direct = q.rental_usd_per_gpu_hour * fsum(
            720 * d for d in factors[: q.term_months]
        )
        reconstructed = fsum(
            b.implied_usd_per_gpu_hour
            * fsum(720 * d for d in factors[b.start_month_offset : b.end_month_offset])
            for b in blocks
            if b.end_month_offset <= q.term_months
        )
        assert reconstructed == pytest.approx(direct)
    recovered = reconstruct_rental_quotes(
        blocks, delivery_hours_per_gpu=HOURS, payment_discount_factors=factors
    )
    assert [q.rental_usd_per_gpu_hour for q in recovered] == pytest.approx([6, 5, 4.4])


def test_unequal_hours_and_scale_cancellation():
    quotes = [RentalQuote(1, 6), RentalQuote(3, 5)]
    hours = [100, 200, 300]
    blocks = imply_rental_blocks(quotes, delivery_hours_per_gpu=hours)
    assert rates(blocks) == pytest.approx([6, 4.8])
    assert rates(
        imply_rental_blocks(quotes, delivery_hours_per_gpu=[x * 10 for x in hours])
    ) == pytest.approx(rates(blocks))
    assert rates(
        imply_rental_blocks(
            quotes, delivery_hours_per_gpu=hours, payment_discount_factors=[1] * 3
        )
    ) == pytest.approx(rates(blocks))
    factors = [1, 0.9, 0.8]
    discounted = imply_rental_blocks(
        quotes, delivery_hours_per_gpu=hours, payment_discount_factors=factors
    )
    assert rates(discounted) == pytest.approx([6, (5 * 520 - 600) / 420])
    assert reconstruct_rental_quotes(
        discounted, delivery_hours_per_gpu=hours, payment_discount_factors=factors
    ) == tuple(quotes)


def test_source_reproduction():
    quotes = [RentalQuote(12, 6.25), RentalQuote(36, 4.85), RentalQuote(60, 4.15)]
    assert rates(
        imply_rental_blocks(quotes, delivery_hours_per_gpu=HOURS)
    ) == pytest.approx([6.25, 4.15, 3.1])
    factors = [
        discount_factor(annual_discount_rate=expm1(0.1), months=m) for m in range(1, 61)
    ]
    assert rates(
        imply_rental_blocks(
            quotes, delivery_hours_per_gpu=HOURS, payment_discount_factors=factors
        )
    ) == pytest.approx([6.25, 4.037731577164609, 2.7989646232791023])
    effective_ten = [
        discount_factor(annual_discount_rate=0.1, months=m) for m in range(1, 61)
    ]
    assert rates(
        imply_rental_blocks(
            quotes, delivery_hours_per_gpu=HOURS, payment_discount_factors=effective_ten
        )
    )[1] != pytest.approx(4.037731577164609)


@pytest.mark.parametrize(
    "quotes,error",
    [
        ([], ValueError),
        ([1], TypeError),
        ([RentalQuote(True, 5)], TypeError),
        ([RentalQuote(1.0, 5)], TypeError),
        ([RentalQuote(0, 5)], ValueError),
        ([RentalQuote(2, 5), RentalQuote(1, 5)], ValueError),
        ([RentalQuote(1, 5), RentalQuote(1, 6)], ValueError),
        ([RentalQuote(1, True)], TypeError),
        ([RentalQuote(1, "5")], TypeError),
        ([RentalQuote(1, -1)], ValueError),
        ([RentalQuote(1, 0)], ValueError),
        ([RentalQuote(1, float("nan"))], ValueError),
        ([RentalQuote(1, float("inf"))], ValueError),
    ],
)
def test_invalid_quotes(quotes, error):
    with pytest.raises(error):
        imply_rental_blocks(quotes, delivery_hours_per_gpu=[720])


@pytest.mark.parametrize(
    "hours,factors,error",
    [
        ([], None, ValueError),
        ([720, 720], None, ValueError),
        ([720], [], ValueError),
        ([True], None, TypeError),
        ([0], None, ValueError),
        ([-1], None, ValueError),
        ([float("nan")], None, ValueError),
        ([float("inf")], None, ValueError),
        ([720], [True], TypeError),
        ([720], [0], ValueError),
        ([720], [1.01], ValueError),
        ([720], [float("nan")], ValueError),
        ([720], [float("inf")], ValueError),
        ([1e-300], [1e-300], ValueError),
        ([1e308], None, ValueError),
    ],
)
def test_invalid_weights(hours, factors, error):
    with pytest.raises(error):
        imply_rental_blocks(
            [RentalQuote(1, 6)],
            delivery_hours_per_gpu=hours,
            payment_discount_factors=factors,
        )


@pytest.mark.parametrize(
    "blocks,error",
    [
        ([], ValueError),
        ([1], TypeError),
        ([ImpliedRentalBlock(1, 2, 5)], ValueError),
        ([ImpliedRentalBlock(0, 0, 5)], ValueError),
        ([ImpliedRentalBlock(True, 1, 5)], TypeError),
        ([ImpliedRentalBlock(0, 1, float("inf"))], ValueError),
        ([ImpliedRentalBlock(0, 1, 5), ImpliedRentalBlock(2, 3, 5)], ValueError),
        ([ImpliedRentalBlock(0, 1, True)], TypeError),
    ],
)
def test_invalid_blocks(blocks, error):
    with pytest.raises(error):
        reconstruct_rental_quotes(blocks, delivery_hours_per_gpu=[720])


def test_signed_reconstruction_and_overflow():
    assert reconstruct_rental_quotes(
        [ImpliedRentalBlock(0, 1, -5)], delivery_hours_per_gpu=[720]
    ) == (RentalQuote(1, -5),)
    with pytest.raises(ValueError):
        reconstruct_rental_quotes(
            [ImpliedRentalBlock(0, 1, 1e308)], delivery_hours_per_gpu=[720]
        )
    with pytest.raises(ValueError):
        imply_rental_blocks([RentalQuote(2, 1)], delivery_hours_per_gpu=[1e308, 1e308])
