import numpy as np

from wachta.features import window_features

SFREQ = 250.0
N = 500


def _noise(rng, scale=10.0):
    return rng.normal(0.0, scale, size=(8, N))


def test_alpha_prominence_is_high_for_occipital_10_hz():
    rng = np.random.default_rng(0)
    window = _noise(rng)
    t = np.arange(N) / SFREQ
    window[6:8] += 30.0 * np.sin(2 * np.pi * 10.0 * t)
    assert window_features(window, SFREQ)["alpha_prom"] > 1.0


def test_alpha_prominence_is_near_zero_for_noise():
    rng = np.random.default_rng(1)
    values = [window_features(_noise(rng), SFREQ)["alpha_prom"] for _ in range(50)]
    assert abs(np.mean(values)) < 0.15


def test_broadband_power_does_not_look_like_alpha():
    rng = np.random.default_rng(2)
    quiet = window_features(_noise(rng, 5.0), SFREQ)
    loud = window_features(_noise(rng, 50.0), SFREQ)
    assert loud["alpha_occ"] > quiet["alpha_occ"] + 1.0
    assert abs(loud["alpha_prom"] - quiet["alpha_prom"]) < 1.0


def test_ptp_reports_the_largest_channel():
    window = np.zeros((8, N))
    window[3, 100] = 400.0
    assert window_features(window, SFREQ)["ptp_uv"] == 400.0
