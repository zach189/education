"""Contract behavior and independent worked examples, not implementation copies."""

from dataclasses import FrozenInstanceError, asdict

import pytest

from liquid_compute import break_even_utilization_fraction, compute_monthly_economics

BASE = dict(
    gpu_count=10,
    hours_per_month=720,
    rental_usd_per_gpu_hour=2,
    customer_usd_per_gpu_hour=4,
    utilization_fraction=0.75,
)


def scenario(**changes):
    return compute_monthly_economics(**(BASE | changes))


def test_worked_example():
    assert asdict(scenario()) == pytest.approx(
        dict(
            purchased_gpu_hours=7200,
            billed_gpu_hours=5400,
            unused_gpu_hours=1800,
            revenue_usd=21600,
            rental_expense_usd=14400,
            contribution_profit_usd=7200,
            break_even_utilization_fraction=0.5,
            contribution_margin_fraction=1 / 3,
        )
    )


@pytest.mark.parametrize(
    "utilization,profit", [(0, -14400), (0.25, -7200), (0.5, 0), (1, 14400)]
)
def test_utilization_boundaries(utilization, profit):
    result = scenario(utilization_fraction=utilization)
    assert result.contribution_profit_usd == pytest.approx(profit, abs=1e-9)
    assert result.rental_expense_usd == 14400
    assert (
        result.billed_gpu_hours + result.unused_gpu_hours == result.purchased_gpu_hours
    )
    if utilization == 0:
        assert result.revenue_usd == 0
        assert result.contribution_margin_fraction is None
    if utilization == 1:
        assert result.unused_gpu_hours == 0


def test_capacity_scaling():
    baseline, doubled = scenario(), scenario(gpu_count=20)
    for name in (
        "purchased_gpu_hours",
        "billed_gpu_hours",
        "unused_gpu_hours",
        "revenue_usd",
        "rental_expense_usd",
        "contribution_profit_usd",
    ):
        assert getattr(doubled, name) == 2 * getattr(baseline, name)
    assert (
        doubled.break_even_utilization_fraction
        == baseline.break_even_utilization_fraction
    )
    assert doubled.contribution_margin_fraction == baseline.contribution_margin_fraction


def test_unprofitable_even_at_capacity():
    for utilization in (0, 0.5, 1):
        result = scenario(rental_usd_per_gpu_hour=5, utilization_fraction=utilization)
        assert result.break_even_utilization_fraction == 1.25
        assert result.contribution_profit_usd < 0
    assert result.contribution_profit_usd == -7200


def test_equal_prices_and_nonbinary_break_even():
    assert (
        scenario(
            rental_usd_per_gpu_hour=4, utilization_fraction=1
        ).contribution_profit_usd
        == 0
    )
    assert (
        break_even_utilization_fraction(
            rental_usd_per_gpu_hour=4, customer_usd_per_gpu_hour=4
        )
        == 1
    )
    threshold = break_even_utilization_fraction(
        rental_usd_per_gpu_hour=2, customer_usd_per_gpu_hour=3
    )
    assert scenario(
        customer_usd_per_gpu_hour=3, utilization_fraction=threshold
    ).contribution_profit_usd == pytest.approx(0, abs=1e-9)


@pytest.mark.parametrize("name", list(BASE))
@pytest.mark.parametrize("value", [True, "2", None, 2 + 0j])
def test_wrong_types(name, value):
    with pytest.raises(TypeError, match=name):
        scenario(**{name: value})


@pytest.mark.parametrize("value", [1.5, float("nan"), float("inf")])
def test_count_must_be_integer(value):
    with pytest.raises(TypeError, match="gpu_count"):
        scenario(gpu_count=value)


@pytest.mark.parametrize(
    "name",
    [
        "hours_per_month",
        "rental_usd_per_gpu_hour",
        "customer_usd_per_gpu_hour",
        "utilization_fraction",
    ],
)
@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_inputs(name, value):
    with pytest.raises(ValueError, match=name):
        scenario(**{name: value})


@pytest.mark.parametrize(
    "name",
    [
        "gpu_count",
        "hours_per_month",
        "rental_usd_per_gpu_hour",
        "customer_usd_per_gpu_hour",
    ],
)
@pytest.mark.parametrize("value", [0, -1])
def test_positive_domain(name, value):
    with pytest.raises(ValueError, match=name):
        scenario(**{name: value})


@pytest.mark.parametrize("value", [-0.01, 1.01])
def test_utilization_range(value):
    with pytest.raises(ValueError, match="utilization_fraction"):
        scenario(utilization_fraction=value)


@pytest.mark.parametrize(
    "name", ["rental_usd_per_gpu_hour", "customer_usd_per_gpu_hour"]
)
@pytest.mark.parametrize(
    "value,error",
    [
        (True, TypeError),
        ("2", TypeError),
        (0, ValueError),
        (-1, ValueError),
        (float("nan"), ValueError),
        (float("inf"), ValueError),
    ],
)
def test_break_even_validates_both_prices(name, value, error):
    inputs = dict(rental_usd_per_gpu_hour=2, customer_usd_per_gpu_hour=4)
    inputs[name] = value
    with pytest.raises(error, match=name):
        break_even_utilization_fraction(**inputs)


@pytest.mark.parametrize(
    "changes",
    [
        dict(gpu_count=10**400),
        dict(hours_per_month=10**400),
        dict(hours_per_month=1e308),
        dict(customer_usd_per_gpu_hour=1e308),
        dict(rental_usd_per_gpu_hour=1e308),
        dict(utilization_fraction=1e-310, rental_usd_per_gpu_hour=1e300),
    ],
)
def test_overflow(changes):
    with pytest.raises(ValueError, match="finite"):
        scenario(**changes)


def test_break_even_overflow():
    with pytest.raises(ValueError, match="finite"):
        break_even_utilization_fraction(
            rental_usd_per_gpu_hour=1e308, customer_usd_per_gpu_hour=1e-308
        )


def test_result_is_immutable():
    with pytest.raises(FrozenInstanceError):
        scenario().revenue_usd = 0
