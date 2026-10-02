"""European cash payoffs and contractual premium cash, independent of valuation."""

from dataclasses import dataclass
from typing import Literal

from .cashflows import _integer
from .economics import _finite_number
from .financing import _nonnegative, _total


@dataclass(frozen=True)
class OptionCashFlow:
    """Signed USD cash to holder/writer at month boundaries, including time zero."""

    month_offset: int
    premium_cash_usd: float
    payoff_cash_usd: float
    net_cash_usd: float


def european_option_payoff_usd(
    *,
    kind: Literal["call", "put"],
    settlement_price_usd_per_gpu_hour: float,
    strike_usd_per_gpu_hour: float,
    covered_gpu_hours: float,
) -> float:
    """Long gross payoff H*max(S-K,0) or H*max(K-S,0), excluding premium.

    Hypothetical European cash settlement; no physical capacity delivery.
    Rates/quantity finite nonnegative numbers, zero strike/quantity valid.
    Negative prices excluded here. Wrong types/bools raise TypeError; invalid
    kind/ranges/nonfinite/overflow raise ValueError. No pricing assumptions.
    """
    if not isinstance(kind, str):
        raise TypeError("kind must be a string")
    if kind not in ("call", "put"):
        raise ValueError("kind must be call or put")
    price = _nonnegative(
        "settlement_price_usd_per_gpu_hour", settlement_price_usd_per_gpu_hour
    )
    strike = _nonnegative("strike_usd_per_gpu_hour", strike_usd_per_gpu_hour)
    quantity = _nonnegative("covered_gpu_hours", covered_gpu_hours)
    intrinsic = max(0, price - strike) if kind == "call" else max(0, strike - price)
    return _finite_number("option payoff", quantity * intrinsic)


def option_cash_flows(
    *,
    kind: Literal["call", "put"],
    settlement_price_usd_per_gpu_hour: float,
    strike_usd_per_gpu_hour: float,
    covered_gpu_hours: float,
    premium_usd_per_gpu_hour: float,
    expiry_month: int,
    position: Literal["long", "short"] = "long",
) -> tuple[OptionCashFlow, ...]:
    """Upfront premium at t=0, European payoff at positive integer expiry month.

    Premium quoted per covered GPU-hour, finite nonnegative; counted once.
    Long pays premium/receives payoff; writer receives premium/pays payoff.
    Both legs reverse for short, preserving zero-sum cash before default/costs.
    All price/quantity validation follows european_option_payoff_usd. Return
    dense monthly cash, not a PV, including zeros between dates.
    """
    if not isinstance(position, str):
        raise TypeError("position must be a string")
    if position not in ("long", "short"):
        raise ValueError("position must be long or short")
    expiry = _integer("expiry_month", expiry_month, minimum=1)
    payoff = european_option_payoff_usd(
        kind=kind,
        settlement_price_usd_per_gpu_hour=settlement_price_usd_per_gpu_hour,
        strike_usd_per_gpu_hour=strike_usd_per_gpu_hour,
        covered_gpu_hours=covered_gpu_hours,
    )
    premium = _finite_number(
        "total premium",
        _nonnegative("premium_usd_per_gpu_hour", premium_usd_per_gpu_hour)
        * covered_gpu_hours,
    )
    sign = 1 if position == "long" else -1
    rows = []
    for month in range(expiry + 1):
        premium_cash = -sign * premium if month == 0 else 0.0
        payoff_cash = sign * payoff if month == expiry else 0.0
        rows.append(
            OptionCashFlow(
                month, premium_cash, payoff_cash, _total([premium_cash, payoff_cash])
            )
        )
    return tuple(rows)


@dataclass(frozen=True)
class StagedOptionCashFlow:
    """Actual holder cash per normalized unit; node option values are excluded."""

    month_offset: int
    premium_cash_usd: float
    exercise_cash_usd: float
    payoff_cash_usd: float
    net_cash_usd: float


def staged_option_cash_flows(
    *,
    premium_usd: float,
    exercise_fee_usd: float,
    exercise_month: int,
    expiry_month: int,
    exercised: bool,
    settlement_price_usd_per_unit: float,
    strike_usd_per_unit: float,
) -> tuple[StagedOptionCashFlow, ...]:
    """Realized purchase-right cash: premium now, optional fee, final call payoff.

    One normalized proxy unit, with explicit 0 < exercise_month < expiry_month.
    Caller supplies an exercise decision, e.g. from compound_call_value; this
    cash function does not optimize it or infer a business launch policy.
    Premium and fee are finite nonnegative USD totals for that unit. If not
    exercised, only premium is paid, even if an unowned call would finish ITM.
    No cash receipt for intermediate valuation surplus. Wrong types/bools in
    numeric fields raise TypeError; invalid ranges/nonfinite/overflow ValueError.
    """
    premium = _nonnegative("premium_usd", premium_usd)
    fee = _nonnegative("exercise_fee_usd", exercise_fee_usd)
    exercise = _integer("exercise_month", exercise_month, minimum=1)
    expiry = _integer("expiry_month", expiry_month, minimum=1)
    if exercise >= expiry:
        raise ValueError("exercise_month must be strictly before expiry_month")
    if not isinstance(exercised, bool):
        raise TypeError("exercised must be a bool")
    payoff = european_option_payoff_usd(
        kind="call",
        settlement_price_usd_per_gpu_hour=settlement_price_usd_per_unit,
        strike_usd_per_gpu_hour=strike_usd_per_unit,
        covered_gpu_hours=1,
    )
    rows = []
    for month in range(expiry + 1):
        premium_cash = -premium if month == 0 else 0.0
        exercise_cash = -fee if month == exercise and exercised else 0.0
        payoff_cash = payoff if month == expiry and exercised else 0.0
        rows.append(
            StagedOptionCashFlow(
                month,
                premium_cash,
                exercise_cash,
                payoff_cash,
                _total([premium_cash, exercise_cash, payoff_cash]),
            )
        )
    return tuple(rows)


def tenor_spread_put_payoff_usd(
    *,
    short_tenor_index_usd_per_gpu_hour: float,
    long_tenor_index_usd_per_gpu_hour: float,
    strike_spread_usd_per_gpu_hour: float,
    covered_gpu_hours: float,
) -> float:
    """Cash put H * max(K - (short-tenor index - long-tenor index), 0).

    Both outright indices finite >=0, quantity finite >=0. Strike spread is
    finite and may be negative, as may the observed spread. All observations
    must follow the agreed matching settlement methodology. This is a payoff,
    not a premium/valuation or proof of physical margin protection. Wrong
    types/bools TypeError; invalid ranges/nonfinite/overflow ValueError.
    """
    short_index = _nonnegative(
        "short_tenor_index_usd_per_gpu_hour", short_tenor_index_usd_per_gpu_hour
    )
    long_index = _nonnegative(
        "long_tenor_index_usd_per_gpu_hour", long_tenor_index_usd_per_gpu_hour
    )
    strike = _finite_number(
        "strike_spread_usd_per_gpu_hour", strike_spread_usd_per_gpu_hour
    )
    hours = _nonnegative("covered_gpu_hours", covered_gpu_hours)
    spread = _total([short_index, -long_index])
    shortfall = max(_total([strike, -spread]), 0.0)
    return _finite_number("spread put payoff", shortfall * hours)
