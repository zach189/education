"""Independent examples and invariants for the revised M1; no notebook execution."""

import pytest

from liquid_compute.tenor_trade import (
    build_reseller_commitment_scenario,
    tenor_tail_outcome,
)

TAIL = dict(
    upstream_commitment_usd=1296000,
    contracted_revenue_usd=691200,
    tail_available_gpu_hours=172800,
    future_resale_usd_per_gpu_hour=6.5,
    placement_fraction=0.9,
    selling_fee_fraction=0.05,
)


def schedule(price=6.5, placement=0.9, gap=0, fee=0.05):
    return build_reseller_commitment_scenario(
        purchased_gpu_hours=[7200] * 36,
        supplier_usd_per_gpu_hour=[5] * 36,
        billed_fractions=[1] * 12 + [0] * gap + [placement] * (24 - gap),
        customer_usd_per_gpu_hour=[8] * 12 + [price] * 24,
        customer_contracted=[True] * 12 + [False] * 24,
        selling_fee_fraction=fee,
    )


def test_full_deal_independent_arithmetic_and_partition():
    rows = schedule()
    assert sum(r.customer_cash_usd for r in rows if r.customer_contracted) == 691200
    assert rows[12].cumulative_cash_usd == pytest.approx(224640)
    assert sum(
        r.customer_cash_usd for r in rows if not r.customer_contracted
    ) == pytest.approx(1010880)
    assert sum(r.selling_cost_usd for r in rows) == pytest.approx(85104)
    assert rows[-1].cumulative_cash_usd == pytest.approx(320976)
    for r in rows:
        assert r.sold_gpu_hours + r.unplaced_gpu_hours == pytest.approx(
            r.purchased_gpu_hours
        )
        assert 0 <= r.sold_gpu_hours <= r.purchased_gpu_hours
        assert r.selling_cost_usd == pytest.approx(r.customer_cash_usd * 0.05)
    assert sum(r.contribution_usd for r in rows) == pytest.approx(
        rows[-1].cumulative_cash_usd
    )
    assert tenor_tail_outcome(**TAIL).contribution_usd == pytest.approx(
        rows[-1].cumulative_cash_usd
    )


def test_hurdles_zero_profit_and_first_year_credit():
    result = tenor_tail_outcome(**TAIL)
    assert result.required_tail_revenue_usd == pytest.approx(673010.5263157895)
    assert result.break_even_resale_usd_per_gpu_hour == pytest.approx(4.327485380116959)
    assert result.break_even_placement_fraction == pytest.approx(0.5991902834008097)
    assert result.placement_attainable and not result.costs_already_recovered
    for change in [
        dict(future_resale_usd_per_gpu_hour=result.break_even_resale_usd_per_gpu_hour),
        dict(placement_fraction=result.break_even_placement_fraction),
    ]:
        assert tenor_tail_outcome(**(TAIL | change)).contribution_usd == pytest.approx(
            0, abs=1e-8
        )
    # Tail-alone break-even price is higher: first-year surplus funds part of the tail.
    assert result.break_even_resale_usd_per_gpu_hour < 5 / (0.9 * 0.95)


def test_zero_placement_keeps_upstream_and_has_no_fees_on_missing_sales():
    rows = schedule(placement=0)
    assert sum(r.supplier_cash_usd for r in rows) == 1296000
    assert all(
        r.selling_cost_usd == 0 and r.contribution_usd == -36000 for r in rows[13:]
    )
    assert rows[-1].cumulative_cash_usd == -639360
    assert (
        tenor_tail_outcome(
            **(TAIL | dict(placement_fraction=0))
        ).break_even_resale_usd_per_gpu_hour
        is None
    )


def test_gap_counted_once_and_lower_price_case():
    gap = schedule(gap=3)
    assert all(r.sold_gpu_hours == 0 for r in gap[13:16])
    assert all(r.sold_gpu_hours == 6480 for r in gap[16:])
    assert gap[-1].cumulative_cash_usd == pytest.approx(200934)
    averaged = tenor_tail_outcome(**(TAIL | dict(placement_fraction=0.9 * 21 / 24)))
    active_hours = tenor_tail_outcome(
        **(TAIL | dict(tail_available_gpu_hours=7200 * 21))
    )
    assert averaged.contribution_usd == pytest.approx(active_hours.contribution_usd)
    assert averaged.contribution_usd == pytest.approx(gap[-1].cumulative_cash_usd)
    assert schedule(price=4)[-1].cumulative_cash_usd == pytest.approx(-48384)


@pytest.mark.parametrize(
    "change", [dict(future_resale_usd_per_gpu_hour=7), dict(placement_fraction=1)]
)
def test_more_price_or_placement_never_reduces_contribution(change):
    assert (
        tenor_tail_outcome(**(TAIL | change)).contribution_usd
        >= tenor_tail_outcome(**TAIL).contribution_usd
    )


@pytest.mark.parametrize("fee", [0, 0.05, 1])
def test_monotonic_grid_including_total_fee(fee):
    for price in [0, 3, 6]:
        values = [
            tenor_tail_outcome(
                **(
                    TAIL
                    | dict(
                        selling_fee_fraction=fee,
                        placement_fraction=f,
                        future_resale_usd_per_gpu_hour=price,
                    )
                )
            ).contribution_usd
            for f in [0, 0.5, 1]
        ]
        assert values == sorted(values)
    if fee == 1:
        result = tenor_tail_outcome(**(TAIL | dict(selling_fee_fraction=fee)))
        assert result.contribution_usd == -1296000
        assert result.required_tail_revenue_usd is None
        assert result.break_even_resale_usd_per_gpu_hour is None
        assert not result.placement_attainable


def test_zero_denominators_and_unattainable_placement_are_explicit():
    zero = tenor_tail_outcome(**(TAIL | dict(future_resale_usd_per_gpu_hour=0)))
    assert zero.break_even_placement_fraction is None
    assert not zero.placement_attainable
    no_hours = tenor_tail_outcome(**(TAIL | dict(tail_available_gpu_hours=0)))
    assert no_hours.break_even_resale_usd_per_gpu_hour is None
    too_low = tenor_tail_outcome(**(TAIL | dict(future_resale_usd_per_gpu_hour=2)))
    assert too_low.break_even_placement_fraction > 1
    assert not too_low.placement_attainable


@pytest.mark.parametrize("cost", [600000, 656640])
def test_costs_already_recovered_do_not_produce_negative_hurdles(cost):
    r = tenor_tail_outcome(
        **(
            TAIL
            | dict(
                upstream_commitment_usd=cost,
                tail_available_gpu_hours=0,
                placement_fraction=0,
                future_resale_usd_per_gpu_hour=0,
            )
        )
    )
    assert r.costs_already_recovered
    assert (
        r.required_tail_revenue_usd
        == r.break_even_resale_usd_per_gpu_hour
        == r.break_even_placement_fraction
        == 0
    )
    assert r.contribution_usd >= 0


@pytest.mark.parametrize("key", list(TAIL))
@pytest.mark.parametrize(
    "bad,error",
    [
        (True, TypeError),
        ("x", TypeError),
        (float("nan"), ValueError),
        (float("inf"), ValueError),
        (-1, ValueError),
    ],
)
def test_invalid_tail_inputs(key, bad, error):
    with pytest.raises(error):
        tenor_tail_outcome(**(TAIL | {key: bad}))


@pytest.mark.parametrize(
    "change",
    [
        dict(placement_fraction=1.1),
        dict(selling_fee_fraction=1.1),
        dict(tail_available_gpu_hours=1e308),
        dict(
            contracted_revenue_usd=1e308,
            upstream_commitment_usd=1e308,
            future_resale_usd_per_gpu_hour=1e308,
        ),
    ],
)
def test_ranges_and_overflow(change):
    with pytest.raises(ValueError):
        tenor_tail_outcome(**(TAIL | change))


@pytest.mark.parametrize(
    "fee,error",
    [
        (True, TypeError),
        (-0.1, ValueError),
        (1.1, ValueError),
        (float("nan"), ValueError),
    ],
)
def test_schedule_rejects_invalid_fee(fee, error):
    with pytest.raises(error):
        schedule(fee=fee)
