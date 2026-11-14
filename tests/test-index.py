import dataclasses

import pytest

from wachta.config import Config
from wachta.index import VigilanceIndex


def _z(alpha_prom=0.0, tab_ratio=0.0):
    return {"alpha_prom": alpha_prom, "tab_ratio": tab_ratio}


def _run(index, start, n, z=None, bad=False):
    out = None
    for i in range(n):
        out = index.update(float(start + i), None if bad else (z or _z()), bad, True)
    return out


def test_state_is_calibrating_until_the_baseline_is_ready():
    index = VigilanceIndex(Config())
    assert index.update(3.0, None, False, False)["state"] == "calibrating"


def test_sustained_alpha_rise_starts_a_lapse_and_it_ends_with_hysteresis():
    index = VigilanceIndex(Config())
    assert _run(index, 0, 30)["state"] == "ok"

    states = [index.update(30.0 + i, _z(alpha_prom=6.0), False, True) for i in range(10)]
    assert sum(s["new_lapse"] for s in states) == 1
    first = next(i for i, s in enumerate(states) if s["new_lapse"])
    assert 3 <= first <= 6          # median over 5 windows, then 3 s above the threshold
    assert states[-1]["state"] == "stop" and states[-1]["lapse"]

    after = _run(index, 40, 10)
    assert not after["lapse"]
    assert after["state"] == "warn"  # a recent lapse keeps the warning on
    assert _run(index, 50, 130)["state"] == "ok"


def test_short_spike_is_not_a_lapse():
    index = VigilanceIndex(Config())
    _run(index, 0, 30)
    states = [index.update(30.0 + i, _z(alpha_prom=6.0), False, True) for i in range(2)]
    states += [index.update(32.0 + i, _z(), False, True) for i in range(10)]
    assert not any(s["new_lapse"] for s in states)


def test_two_lapses_in_two_minutes_keep_the_state_at_stop():
    index = VigilanceIndex(Config())
    _run(index, 0, 30)
    _run(index, 30, 10, _z(alpha_prom=6.0))
    _run(index, 40, 10)
    _run(index, 50, 10, _z(alpha_prom=6.0))
    assert _run(index, 60, 10)["state"] == "stop"


def test_reserve_drains_with_work_and_recovers_on_break():
    cfg = dataclasses.replace(Config(), time_scale=3600.0)   # one real second is one shift hour
    index = VigilanceIndex(cfg)
    out = _run(index, 0, 4)
    assert out["reserve"] == pytest.approx(100.0 - 4 * cfg.drain_per_hour)
    assert out["state"] == "ok"
    assert _run(index, 4, 1)["state"] == "warn"              # below 50 after five hours
    index.start_break()
    out = _run(index, 5, 1)
    assert out["state"] == "break"
    assert out["reserve"] == pytest.approx(100.0 - 5 * cfg.drain_per_hour + cfg.recharge_per_hour)


def test_fatigue_trend_makes_the_reserve_drain_faster():
    cfg = dataclasses.replace(Config(), time_scale=60.0)
    rested, tired = VigilanceIndex(cfg), VigilanceIndex(cfg)
    a = _run(rested, 0, 120)
    b = _run(tired, 0, 120, _z(tab_ratio=2.0))
    assert b["reserve"] < a["reserve"]
    assert b["drain_per_hour"] == pytest.approx(cfg.drain_per_hour * 2.0)
    assert b["minutes_to_stop"] < a["minutes_to_stop"]


def test_mostly_bad_windows_mean_no_signal_instead_of_a_guess():
    index = VigilanceIndex(Config())
    _run(index, 0, 30)
    assert _run(index, 30, 30, bad=True)["state"] == "no_signal"
