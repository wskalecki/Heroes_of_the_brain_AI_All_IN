"""Spectral features of one EEG window.

The feature definitions come from the notebooks in ``data/analysis/``:
band power per region (notebook 03) and alpha prominence, i.e. alpha power
relative to its spectral neighbours (notebook 01).
"""

import numpy as np
from scipy.signal import welch

from .config import BANDS, FRONTAL, OCCIPITAL, PARIETAL

_EPS = 1e-12


def _band_power(psd: np.ndarray, freqs: np.ndarray, lo: float, hi: float) -> np.ndarray:
    """Integrated power in [lo, hi] Hz for each channel, in µV²."""
    mask = (freqs >= lo) & (freqs <= hi)
    return psd[..., mask].sum(-1) * (freqs[1] - freqs[0])


def _band_mean(psd: np.ndarray, freqs: np.ndarray, lo: float, hi: float) -> float:
    mask = (freqs >= lo) & (freqs <= hi)
    return float(psd[..., mask].mean())


def window_features(window_uv: np.ndarray, sfreq: float) -> dict[str, float]:
    """Compute features for one window.

    Parameters
    ----------
    window_uv : array, shape (8, n_samples)
        Band-pass filtered EEG in microvolts, channels ordered as ``config.CHANNELS``.
    sfreq : float
        Sampling rate in Hz.
    """
    n = window_uv.shape[-1]
    freqs, psd = welch(window_uv, sfreq, nperseg=n, axis=-1)
    power = {name: _band_power(psd, freqs, lo, hi) for name, (lo, hi) in BANDS.items()}

    occ = psd[list(OCCIPITAL)].mean(0)
    neighbours = np.sqrt(_band_mean(occ, freqs, 5, 7) * _band_mean(occ, freqs, 14, 16))
    alpha_prom = np.log10((_band_mean(occ, freqs, 8, 12) + _EPS) / (neighbours + _EPS))

    slow_waves = power["theta"].mean() + power["alpha"].mean()
    return {
        "alpha_prom": float(alpha_prom),
        "alpha_occ": float(np.log10(power["alpha"][list(OCCIPITAL)].mean() + _EPS)),
        "theta_front": float(np.log10(power["theta"][list(FRONTAL)].mean() + _EPS)),
        "alpha_par": float(np.log10(power["alpha"][list(PARIETAL)].mean() + _EPS)),
        "tab_ratio": float(np.log10((slow_waves + _EPS) / (power["beta"].mean() + _EPS))),
        "ptp_uv": float(np.ptp(window_uv, axis=-1).max()),
    }
