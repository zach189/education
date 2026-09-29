"""Simple-period loan interest and fixed-pay swap cash, not benchmark methodology."""

from collections.abc import Sequence
from dataclasses import dataclass

from .economics import _finite_number, _positive_number
from .financing import _nonnegative
from .hedging import _months, forward_settlements_usd


@dataclass(frozen=True)
class RatePayment:
    """USD outflow at a positive month boundary; negative means cash received."""

    payment_month: int
    outflow_usd: float


def _periods(
    balances: Sequence[float],
    reference_rates: Sequence[float],
    year_fractions: Sequence[float],
    payment_months: Sequence[int],
) -> tuple[tuple[float, float, float, int], ...]:
    months = _months(payment_months)
    if not months or not len(balances) == len(reference_rates) == len(
        year_fractions
    ) == len(months):
        raise ValueError("period arrays must be nonempty and equal length")
    return tuple(
        (
            _nonnegative("balance/notional USD", balance),
            _nonnegative("reference annual rate", rate),
            _positive_number("year_fraction", fraction),
            month,
        )
        for balance, rate, fraction, month in zip(
            balances, reference_rates, year_fractions, months
        )
    )


def floating_loan_interest_usd(
    *,
    opening_principal_usd: Sequence[float],
    reference_rates: Sequence[float],
    spread: float,
    year_fractions: Sequence[float],
    payment_months: Sequence[int],
    reference_floor: float = 0.0,
) -> tuple[RatePayment, ...]:
    """Positive loan interest P*(max(reference,floor)+spread)*year_fraction.

    Rates are simple nominal annual fractions, fixed at each declared period's
    start; this is NOT compounded SOFR or a benchmark fixing implementation.
    Floor applies to reference before adding spread. Principal is a supplied
    opening balance, never repaid by this function. Rates/balances nonnegative;
    fractions positive; all numeric inputs finite, excluding bool. Payment months
    positive strictly increasing integers, nonempty equal-length arrays.
    Invalid types raise TypeError; ranges/nonfinite/overflow raise ValueError.
    """
    margin = _nonnegative("spread", spread)
    floor = _nonnegative("reference_floor", reference_floor)
    periods = _periods(
        opening_principal_usd, reference_rates, year_fractions, payment_months
    )
    return tuple(
        RatePayment(
            month,
            _finite_number(
                "loan interest",
                principal
                * _finite_number("loan annual rate", max(rate, floor) + margin)
                * fraction,
            ),
        )
        for principal, rate, fraction, month in periods
    )


def fixed_pay_swap_settlements_usd(
    *,
    notional_usd: Sequence[float],
    reference_rates: Sequence[float],
    fixed_rate: float,
    year_fractions: Sequence[float],
    payment_months: Sequence[int],
) -> tuple[RatePayment, ...]:
    """Signed fixed-pay outflow N*(fixed-reference)*year_fraction; negative receipt.

    Explicit adapter to M2's signed difference engine: its strike becomes the
    fixed annual rate, benchmark the received annual reference, and quantity
    becomes USD notional times year fraction. This algebraic mapping does NOT
    label a rate swap a commodity forward or assign GPU-hour units to rates.
    M2 buyer receipt is negated to report payer outflow. No notional exchanges,
    spread hedge, floors, collateral, fees or fair-strike valuation. Validation
    follows floating_loan_interest_usd, with finite nonnegative fixed rate.
    """
    fixed = _nonnegative("fixed_rate", fixed_rate)
    periods = _periods(notional_usd, reference_rates, year_fractions, payment_months)
    receipts = forward_settlements_usd(
        benchmark_usd_per_gpu_hour=[rate for _, rate, _, _ in periods],
        strike_usd_per_gpu_hour=fixed,
        hedge_gpu_hours=[
            _finite_number("notional times accrual fraction", n * fraction)
            for n, _, fraction, _ in periods
        ],
        settlement_months=[month for _, _, _, month in periods],
        side="buyer",
    )
    return tuple(RatePayment(row.month_offset, -row.amount_usd) for row in receipts)
