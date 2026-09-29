from math import log, sqrt

import pytest

from liquid_compute.risk_statistics import (
    MonthlyPrice,
    monthly_log_returns,
    sample_volatility,
)


def test_reference_log_changes_and_independent_sample_variance():
    prices = [10, 11, 10, 11, 10, 11, 10, 20]
    rows = monthly_log_returns(
        [MonthlyPrice(2025 * 12 + i, p) for i, p in enumerate(prices)]
    )
    expected = [log(1.1), -log(1.1)] * 3 + [log(2)]
    assert [r.log_change for r in rows] == pytest.approx(expected)
    mean = sum(expected) / 7
    square_sum = sum((value - mean) ** 2 for value in expected)
    result = sample_volatility([r.log_change for r in rows], periods_per_year=12)
    assert result.count == 7 and result.omitted_count == 0
    assert result.sample_sd == pytest.approx(sqrt(square_sum / 6))
    assert result.sample_sd != pytest.approx(sqrt(square_sum / 7))
    assert result.annualized_sd == pytest.approx(sqrt(12) * sqrt(square_sum / 6))
    assert rows[0].start_month == 2025 * 12
    assert rows[-1].end_month == 2025 * 12 + 7


def test_constant_and_insufficient_are_distinct():
    assert sample_volatility([0, 0, 0]).sample_sd == 0
    for values, count, missing in (([], 0, 0), ([None], 0, 1), ([0, None], 1, 1)):
        result = sample_volatility(values, periods_per_year=12)
        assert result.count == count and result.omitted_count == missing
        assert result.sample_sd is result.annualized_sd is None
        assert result.unavailable_reason is not None


def test_missing_prices_and_absent_months_are_not_bridged():
    explicit = monthly_log_returns(
        [
            MonthlyPrice(0, 10),
            MonthlyPrice(1, None),
            MonthlyPrice(2, 20),
            MonthlyPrice(3, 22),
        ]
    )
    absent = monthly_log_returns(
        [MonthlyPrice(0, 10), MonthlyPrice(2, 20), MonthlyPrice(3, 22)]
    )
    assert explicit == absent
    assert [r.log_change for r in absent[:2]] == [None, None]
    assert absent[-1].log_change == pytest.approx(log(1.1))
    estimate = sample_volatility([r.log_change for r in absent])
    assert estimate.count == 1 and estimate.omitted_count == 2
    assert estimate.sample_sd is None


def test_extreme_positive_prices_do_not_overflow_ratio():
    result = monthly_log_returns([MonthlyPrice(0, 1e-300), MonthlyPrice(1, 1e300)])
    assert result[0].log_change == pytest.approx(600 * log(10))


@pytest.mark.parametrize(
    "observations,error",
    [
        ([MonthlyPrice(1, 10), MonthlyPrice(1, 11)], ValueError),
        ([MonthlyPrice(2, 10), MonthlyPrice(1, 11)], ValueError),
        ([MonthlyPrice(True, 10)], TypeError),
        ([MonthlyPrice(-1, 10)], ValueError),
        ([MonthlyPrice(0, 0)], ValueError),
        ([MonthlyPrice(0, -1)], ValueError),
        ([MonthlyPrice(0, True)], TypeError),
        ([MonthlyPrice(0, float("nan"))], ValueError),
        ([(0, 10)], TypeError),
    ],
)
def test_invalid_observations(observations, error):
    with pytest.raises(error):
        monthly_log_returns(observations)


@pytest.mark.parametrize(
    "values,frequency,error",
    [
        ([True, 0], None, TypeError),
        ([float("inf"), 0], None, ValueError),
        ([0, 1], 0, ValueError),
        ([0, 1], True, TypeError),
        ([1e308, -1e308], 12, ValueError),
    ],
)
def test_invalid_sample_inputs(values, frequency, error):
    with pytest.raises(error):
        sample_volatility(values, periods_per_year=frequency)
