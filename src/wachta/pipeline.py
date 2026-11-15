"""Streaming pipeline: raw EEG chunks in, one result per one-second step out.

The same code runs on live data and on recordings, so offline accuracy numbers
describe what the demo actually does.
"""

import numpy as np
from scipy.signal import butter, iirnotch, sosfilt, sosfilt_zi, tf2sos

from .baseline import Baseline
from .blinks import BlinkDetector
from .config import CHANNELS, Z_FEATURES, Config
from .features import window_features
from .index import VigilanceIndex


class StreamFilter:
    """Causal 1-40 Hz band-pass with a mains notch, applied chunk by chunk.

    Dry electrodes drift by tens of millivolts, so the filter state starts at
    the steady state for the first sample to avoid a start-up transient.
    """

    def __init__(self, cfg: Config) -> None:
        highpass = butter(4, cfg.highpass_hz, "highpass", fs=cfg.sfreq, output="sos")
        lowpass = butter(8, cfg.lowpass_hz, "lowpass", fs=cfg.sfreq, output="sos")
        notch = tf2sos(*iirnotch(cfg.line_hz, 30.0, fs=cfg.sfreq))
        self._sos = np.vstack([highpass, lowpass, notch])
        self._zi: np.ndarray | None = None

    def __call__(self, chunk: np.ndarray) -> np.ndarray:
        if chunk.shape[1] == 0:
            return chunk
        if self._zi is None:
            self._zi = sosfilt_zi(self._sos)[:, None, :] * chunk[None, :, :1]
        out, self._zi = sosfilt(self._sos, chunk, axis=-1, zi=self._zi)
        return out


class Pipeline:
    """Turns a stream of raw EEG into features, z-scores, state and reserve."""

    def __init__(self, cfg: Config | None = None) -> None:
        self.cfg = cfg or Config()
        self.index = VigilanceIndex(self.cfg)
        self._filter = StreamFilter(self.cfg)
        self._buffer = np.zeros((len(CHANNELS), 0))
        self._consumed = 0
        self._pushed = 0
        self.blinks = BlinkDetector(self.cfg)
        self.baseline = Baseline(Z_FEATURES, self.cfg.cal_windows)
        self._bad_before = 0       # windows starting before this sample are not trusted (stream glitch, filter restart)

    def reset_stream(self) -> None:
        """Restart the filters after a gap or corrupt samples; windows touching the restart are marked bad."""
        self._filter = StreamFilter(self.cfg)
        self.blinks.reset_filter()
        self._bad_before = self._pushed + int(round(self.cfg.settle_s * self.cfg.sfreq))

    def new_shift(self) -> None:
        """Start a new shift for the same, already calibrated person: full reserve, clock back to start."""
        self.index = VigilanceIndex(self.cfg)

    def recalibrate(self) -> None:
        """Start a new personal baseline from the next clean windows."""
        self.baseline = Baseline(Z_FEATURES, self.cfg.cal_windows)
        self.index.reset_detection()

    def push(self, eeg_volts: np.ndarray) -> list[dict]:
        """Feed raw samples, shape (8, n) in volts; returns the windows completed by them."""
        chunk = np.asarray(eeg_volts, dtype=float) * 1e6
        if chunk.ndim != 2 or chunk.shape[0] != len(CHANNELS):
            raise ValueError(f"Expected shape ({len(CHANNELS)}, n), got {chunk.shape}")
        corrupt = not np.isfinite(chunk).all()
        if corrupt:
            # NaN or Inf would poison the filter state for good, so zero them and restart the filters afterwards.
            chunk = np.nan_to_num(chunk, nan=0.0, posinf=0.0, neginf=0.0)
        filtered = self._filter(chunk)
        self.blinks.push(filtered, self._pushed)
        self._pushed += filtered.shape[1]
        self._buffer = np.concatenate([self._buffer, filtered], axis=1)
        if corrupt:
            self.reset_stream()

        cfg = self.cfg
        results = []
        while self._buffer.shape[1] >= cfg.win_samples:
            t_end = (self._consumed + cfg.win_samples) / cfg.sfreq
            if t_end >= cfg.settle_s:
                results.append(self._process(self._buffer[:, : cfg.win_samples], t_end, untrusted=self._consumed < self._bad_before))
            self._buffer = self._buffer[:, cfg.step_samples :]
            self._consumed += cfg.step_samples
        return results

    def _process(self, window: np.ndarray, t_end: float, untrusted: bool = False) -> dict:
        features = window_features(window, self.cfg.sfreq)
        ptp = features["ptp_uv"]
        # Too large (movement), too flat (headset off, frozen stream), not a number, or right after a stream glitch.
        bad = untrusted or not np.isfinite(ptp) or ptp > self.cfg.reject_uv or ptp < self.cfg.flat_uv
        if not bad:
            self.baseline.add(features)
        calibrated = self.baseline.ready
        z = self.baseline.z(features) if calibrated and not bad else None
        result = {
            "t": round(t_end, 3),
            "bad": bool(bad),
            "calibrated": calibrated,
            "calibration": round(self.baseline.progress, 3),
            "features": {k: round(v, 4) for k, v in features.items()},
            "z": None if z is None else {k: round(v, 3) for k, v in z.items()},
        }
        result.update(self.index.update(
            t_end, z, bool(bad), calibrated,
            last_blink=self.blinks.last_blink(), blinks_ready=self.blinks.ready,
        ))
        rate = self.blinks.rate_per_min(t_end)
        result["blinks_per_min"] = None if rate is None else round(rate, 1)
        return result


def run_offline(eeg_volts: np.ndarray, cfg: Config | None = None) -> list[dict]:
    """Run a whole recording through the pipeline, one second at a time."""
    pipeline = Pipeline(cfg)
    step = pipeline.cfg.step_samples
    results: list[dict] = []
    for start in range(0, eeg_volts.shape[1], step):
        results.extend(pipeline.push(eeg_volts[:, start : start + step]))
    return results
