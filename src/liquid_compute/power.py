"""Electricity bills for a party explicitly responsible for facility power."""

from dataclasses import dataclass

from .cashflows import _integer
from .economics import _finite_number, _positive_number
from .financing import _fraction, _nonnegative, _total


@dataclass(frozen=True)
class ElectricityCost:
    """Energy in kWh; separately specified fixed service charge in USD."""

    it_energy_kwh: float
    facility_energy_kwh: float
    energy_cost_usd: float
    fixed_charge_usd: float
    total_bill_usd: float


def electricity_cost_usd(
    *,
    gpu_count: int,
    hours: float,
    it_kw_per_gpu: float,
    facility_multiplier: float,
    delivered_usd_per_kwh: float,
    fixed_charge_usd: float,
) -> ElectricityCost:
    """Count * hours * kW, times facility factor and delivered energy rate.

    Positive integer GPU count and positive hours. Draw, rate and fixed charge
    finite nonnegative; facility multiplier >=1. Zero draw/rate leaves the fixed
    charge. Fixed multiplier is an illustrative energy model, not measured PUE.
    No demand charges, time-of-use rates or electricity already embedded in rent.
    Inputs must be kW, not W; rates USD/kWh, not cents/kWh. Numeric validation
    cannot infer unit mistakes. Wrong types/bools TypeError; range/nonfinite or
    overflow ValueError. No payment dates or financing are inferred.
    """
    count = _finite_number("gpu_count", _integer("gpu_count", gpu_count, minimum=1))
    duration = _positive_number("hours", hours)
    draw = _nonnegative("it_kw_per_gpu", it_kw_per_gpu)
    multiplier = _nonnegative("facility_multiplier", facility_multiplier)
    rate = _nonnegative("delivered_usd_per_kwh", delivered_usd_per_kwh)
    fixed = _nonnegative("fixed_charge_usd", fixed_charge_usd)
    if multiplier < 1:
        raise ValueError("facility_multiplier must be at least 1")
    gpu_hours = _finite_number("GPU-hours", count * duration)
    it_energy = _finite_number("IT kWh", gpu_hours * draw)
    facility_energy = _finite_number("facility kWh", it_energy * multiplier)
    energy_cost = _finite_number("energy cost", facility_energy * rate)
    return ElectricityCost(
        it_energy, facility_energy, energy_cost, fixed, _total([energy_cost, fixed])
    )


def average_it_kw_per_gpu(
    *,
    idle_kw_per_gpu: float,
    active_kw_per_gpu: float,
    technical_active_fraction: float,
) -> float:
    """Linear idle/active draw interpolation, independent of billed utilization.

    Finite nonnegative draw, active >= idle, technical fraction in [0,1]. This
    is an assumed average-load model, not a hardware specification. No billed
    utilization parameter: utilization used for revenue is a separate input.
    """
    idle = _nonnegative("idle_kw_per_gpu", idle_kw_per_gpu)
    active = _nonnegative("active_kw_per_gpu", active_kw_per_gpu)
    fraction = _fraction(
        "technical_active_fraction", technical_active_fraction, inclusive=True
    )
    if active < idle:
        raise ValueError("active_kw_per_gpu must be at least idle_kw_per_gpu")
    return _finite_number("average IT kW", idle + fraction * (active - idle))


def power_swap_receipt_usd(
    *, energy_mwh: float, market_usd_per_mwh: float, fixed_usd_per_mwh: float
) -> float:
    """Power buyer receives floating, pays fixed: MWh * (market - fixed).

    Positive USD offsets a higher physical power bill; negative is a payment.
    Energy finite >=0; both prices finite, signed (power prices can be negative).
    No delivered tariff basis, demand charges, load variation or credit model.
    Wrong types/bools TypeError; range/nonfinite/overflow ValueError.
    """
    energy = _nonnegative("energy_mwh", energy_mwh)
    market = _finite_number("market_usd_per_mwh", market_usd_per_mwh)
    fixed = _finite_number("fixed_usd_per_mwh", fixed_usd_per_mwh)
    return _finite_number("power swap receipt", energy * _total([market, -fixed]))
