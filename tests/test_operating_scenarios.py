import pytest

from liquid_compute.hedging import basis_exposure_summary, forward_settlements_usd
from liquid_compute.scenarios import OperatingScenario, evaluate_reseller_scenarios


def evaluate(cases):
    return evaluate_reseller_scenarios(
        cases, purchased_gpu_hours=7200, supplier_usd_per_gpu_hour=5
    )


def test_demand_price_and_delay_are_separate():
    results = evaluate(
        [
            OperatingScenario("Base", 8, 5400),
            OperatingScenario("Demand", 8, 2700),
            OperatingScenario("Price", 6, 5400),
            OperatingScenario("Delay", 8, 5400, 1),
            OperatingScenario("Cancel", 8, 0),
        ]
    )
    assert [r.total_contribution_usd for r in results] == [
        7200,
        -14400,
        -3600,
        7200,
        -36000,
    ]
    assert all(r.supplier_commitment_usd == 36000 for r in results)
    delay = results[3]
    assert delay.customer_receipts_usd == (0, 0, 43200)
    assert delay.supplier_payments_usd == (0, 36000, 0)
    assert delay.funding_requirement_usd == 36000
    assert delay.cumulative_cash_usd == (0, -36000, 7200)
    assert results[0].funding_requirement_usd == 0


def test_hedge_survives_changed_quantity_and_reuses_basis():
    settlements = forward_settlements_usd(
        benchmark_usd_per_gpu_hour=[3],
        strike_usd_per_gpu_hour=5,
        hedge_gpu_hours=[7200],
        settlement_months=[1],
        side="buyer",
    )
    for physical, expected in [(3600, 25200), (0, 14400)]:
        result = basis_exposure_summary(
            actual_usd_per_gpu_hour=[3],
            physical_gpu_hours=[physical],
            benchmark_usd_per_gpu_hour=[3],
            hedge_gpu_hours=[7200],
            strike_usd_per_gpu_hour=5,
            physical_payment_months=[1],
            settlements=settlements,
        )
        assert result.net_cost_usd == expected
    unhedged = forward_settlements_usd(
        benchmark_usd_per_gpu_hour=[3],
        strike_usd_per_gpu_hour=5,
        hedge_gpu_hours=[0],
        settlement_months=[1],
        side="buyer",
    )
    assert unhedged[0].amount_usd == 0


@pytest.mark.parametrize(
    "scenario,error",
    [
        (OperatingScenario("Too much", 8, 7201), ValueError),
        (OperatingScenario("Bad", 8, True), TypeError),
        (OperatingScenario("Bad", 8, 1, -1), ValueError),
        (OperatingScenario("Bad", 8, 1, True), TypeError),
        (OperatingScenario("Bad", float("inf"), 1), ValueError),
        (OperatingScenario("", 8, 1), ValueError),
    ],
)
def test_invalid(scenario, error):
    with pytest.raises(error):
        evaluate([scenario])


def test_full_usage_delayed_final_boundary_and_duplicate_names():
    result = evaluate([OperatingScenario("Full", 8, 7200, 3)])[0]
    assert result.delivered_month == 4 and len(result.net_cash_usd) == 5
    assert result.total_contribution_usd == 21600
    with pytest.raises(ValueError):
        evaluate([OperatingScenario("A", 8, 1), OperatingScenario("A", 8, 2)])
