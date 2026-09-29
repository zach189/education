import pytest

from liquid_compute.workload_costs import decompose_workload_spend, useful_output_costs


def test_single_workload_efficiency_and_volume_reference():
    base = useful_output_costs(
        task_counts={"task": 10000},
        gpu_hours_per_task={"task": 0.01},
        usd_per_gpu_hour=4,
    )
    changed = useful_output_costs(
        task_counts={"task": 15000},
        gpu_hours_per_task={"task": 0.008},
        usd_per_gpu_hour=4,
    )
    assert (base.consumed_gpu_hours, base.total_cost_usd, base.usd_per_task) == (
        100,
        400,
        0.04,
    )
    assert (
        changed.consumed_gpu_hours,
        changed.total_cost_usd,
        changed.usd_per_task,
    ) == (120, 480, 0.032)


def test_weighted_mix_not_unweighted_category_average_and_zero_tasks():
    intensities = {"light": 0.005, "heavy": 0.02}
    for counts, cost, unit in (
        ({"light": 8000, "heavy": 2000}, 320, 0.032),
        ({"light": 5000, "heavy": 5000}, 500, 0.05),
        ({"light": 0, "heavy": 0}, 0, None),
    ):
        result = useful_output_costs(
            task_counts=counts, gpu_hours_per_task=intensities, usd_per_gpu_hour=4
        )
        assert result.total_cost_usd == cost
        assert result.usd_per_task == unit


def test_ordered_decomposition_all_four_effects_and_input_independence():
    counts = {"light": 8000, "heavy": 2000}
    result = decompose_workload_spend(
        before_task_counts=counts,
        after_task_counts={"light": 7500, "heavy": 7500},
        before_gpu_hours_per_task={"light": 0.005, "heavy": 0.02},
        after_gpu_hours_per_task={"light": 0.004, "heavy": 0.016},
        before_usd_per_gpu_hour=4,
        after_usd_per_gpu_hour=5,
    )
    assert counts == {"light": 8000, "heavy": 2000}
    assert (
        result.volume_usd,
        result.mix_usd,
        result.intensity_usd,
        result.price_usd,
    ) == pytest.approx((160, 270, -150, 150))
    assert result.total_change_usd == 430
    assert result.reconciliation_residual_usd == pytest.approx(0)


@pytest.mark.parametrize("before,after", [(0, 0), (0, 100), (100, 0), (100, 100)])
def test_zero_volume_convention_and_unchanged_inputs(before, after):
    result = decompose_workload_spend(
        before_task_counts={"task": before},
        after_task_counts={"task": after},
        before_gpu_hours_per_task={"task": 0.01},
        after_gpu_hours_per_task={"task": 0.01},
        before_usd_per_gpu_hour=4,
        after_usd_per_gpu_hour=4,
    )
    assert result.volume_usd == pytest.approx((after - before) * 0.04)
    assert result.mix_usd == result.intensity_usd == result.price_usd == 0
    assert result.reconciliation_residual_usd == pytest.approx(0)


@pytest.mark.parametrize(
    "counts,intensities,rate,error",
    [
        ({}, {}, 4, ValueError),
        ({"a": 1}, {"b": 0.1}, 4, ValueError),
        ({"a": 1, "A": 1}, {"a": 0.1, "A": 0.1}, 4, ValueError),
        ({" a": 1}, {" a": 0.1}, 4, ValueError),
        ({"a": True}, {"a": 0.1}, 4, TypeError),
        ({"a": -1}, {"a": 0.1}, 4, ValueError),
        ({"a": 1}, {"a": float("nan")}, 4, ValueError),
        ({"a": 1e308}, {"a": 100}, 4, ValueError),
        ({"a": 1}, {"a": 0.1}, -1, ValueError),
    ],
)
def test_invalid_units_categories_and_values(counts, intensities, rate, error):
    with pytest.raises(error):
        useful_output_costs(
            task_counts=counts, gpu_hours_per_task=intensities, usd_per_gpu_hour=rate
        )


def test_decomposition_requires_stable_categories():
    with pytest.raises(ValueError):
        decompose_workload_spend(
            before_task_counts={"a": 1},
            after_task_counts={"b": 1},
            before_gpu_hours_per_task={"a": 0.1},
            after_gpu_hours_per_task={"b": 0.1},
            before_usd_per_gpu_hour=4,
            after_usd_per_gpu_hour=4,
        )
