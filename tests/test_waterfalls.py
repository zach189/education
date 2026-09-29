import pytest

from liquid_compute.waterfalls import (
    WaterfallState,
    allocate_period_cash,
    build_cash_waterfall,
    equity_return_summary,
)

BASE = dict(
    cash_after_operations_usd=[10000, 10000, 3000] + [10000] * 22,
    initial_debt_usd=100000,
    nominal_annual_interest_rate=0.12,
    scheduled_principal_usd=[4000] * 25,
    opening_reserve_usd=2000,
    reserve_target_usd=6000,
    sweep_fraction=0.5,
)


def test_reference_interest_recomputed_and_cash_conservation():
    rows = build_cash_waterfall(**BASE)
    first = rows[0]
    assert (
        first.interest_paid_usd,
        first.principal_paid_usd,
        first.reserve_topup_usd,
        first.sweep_usd,
        first.distribution_usd,
    ) == (1000, 4000, 4000, 500, 500)
    assert first.closing.debt_usd == 95500
    assert rows[1].current_interest_usd == 955
    assert rows[2].reserve_draw_usd > 0 and rows[2].distribution_usd == 0
    assert rows[-1].closing.debt_usd == rows[-1].closing.reserve_usd == 0
    for row in rows:
        inflow = (
            row.opening.unrestricted_cash_usd
            + row.cash_available_usd
            + row.reserve_draw_usd
            + row.reserve_release_usd
        )
        used = (
            row.operating_paid_usd
            + row.interest_paid_usd
            + row.principal_paid_usd
            + row.reserve_topup_usd
            + row.sweep_usd
            + row.distribution_usd
            + row.closing.unrestricted_cash_usd
        )
        assert inflow == pytest.approx(used)
        assert row.closing.reserve_usd == pytest.approx(
            row.opening.reserve_usd
            - row.reserve_draw_usd
            + row.reserve_topup_usd
            - row.reserve_release_usd
        )
        assert row.closing.debt_usd == pytest.approx(
            row.opening.debt_usd - row.principal_paid_usd - row.sweep_usd
        )
    assert sum(r.principal_paid_usd + r.sweep_usd for r in rows) == pytest.approx(
        100000
    )
    assert sum(r.reserve_release_usd for r in rows) <= 6000


def test_arrears_priority_and_no_capitalized_interest():
    rows = build_cash_waterfall(
        **(
            BASE
            | dict(
                cash_after_operations_usd=[0, 500, 10000] + [10000] * 22,
                opening_reserve_usd=0,
            )
        )
    )
    assert rows[0].closing.interest_arrears_usd == 1000
    assert rows[0].closing.principal_arrears_usd == 4000
    assert rows[0].closing.debt_usd == 100000
    assert rows[1].current_interest_usd == 1000
    assert rows[1].interest_paid_usd == 500 and rows[1].principal_paid_usd == 0
    assert rows[1].closing.interest_arrears_usd == 1500
    assert all(
        r.distribution_usd == 0
        for r in rows
        if r.closing.interest_arrears_usd or r.closing.principal_arrears_usd
    )


def test_operating_shortfall_and_lock_retention():
    rows = build_cash_waterfall(
        **(BASE | dict(cash_after_operations_usd=[-3000] + [10000] * 24))
    )
    assert (
        rows[0].operating_paid_usd == 2000
        and rows[0].closing.operating_arrears_usd == 1000
    )
    assert rows[0].interest_paid_usd == 0
    locked = build_cash_waterfall(
        **(BASE | dict(distribution_locks=[True] * 24 + [False]))
    )
    assert all(r.distribution_usd == 0 for r in locked[:24])
    assert locked[-1].distribution_usd > 0
    assert locked[-1].closing.unrestricted_cash_usd == 0


def test_sweep_cap_zero_debt_release_and_moic():
    row = allocate_period_cash(
        state=WaterfallState(100, 200),
        cash_available_usd=10000,
        scheduled_interest_usd=0,
        scheduled_principal_usd=0,
        reserve_target_usd=200,
        sweep_fraction=1,
    )
    assert (
        row.sweep_usd == 100
        and row.reserve_release_usd == 200
        and row.distribution_usd == 10100
    )
    result = equity_return_summary(
        equity_investments_usd=[30000], equity_distributions_usd=[10000, 25000]
    )
    assert result.net_gain_usd == 5000 and result.moic == pytest.approx(35 / 30)
    assert (
        equity_return_summary(
            equity_investments_usd=[], equity_distributions_usd=[]
        ).moic
        is None
    )
    with pytest.raises(ValueError):
        build_cash_waterfall(**(BASE | dict(sweep_fraction=2)))
    with pytest.raises(TypeError):
        build_cash_waterfall(**(BASE | dict(distribution_locks=[1] * 25)))
