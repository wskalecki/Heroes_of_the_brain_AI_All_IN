"""Shared constants and tunable parameters.

Window sizes and thresholds follow the team's analysis notebooks in
``data/analysis/``. The reserve parameters are assumptions for the demo,
anchored to the EU driving-time rule (4.5 h of driving, then a 45 min break);
they are not fitted to data.
"""

from dataclasses import dataclass

CHANNELS = ("F3", "F4", "C3", "C4", "P3", "P4", "O1", "O2")
FRONTAL = (0, 1)
PARIETAL = (4, 5)
OCCIPITAL = (6, 7)

BANDS = {"theta": (4.0, 7.0), "alpha": (8.0, 12.0), "beta": (13.0, 30.0)}

# Features that get a calibration baseline and a z-score.
Z_FEATURES = ("alpha_prom", "alpha_occ", "theta_front", "alpha_par", "tab_ratio")


@dataclass(frozen=True)
class Config:
    # Signal
    sfreq: float = 250.0
    win_s: float = 2.0
    step_s: float = 1.0
    highpass_hz: float = 1.0
    lowpass_hz: float = 40.0
    line_hz: float = 50.0
    settle_s: float = 3.0          # windows ending before this are ignored (filter warm-up)
    reject_uv: float = 300.0       # peak-to-peak above this on any channel marks the window as bad

    # Calibration
    cal_windows: int = 60          # first clean windows used as the personal baseline

    # Fast index: vigilance lapses (eyes closing, alpha bursts)
    smooth_windows: int = 5
    # 2.5 was chosen on the four annotated team recordings: all eyes-closed blocks are
    # still detected, with one false alarm in total instead of six at 2.0.
    z_enter: float = 2.5
    z_exit: float = 1.0
    lapse_min_s: float = 3.0
    lapse_exit_s: float = 2.0
    recent_lapse_s: float = 120.0  # a lapse keeps the state at "warn" for this long (real seconds)

    # Eye state from blinks on F3/F4 (A7)
    blink_cal_s: float = 20.0      # seconds of signal used for the blink threshold
    blink_k: float = 5.0           # threshold = k * MAD of the frontal signal
    blink_lowpass_hz: float = 4.0
    blink_min_uv: float = 20.0
    blink_min_s: float = 0.04
    blink_max_s: float = 0.5
    blink_refractory_s: float = 0.3
    eyes_closed_after_s: float = 10.0  # no blink for this long: eyes probably closed
    lapse_blink_lookback_s: float = 2.0  # a blink this soon before the lapse or later: eyes open
    lapse_kind_settle_s: float = 5.0     # count the lapse by the kind it has after this long

    # Reaction probes (A8). Lapse threshold as in PVT-B (Basner et al. 2011).
    probe_z: float = 1.5           # the fast index above this, but below z_enter ...
    probe_min_s: float = 2.0       # ... for this long triggers a probe
    probe_cooldown_s: float = 45.0
    probe_lapse_ms: float = 355.0
    probe_timeout_ms: float = 3000.0

    # Slow index: fatigue trend
    slow_window_s: float = 60.0

    # Signal quality
    quality_window_s: float = 30.0
    quality_min: float = 0.5

    # Reserve (assumptions, see module docstring)
    time_scale: float = 1.0        # shift seconds per real second (demo time compression)
    drain_per_hour: float = 12.0   # baseline: 100 -> 46 after 4.5 h of work
    slow_gain: float = 0.5         # extra drain per sigma of the slow index
    slow_cap: float = 3.0
    lapse_penalty: float = 8.0     # reserve points lost per lapse
    recharge_per_hour: float = 60.0  # a 45 min break restores 45 points
    warn_below: float = 50.0
    stop_below: float = 25.0

    # Context (A9): simplified two-process model, assumptions. Off unless start_clock_h is set.
    start_clock_h: float | None = None     # time of day at calibration, in hours
    awake_at_start_h: float | None = None  # hours awake at calibration
    circadian_night_gain: float = 0.6      # drain +60% around the circadian low ...
    circadian_night_h: float = 4.5         # ... centred at 04:30
    circadian_night_width_h: float = 2.5
    circadian_dip_gain: float = 0.2        # post-lunch dip
    circadian_dip_h: float = 15.0
    circadian_dip_width_h: float = 1.5
    awake_gain_per_h: float = 0.06         # +6% drain per hour awake beyond awake_free_h
    awake_free_h: float = 8.0

    @property
    def win_samples(self) -> int:
        return int(round(self.win_s * self.sfreq))

    @property
    def step_samples(self) -> int:
        return int(round(self.step_s * self.sfreq))
