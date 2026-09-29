"""Procurement cash, explicit ownership rights and illustrative book arithmetic."""

from collections.abc import Sequence
from dataclasses import dataclass

from .cashflows import _integer
from .discounting import present_value_usd
from .economics import _finite_number
from .financing import _nonnegative, _total, build_amortizing_loan_schedule


@dataclass(frozen=True)
class ProcurementComparison:
    """Signed cash outflows in USD; t=0 included, resale is a negative cost."""

    purchase_outflows_usd: tuple[float, ...]
    lease_outflows_usd: tuple[float, ...]
    purchase_nominal_cost_usd: float
    lease_nominal_cost_usd: float
    purchase_pv_cost_usd: float
    lease_pv_cost_usd: float


def compare_purchase_lease_cash_flows(
    *,
    purchase_price_usd: float,
    lease_payments_usd: Sequence[float],
    exit_month: int,
    resale_proceeds_usd: float,
    has_resale_rights: bool,
    annual_discount_rate: float,
) -> ProcurementComparison:
    """Same service horizon; unlevered purchase versus lease with no buyout.

    Lease entries represent months 1..exit, not t=0. Purchase paid at t=0,
    resale once at exit. Price/payments/proceeds finite nonnegative; positive
    integer exit, explicit bool rights. Positive resale without rights fails.
    Business PV uses existing effective annual discounting (rate > -1).
    Wrong types raise TypeError, invalid ranges/overflow ValueError.
    """
    price = _nonnegative("purchase_price_usd", purchase_price_usd)
    sale = _nonnegative("resale_proceeds_usd", resale_proceeds_usd)
    end = _integer("exit_month", exit_month, minimum=1)
    if not isinstance(has_resale_rights, bool):
        raise TypeError("has_resale_rights must be bool")
    if sale and not has_resale_rights:
        raise ValueError("resale proceeds require ownership/resale rights")
    lease = (0.0,) + tuple(_nonnegative("lease payment", v) for v in lease_payments_usd)
    if len(lease) != end + 1:
        raise ValueError("lease must cover exactly the purchase service horizon")
    purchase = (price,) + (0.0,) * (end - 1) + (-sale,)
    return ProcurementComparison(
        purchase,
        lease,
        _total(purchase),
        _total(lease),
        present_value_usd(purchase, annual_discount_rate=annual_discount_rate),
        present_value_usd(lease, annual_discount_rate=annual_discount_rate),
    )


def equipment_exit_equity_usd(
    *, sale_proceeds_usd: float, debt_payoff_usd: float
) -> float:
    """Signed USD to equity after debt payoff; negative means additional cash need."""
    return _finite_number(
        "exit equity",
        _nonnegative("sale proceeds", sale_proceeds_usd)
        - _nonnegative("debt payoff", debt_payoff_usd),
    )


def straight_line_book_values(
    *,
    purchase_price_usd: float,
    assumed_book_residual_usd: float,
    useful_life_months: int,
) -> tuple[float, ...]:
    """Illustrative straight-line book USD at t=0..life; not tax/market values.

    Residual must be between zero and finite nonnegative price, life integer >0.
    Changing actual sale proceeds never changes these independent assumptions.
    """
    price = _nonnegative("purchase_price_usd", purchase_price_usd)
    residual = _nonnegative("assumed_book_residual_usd", assumed_book_residual_usd)
    life = _integer("useful_life_months", useful_life_months, minimum=1)
    if residual > price:
        raise ValueError("book residual cannot exceed purchase price")
    return tuple(
        residual if t == life else price - (price - residual) * (t / life)
        for t in range(life + 1)
    )


@dataclass(frozen=True)
class FinancedEquipmentExit:
    """Owner procurement cash through sale only; mandatory debt payoff at exit."""

    owner_outflows_usd: tuple[float, ...]
    debt_payoff_usd: float
    equity_from_sale_usd: float


def financed_equipment_exit(
    *,
    purchase_price_usd: float,
    loan_principal_usd: float,
    nominal_annual_interest_rate: float,
    loan_term_months: int,
    sale_month: int,
    sale_proceeds_usd: float,
) -> FinancedEquipmentExit:
    """Owned equipment sale AFTER scheduled payment, canceling all later debt.

    No fees/prepayment penalty. Price/principal/sale nonnegative finite USD;
    loan cannot exceed price. Sale positive month; may follow loan maturity.
    F1 validates loan rate/term. No lease resale or implied book-value recovery.
    """
    price = _nonnegative("purchase_price_usd", purchase_price_usd)
    principal = _nonnegative("loan_principal_usd", loan_principal_usd)
    sale = _nonnegative("sale_proceeds_usd", sale_proceeds_usd)
    end = _integer("sale_month", sale_month, minimum=1)
    if principal > price:
        raise ValueError("procurement loan cannot exceed price")
    loan = build_amortizing_loan_schedule(
        principal_usd=principal,
        nominal_annual_interest_rate=nominal_annual_interest_rate,
        loan_term_months=loan_term_months,
    )
    payoff = loan[end].closing_debt_usd if end < len(loan) else 0.0
    flows = [price - principal]
    for t in range(1, end + 1):
        service = (
            _total([loan[t].interest_usd, loan[t].principal_repayment_usd])
            if t < len(loan)
            else 0.0
        )
        flows.append(_total([service, payoff, -sale]) if t == end else service)
    return FinancedEquipmentExit(
        tuple(flows),
        payoff,
        equipment_exit_equity_usd(sale_proceeds_usd=sale, debt_payoff_usd=payoff),
    )
