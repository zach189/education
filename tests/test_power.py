import pytest

from liquid_compute.power import average_it_kw_per_gpu, electricity_cost_usd

BASE = dict(
    gpu_count=10,
    hours=720,
    it_kw_per_gpu=0.7,
    facility_multiplier=1.2,
    delivered_usd_per_kwh=0.1,
    fixed_charge_usd=200,
)


def test_independent_energy_and_contribution_reference():
    bill = electricity_cost_usd(**BASE)
    assert bill.it_energy_kwh == 5040
    assert bill.facility_energy_kwh == pytest.approx(6048)
    assert bill.energy_cost_usd == pytest.approx(604.8)
    assert bill.total_bill_usd == pytest.approx(804.8)
    assert 21600 - 14400 - bill.total_bill_usd == pytest.approx(6395.2)
    expensive = electricity_cost_usd(**(BASE | {"delivered_usd_per_kwh": 0.2}))
    assert expensive.energy_cost_usd == 2 * bill.energy_cost_usd
    assert expensive.fixed_charge_usd == bill.fixed_charge_usd == 200
    assert expensive.total_bill_usd == pytest.approx(1409.6)


@pytest.mark.parametrize(
    "changed", [{"it_kw_per_gpu": 0}, {"delivered_usd_per_kwh": 0}]
)
def test_zero_variable_cost_preserves_fixed_charge(changed):
    bill = electricity_cost_usd(**(BASE | changed))
    assert bill.total_bill_usd == 200


def test_multiplier_one_and_technical_load_independent_of_billing():
    bill = electricity_cost_usd(**(BASE | {"facility_multiplier": 1}))
    assert bill.it_energy_kwh == bill.facility_energy_kwh
    for fraction, expected in ((0, 0.2), (0.5, 0.45), (1, 0.7)):
        draw = average_it_kw_per_gpu(
            idle_kw_per_gpu=0.2,
            active_kw_per_gpu=0.7,
            technical_active_fraction=fraction,
        )
        assert draw == pytest.approx(expected)
        load_bill = electricity_cost_usd(**(BASE | {"it_kw_per_gpu": draw}))
        # The same billed service can support different technical loads.
        assert 7200 * 0.75 * 4 == 21600
        assert load_bill.it_energy_kwh == pytest.approx(7200 * expected)


@pytest.mark.parametrize(
    "changes,error",
    [
        ({"gpu_count": True}, TypeError),
        ({"gpu_count": 1.5}, TypeError),
        ({"gpu_count": 0}, ValueError),
        ({"hours": 0}, ValueError),
        ({"facility_multiplier": 0.9}, ValueError),
        ({"it_kw_per_gpu": -1}, ValueError),
        ({"fixed_charge_usd": -1}, ValueError),
        ({"delivered_usd_per_kwh": float("nan")}, ValueError),
        ({"hours": float("inf")}, ValueError),
        ({"it_kw_per_gpu": "700 W"}, TypeError),
        ({"hours": 1e308}, ValueError),
    ],
)
def test_invalid_bill_inputs(changes, error):
    with pytest.raises(error):
        electricity_cost_usd(**(BASE | changes))


@pytest.mark.parametrize(
    "changes,error",
    [
        ({"active_kw_per_gpu": 0.1}, ValueError),
        ({"technical_active_fraction": 1.1}, ValueError),
        ({"technical_active_fraction": True}, TypeError),
        ({"idle_kw_per_gpu": float("inf")}, ValueError),
    ],
)
def test_invalid_technical_load(changes, error):
    args = dict(
        idle_kw_per_gpu=0.2, active_kw_per_gpu=0.7, technical_active_fraction=0.5
    )
    with pytest.raises(error):
        average_it_kw_per_gpu(**(args | changes))
