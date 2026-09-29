from dataclasses import replace

import pytest

from liquid_compute.hedging import (
    BenchmarkMatch,
    Settlement,
    basis_exposure_summary,
    compare_benchmark_attributes,
    forward_settlements_usd,
)


def basis(
    actual=7.5,
    benchmark=7,
    quantity=7200,
    hedge=7200,
    physical_month=12,
    settlement_month=12,
):
    settlements = forward_settlements_usd(
        benchmark_usd_per_gpu_hour=[benchmark],
        strike_usd_per_gpu_hour=5,
        hedge_gpu_hours=[hedge],
        settlement_months=[settlement_month],
        side="buyer",
    )
    return basis_exposure_summary(
        actual_usd_per_gpu_hour=[actual],
        physical_gpu_hours=[quantity],
        benchmark_usd_per_gpu_hour=[benchmark],
        hedge_gpu_hours=[hedge],
        strike_usd_per_gpu_hour=5,
        physical_payment_months=[physical_month],
        settlements=settlements,
    )


def test_basis_reference_and_exact_lock():
    result = basis()
    assert result.unhedged_cost_usd == 54000 and result.hedge_receipts_usd == 14400
    assert result.net_cost_usd == 39600
    assert (
        result.rows[0].basis_cost_usd == 3600
        and result.rows[0].strike_component_usd == 36000
    )
    assert basis(actual=7).net_cost_usd == 36000
    assert basis(actual=6.5).rows[0].basis_cost_usd == -3600


@pytest.mark.parametrize("hedge", [0, 5400, 7200, 9000, 100000])
def test_decomposition_and_signed_overhedge(hedge):
    result = basis(hedge=hedge)
    row = result.rows[0]
    assert (
        row.net_cost_usd
        == row.unmatched_benchmark_cost_usd
        + row.basis_cost_usd
        + row.strike_component_usd
    )
    assert row.unmatched_gpu_hours == 7200 - hedge
    assert result.cash_flows[-1].cumulative_cash_usd == -result.net_cost_usd
    if hedge == 100000:
        assert row.net_cost_usd < 0  # Do not floor a speculative excess receipt.


def test_time_basis_and_payment_dates_are_distinct():
    result = basis(actual=8, benchmark=7, physical_month=12, settlement_month=11)
    assert result.net_cost_usd == 43200
    assert (
        result.rows[0].physical_payment_month == 12
        and result.rows[0].settlement_month == 11
    )
    assert result.cash_flows[11].hedge_cash_usd == 14400
    assert result.cash_flows[12].physical_cash_usd == -57600


def test_metadata_is_checklist_not_matching_score():
    physical = BenchmarkMatch(
        "USD/GPU-hour", "Provider A", "Region X", "Month 12", "GPU family X", "24/7"
    )
    assert compare_benchmark_attributes(physical, physical) == ()
    other = replace(physical, provider="Provider B", delivery_period="Month 11")
    assert compare_benchmark_attributes(physical, other) == (
        "provider",
        "delivery_period",
    )
    with pytest.raises(ValueError):
        compare_benchmark_attributes(physical, replace(physical, unit="USD/GPU-day"))
    with pytest.raises(TypeError):
        compare_benchmark_attributes(physical, replace(physical, region=True))


def test_mismatched_settlement_and_invalid_inputs():
    args = dict(
        actual_usd_per_gpu_hour=[7.5],
        physical_gpu_hours=[7200],
        benchmark_usd_per_gpu_hour=[7],
        hedge_gpu_hours=[7200],
        strike_usd_per_gpu_hour=5,
        physical_payment_months=[12],
        settlements=[Settlement(12, 14400)],
    )
    with pytest.raises(ValueError):
        basis_exposure_summary(**(args | dict(settlements=[Settlement(12, -14400)])))
    with pytest.raises(ValueError):
        basis_exposure_summary(**(args | dict(actual_usd_per_gpu_hour=[])))
    with pytest.raises(TypeError):
        basis_exposure_summary(**(args | dict(physical_gpu_hours=[True])))
    with pytest.raises(ValueError):
        basis_exposure_summary(**(args | dict(actual_usd_per_gpu_hour=[float("inf")])))
