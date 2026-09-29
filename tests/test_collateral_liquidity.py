import pytest

from liquid_compute.collateral_liquidity import (
    futures_variation_cash_flows,
    otc_collateral_transfers,
)

BASE = dict(
    entry_usd_per_gpu_hour=5,
    marks_usd_per_gpu_hour=[6, 7, 5],
    hedge_gpu_hours=7200,
    mark_months=[1, 2, 3],
    side="seller",
)


def test_futures_variation_and_initial_margin_are_separate():
    rows = futures_variation_cash_flows(**BASE, initial_margin_usd=5000)
    assert [r.derivative_settlement_usd for r in rows] == [0, -7200, -7200, 14400]
    assert [r.collateral_transfer_usd for r in rows] == [-5000, 0, 0, 5000]
    assert [r.restricted_balance_usd for r in rows] == [5000, 5000, 5000, 0]
    assert min(r.cumulative_cash_usd for r in rows) == -19400
    assert rows[-1].cumulative_cash_usd == 0
    flat = futures_variation_cash_flows(
        **(BASE | {"marks_usd_per_gpu_hour": [5, 5, 5]}), initial_margin_usd=5000
    )
    assert flat[-1].cumulative_cash_usd == rows[-1].cumulative_cash_usd
    assert min(r.cumulative_cash_usd for r in flat) == -5000


@pytest.mark.parametrize("side,sign", [("buyer", 1), ("seller", -1)])
def test_variation_telescopes_with_no_extra_terminal_payment(side, sign):
    rows = futures_variation_cash_flows(
        **(BASE | {"side": side, "marks_usd_per_gpu_hour": [6, 4, 7]}),
        initial_margin_usd=0,
    )
    assert sum(r.derivative_settlement_usd for r in rows) == sign * 14400
    assert rows[-1].cumulative_cash_usd == sign * 14400
    assert all(r.restricted_balance_usd == 0 for r in rows)


def test_otc_balances_transfers_and_threshold():
    rows = otc_collateral_transfers(**BASE, threshold_usd=5000)
    assert [r.restricted_balance_usd for r in rows] == [0, 2200, 9400, 0]
    assert [r.collateral_transfer_usd for r in rows] == [0, -2200, -7200, 9400]
    assert sum(r.collateral_transfer_usd for r in rows) == 0
    assert min(r.cumulative_cash_usd for r in rows) == -9400
    zero = otc_collateral_transfers(**BASE, threshold_usd=0)
    assert min(r.cumulative_cash_usd for r in zero) == -14400


def test_otc_terminal_loss_is_settled_once_after_collateral_return():
    rows = otc_collateral_transfers(
        **(BASE | {"marks_usd_per_gpu_hour": [6, 7, 6]}), threshold_usd=5000
    )
    assert rows[-1].collateral_transfer_usd == 9400
    assert rows[-1].derivative_settlement_usd == -7200
    assert sum(r.net_cash_usd for r in rows) == -7200
    positive = otc_collateral_transfers(**(BASE | {"side": "buyer"}), threshold_usd=0)
    assert all(r.collateral_transfer_usd == 0 for r in positive)


@pytest.mark.parametrize(
    "changes,error",
    [
        ({"marks_usd_per_gpu_hour": []}, ValueError),
        ({"mark_months": [1, 1, 3]}, ValueError),
        ({"mark_months": [0, 2, 3]}, ValueError),
        ({"mark_months": [True, 2, 3]}, TypeError),
        ({"hedge_gpu_hours": -1}, ValueError),
        ({"hedge_gpu_hours": float("nan")}, ValueError),
        ({"marks_usd_per_gpu_hour": [6, float("inf"), 5]}, ValueError),
        ({"marks_usd_per_gpu_hour": [6, True, 5]}, TypeError),
        ({"hedge_gpu_hours": 1e308}, ValueError),
    ],
)
def test_invalid_inputs(changes, error):
    for function, extra in (
        (futures_variation_cash_flows, {"initial_margin_usd": 5000}),
        (otc_collateral_transfers, {"threshold_usd": 5000}),
    ):
        with pytest.raises(error):
            function(**(BASE | changes), **extra)


@pytest.mark.parametrize(
    "value,error", [(-1, ValueError), (True, TypeError), (float("inf"), ValueError)]
)
def test_invalid_margin_and_threshold(value, error):
    with pytest.raises(error):
        futures_variation_cash_flows(**BASE, initial_margin_usd=value)
    with pytest.raises(error):
        otc_collateral_transfers(**BASE, threshold_usd=value)


def test_sparse_marks_keep_balance_between_dates():
    rows = otc_collateral_transfers(
        **(BASE | {"mark_months": [1, 3, 5]}), threshold_usd=5000
    )
    assert [r.restricted_balance_usd for r in rows] == [0, 2200, 2200, 9400, 9400, 0]
    assert rows[2].net_cash_usd == rows[4].net_cash_usd == 0
    assert rows[-1].cumulative_cash_usd == 0
