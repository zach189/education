"""Finite unweighted business scenarios; no probabilities or option pricing."""

from collections.abc import Sequence
from dataclasses import dataclass

from .cashflows import _integer, maximum_funding_requirement_usd
from .economics import _positive_number
from .financing import _nonnegative, _total
from .tenor_trade import build_reseller_commitment_scenario


@dataclass(frozen=True)
class OperatingScenario:
    """One original service block, with scenario price, billed GPU-hours and delay."""

    name: str
    customer_usd_per_gpu_hour: float
    billed_gpu_hours: float
    delivery_delay_months: int = 0


@dataclass(frozen=True)
class OperatingScenarioResult:
    """Dense USD cash t=0..last payment/receipt; same modeled service eventually delivered."""

    name: str
    delivered_month: int
    purchased_gpu_hours: float
    realized_billed_gpu_hours: float
    supplier_commitment_usd: float
    total_contribution_usd: float
    customer_receipts_usd: tuple[float, ...]
    supplier_payments_usd: tuple[float, ...]
    net_cash_usd: tuple[float, ...]
    cumulative_cash_usd: tuple[float, ...]
    funding_requirement_usd: float


def evaluate_reseller_scenarios(
    scenarios: Sequence[OperatingScenario],
    *,
    purchased_gpu_hours: float,
    supplier_usd_per_gpu_hour: float,
    supplier_payment_month: int = 1,
) -> tuple[OperatingScenarioResult, ...]:
    """Compose M1 economics with explicit delay of service and customer settlement.

    One service block was planned for month 1. Delay shifts delivery and the
    entire customer receipt to 1+delay, but supplier payment stays at its stated
    month. No service is lost, no replacement purchase/refund/penalty assumed.
    This is a timing scenario, not an automatic contractual delivery remedy.
    Capacity strictly positive, prices nonnegative finite, billed hours in
    [0,capacity], months integers >=0 (supplier payment >0). Names unique and
    nonempty. Type errors raise TypeError; ranges/overflow ValueError.
    """
    capacity = _positive_number("purchased_gpu_hours", purchased_gpu_hours)
    supplier = _nonnegative("supplier_usd_per_gpu_hour", supplier_usd_per_gpu_hour)
    payment_month = _integer(
        "supplier_payment_month", supplier_payment_month, minimum=1
    )
    if not scenarios:
        raise ValueError("at least one explicit scenario is required")
    seen: set[str] = set()
    results = []
    for scenario in scenarios:
        if not isinstance(scenario, OperatingScenario):
            raise TypeError("scenarios must contain OperatingScenario records")
        if not isinstance(scenario.name, str):
            raise TypeError("scenario name must be a string")
        if not scenario.name.strip() or scenario.name in seen:
            raise ValueError("scenario names must be nonempty and unique")
        seen.add(scenario.name)
        billed = _nonnegative("billed_gpu_hours", scenario.billed_gpu_hours)
        if billed > capacity:
            raise ValueError("billed demand exceeds purchased capacity")
        price = _nonnegative(
            "customer_usd_per_gpu_hour", scenario.customer_usd_per_gpu_hour
        )
        delivery = 1 + _integer("delivery_delay_months", scenario.delivery_delay_months)
        economics = build_reseller_commitment_scenario(
            purchased_gpu_hours=[capacity],
            supplier_usd_per_gpu_hour=[supplier],
            billed_fractions=[billed / capacity],
            customer_usd_per_gpu_hour=[price],
            customer_contracted=[False],
        )[1]
        horizon = max(delivery, payment_month)
        receipts = tuple(
            economics.customer_cash_usd if t == delivery else 0.0
            for t in range(horizon + 1)
        )
        payments = tuple(
            economics.supplier_cash_usd if t == payment_month else 0.0
            for t in range(horizon + 1)
        )
        net = tuple(_total([r, -p]) for r, p in zip(receipts, payments))
        cumulative = []
        cash = 0.0
        for amount in net:
            cash = _total([cash, amount])
            cumulative.append(cash)
        results.append(
            OperatingScenarioResult(
                scenario.name,
                delivery,
                capacity,
                billed,
                economics.supplier_cash_usd,
                economics.contribution_usd,
                receipts,
                payments,
                net,
                tuple(cumulative),
                maximum_funding_requirement_usd(net),
            )
        )
    return tuple(results)
