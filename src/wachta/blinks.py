"""Blink detection on the frontal channels, used as evidence that the eyes are open.

With the reference at Fp1 (BrainAccess MINI), a blink shows up as a short,
large deflection on F3/F4. A blink is a run of samples above a personal
threshold lasting 40-500 ms; longer runs are movement, not blinks.
The threshold is a multiple of the median absolute deviation of the frontal
signal during the first seconds of the stream.
"""

import numpy as np
from scipy.signal import butter, sosfilt, sosfilt_zi

from .config import FRONTAL, Config


class BlinkDetector:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.threshold: float | None = None
        self._calibration: list[np.ndarray] = []
        self._calibration_n = 0
        self._run_start: int | None = None
        self._run_peak = 0.0
        self._last_blink = -10**9
        self.blinks: list[float] = []     # blink times in seconds since stream start
        # Blinks carry most energy below 4 Hz; the low-pass keeps frontal alpha from looking like blinks.
        self._sos = butter(2, cfg.blink_lowpass_hz, "lowpass", fs=cfg.sfreq, output="sos")
        self._zi: np.ndarray | None = None

    @property
    def ready(self) -> bool:
        return self.threshold is not None

    def push(self, filtered_uv: np.ndarray, first_sample: int) -> list[float]:
        """Feed band-passed EEG (8, n) in µV whose first column is sample ``first_sample``."""
        cfg = self.cfg
        frontal = filtered_uv[list(FRONTAL)].mean(0)
        if frontal.size == 0:
            return []
        if self._zi is None:
            self._zi = sosfilt_zi(self._sos) * frontal[0]
        frontal, self._zi = sosfilt(self._sos, frontal, zi=self._zi)
        if not self.ready:
            start_skip = max(0, int(cfg.settle_s * cfg.sfreq) - first_sample)
            if start_skip < frontal.size:
                self._calibration.append(frontal[start_skip:])
                self._calibration_n += frontal.size - start_skip
            if self._calibration_n >= cfg.blink_cal_s * cfg.sfreq:
                x = np.concatenate(self._calibration)
                mad = np.median(np.abs(x - np.median(x)))
                self.threshold = max(cfg.blink_k * mad, cfg.blink_min_uv)
                self._calibration = []
            return []

        found = []
        above = np.abs(frontal) > self.threshold
        min_len = int(cfg.blink_min_s * cfg.sfreq)
        max_len = int(cfg.blink_max_s * cfg.sfreq)
        refractory = int(cfg.blink_refractory_s * cfg.sfreq)
        for i, flag in enumerate(above):
            sample = first_sample + i
            if flag and self._run_start is None:
                self._run_start = sample
            elif not flag and self._run_start is not None:
                length = sample - self._run_start
                if min_len <= length <= max_len and self._run_start - self._last_blink >= refractory:
                    self._last_blink = self._run_start
                    found.append(self._run_start / cfg.sfreq)
                self._run_start = None
        self.blinks.extend(found)
        if len(self.blinks) > 2000:
            del self.blinks[:1000]
        return found

    def last_blink(self) -> float | None:
        return self.blinks[-1] if self.blinks else None

    def rate_per_min(self, t: float, window_s: float = 60.0) -> float | None:
        if not self.ready:
            return None
        span = min(window_s, max(t - self.cfg.settle_s - self.cfg.blink_cal_s, 1.0))
        return sum(1 for b in self.blinks if t - window_s <= b <= t) * 60.0 / span
