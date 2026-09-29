"""Milestone equipment funding and post-acceptance F1 amortization."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from .cashflows import _integer
from .economics import _finite_number
from .financing import _fraction, _nonnegative, _total, build_amortizing_loan_schedule


@dataclass(frozen=True)
class DeploymentRow:
    """USD components at each monthly boundary, before any owner funding."""

    month_offset: int
    capex_usd: float
    site_cost_usd: float
    receipts_usd: float
    operating_cost_usd: float
    draw_usd: float
    interest_usd: float
    principal_repayment_usd: float
    closing_debt_usd: float
    net_cash_usd: float
    cumulative_cash_usd: float


def build_deployment_funding_schedule(
    *,
    milestone_months: Sequence[int],
    milestone_payments_usd: Sequence[float],
    operating_start_month: int,
    operating_receipts_usd: Sequence[float],
    operating_costs_usd: Sequence[float],
    monthly_site_cost_usd: float,
    draw_strategy: Literal["immediate", "staged"],
    debt_fraction: float,
    nominal_annual_interest_rate: float,
    repayment_term_months: int,
) -> tuple[DeploymentRow, ...]:
    """Deposit at t=0, strictly later milestones ending at acceptance.

    Interest paid on opening debt; boundary draws accrue next month. No fees or
    capitalization. Site costs at t=1..acceptance, operations start afterward.
    Fully amortize all debt from acceptance+1 using F1, extending to last cash
    or debt payment. USD arrays start at the first operating month, NOT t=0.
    Finite nonnegative amounts/rate, debt fraction [0,1], integer months.
    Reject bool/wrong types with TypeError, invalid values/overflow ValueError.
    """
    months = tuple(_integer("milestone month", t) for t in milestone_months)
    payments = tuple(
        _nonnegative("milestone payment", p) for p in milestone_payments_usd
    )
    if (
        len(months) < 2
        or len(months) != len(payments)
        or months[0] != 0
        or any(b <= a for a, b in zip(months, months[1:]))
    ):
        raise ValueError(
            "require increasing milestones from zero, with matching payments"
        )
    acceptance = months[-1]
    start = _integer("operating_start_month", operating_start_month, minimum=1)
    if start <= acceptance:
        raise ValueError("operations must start after acceptance")
    receipts = tuple(
        _nonnegative("operating receipt", v) for v in operating_receipts_usd
    )
    costs = tuple(_nonnegative("operating cost", v) for v in operating_costs_usd)
    if not receipts or len(receipts) != len(costs):
        raise ValueError("operating arrays must be nonempty and equal length")
    site = _nonnegative("monthly_site_cost_usd", monthly_site_cost_usd)
    fraction = _fraction("debt_fraction", debt_fraction, inclusive=True)
    rate = _nonnegative("nominal_annual_interest_rate", nominal_annual_interest_rate)
    term = _integer("repayment_term_months", repayment_term_months, minimum=1)
    if not isinstance(draw_strategy, str):
        raise TypeError("draw_strategy must be a string")
    if draw_strategy not in ("immediate", "staged"):
        raise ValueError("draw_strategy must be immediate or staged")
    total_debt = _finite_number("total debt", _total(payments) * fraction)
    loan = build_amortizing_loan_schedule(
        principal_usd=total_debt,
        nominal_annual_interest_rate=rate,
        loan_term_months=term,
    )
    capex = dict(zip(months, payments))
    horizon = max(start + len(receipts) - 1, acceptance + term)
    debt = cumulative = 0.0
    rows = []
    for t in range(horizon + 1):
        payment = capex.get(t, 0.0)
        draw = (
            (total_debt if t == 0 else 0.0)
            if draw_strategy == "immediate"
            else payment * fraction
        )
        interest = (
            _finite_number("interest", debt * (rate / 12))
            if t <= acceptance
            else loan[t - acceptance].interest_usd
            if t <= acceptance + term
            else 0.0
        )
        principal = (
            loan[t - acceptance].principal_repayment_usd
            if acceptance < t <= acceptance + term
            else 0.0
        )
        debt = _total([debt, draw, -principal])
        if t >= acceptance + term:
            debt = 0.0
        receipt = receipts[t - start] if start <= t < start + len(receipts) else 0.0
        cost = costs[t - start] if start <= t < start + len(costs) else 0.0
        site_payment = site if 1 <= t <= acceptance else 0.0
        net = _total(
            [draw, receipt, -payment, -cost, -site_payment, -interest, -principal]
        )
        cumulative = _total([cumulative, net])
        rows.append(
            DeploymentRow(
                t,
                payment,
                site_payment,
                receipt,
                cost,
                draw,
                interest,
                principal,
                debt,
                net,
                cumulative,
            )
        )
    return tuple(rows)
