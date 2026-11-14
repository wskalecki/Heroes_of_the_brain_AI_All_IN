"""Vigilance index: lapse detection, fatigue trend, reserve and state.

Two signals feed the state:

* fast: z-score of alpha prominence over the occipital channels. A sustained
  rise means the eyes are closing or alpha bursts appear, i.e. a vigilance lapse.
* slow: one-minute mean of the z-scored (theta + alpha) / beta ratio, a fatigue
  marker from the literature. It only changes how fast the reserve drains.

The reserve is a simple, explicit model (see ``config.Config``); its parameters
are assumptions, not fitted values.
"""

import math
from collections import deque

from .config import Config

STATES = ("calibrating", "no_signal", "break", "ok", "warn", "stop")


class VigilanceIndex:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.reserve = 100.0
        self.on_break = False
        self.work_s = 0.0          # shift seconds worked since calibration
        self.lapse_count = 0
        self.reset_detection()

    def reset_detection(self) -> None:
        """Forget signal history (used on recalibration); reserve and shift time stay."""
        self._fast_hist: deque[float] = deque(maxlen=self.cfg.smooth_windows)
        self._slow_hist: deque[tuple[float, float]] = deque()
        self._quality_hist: deque[tuple[float, bool]] = deque()
        self._lapse_starts: deque[float] = deque()
        self._above = 0
        self._below = 0
        self.lapse = False

    def start_break(self) -> None:
        self.on_break = True

    def end_break(self) -> None:
        self.on_break = False

    # -- helpers ---------------------------------------------------------

    def _fast(self) -> float:
        valid = sorted(v for v in self._fast_hist if not math.isnan(v))
        if len(valid) < (self.cfg.smooth_windows + 1) // 2:
            return math.nan
        mid = len(valid) // 2
        return valid[mid] if len(valid) % 2 else 0.5 * (valid[mid - 1] + valid[mid])

    def _slow(self, t: float) -> float:
        while self._slow_hist and self._slow_hist[0][0] < t - self.cfg.slow_window_s:
            self._slow_hist.popleft()
        if len(self._slow_hist) < 10:
            return 0.0
        return sum(v for _, v in self._slow_hist) / len(self._slow_hist)

    def _quality(self, t: float) -> float:
        while self._quality_hist and self._quality_hist[0][0] < t - self.cfg.quality_window_s:
            self._quality_hist.popleft()
        if not self._quality_hist:
            return 0.0
        return sum(1 for _, clean in self._quality_hist if clean) / len(self._quality_hist)

    def _update_lapse(self, t: float, fast: float) -> bool:
        """Hysteresis on the fast index. Returns True when a new lapse starts."""
        cfg = self.cfg
        if math.isnan(fast):
            self._above = 0
            return False
        self._above = self._above + 1 if fast > cfg.z_enter else 0
        self._below = self._below + 1 if fast < cfg.z_exit else 0
        if not self.lapse and self._above * cfg.step_s >= cfg.lapse_min_s:
            self.lapse = True
            self.lapse_count += 1
            self._lapse_starts.append(t)
            return True
        if self.lapse and self._below * cfg.step_s >= cfg.lapse_exit_s:
            self.lapse = False
        return False

    # -- main entry point ------------------------------------------------

    def update(self, t: float, z: dict[str, float] | None, bad: bool, calibrated: bool) -> dict:
        """Advance by one window.

        ``t`` is the window end in real seconds since the stream started,
        ``z`` holds the z-scored features of a clean, calibrated window (else None).
        """
        cfg = self.cfg
        self._quality_hist.append((t, not bad))
        quality = self._quality(t)

        if z is not None:
            self._fast_hist.append(z["alpha_prom"])
            self._slow_hist.append((t, z["tab_ratio"]))
        else:
            self._fast_hist.append(math.nan)
        fast = self._fast()
        slow = self._slow(t)

        new_lapse = self._update_lapse(t, fast) if calibrated else False
        while self._lapse_starts and self._lapse_starts[0] < t - cfg.recent_lapse_s:
            self._lapse_starts.popleft()
        recent = len(self._lapse_starts)

        rate = cfg.drain_per_hour * (1.0 + cfg.slow_gain * min(max(slow, 0.0), cfg.slow_cap))
        if calibrated:
            shift_dt = cfg.step_s * cfg.time_scale
            if self.on_break:
                self.reserve += cfg.recharge_per_hour * shift_dt / 3600.0
            else:
                self.reserve -= rate * shift_dt / 3600.0
                self.work_s += shift_dt
            if new_lapse:
                self.reserve -= cfg.lapse_penalty
            self.reserve = min(100.0, max(0.0, self.reserve))

        if not calibrated:
            state = "calibrating"
        elif quality < cfg.quality_min:
            state = "no_signal"
        elif self.on_break:
            state = "break"
        elif self.lapse or self.reserve < cfg.stop_below or recent >= 2:
            state = "stop"
        elif self.reserve < cfg.warn_below or recent >= 1:
            state = "warn"
        else:
            state = "ok"

        def minutes_to(level: float) -> float | None:
            if self.on_break or not calibrated or self.reserve <= level:
                return None
            return (self.reserve - level) / rate * 60.0

        return {
            "state": state,
            "reserve": round(self.reserve, 2),
            "fast": None if math.isnan(fast) else round(fast, 3),
            "slow": round(slow, 3),
            "lapse": self.lapse,
            "new_lapse": new_lapse,
            "lapses_recent": recent,
            "lapse_count": self.lapse_count,
            "quality": round(quality, 3),
            "drain_per_hour": round(rate, 2),
            "minutes_to_warn": minutes_to(cfg.warn_below),
            "minutes_to_stop": minutes_to(cfg.stop_below),
            "work_min": round(self.work_s / 60.0, 2),
            "on_break": self.on_break,
        }
