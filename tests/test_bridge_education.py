import sys

import matplotlib

matplotlib.use("Agg")

from liquid_compute.education import explore_deposit_bridge

BASE = dict(
    deposit_usd=200000,
    draw_usd=200000,
    prepayment_usd=250000,
    nominal_annual_interest_rate=0.12,
    fee_fraction=0.01,
    condition_met=True,
    documentation_day=10,
    due_day=15,
    receipt_day=20,
    horizon_day=60,
    refund_day=None,
    refund_usd=0,
)


def test_explorer_precision_independence_recovery(monkeypatch):
    monkeypatch.setattr("IPython.display.display", lambda *args, **kwargs: None)
    first = explore_deposit_bridge(BASE | dict(prepayment_usd=250000.12345))
    second = explore_deposit_bridge(BASE)
    assert first.children[1].value == 250000.12345
    first.children[0].value = 50
    assert "3,287.67" in first.children[-1].outputs[0]["data"]["text/markdown"]
    assert second.children[0].value == 20
    first.children[0].value = 9
    assert "Check the inputs" in first.children[-1].outputs[0]["data"]["text/markdown"]
    assert len(first.children[-1].outputs) == 1
    first.children[0].value = 20
    assert "image/png" in first.children[-1].outputs[1]["data"]
    first.close()
    second.close()


def test_widget_free_fallback(monkeypatch, capsys):
    captured = []
    monkeypatch.setattr("IPython.display.display", lambda item: captured.append(item))
    monkeypatch.setitem(sys.modules, "ipywidgets", None)
    assert explore_deposit_bridge(BASE) is None
    assert "edit the assumptions" in capsys.readouterr().out
    assert "46,684.93" in captured[0].data
    captured[1].canvas.draw()
