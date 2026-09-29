import pytest

from liquid_compute.revenue_sharing import (
    delivered_hour_revenue_share,
    minimum_revenue_share_usd,
)


@pytest.mark.parametrize(
    "price,supplier,counterparty",
    [(3, 28800, -7200), (5, 32400, 3600), (7, 39600, 10800)],
)
def test_reference_allocation_and_conservation(price, supplier, counterparty):
    result = delivered_hour_revenue_share(
        delivered_gpu_hours=7200,
        reference_usd_per_gpu_hour=price,
        guarantee_usd_per_gpu_hour=4,
        supplier_upside_fraction=0.5,
    )
    assert result.supplier_receipts_usd == supplier
    assert result.counterparty_net_usd == counterparty
    assert supplier + counterparty == result.reference_revenue_usd


@pytest.mark.parametrize("revenue", [0, 20000, 28800, 50000])
def test_fraction_endpoints_and_intermediate_conservation(revenue):
    for alpha in (0, 0.125, 0.5, 1):
        result = minimum_revenue_share_usd(
            reference_revenue_usd=revenue,
            guaranteed_revenue_usd=28800,
            supplier_upside_fraction=alpha,
        )
        assert result.supplier_receipts_usd + result.counterparty_net_usd == revenue
        if alpha == 0:
            assert result.supplier_receipts_usd == 28800
        if alpha == 1:
            assert result.supplier_receipts_usd == max(revenue, 28800)


def test_per_hour_and_fixed_total_guarantee_remain_distinct():
    for hours, per_hour, fixed in ((3600, 16200, 28800), (0, 0, 28800)):
        delivered = delivered_hour_revenue_share(
            delivered_gpu_hours=hours,
            reference_usd_per_gpu_hour=5,
            guarantee_usd_per_gpu_hour=4,
            supplier_upside_fraction=0.5,
        )
        total = minimum_revenue_share_usd(
            reference_revenue_usd=hours * 5,
            guaranteed_revenue_usd=28800,
            supplier_upside_fraction=0.5,
        )
        assert delivered.supplier_receipts_usd == per_hour
        assert total.supplier_receipts_usd == fixed
        assert total.counterparty_net_usd == hours * 5 - fixed


@pytest.mark.parametrize(
    "field",
    ["reference_revenue_usd", "guaranteed_revenue_usd", "supplier_upside_fraction"],
)
@pytest.mark.parametrize(
    "value,error",
    [(True, TypeError), ("1", TypeError), (-1, ValueError), (float("inf"), ValueError)],
)
def test_invalid_core_inputs(field, value, error):
    args = dict(
        reference_revenue_usd=36000,
        guaranteed_revenue_usd=28800,
        supplier_upside_fraction=0.5,
    )
    with pytest.raises(error):
        minimum_revenue_share_usd(**(args | {field: value}))


def test_fraction_upper_bound_and_conversion_overflow():
    with pytest.raises(ValueError):
        minimum_revenue_share_usd(
            reference_revenue_usd=1,
            guaranteed_revenue_usd=1,
            supplier_upside_fraction=1.01,
        )
    with pytest.raises(ValueError):
        delivered_hour_revenue_share(
            delivered_gpu_hours=1e308,
            reference_usd_per_gpu_hour=5,
            guarantee_usd_per_gpu_hour=4,
            supplier_upside_fraction=0.5,
        )
