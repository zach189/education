import pytest

from liquid_compute.deployment import build_deployment_funding_schedule

BASE = dict(
    milestone_months=(0, 3, 4),
    milestone_payments_usd=(200000, 600000, 200000),
    operating_start_month=5,
    operating_receipts_usd=(110000,) * 12,
    operating_costs_usd=(15000,) * 12,
    monthly_site_cost_usd=5000,
    draw_strategy="staged",
    debt_fraction=0.8,
    nominal_annual_interest_rate=0.12,
    repayment_term_months=12,
)


def test_staged_interest_and_conservation():
    staged = build_deployment_funding_schedule(**BASE)
    immediate = build_deployment_funding_schedule(
        **(BASE | dict(draw_strategy="immediate"))
    )
    assert sum(r.interest_usd for r in staged[:5]) == 11200
    assert sum(r.interest_usd for r in immediate[:5]) == 32000
    assert sum(r.capex_usd for r in staged) == 1000000
    assert staged[3].interest_usd == 1600 and staged[4].interest_usd == 6400
    assert staged[-1].closing_debt_usd == 0
    assert sum(r.principal_repayment_usd for r in staged) == pytest.approx(800000)
    for a, b in zip(staged, staged[1:]):
        assert b.closing_debt_usd == pytest.approx(
            a.closing_debt_usd + b.draw_usd - b.principal_repayment_usd, abs=1e-8
        )


def test_delay_and_equity():
    delayed = build_deployment_funding_schedule(
        **(BASE | dict(milestone_months=(0, 5, 6), operating_start_month=7))
    )
    assert len(delayed) == 19
    assert sum(r.receipts_usd for r in delayed) == 1320000
    assert sum(r.site_cost_usd for r in delayed) == 30000
    equity = build_deployment_funding_schedule(**(BASE | dict(debt_fraction=0)))
    assert all(
        r.interest_usd == r.draw_usd == r.principal_repayment_usd == 0 for r in equity
    )
    zero = build_deployment_funding_schedule(
        **(BASE | dict(nominal_annual_interest_rate=0))
    )
    assert sum(r.interest_usd for r in zero) == 0


@pytest.mark.parametrize(
    "changes",
    [
        dict(milestone_months=(0, 3, 3)),
        dict(operating_start_month=4),
        dict(operating_costs_usd=()),
        dict(debt_fraction=1.1),
        dict(draw_strategy="unknown"),
    ],
)
def test_invalid(changes):
    with pytest.raises(ValueError):
        build_deployment_funding_schedule(**(BASE | changes))
