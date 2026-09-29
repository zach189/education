"""Consumed compute per quality-qualified task, with ordered spend attribution."""

from collections.abc import Mapping
from dataclasses import dataclass

from .economics import _finite_number
from .financing import _nonnegative, _total


@dataclass(frozen=True)
class UsefulOutputCosts:
    """Counts are useful tasks under one declared quality criterion, not tokens."""

    useful_tasks: float
    consumed_gpu_hours: float
    total_cost_usd: float
    usd_per_task: float | None


@dataclass(frozen=True)
class WorkloadSpendDecomposition:
    """USD effects in fixed volume -> mix -> intensity -> price order."""

    before: UsefulOutputCosts
    after: UsefulOutputCosts
    volume_usd: float
    mix_usd: float
    intensity_usd: float
    price_usd: float
    total_change_usd: float
    reconciliation_residual_usd: float


def _workloads(
    task_counts: Mapping[str, float],
    gpu_hours_per_task: Mapping[str, float],
) -> tuple[dict[str, float], dict[str, float]]:
    if not isinstance(task_counts, Mapping) or not isinstance(
        gpu_hours_per_task, Mapping
    ):
        raise TypeError("counts and intensities must be mappings")
    if not task_counts or set(task_counts) != set(gpu_hours_per_task):
        raise ValueError("nonempty matching workload categories required")
    names = tuple(task_counts)
    if any(not isinstance(name, str) for name in names):
        raise TypeError("workload category names must be strings")
    if any(not name or name != name.strip() for name in names):
        raise ValueError(
            "category names must be nonempty with no surrounding whitespace"
        )
    if len({name.casefold() for name in names}) != len(names):
        raise ValueError("overlapping category names after case normalization")
    return (
        {name: _nonnegative("task count", task_counts[name]) for name in names},
        {
            name: _nonnegative("GPU-hours per task", gpu_hours_per_task[name])
            for name in names
        },
    )


def useful_output_costs(
    *,
    task_counts: Mapping[str, float],
    gpu_hours_per_task: Mapping[str, float],
    usd_per_gpu_hour: float,
) -> UsefulOutputCosts:
    """Sum count*intensity, multiply consumed GPU-hours by one common USD rate.

    Nonempty matching disjoint categories; finite nonnegative counts, intensities
    and rate. Fractional counts permitted for modeled workload allocations. Each
    useful task must appear in exactly one category; semantic overlap cannot be
    inferred from labels. Case-equivalent/blank/whitespace labels are rejected.
    Zero total tasks yields zero spend and None unit cost. No reserved capacity,
    retries, power or quality comparison is inferred. Wrong types/bools raise
    TypeError; invalid dimensions/ranges/nonfinite/overflow raise ValueError.
    """
    counts, intensities = _workloads(task_counts, gpu_hours_per_task)
    rate = _nonnegative("usd_per_gpu_hour", usd_per_gpu_hour)
    tasks = _total(list(counts.values()))
    hours = _total(
        [
            _finite_number("workload GPU-hours", counts[name] * intensities[name])
            for name in counts
        ]
    )
    cost = _finite_number("total spend", hours * rate)
    unit = None if tasks == 0 else _finite_number("USD per task", cost / tasks)
    return UsefulOutputCosts(tasks, hours, cost, unit)


def decompose_workload_spend(
    *,
    before_task_counts: Mapping[str, float],
    after_task_counts: Mapping[str, float],
    before_gpu_hours_per_task: Mapping[str, float],
    after_gpu_hours_per_task: Mapping[str, float],
    before_usd_per_gpu_hour: float,
    after_usd_per_gpu_hour: float,
) -> WorkloadSpendDecomposition:
    """Sequential exact replacement: total volume, category mix, intensity, price.

    Stable category identities across both mappings, including zero-count rows.
    Reuse useful_output_costs validation. If baseline volume is zero, use target
    mix as the baseline mix so entry spend is attributed to volume; if both zero,
    all effects zero. Mix is undefined at zero volume, so that attribution is an
    explicit convention. Attribution changes with order, total change does not.
    Residual reports floating-point reconciliation, normally near zero, not a new
    economic effect. Inputs are not mutated; no forecast or causal claim.
    """
    before_counts, before_intensities = _workloads(
        before_task_counts, before_gpu_hours_per_task
    )
    after_counts, after_intensities = _workloads(
        after_task_counts, after_gpu_hours_per_task
    )
    if set(before_counts) != set(after_counts):
        raise ValueError("stable workload categories required across scenarios")
    before = useful_output_costs(
        task_counts=before_counts,
        gpu_hours_per_task=before_intensities,
        usd_per_gpu_hour=before_usd_per_gpu_hour,
    )
    after = useful_output_costs(
        task_counts=after_counts,
        gpu_hours_per_task=after_intensities,
        usd_per_gpu_hour=after_usd_per_gpu_hour,
    )
    volume_counts = (
        {
            name: after.useful_tasks * (count / before.useful_tasks)
            for name, count in before_counts.items()
        }
        if before.useful_tasks
        else after_counts.copy()
    )
    volume_stage = useful_output_costs(
        task_counts=volume_counts,
        gpu_hours_per_task=before_intensities,
        usd_per_gpu_hour=before_usd_per_gpu_hour,
    )
    mix_stage = useful_output_costs(
        task_counts=after_counts,
        gpu_hours_per_task=before_intensities,
        usd_per_gpu_hour=before_usd_per_gpu_hour,
    )
    intensity_stage = useful_output_costs(
        task_counts=after_counts,
        gpu_hours_per_task=after_intensities,
        usd_per_gpu_hour=before_usd_per_gpu_hour,
    )
    volume = _finite_number(
        "volume effect", volume_stage.total_cost_usd - before.total_cost_usd
    )
    mix = _finite_number(
        "mix effect", mix_stage.total_cost_usd - volume_stage.total_cost_usd
    )
    intensity = _finite_number(
        "intensity effect", intensity_stage.total_cost_usd - mix_stage.total_cost_usd
    )
    price = _finite_number(
        "price effect", after.total_cost_usd - intensity_stage.total_cost_usd
    )
    change = _finite_number(
        "total change", after.total_cost_usd - before.total_cost_usd
    )
    residual = _finite_number(
        "reconciliation residual", change - _total([volume, mix, intensity, price])
    )
    return WorkloadSpendDecomposition(
        before, after, volume, mix, intensity, price, change, residual
    )
