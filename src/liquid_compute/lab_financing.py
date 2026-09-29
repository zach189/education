"""Deterministic lab-owner case; hypothetical cash capacity, not a credit quote."""

from dataclasses import dataclass, fields, replace
from typing import Literal

from .cashflows import _integer, maximum_funding_requirement_usd
from .economics import _finite_number
from .financing import (
    LoanCashFlow,
    _fraction,
    _nonnegative,
    _total,
    build_amortizing_loan_schedule,
    debt_service_coverage,
)


@dataclass(frozen=True)
class LabInputs:
    """USD, GPU-hours and monthly boundaries; all defaults hypothetical.

    Share fractions refer to usable capacity, spot utilization to the remainder.
    Costs include training. Fixed costs continue before deployment. Payments lost
    in the interruption window are never recovered; debt never pauses. Reserve
    is locked through the horizon, not available to mask an operating shortfall.
    Support is separately committed project cash, beyond purchase equity/reserve.
    """

    equipment_usd: float = 1_000_000_000
    advance_fraction: float = 0.5
    gpu_count: int = 32_000
    hours_per_month: float = 720
    availability_fraction: float = 0.95
    training_fraction: float = 0.4
    contracted_fraction: float = 0.4
    contract_usd_per_gpu_hour: float = 4
    spot_usd_per_gpu_hour: float = 2
    spot_utilization_fraction: float = 0.5
    active_cost_usd_per_gpu_hour: float = 0.6
    fixed_cost_usd_per_month: float = 3_000_000
    nominal_annual_rate: float = 0.17
    term_months: int = 60
    fee_fraction: float = 0.015
    reserve_months: int = 3
    deployment_delay_months: int = 0
    interruption_start_month: int = 13
    interruption_months: int = 0
    support_cash_usd: float = 0
    minimum_dscr: float = 1.25
    repayment: Literal["level", "balloon"] = "level"
    annual_value_retention_fraction: float = 0.65
    liquidation_haircut_fraction: float = 0.25
    selling_cost_fraction: float = 0.1
    recovery_delay_months: int = 6


@dataclass(frozen=True)
class LabMonth:
    """Service months 1..term; signed cash before financing, no tax/reinvestment."""

    month: int
    training_gpu_hours: float
    contracted_gpu_hours: float
    spot_gpu_hours: float
    unsold_gpu_hours: float
    external_receipts_usd: float
    operating_cost_usd: float
    cfads_usd: float
    debt_service_usd: float
    closing_debt_usd: float


@dataclass(frozen=True)
class LabResult:
    """Cash-only sizing and funding, conditional on the supplied assumptions."""

    months: tuple[LabMonth, ...]
    loan: tuple[LoanCashFlow, ...]
    fee_usd: float
    reserve_usd: float
    operating_buffer_usd: float
    additional_cash_usd: float
    uncovered_cash_usd: float
    minimum_dscr: float | None
    supportable_loan_usd: float


def _validate(p: LabInputs) -> None:
    if not isinstance(p, LabInputs):
        raise TypeError("inputs must be LabInputs")
    integers = {
        "gpu_count",
        "term_months",
        "reserve_months",
        "deployment_delay_months",
        "interruption_start_month",
        "interruption_months",
        "recovery_delay_months",
    }
    for field in fields(p):
        name, value = field.name, getattr(p, field.name)
        if name == "repayment":
            if not isinstance(value, str):
                raise TypeError("repayment must be a string")
            if value not in ("level", "balloon"):
                raise ValueError("repayment must be level or balloon")
        elif name in integers:
            _integer(
                name,
                value,
                minimum=1
                if name in {"gpu_count", "term_months", "interruption_start_month"}
                else 0,
            )
        elif name.endswith("fraction"):
            _fraction(name, value, inclusive=True)
        else:
            _nonnegative(name, value)
    if p.training_fraction + p.contracted_fraction > 1 + 1e-12:
        raise ValueError("training and contracted shares must sum to at most one")
    if p.hours_per_month <= 0 or p.equipment_usd <= 0 or p.minimum_dscr < 1:
        raise ValueError("hours/equipment must be positive; minimum_dscr >= 1")
    if p.fee_fraction == 1:
        raise ValueError("fee_fraction must be less than one")


def _loan(p: LabInputs, principal: float) -> tuple[LoanCashFlow, ...]:
    if p.repayment == "level":
        return build_amortizing_loan_schedule(
            principal_usd=principal,
            nominal_annual_interest_rate=p.nominal_annual_rate,
            loan_term_months=p.term_months,
            origination_fee_fraction=p.fee_fraction,
        )
    interest = _finite_number("interest", principal * p.nominal_annual_rate / 12)
    return (
        LoanCashFlow(0, 0, principal, 0, 0, principal * p.fee_fraction, principal),
    ) + tuple(
        LoanCashFlow(
            t,
            principal,
            0,
            interest,
            principal if t == p.term_months else 0,
            0,
            0 if t == p.term_months else principal,
        )
        for t in range(1, p.term_months + 1)
    )


def model_lab(p: LabInputs) -> LabResult:
    """Monthly cash and selected repayment profile; finite numbers, no bool inputs.

    Equipment/draw/fee/reserve funded at t=0; all operating receipts and payments
    net at each month-end. No working-capital lag, tax, replacement capex, reserve
    interest/release or distributions. Sizing excludes support and liquidation;
    any negative CFADS supports zero debt under this every-month coverage rule.
    Buffer retains prior surpluses; reserve is additional locked cash. Invalid
    types raise TypeError; invalid ranges or overflow raise ValueError.
    """
    _validate(p)
    loan = _loan(p, p.equipment_usd * p.advance_fraction)
    unit = _loan(p, 1)
    hours = _finite_number(
        "usable hours", p.gpu_count * p.hours_per_month * p.availability_fraction
    )
    rows = []
    for t in range(1, p.term_months + 1):
        available = hours if t > p.deployment_delay_months else 0
        training = available * p.training_fraction
        contract = available * p.contracted_fraction
        remaining = max(0, available - training - contract)
        spot = remaining * p.spot_utilization_fraction
        interrupted = (
            p.interruption_start_month
            <= t
            < p.interruption_start_month + p.interruption_months
        )
        receipts = _total(
            [
                0 if interrupted else contract * p.contract_usd_per_gpu_hour,
                spot * p.spot_usd_per_gpu_hour,
            ]
        )
        cost = _total(
            [
                p.fixed_cost_usd_per_month,
                (training + contract + spot) * p.active_cost_usd_per_gpu_hour,
            ]
        )
        rows.append(
            LabMonth(
                t,
                training,
                contract,
                spot,
                remaining - spot,
                receipts,
                cost,
                _total([receipts, -cost]),
                _total([loan[t].interest_usd, loan[t].principal_repayment_usd]),
                loan[t].closing_debt_usd,
            )
        )
    capacities = [
        r.cfads_usd / p.minimum_dscr / (u.interest_usd + u.principal_repayment_usd)
        for r, u in zip(rows, unit[1:])
        if u.interest_usd + u.principal_repayment_usd > 0
    ]
    capacity = max(0.0, min(capacities)) if min(r.cfads_usd for r in rows) >= 0 else 0.0
    cover = [
        debt_service_coverage(
            cfads_usd=r.cfads_usd, debt_service_usd=r.debt_service_usd
        )
        for r in rows
        if r.debt_service_usd > 0
    ]
    buffer = maximum_funding_requirement_usd(
        [0] + [r.cfads_usd - r.debt_service_usd for r in rows]
    )
    # Reserve covers first N scheduled debt payments, including a balloon if reached.
    reserve = _total([r.debt_service_usd for r in rows[: p.reserve_months]])
    extra = _total([loan[0].fee_usd, reserve, buffer])
    return LabResult(
        tuple(rows),
        loan,
        loan[0].fee_usd,
        reserve,
        buffer,
        extra,
        max(0, buffer - p.support_cash_usd),
        min(c for c in cover if c is not None) if cover else None,
        _finite_number("capacity", capacity),
    )


def minimum_contract_fraction(p: LabInputs) -> float | None:
    """Exact affine threshold at fixed training; None means no feasible share.

    Every month must reach target coverage, including balloon. Zero debt still
    requires nonnegative CFADS. No support/reserve/terminal proceeds in coverage.
    Handles cases where contract price is below displaced spot contribution.
    """
    _validate(p)
    upper = 1 - p.training_fraction
    low_rows = model_lab(replace(p, contracted_fraction=0)).months
    high_rows = model_lab(replace(p, contracted_fraction=upper)).months
    lower, ceiling = 0.0, upper
    for lo, hi in zip(low_rows, high_rows):
        gap = p.minimum_dscr * lo.debt_service_usd - lo.cfads_usd
        slope = (hi.cfads_usd - lo.cfads_usd) / upper if upper else 0
        if slope > 0:
            lower = max(lower, gap / slope)
        elif slope < 0:
            ceiling = min(ceiling, gap / slope)
        elif gap > 1e-7:
            return None
    return lower if lower <= ceiling + 1e-12 and lower <= upper + 1e-12 else None


def liquidation_stress(
    p: LabInputs, *, default_month: int
) -> tuple[float, float, float]:
    """Return net sale, claim, recovery USD after default just AFTER scheduled pay.

    Freeze debt then accrue simple nominal interest during recovery delay; no
    further scheduled payments. Sale value decays through delay, then haircut
    and selling costs apply. Excludes reserve, guarantees and prior arrears;
    assumes enforceable first-priority security and ownership. No discounting.
    """
    _validate(p)
    t = _integer("default_month", default_month)
    if t > p.term_months:
        raise ValueError("default month cannot exceed term")
    debt = _loan(p, p.equipment_usd * p.advance_fraction)[t].closing_debt_usd
    proceeds = _finite_number(
        "sale",
        p.equipment_usd
        * p.annual_value_retention_fraction ** ((t + p.recovery_delay_months) / 12)
        * (1 - p.liquidation_haircut_fraction)
        * (1 - p.selling_cost_fraction),
    )
    claim = _finite_number(
        "claim", debt * (1 + p.nominal_annual_rate * p.recovery_delay_months / 12)
    )
    return proceeds, claim, min(proceeds, claim)
