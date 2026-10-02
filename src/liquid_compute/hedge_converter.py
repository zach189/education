"""Translate business thresholds to illustrative option size, not option prices.

Adapted from Liquid Compute Trading Tools v1 (1 October 2026), pages 1–2,
and its companion workbook, Converter sheet. Timing/index specifications are
separate contract assumptions. Payoffs remain owned by liquid_compute.options.
"""

from dataclasses import dataclass
from typing import Literal

from .cashflows import _integer
from .economics import _finite_number, _positive_number
from .financing import _fraction, _nonnegative


@dataclass(frozen=True)
class HedgeTerms:
    """Gross cash payoff inputs; notional is GPU-hours, strike is USD/GPU-hour."""

    kind: Literal["put", "call"]
    strike_usd_per_gpu_hour: float
    notional_gpu_hours: float


def lender_hedge_terms(
    *,
    contract_usd_per_gpu_hour: float,
    prepaid_usd: float,
    advance_fraction: float,
    remarketing_fee_fraction: float,
) -> HedgeTerms:
    """Match principal shortfall when all prepaid hours can be re-let at the index.

    H=P/r, principal=a*P, net recovery=S*(1-f)*H. Thus K=a*r/(1-f),
    N=H*(1-f). Assumes enforceable transferable capacity rights and full recovery
    of hours; no hardware ownership, interest, premium or default guarantee.
    Rate >0, prepayment >=0, advance in [0,1], fee in [0,1).
    All numeric inputs must be finite int/float excluding bool. Wrong types
    raise TypeError; invalid ranges, nonfinite inputs/outputs raise ValueError.
    """
    rate = _positive_number("contract_usd_per_gpu_hour", contract_usd_per_gpu_hour)
    prepaid = _nonnegative("prepaid_usd", prepaid_usd)
    advance = _fraction("advance_fraction", advance_fraction, inclusive=True)
    fee = _fraction("remarketing_fee_fraction", remarketing_fee_fraction)
    hours = _finite_number("prepaid GPU-hours", prepaid / rate)
    return HedgeTerms(
        "put",
        _finite_number("strike", advance * rate / (1 - fee)),
        _finite_number("notional GPU-hours", hours * (1 - fee)),
    )


def _hours_per_gpu(
    months: int, utilization_fraction: float, hours_per_gpu_month: float
) -> float:
    months = _integer("months", months, minimum=1)
    utilization = _fraction(
        "utilization_fraction", utilization_fraction, inclusive=True
    )
    hours = _positive_number("hours_per_gpu_month", hours_per_gpu_month)
    return _finite_number(
        "hours per GPU", hours * _finite_number("months", months) * utilization
    )


def lessor_hedge_terms(
    *,
    gpu_count: int,
    residual_usd_per_gpu: float,
    relet_months: int,
    utilization_fraction: float,
    opex_usd_per_billed_gpu_hour: float,
    hours_per_gpu_month: float = 730,
) -> HedgeTerms:
    """Translate a residual recovery target into undiscounted re-let economics.

    h=u*h_month*months, K=residual/h+opex, N=GPUs*h. Costs scale with
    billed hours; excludes fixed costs and hardware sale proceeds. This is not
    a hardware valuation. A final-month index only matches later rental income
    if the entire re-let term can be priced at that index observation.
    GPU count integer >=0, months integer >0, utilization in (0,1], monthly
    hours >0, residual/opex >=0. Type/range/overflow errors as lender converter.
    """
    count = _finite_number("gpu_count", _integer("gpu_count", gpu_count, minimum=0))
    residual = _nonnegative("residual_usd_per_gpu", residual_usd_per_gpu)
    opex = _nonnegative("opex_usd_per_billed_gpu_hour", opex_usd_per_billed_gpu_hour)
    hours = _positive_number(
        "re-let hours per GPU",
        _hours_per_gpu(relet_months, utilization_fraction, hours_per_gpu_month),
    )
    return HedgeTerms(
        "put",
        _finite_number("strike", residual / hours + opex),
        _finite_number("notional GPU-hours", count * hours),
    )


def operator_hedge_terms(
    *,
    gpu_count: int,
    months: int,
    utilization_fraction: float,
    breakeven_usd_per_gpu_hour: float,
    hours_per_gpu_month: float = 730,
) -> HedgeTerms:
    """Put at a supplied break-even threshold over planned billed hours.

    This does not derive costs or recompute break-even if utilization changes.
    Count integer >=0, months integer >0, utilization [0,1], break-even >=0,
    monthly hours >0. Numeric validation and errors as lender converter.
    """
    count = _finite_number("gpu_count", _integer("gpu_count", gpu_count, minimum=0))
    strike = _nonnegative("breakeven_usd_per_gpu_hour", breakeven_usd_per_gpu_hour)
    hours = _hours_per_gpu(months, utilization_fraction, hours_per_gpu_month)
    return HedgeTerms(
        "put", strike, _finite_number("notional GPU-hours", count * hours)
    )


def buyer_hedge_terms(
    *,
    gpu_count: int,
    months: int,
    budget_usd_per_gpu_hour: float,
    hours_per_gpu_month: float = 730,
) -> HedgeTerms:
    """Call at a supplied budget over all reserved hours, even if some go unused.

    Count integer >=0, months integer >0, budget >=0, monthly hours >0.
    Numeric validation and errors as lender converter. Premium is additional.
    """
    count = _finite_number("gpu_count", _integer("gpu_count", gpu_count, minimum=0))
    strike = _nonnegative("budget_usd_per_gpu_hour", budget_usd_per_gpu_hour)
    hours = _hours_per_gpu(months, 1.0, hours_per_gpu_month)
    return HedgeTerms(
        "call", strike, _finite_number("notional GPU-hours", count * hours)
    )
