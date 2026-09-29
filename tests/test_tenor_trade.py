from dataclasses import FrozenInstanceError

import pytest

from liquid_compute.forward_curves import RentalQuote, imply_rental_blocks
from liquid_compute.tenor_trade import (
    build_reseller_commitment_scenario,
    compare_tenor_strategies,
)

BASE = dict(
    purchased_gpu_hours=[7200] * 36,
    supplier_usd_per_gpu_hour=[5] * 36,
    billed_fractions=[0.75] * 36,
    customer_usd_per_gpu_hour=[8] * 36,
    customer_contracted=[True] * 12 + [False] * 24,
)


def test_reference_and_fixed_package_invoices():
    rows = build_reseller_commitment_scenario(**BASE)
    assert len(rows) == 37 and rows[0].cumulative_cash_usd == 0
    assert rows[12].cumulative_cash_usd == 86400
    assert rows[-1].cumulative_cash_usd == 259200
    assert all(r.supplier_cash_usd == 36000 for r in rows[1:])
    assert sum(r.supplier_cash_usd for r in rows) == 36 * 7200 * 5
    blocks = imply_rental_blocks(
        [RentalQuote(12, 6), RentalQuote(36, 5)], delivery_hours_per_gpu=[720] * 36
    )
    assert blocks[1].implied_usd_per_gpu_hour == 4.5
    assert rows[13].supplier_usd_per_gpu_hour == 5  # Never substitute implied 4.5.
    with pytest.raises(FrozenInstanceError):
        rows[1].supplier_cash_usd = 1


def test_renewal_and_contract_only_keep_full_horizon():
    low = build_reseller_commitment_scenario(
        **(BASE | dict(customer_usd_per_gpu_hour=[8] * 12 + [6] * 24))
    )
    assert low[-1].cumulative_cash_usd == 0
    assert low[13].contribution_usd == -3600
    contract = build_reseller_commitment_scenario(
        **(BASE | dict(billed_fractions=[0.75] * 12 + [0] * 24))
    )
    assert contract[-1].month_offset == 36
    assert sum(r.customer_cash_usd for r in contract) == 518400
    assert contract[-1].cumulative_cash_usd == -777600
    empty = build_reseller_commitment_scenario(
        **(BASE | dict(billed_fractions=[0] * 36))
    )
    full = build_reseller_commitment_scenario(
        **(BASE | dict(billed_fractions=[1] * 36))
    )
    assert empty[1].supplier_cash_usd == full[1].supplier_cash_usd == 36000
    assert full[1].billed_gpu_hours == 7200


def test_explicit_annual_scenarios_and_cash_conservation():
    inputs = {
        key: value for key, value in BASE.items() if key != "supplier_usd_per_gpu_hour"
    }
    cases = compare_tenor_strategies(
        **inputs,
        supplier_rate_scenarios={"Long": [5] * 36, "Annual assumption": [6] * 36},
    )
    assert cases["Annual assumption"][-1].cumulative_cash_usd == 0
    for rows in cases.values():
        assert (
            sum(r.customer_cash_usd - r.supplier_cash_usd for r in rows)
            == rows[-1].cumulative_cash_usd
        )


@pytest.mark.parametrize(
    "changes,error",
    [
        (dict(purchased_gpu_hours=[]), ValueError),
        (dict(customer_usd_per_gpu_hour=[8]), ValueError),
        (dict(billed_fractions=[1.01] * 36), ValueError),
        (dict(billed_fractions=[True] * 36), TypeError),
        (dict(customer_contracted=[1] * 36), TypeError),
        (dict(supplier_usd_per_gpu_hour=[float("nan")] * 36), ValueError),
        (dict(purchased_gpu_hours=[1e308] * 36), ValueError),
        (dict(customer_usd_per_gpu_hour=[-1] * 36), ValueError),
    ],
)
def test_invalid(changes, error):
    with pytest.raises(error):
        build_reseller_commitment_scenario(**(BASE | changes))
