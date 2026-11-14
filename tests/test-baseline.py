import numpy as np
import pytest

from wachta.baseline import Baseline


def test_baseline_becomes_ready_after_enough_windows():
    baseline = Baseline(("a",), n_windows=5)
    for i in range(4):
        baseline.add({"a": float(i)})
        assert not baseline.ready
    assert baseline.progress == pytest.approx(0.8)
    baseline.add({"a": 4.0})
    assert baseline.ready and baseline.progress == 1.0


def test_z_scores_are_centred_on_the_calibration_data():
    rng = np.random.default_rng(0)
    baseline = Baseline(("a", "b"), n_windows=200)
    for _ in range(200):
        baseline.add({"a": rng.normal(5.0, 2.0), "b": rng.normal(-1.0, 0.5)})
    z = baseline.z({"a": 5.0, "b": -1.0})
    assert abs(z["a"]) < 0.3 and abs(z["b"]) < 0.3
    assert baseline.z({"a": 9.0, "b": -1.0})["a"] == pytest.approx(2.0, abs=0.5)


def test_outliers_during_calibration_do_not_widen_the_baseline():
    baseline = Baseline(("a",), n_windows=50)
    for i in range(50):
        baseline.add({"a": 100.0 if i % 10 == 0 else (i % 5) * 0.1})
    assert baseline.z({"a": 2.0})["a"] > 5.0


def test_flat_calibration_signal_does_not_divide_by_zero():
    baseline = Baseline(("a",), n_windows=3)
    for _ in range(3):
        baseline.add({"a": 1.0})
    assert np.isfinite(baseline.z({"a": 2.0})["a"])


def test_z_before_calibration_is_an_error():
    with pytest.raises(RuntimeError):
        Baseline(("a",), n_windows=3).z({"a": 1.0})
