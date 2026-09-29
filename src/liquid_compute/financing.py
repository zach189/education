"""Contractual amortization and owner funding; no collateral or credit valuation."""

from collections.abc import Sequence
from dataclasses import dataclass, fields
from math import expm1, fsum, isclose, log1p
from typing import Literal, TypedDict

from .cashflows import (
    MonthlyCashFlow,
    _integer,
    build_cash_flow_schedule,
    maximum_funding_requirement_usd,
)
from .discounting import present_value_usd
from .economics import _finite_number


class FinancingInputs(TypedDict):
    """Explicit USD/month amounts, integer terms, and dimensionless fractions."""

    monthly_revenue_usd: float
    base_monthly_rental_expense_usd: float
    service_months: int
    customer_payment_lag_months: int
    prepayment_discount_fraction: float
    financed_fraction: float
    nominal_annual_interest_rate: float
    loan_term_months: int
    origination_fee_fraction: float


class _ContractInputs(TypedDict):
    monthly_revenue_usd: float
    base_monthly_rental_expense_usd: float
    service_months: int
    customer_payment_lag_months: int


class _LoanTerms(TypedDict):
    nominal_annual_interest_rate: float
    loan_term_months: int
    origination_fee_fraction: float


def _nonnegative(name: str, value: float) -> float:
    value = _finite_number(name, value)
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")
    return value


def _fraction(name: str, value: float, *, inclusive: bool = False) -> float:
    value = _nonnegative(name, value)
    if value > 1 or (value == 1 and not inclusive):
        raise ValueError(f"{name} must be in [0, {'1]' if inclusive else '1)'}")
    return value


def _total(values: Sequence[float]) -> float:
    try:
        return _finite_number("total", fsum(values))
    except OverflowError as exc:
        raise ValueError("total must be finite") from exc


@dataclass(frozen=True)
class LoanCashFlow:
    """USD at monthly boundaries; t=0 draw/fee, repayments t=1,...,n."""

    month_offset: int
    opening_debt_usd: float
    loan_draw_usd: float
    interest_usd: float
    principal_repayment_usd: float
    fee_usd: float
    closing_debt_usd: float


@dataclass(frozen=True)
class FinancedCashFlow:
    """Positive receipts/payments, signed net/cumulative USD before owner funding."""

    month_offset: int
    supplier_payments_usd: float
    customer_receipts_usd: float
    loan_proceeds_usd: float
    interest_usd: float
    principal_repayments_usd: float
    fees_usd: float
    closing_debt_usd: float
    net_cash_flow_usd: float
    cumulative_cash_usd: float


@dataclass(frozen=True)
class FinancingSummary:
    """Undiscounted costs and cash requirements in USD, excluding owner funding."""

    supplier_cost_usd: float
    interest_usd: float
    fees_usd: float
    combined_cost_usd: float
    initial_own_cash_usd: float
    required_initial_cash_buffer_usd: float


def build_amortizing_loan_schedule(
    *,
    principal_usd: float,
    nominal_annual_interest_rate: float,
    loan_term_months: int,
    origination_fee_fraction: float = 0.0,
) -> tuple[LoanCashFlow, ...]:
    """Fully amortize a t=0 draw with equal monthly payments beginning at t=1.

    Nominal annual interest / 12 is the monthly rate, not an effective annual
    rate or APR. Fee [0,1) multiplies principal and is paid separately at t=0.
    Principal/rate are finite nonnegative numbers; term is a positive integer.
    Zero principal has zero fees/payments. No balloon, grace period or rounding
    to cents; final principal clears numerical residue. Wrong types/bools raise
    TypeError; invalid values or nonfinite arithmetic raise ValueError.
    """
    principal = _nonnegative("principal_usd", principal_usd)
    rate = _nonnegative("nominal_annual_interest_rate", nominal_annual_interest_rate)
    n = _integer("loan_term_months", loan_term_months, minimum=1)
    fee = _fraction("origination_fee_fraction", origination_fee_fraction)
    j = rate / 12
    if j == 0:
        payment = principal / n
    else:
        payment = _finite_number(
            "monthly payment", principal * (j / -expm1(-n * log1p(j)))
        )
    rows = [
        LoanCashFlow(
            0,
            0.0,
            principal,
            0.0,
            0.0,
            _finite_number("fee", principal * fee),
            principal,
        )
    ]
    balance = principal
    for month in range(1, n + 1):
        interest = _finite_number("interest", balance * j)
        repaid = balance if month == n else min(balance, max(0.0, payment - interest))
        _finite_number("repayment", repaid + interest)
        closing = max(0.0, balance - repaid)
        rows.append(LoanCashFlow(month, balance, 0.0, interest, repaid, 0.0, closing))
        balance = closing
    return tuple(rows)


def _validate_rows(
    rows: Sequence[MonthlyCashFlow]
    | Sequence[LoanCashFlow]
    | Sequence[FinancedCashFlow],
    kind: type[MonthlyCashFlow] | type[LoanCashFlow] | type[FinancedCashFlow],
) -> None:
    if not rows:
        raise ValueError("schedule must be nonempty")
    for t, row in enumerate(rows):
        if not isinstance(row, kind):
            raise TypeError(f"schedule must contain {kind.__name__} records")
        if _integer("month_offset", row.month_offset) != t:
            raise ValueError("schedule must start at zero with consecutive boundaries")
        for field in fields(row):
            if field.name != "month_offset":
                value = _finite_number(field.name, getattr(row, field.name))
                if field.name not in ("net_cash_flow_usd", "cumulative_cash_usd"):
                    _nonnegative(field.name, value)


def combine_financing_cash_flows(
    *,
    contract_schedule: Sequence[MonthlyCashFlow],
    loan_schedule: Sequence[LoanCashFlow],
) -> tuple[FinancedCashFlow, ...]:
    """Net simultaneous receipts/draws and payments; extend to the later endpoint.

    Inputs start at zero with consecutive boundaries. Loan opening/closing debt
    must reconcile and end at zero. All amounts must be finite; receipts and
    payment components nonnegative. No owner cash is injected. Customer receipts
    come only from the contract, and loan proceeds never become revenue.
    """
    _validate_rows(contract_schedule, MonthlyCashFlow)
    _validate_rows(loan_schedule, LoanCashFlow)
    previous = 0.0
    for row in loan_schedule:
        expected = _total(
            [row.opening_debt_usd, row.loan_draw_usd, -row.principal_repayment_usd]
        )
        if not isclose(row.opening_debt_usd, previous, abs_tol=1e-8) or not isclose(
            expected, row.closing_debt_usd, abs_tol=1e-8
        ):
            raise ValueError("loan debt balances must reconcile")
        previous = row.closing_debt_usd
    if not isclose(previous, 0.0, abs_tol=1e-8):
        raise ValueError("loan must finish fully repaid")
    result = []
    balance = 0.0
    for t in range(max(len(contract_schedule), len(loan_schedule))):
        c = contract_schedule[t] if t < len(contract_schedule) else None
        loan = loan_schedule[t] if t < len(loan_schedule) else None
        supplier = c.supplier_payments_usd if c else 0.0
        customer = c.customer_receipts_usd if c else 0.0
        draw = loan.loan_draw_usd if loan else 0.0
        interest = loan.interest_usd if loan else 0.0
        principal = loan.principal_repayment_usd if loan else 0.0
        fee = loan.fee_usd if loan else 0.0
        net = _total([customer, draw, -supplier, -interest, -principal, -fee])
        balance = _total([balance, net])
        result.append(
            FinancedCashFlow(
                t,
                supplier,
                customer,
                draw,
                interest,
                principal,
                fee,
                loan.closing_debt_usd if loan else 0.0,
                net,
                balance,
            )
        )
    return tuple(result)


def net_procurement_outflows_usd(
    schedule: Sequence[FinancedCashFlow],
) -> tuple[float, ...]:
    """Positive net costs, index zero at t=0; exclude identical customer receipts.

    Include principal payments AND subtract loan proceeds. Use with
    present_value_usd for a chosen-rate comparison, not a credit-risk valuation.
    """
    _validate_rows(schedule, FinancedCashFlow)
    return tuple(
        _total(
            [
                r.supplier_payments_usd,
                r.interest_usd,
                r.principal_repayments_usd,
                r.fees_usd,
                -r.loan_proceeds_usd,
            ]
        )
        for r in schedule
    )


def summarize_financing_cash_flows(
    schedule: Sequence[FinancedCashFlow],
) -> FinancingSummary:
    """Supplier + interest + fees is cost; principal is not an operating expense.

    Initial own cash covers t=0. Buffer covers the lowest cumulative cash over
    all boundaries, including opening zero. Same-boundary cash is netted.
    """
    outflows = net_procurement_outflows_usd(schedule)
    net = tuple(
        _total([r.customer_receipts_usd, -cost]) for r, cost in zip(schedule, outflows)
    )
    balance = 0.0
    for r, movement in zip(schedule, net):
        balance = _total([balance, movement])
        if not isclose(r.net_cash_flow_usd, movement, abs_tol=1e-8) or not isclose(
            r.cumulative_cash_usd, balance, abs_tol=1e-8
        ):
            raise ValueError("net and cumulative cash must reconcile")
    supplier = _total([r.supplier_payments_usd for r in schedule])
    interest = _total([r.interest_usd for r in schedule])
    fees = _total([r.fees_usd for r in schedule])
    return FinancingSummary(
        supplier,
        interest,
        fees,
        _total([supplier, interest, fees]),
        max(0.0, -net[0]),
        maximum_funding_requirement_usd(net),
    )


def financed_prepayment_break_even_discount_fraction(
    *,
    service_months: int,
    loan_term_months: int,
    financed_fraction: float,
    nominal_annual_interest_rate: float,
    origination_fee_fraction: float,
    cost_measure: Literal["undiscounted", "present_value"],
    annual_discount_rate: float,
) -> float:
    """Discount matching monthly-in-advance purchasing on the specified measure.

    Normalize undiscounted supplier total to one USD; financing terms scale
    linearly with prepayment. Return a signed threshold, never clipped. Effective
    annual comparison rate is independent of nominal loan rate. No credit-risk
    adjustment; same service and customer receipts in all alternatives.
    """
    months = _integer("service_months", service_months, minimum=1)
    fraction = _fraction("financed_fraction", financed_fraction, inclusive=True)
    if not isinstance(cost_measure, str):
        raise TypeError("cost_measure must be a string")
    if cost_measure not in ("undiscounted", "present_value"):
        raise ValueError("unsupported cost_measure")
    loan = build_amortizing_loan_schedule(
        principal_usd=fraction,
        nominal_annual_interest_rate=nominal_annual_interest_rate,
        loan_term_months=loan_term_months,
        origination_fee_fraction=origination_fee_fraction,
    )
    upfront = build_cash_flow_schedule(
        monthly_revenue_usd=0,
        base_monthly_rental_expense_usd=1 / months,
        service_months=months,
        customer_payment_lag_months=0,
        supplier_terms="upfront",
    )
    costs = net_procurement_outflows_usd(
        combine_financing_cash_flows(contract_schedule=upfront, loan_schedule=loan)
    )
    # Validate the comparison rate even when it does not enter undiscounted cost.
    pv = present_value_usd(costs, annual_discount_rate=annual_discount_rate)
    monthly = [1 / months] * months
    denominator = _total(costs) if cost_measure == "undiscounted" else pv
    numerator = (
        1.0
        if cost_measure == "undiscounted"
        else present_value_usd(monthly, annual_discount_rate=annual_discount_rate)
    )
    if denominator <= 0:
        raise ValueError("comparison cost must be positive")
    return _finite_number("break-even discount", 1 - numerator / denominator)


def compare_prepayment_financing(
    *,
    monthly_revenue_usd: float,
    base_monthly_rental_expense_usd: float,
    service_months: int,
    customer_payment_lag_months: int,
    prepayment_discount_fraction: float,
    financed_fraction: float,
    nominal_annual_interest_rate: float,
    loan_term_months: int,
    origination_fee_fraction: float,
) -> dict[str, tuple[FinancedCashFlow, ...]]:
    """Build F1's three alternatives with identical service/customer receipts.

    Monthly purchasing is in advance; prepayment replaces all supplier payments.
    Financing fraction [0,1] applies only to supplier prepayment, not the fee.
    All validation/units follow the contract and loan builders.
    """
    fraction = _fraction("financed_fraction", financed_fraction, inclusive=True)
    inputs: _ContractInputs = dict(
        monthly_revenue_usd=monthly_revenue_usd,
        base_monthly_rental_expense_usd=base_monthly_rental_expense_usd,
        service_months=service_months,
        customer_payment_lag_months=customer_payment_lag_months,
    )
    monthly = build_cash_flow_schedule(**inputs, supplier_terms="monthly_in_advance")
    upfront = build_cash_flow_schedule(
        **inputs,
        supplier_terms="upfront",
        prepayment_discount_fraction=prepayment_discount_fraction,
    )
    terms: _LoanTerms = dict(
        nominal_annual_interest_rate=nominal_annual_interest_rate,
        loan_term_months=loan_term_months,
        origination_fee_fraction=origination_fee_fraction,
    )
    zero = build_amortizing_loan_schedule(principal_usd=0, **terms)
    loan = build_amortizing_loan_schedule(
        principal_usd=upfront[0].supplier_payments_usd * fraction, **terms
    )
    return {
        "Monthly": combine_financing_cash_flows(
            contract_schedule=monthly, loan_schedule=zero
        ),
        "Own-cash prepayment": combine_financing_cash_flows(
            contract_schedule=upfront, loan_schedule=zero
        ),
        "Borrowed prepayment": combine_financing_cash_flows(
            contract_schedule=upfront, loan_schedule=loan
        ),
    }


def debt_service_coverage(*, cfads_usd: float, debt_service_usd: float) -> float | None:
    """Period CFADS / interest-plus-principal; None for zero debt service.

    CFADS may be negative. Inputs must be finite numbers excluding bool; debt
    service must be nonnegative. Raises TypeError/ValueError on invalid inputs.
    """
    cash = _finite_number("cfads_usd", cfads_usd)
    service = _nonnegative("debt_service_usd", debt_service_usd)
    return None if service == 0 else _finite_number("DSCR", cash / service)


def _capacity_inputs(
    cfads_usd: Sequence[float], minimum_dscr: float, rate: float
) -> tuple[tuple[float, ...], float, float]:
    cash = tuple(_nonnegative("sizing CFADS", c) for c in cfads_usd)
    if not cash:
        raise ValueError("sizing requires at least one service month")
    k = _finite_number("minimum_dscr", minimum_dscr)
    if k < 1:
        raise ValueError("minimum_dscr must be at least one")
    return cash, k, _nonnegative("nominal annual rate", rate) / 12


def level_payment_debt_capacity_usd(
    *,
    cfads_usd: Sequence[float],
    minimum_dscr: float,
    nominal_annual_interest_rate: float,
) -> float:
    """Maximum level-payment initial USD loan under every monthly DSCR constraint.

    CFADS starts at service month 1 (no t=0), must be finite/nonnegative.
    Threshold >=1; nominal annual rate >=0, monthly accrual rate=annual/12.
    No terminal proceeds or owner funding. Negative cash must be discussed as
    unsupported by this sizing rule, not silently clipped into the inputs.
    """
    cash, k, j = _capacity_inputs(cfads_usd, minimum_dscr, nominal_annual_interest_rate)
    factor = len(cash) if j == 0 else -expm1(-len(cash) * log1p(j)) / j
    return _finite_number("debt capacity", min(cash) / k * factor)


@dataclass(frozen=True)
class ShapedDebtResult:
    """Feasible initial capacity and F1-compatible rows including time zero.

    Infeasible no-capitalization profiles return zero capacity and no rows;
    candidate_capacity_usd is the mathematical PV, not supported borrowing.
    """

    capacity_usd: float
    candidate_capacity_usd: float
    rows: tuple[LoanCashFlow, ...]
    minimum_defined_dscr: float | None
    feasible: bool
    reason: str


def shape_debt_service(
    *,
    cfads_usd: Sequence[float],
    minimum_dscr: float,
    nominal_annual_interest_rate: float,
) -> ShapedDebtResult:
    """Shape service to CFADS/DSCR, rejecting interest capitalization.

    Input conventions match level_payment_debt_capacity_usd. Discount service
    at the loan's monthly rate, not a business valuation rate. Finite ranges
    are checked; wrong types raise TypeError, invalid values ValueError.
    """
    cash, k, j = _capacity_inputs(cfads_usd, minimum_dscr, nominal_annual_interest_rate)
    services = tuple(c / k for c in cash)
    capacity = 0.0
    for service in reversed(services):
        capacity = _total([service, capacity]) / (1 + j)
    debt = capacity
    rows = [LoanCashFlow(0, 0, capacity, 0, 0, 0, capacity)]
    covers: list[float] = []
    tolerance = 1e-10 * max(1, capacity)
    for t, (available, service) in enumerate(zip(cash, services), 1):
        interest = _finite_number("interest", debt * j)
        if service < interest - tolerance:
            return ShapedDebtResult(
                0,
                capacity,
                (),
                None,
                False,
                f"Month {t} service is below interest; capitalization is excluded",
            )
        principal = min(debt, max(0, service - interest))
        if t == len(cash):
            principal = debt
        closing = max(0, debt - principal)
        rows.append(LoanCashFlow(t, debt, 0, interest, principal, 0, closing))
        coverage = debt_service_coverage(
            cfads_usd=available, debt_service_usd=interest + principal
        )
        if coverage is not None:
            covers.append(coverage)
        debt = closing
    return ShapedDebtResult(
        capacity,
        capacity,
        tuple(rows),
        min(covers) if covers else None,
        True,
        "All periods cover interest without capitalization",
    )
