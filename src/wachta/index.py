"""Vigilance index: lapse detection, eye state, reaction probes, reserve and state.

Signals that feed the state:

* fast: z-score of alpha prominence over the occipital channels. A sustained
  rise is an acute event: eyes closing or an alpha wave right now. It detects,
  it does not predict (notebook 06: alpha with open eyes does not forecast lapses).
  Lapses closer than ``lapse_merge_s`` are one event (issue #11).
* eye state: blinks on the frontal channels (``blinks.py``). A lapse without
  blinks is "eyes closed" (what a driver camera also sees); a lapse while the
  person keeps blinking is labelled "eyes open".
* reaction probes (issue #14): after each acute event and on a schedule. A missing
  response or one slower than the personal norm (1.5 x own median, PVT-B 355 ms
  until enough responses) is a failed probe.
* slow: one-minute mean of the z-scored (theta + alpha) / beta ratio. It only
  changes how fast the reserve drains.
* context: hours awake and time of day (simplified two-process model). Also
  only changes the drain rate.

The reserve and context parameters are assumptions, not fitted values
(see ``config.Config``).
"""

import math
from collections import deque

from .config import Config

STATES = ("calibrating", "no_signal", "break", "ok", "warn", "stop")


def _circular_bump(hour: float, centre: float, width: float) -> float:
    distance = abs((hour - centre + 12.0) % 24.0 - 12.0)
    return math.exp(-0.5 * (distance / width) ** 2)


class VigilanceIndex:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.reserve = 100.0
        self.on_break = False
        self.work_s = 0.0          # shift seconds worked since calibration
        self.shift_s = 0.0         # shift seconds since calibration, breaks included
        self.lapse_count = 0
        self.lapse_kinds = {"eyes_closed": 0, "eyes_open": 0, "unknown": 0}
        self.probes_done = 0
        self.probe_lapses = 0
        self.last_rt_ms: float | None = None
        self._passed_rts: list[float] = []
        self._probe_requested = False
        self._probe_reason: str | None = None
        self._last_probe_t = -math.inf
        self._next_scheduled_t: float | None = None
        self._failed_probe_t = -math.inf
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
        self.lapse_kind: str | None = None
        self._lapse_t0 = 0.0
        self._counted_kind: str | None = None
        self._last_lapse_end = -math.inf
        self._event_probe_pending = False

    def start_break(self) -> None:
        """Rest is not work: eyes closed during a break is neither an event nor a penalty."""
        self.on_break = True
        self.lapse = False
        self.lapse_kind = None
        self._above = self._below = 0
        self._event_probe_pending = False
        self._probe_requested = False

    def end_break(self) -> None:
        self.on_break = False

    def request_probe(self) -> None:
        """Ask for a reaction probe at the next window (manual check)."""
        self._probe_requested = True

    def probe_threshold_ms(self) -> float:
        """Reaction time above which a probe fails: personal norm once known, else the PVT-B lapse."""
        cfg = self.cfg
        if len(self._passed_rts) < cfg.probe_norm_min:
            return cfg.probe_lapse_ms
        rts = sorted(self._passed_rts)
        mid = len(rts) // 2
        median = rts[mid] if len(rts) % 2 else 0.5 * (rts[mid - 1] + rts[mid])
        return cfg.probe_norm_factor * median

    def record_probe(self, t: float, rt_ms: float | None) -> bool:
        """Store a probe result; returns True when the probe failed.

        A reaction that is not a number, negative or faster than ``probe_min_rt_ms`` is a false start or bad
        input: it is not counted at all, neither as a pass nor as a lapse.
        """
        cfg = self.cfg
        if rt_ms is not None and not (math.isfinite(rt_ms) and rt_ms >= cfg.probe_min_rt_ms):
            return False
        threshold = self.probe_threshold_ms()
        self.probes_done += 1
        self.last_rt_ms = rt_ms
        failed = rt_ms is None or rt_ms > threshold
        if failed:
            self.probe_lapses += 1
            self.reserve = max(0.0, self.reserve - cfg.lapse_penalty)
            self._lapse_starts.append(t)
            self._failed_probe_t = t
        else:
            self._passed_rts.append(float(rt_ms))
            self._failed_probe_t = -math.inf        # a passed probe clears the stop
        return failed

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
        """Hysteresis on the fast index. Returns True when a new acute event starts.

        A lapse that starts within ``lapse_merge_s`` of the previous one continues that
        event: no new count, no new penalty, no new probe.
        """
        cfg = self.cfg
        if math.isnan(fast):
            self._above = 0
            return False
        self._above = self._above + 1 if fast > cfg.z_enter else 0
        self._below = self._below + 1 if fast < cfg.z_exit else 0
        if not self.lapse and self._above * cfg.step_s >= cfg.lapse_min_s:
            self.lapse = True
            if t - self._last_lapse_end < cfg.lapse_merge_s:
                return False
            self.lapse_count += 1
            self._lapse_t0 = t
            self._lapse_starts.append(t)
            self._counted_kind = None
            self._event_probe_pending = True
            return True
        if self.lapse and self._below * cfg.step_s >= cfg.lapse_exit_s:
            self.lapse = False
            self._last_lapse_end = t
        return False

    def _eye_state(self, t: float, last_blink: float | None, blinks_ready: bool) -> str | None:
        if not blinks_ready:
            return None
        if last_blink is None or t - last_blink >= self.cfg.eyes_closed_after_s:
            return "closed"
        return "open"

    def _classify_lapse(self, t: float, last_blink: float | None, blinks_ready: bool) -> str:
        """Eyes closed if there was no blink since shortly before the lapse began."""
        if not blinks_ready:
            return "unknown"
        since = self._lapse_t0 - self.cfg.lapse_blink_lookback_s
        return "eyes_open" if last_blink is not None and last_blink >= since else "eyes_closed"

    def _context(self) -> tuple[float, float | None, float | None]:
        """Drain multiplier from hours awake and time of day, plus the two values."""
        cfg = self.cfg
        if cfg.start_clock_h is None:
            return 1.0, None, None
        clock = (cfg.start_clock_h + self.shift_s / 3600.0) % 24.0
        factor = (1.0 + cfg.circadian_night_gain * _circular_bump(clock, cfg.circadian_night_h, cfg.circadian_night_width_h)
                  + cfg.circadian_dip_gain * _circular_bump(clock, cfg.circadian_dip_h, cfg.circadian_dip_width_h))
        awake = None
        if cfg.awake_at_start_h is not None:
            awake = cfg.awake_at_start_h + self.shift_s / 3600.0
            factor *= 1.0 + cfg.awake_gain_per_h * max(0.0, awake - cfg.awake_free_h)
        return factor, clock, awake

    # -- main entry point ------------------------------------------------

    def update(
        self,
        t: float,
        z: dict[str, float] | None,
        bad: bool,
        calibrated: bool,
        last_blink: float | None = None,
        blinks_ready: bool = False,
    ) -> dict:
        """Advance by one window.

        ``t`` is the window end in real seconds since the stream started,
        ``z`` holds the z-scored features of a clean, calibrated window (else None),
        ``last_blink`` is the time of the most recent blink in the same clock.
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

        if self.on_break:
            self._above = self._below = 0          # no events while resting
        new_lapse = self._update_lapse(t, fast) if calibrated and not self.on_break else False
        if self.lapse:
            self.lapse_kind = self._classify_lapse(t, last_blink, blinks_ready)
            # Count each event once, by the kind it settles on after the confirmation period.
            if self._counted_kind is None and t - self._lapse_t0 >= cfg.lapse_kind_settle_s:
                self._counted_kind = self.lapse_kind
                self.lapse_kinds[self.lapse_kind] += 1
        else:
            if self._counted_kind is None and self.lapse_kind is not None:
                self._counted_kind = self.lapse_kind
                self.lapse_kinds[self.lapse_kind] += 1
            self.lapse_kind = None

        # Reaction probe: right after an acute event ends, on the schedule, or on request.
        probe, probe_reason = False, None
        if calibrated and self._next_scheduled_t is None:
            self._next_scheduled_t = t + cfg.probe_interval_s
        if calibrated and not self.on_break and quality >= cfg.quality_min and not self.lapse:
            cooled = t - self._last_probe_t >= cfg.probe_cooldown_s
            if self._probe_requested:
                probe_reason = "manual"
            elif self._event_probe_pending and cooled and t - self._last_lapse_end >= cfg.probe_event_delay_s:
                probe_reason = "event"
            elif self._next_scheduled_t is not None and t >= self._next_scheduled_t and cooled:
                probe_reason = "schedule"
            if probe_reason is not None:
                probe = True
                self._probe_requested = False
                self._event_probe_pending = False
                self._last_probe_t = t
                self._next_scheduled_t = t + cfg.probe_interval_s

        while self._lapse_starts and self._lapse_starts[0] < t - cfg.recent_lapse_s:
            self._lapse_starts.popleft()
        recent = len(self._lapse_starts)

        context, clock, awake = self._context()
        rate = cfg.drain_per_hour * context * (1.0 + cfg.slow_gain * min(max(slow, 0.0), cfg.slow_cap))
        if calibrated:
            shift_dt = cfg.step_s * cfg.time_scale
            self.shift_s += shift_dt
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
        elif self.lapse or self.reserve < cfg.stop_below or t - self._failed_probe_t < cfg.probe_stop_s:
            # "Stop" means now: a lapse in progress, an exhausted reserve or a failed reaction probe.
            state = "stop"
        elif self.reserve < cfg.warn_below or recent >= 1:
            # Recent events lower the reserve and raise attention, but do not hold "stop" (issue #11).
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
            "lapse_kind": self.lapse_kind,
            "new_lapse": new_lapse,
            "lapses_recent": recent,
            "lapse_count": self.lapse_count,
            "lapses_eyes_closed": self.lapse_kinds["eyes_closed"],
            "lapses_eyes_open": self.lapse_kinds["eyes_open"],
            # During a lapse the eye state follows the lapse kind, so the banner and the tile agree.
            "eye_state": {"eyes_closed": "closed", "eyes_open": "open"}.get(
                self.lapse_kind, self._eye_state(t, last_blink, blinks_ready)
            ),
            "probe": probe,
            "probe_reason": probe_reason,
            "probe_threshold_ms": round(self.probe_threshold_ms(), 1),
            "probe_failed_recently": t - self._failed_probe_t < cfg.probe_stop_s,
            "probes_done": self.probes_done,
            "probe_lapses": self.probe_lapses,
            "last_rt_ms": self.last_rt_ms,
            "quality": round(quality, 3),
            "drain_per_hour": round(rate, 2),
            "context_factor": round(context, 3),
            "clock_h": None if clock is None else round(clock, 3),
            "awake_h": None if awake is None else round(awake, 2),
            "minutes_to_warn": minutes_to(cfg.warn_below),
            "minutes_to_stop": minutes_to(cfg.stop_below),
            "work_min": round(self.work_s / 60.0, 2),
            "on_break": self.on_break,
        }
