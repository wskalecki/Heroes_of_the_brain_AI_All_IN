import numpy as np

from wachta.blinks import BlinkDetector
from wachta.config import Config

SFREQ = 250


def _frontal_noise(seconds, seed=0):
    rng = np.random.default_rng(seed)
    return rng.normal(0.0, 8.0, size=(8, int(seconds * SFREQ)))


def _add_blink(x, at_s, amplitude=-200.0, width_s=0.25):
    n = int(width_s * SFREQ)
    start = int(at_s * SFREQ)
    shape = amplitude * np.hanning(n)
    x[0:2, start : start + n] += shape


def _feed(detector, x):
    for start in range(0, x.shape[1], 125):
        detector.push(x[:, start : start + 125], start)


def test_blinks_after_calibration_are_found_at_the_right_time():
    x = _frontal_noise(60)
    times = [30.0, 34.0, 41.5, 50.0]
    for t in times:
        _add_blink(x, t)
    detector = BlinkDetector(Config())
    _feed(detector, x)
    assert detector.ready
    assert len(detector.blinks) == len(times)
    assert np.allclose(detector.blinks, times, atol=0.15)


def test_noise_and_occipital_alpha_are_not_blinks():
    x = _frontal_noise(60, seed=1)
    t = np.arange(x.shape[1]) / SFREQ
    x[0:2] += 25.0 * np.sin(2 * np.pi * 10.0 * t)     # frontal alpha leaking in
    detector = BlinkDetector(Config())
    _feed(detector, x)
    assert detector.blinks == []


def test_long_deflections_are_movement_not_blinks():
    x = _frontal_noise(60, seed=2)
    x[0:2, 30 * SFREQ : 32 * SFREQ] += 300.0          # 2 s step: head movement
    detector = BlinkDetector(Config())
    _feed(detector, x)
    assert detector.blinks == []


def test_rate_per_minute():
    x = _frontal_noise(90, seed=3)
    for t in range(30, 90, 5):
        _add_blink(x, float(t))
    detector = BlinkDetector(Config())
    _feed(detector, x)
    assert 10 <= detector.rate_per_min(90.0) <= 14
