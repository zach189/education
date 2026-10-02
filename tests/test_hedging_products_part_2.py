"""Period cash protection, signed settlements and independent worked examples."""

import pytest

from liquid_compute.financing import debt_service_coverage
from liquid_compute.hedge_converter import (
    financing_hedge_requirement,
    revenue_floor_hedge_terms,
)
from liquid_compute.hedging import spread_swap_settlement_usd
from liquid_compute.options import (
    european_option_payoff_usd,
    tenor_spread_put_payoff_usd,
)
from liquid_compute.power import power_swap_receipt_usd


def test_quarter_floor_matches_required_revenue() -> None:
    for target, strike in zip(
        [2_000_000, 1_800_000, 1_500_000, 1_200_000], [5 / 3, 1.5, 1.25, 1]
    ):
        terms = revenue_floor_hedge_terms(
            required_revenue_usd=target, expected_gpu_hours=1_200_000
        )
        assert terms.strike_usd_per_gpu_hour == pytest.approx(strike)
        for index in [0, 0.8, 1.4, 2.5]:
            payoff = european_option_payoff_usd(
                kind="put",
                settlement_price_usd_per_gpu_hour=index,
                strike_usd_per_gpu_hour=terms.strike_usd_per_gpu_hour,
                covered_gpu_hours=terms.notional_gpu_hours,
            )
            assert index * 1_200_000 + payoff == pytest.approx(
                max(target, index * 1_200_000)
            )


@pytest.mark.parametrize("index", [0, 1, 1.75, 2.5, 3.5, 4.5, 100])
def test_collar_and_embedded_invoice_are_same_cash_rule(index: float) -> None:
    hours, basis, floor, cap = 73_000, 0.2, 3.75, 5.5
    put = european_option_payoff_usd(
        kind="put",
        settlement_price_usd_per_gpu_hour=index,
        strike_usd_per_gpu_hour=floor - basis,
        covered_gpu_hours=hours,
    )
    call = european_option_payoff_usd(
        kind="call",
        settlement_price_usd_per_gpu_hour=index,
        strike_usd_per_gpu_hour=cap - basis,
        covered_gpu_hours=hours,
    )
    assert (index + basis) * hours + put - call == pytest.approx(
        min(max(index + basis, floor), cap) * hours
    )


@pytest.mark.parametrize(
    "sale,purchase,fixed,expected",
    [
        (5.3, 5, 0.25, -35_040),
        (4.75, 4.7, 0.25, 140_160),
        (4.5, 4.7, 0.25, 315_360),
        (4.5, 4.7, -0.3, -70_080),
    ],
)
def test_spread_receipt_and_physical_margin(
    sale: float, purchase: float, fixed: float, expected: float
) -> None:
    receipt = spread_swap_settlement_usd(
        sale_index_usd_per_gpu_hour=sale,
        purchase_index_usd_per_gpu_hour=purchase,
        fixed_spread_usd_per_gpu_hour=fixed,
        covered_gpu_hours=700_800,
    )
    assert receipt == pytest.approx(expected)
    assert (sale - purchase - 0.1) * 700_800 + receipt == pytest.approx(
        (fixed - 0.1) * 700_800
    )


@pytest.mark.parametrize(
    "market,expected", [(100, 280_000), (40, -140_000), (-20, -560_000)]
)
def test_power_swap_fixes_matched_bill(market: float, expected: float) -> None:
    receipt = power_swap_receipt_usd(
        energy_mwh=7_000, market_usd_per_mwh=market, fixed_usd_per_mwh=60
    )
    assert receipt == expected
    assert 7_000 * market - receipt == 420_000


def test_financing_requirement_and_quantity_failure() -> None:
    terms = financing_hedge_requirement(
        target_dscr=1.25,
        debt_service_usd=20_000_000,
        operating_cost_usd=10_000_000,
        contracted_receipts_usd=12_000_000,
        merchant_gpu_hours=8_000_000,
    )
    assert terms.required_merchant_revenue_usd == 23_000_000
    assert terms.strike_usd_per_gpu_hour == 2.875
    assert terms.notional_gpu_hours == 8_000_000
    for price, hours, expected in [
        (1.5, 8_000_000, 1.25),
        (4, 8_000_000, 1.7),
        (4, 4_000_000, 0.9),
    ]:
        put = european_option_payoff_usd(
            kind="put",
            settlement_price_usd_per_gpu_hour=price,
            strike_usd_per_gpu_hour=2.875,
            covered_gpu_hours=terms.notional_gpu_hours,
        )
        cfads = 12_000_000 + price * hours + put - 10_000_000
        assert debt_service_coverage(
            cfads_usd=cfads, debt_service_usd=20_000_000
        ) == pytest.approx(expected)


@pytest.mark.parametrize(
    "receipts,hours,strike", [(40, 0, 0), (40, 8, 0), (12, 0, None)]
)
def test_financing_zero_gap_and_no_price_solution(
    receipts: float, hours: float, strike: float | None
) -> None:
    terms = financing_hedge_requirement(
        target_dscr=1.25,
        debt_service_usd=20,
        operating_cost_usd=10,
        contracted_receipts_usd=receipts,
        merchant_gpu_hours=hours,
    )
    assert terms.strike_usd_per_gpu_hour == strike


CASES = [
    (
        tenor_spread_put_payoff_usd,
        dict(
            short_tenor_index_usd_per_gpu_hour=4.8,
            long_tenor_index_usd_per_gpu_hour=4.75,
            strike_spread_usd_per_gpu_hour=0.2,
            covered_gpu_hours=1_000_000.0,
        ),
    ),
    (
        revenue_floor_hedge_terms,
        dict(required_revenue_usd=20.0, expected_gpu_hours=10.0),
    ),
    (
        financing_hedge_requirement,
        dict(
            target_dscr=1.25,
            debt_service_usd=20.0,
            operating_cost_usd=10.0,
            contracted_receipts_usd=12.0,
            merchant_gpu_hours=8.0,
        ),
    ),
    (
        spread_swap_settlement_usd,
        dict(
            sale_index_usd_per_gpu_hour=5.3,
            purchase_index_usd_per_gpu_hour=5.0,
            fixed_spread_usd_per_gpu_hour=0.25,
            covered_gpu_hours=100.0,
        ),
    ),
    (
        power_swap_receipt_usd,
        dict(energy_mwh=7_000.0, market_usd_per_mwh=100.0, fixed_usd_per_mwh=60.0),
    ),
]


@pytest.mark.parametrize("function,inputs", CASES)
@pytest.mark.parametrize(
    "bad,error",
    [
        (True, TypeError),
        ("1", TypeError),
        (None, TypeError),
        (float("nan"), ValueError),
        (float("inf"), ValueError),
        (10**1000, ValueError),
    ],
)
def test_new_calculators_validate_every_input(function, inputs, bad, error) -> None:
    for name in inputs:
        with pytest.raises(error):
            function(**(inputs | {name: bad}))


@pytest.mark.parametrize("function,inputs", CASES)
def test_new_calculators_reject_invalid_ranges(function, inputs) -> None:
    signed = {
        "fixed_spread_usd_per_gpu_hour",
        "strike_spread_usd_per_gpu_hour",
        "market_usd_per_mwh",
        "fixed_usd_per_mwh",
    }
    for name in inputs.keys() - signed:
        with pytest.raises(ValueError):
            function(**(inputs | {name: -1}))


def test_zero_quantity_and_overflow() -> None:
    with pytest.raises(ValueError):
        revenue_floor_hedge_terms(required_revenue_usd=1, expected_gpu_hours=0)
    assert (
        revenue_floor_hedge_terms(
            required_revenue_usd=0, expected_gpu_hours=1
        ).strike_usd_per_gpu_hour
        == 0
    )
    assert (
        power_swap_receipt_usd(
            energy_mwh=0, market_usd_per_mwh=-10, fixed_usd_per_mwh=20
        )
        == 0
    )
    with pytest.raises(ValueError):
        revenue_floor_hedge_terms(required_revenue_usd=1e308, expected_gpu_hours=1e-308)
    with pytest.raises(ValueError):
        power_swap_receipt_usd(
            energy_mwh=1e308, market_usd_per_mwh=100, fixed_usd_per_mwh=0
        )
    with pytest.raises(ValueError):
        spread_swap_settlement_usd(
            sale_index_usd_per_gpu_hour=1e308,
            purchase_index_usd_per_gpu_hour=0,
            fixed_spread_usd_per_gpu_hour=-1e308,
            covered_gpu_hours=1,
        )
    with pytest.raises(ValueError):
        financing_hedge_requirement(
            target_dscr=2,
            debt_service_usd=1e308,
            operating_cost_usd=0,
            contracted_receipts_usd=0,
            merchant_gpu_hours=1,
        )
    with pytest.raises(ValueError):
        financing_hedge_requirement(
            target_dscr=0.9,
            debt_service_usd=1,
            operating_cost_usd=0,
            contracted_receipts_usd=0,
            merchant_gpu_hours=1,
        )


def test_indexed_offtake_separate_options_and_premium_budgets() -> None:
    """Independent supplied H100 bills and both sides' financial receipts."""
    hours = 511_000
    for index, invoice, call_cash, put_cash in [
        (3.5, 1_865_150, 332_150, 0),
        (1.2, 689_850, 0, 204_400),
        (2.3, 1_251_950, 0, 0),
    ]:
        call = european_option_payoff_usd(
            kind="call",
            settlement_price_usd_per_gpu_hour=index,
            strike_usd_per_gpu_hour=2.85,
            covered_gpu_hours=hours,
        )
        put = european_option_payoff_usd(
            kind="put",
            settlement_price_usd_per_gpu_hour=index,
            strike_usd_per_gpu_hour=1.60,
            covered_gpu_hours=hours,
        )
        assert call == pytest.approx(call_cash)
        assert put == pytest.approx(put_cash)
        assert (index + 0.15) * hours == pytest.approx(invoice)
        assert (invoice - call + 0.10 * hours) / hours <= 3.10 + 1e-12
        assert (invoice + put - 0.08 * hours) / hours >= 1.67 - 1e-12
    assert hours * 24 == 12_264_000
    assert hours * 24 * 0.10 == 1_226_400
    assert hours * 24 * 0.08 == 981_120
    # Extra usage is unhedged despite the same physical contract.
    assert (730_000 * 3.65 - 332_150) / 730_000 == pytest.approx(3.195)
    assert (730_000 * 3.65 - 332_150 + 51_100) / 730_000 == pytest.approx(3.265)


def test_monthly_offtake_strip_is_not_a_long_average_option() -> None:
    """High and low months can cancel before an average-price option pays."""
    indices = [1.0, 4.0] * 12
    monthly_payments = [
        european_option_payoff_usd(
            kind="call",
            settlement_price_usd_per_gpu_hour=index,
            strike_usd_per_gpu_hour=2.85,
            covered_gpu_hours=511_000,
        )
        for index in indices
    ]
    assert sum(monthly_payments) == pytest.approx(7_051_800)
    one_average_payment = european_option_payoff_usd(
        kind="call",
        settlement_price_usd_per_gpu_hour=sum(indices) / 24,
        strike_usd_per_gpu_hour=2.85,
        covered_gpu_hours=12_264_000,
    )
    assert one_average_payment == 0


@pytest.mark.parametrize(
    "short,long,strike,expected",
    [
        (4.8, 4.75, 0.2, 150_000),
        (5.75, 5.1, 0.2, 0),
        (4.5, 4.75, 0.2, 450_000),
        (4.5, 4.75, -0.1, 150_000),
        (5.3, 5.0, 0.2, 0),
    ],
)
def test_spread_put_preserves_upside_and_accepts_negative_spread(
    short: float, long: float, strike: float, expected: float
) -> None:
    receipt = tenor_spread_put_payoff_usd(
        short_tenor_index_usd_per_gpu_hour=short,
        long_tenor_index_usd_per_gpu_hour=long,
        strike_spread_usd_per_gpu_hour=strike,
        covered_gpu_hours=1_000_000,
    )
    assert receipt == pytest.approx(expected)
    assert (short - long) * 1_000_000 + receipt == pytest.approx(
        max(short - long, strike) * 1_000_000
    )


def test_spread_put_zero_and_overflow() -> None:
    inputs = dict(
        short_tenor_index_usd_per_gpu_hour=4.8,
        long_tenor_index_usd_per_gpu_hour=4.75,
        strike_spread_usd_per_gpu_hour=0.2,
        covered_gpu_hours=0,
    )
    assert tenor_spread_put_payoff_usd(**inputs) == 0
    with pytest.raises(ValueError):
        tenor_spread_put_payoff_usd(
            short_tenor_index_usd_per_gpu_hour=0,
            long_tenor_index_usd_per_gpu_hour=1e308,
            strike_spread_usd_per_gpu_hour=1e308,
            covered_gpu_hours=1,
        )
    with pytest.raises(ValueError):
        tenor_spread_put_payoff_usd(
            short_tenor_index_usd_per_gpu_hour=0,
            long_tenor_index_usd_per_gpu_hour=10,
            strike_spread_usd_per_gpu_hour=0,
            covered_gpu_hours=1e308,
        )


def test_layered_rates_reconcile_with_monthly_cash_and_idle_cost() -> None:
    from liquid_compute.hedging import forward_settlements_usd

    quantities, rates = [126_144, 126_144, 100_915.2], [4.9, 5.1, 4.75]
    assert sum(quantities) == pytest.approx(353_203.2)
    weighted_rate = sum(q * r for q, r in zip(quantities, rates)) / sum(quantities)
    assert weighted_rate == pytest.approx(34.5 / 7)
    for index, blended in [(4, 4.65), (6, 5.25)]:
        receipt = sum(
            sum(
                row.amount_usd
                for row in forward_settlements_usd(
                    benchmark_usd_per_gpu_hour=[index] * 12,
                    strike_usd_per_gpu_hour=rate,
                    hedge_gpu_hours=[hours / 12] * 12,
                    settlement_months=list(range(13, 25)),
                    side="seller",
                )
            )
            for hours, rate in zip(quantities, rates)
        )
        cash = 504_576 * index + receipt
        assert cash / 504_576 == pytest.approx(blended)
        if index == 4:
            assert cash - 560_640 * 4.25 == pytest.approx(-36_441.6)
