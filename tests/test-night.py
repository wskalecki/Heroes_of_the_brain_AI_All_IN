from datetime import datetime, timedelta, timezone

import numpy as np

from wachta.night import analyze_signals, format_table, heart_from_frames, heart_per_block, rmssd, task_parts
from wachta.recordings import Block

SFREQ = 250


def _night_recording(seed=0):
    """eyes_open 60 s, eyes_closed 60 s, math 60 s, monotony 600 s with alpha growing while blinking."""
    rng = np.random.default_rng(seed)
    total = 840
    n = total * SFREQ
    t = np.arange(n) / SFREQ
    eeg = rng.normal(0.0, 10e-6, size=(8, n)) + 0.05
    blink = -200e-6 * np.hanning(int(0.25 * SFREQ))

    def blinks(start, end, every):
        for b in np.arange(start + 1, end - 1, every):
            i = int(b * SFREQ)
            eeg[0:2, i : i + blink.size] += blink

    blinks(0, 60, 3.0)
    closed = (t >= 60) & (t < 120)
    eeg[6:8, closed] += 30e-6 * np.sin(2 * np.pi * 10 * t[closed])
    blinks(120, 180, 3.0)
    mono = t >= 180
    ramp = np.clip((t[mono] - 180) / 600, 0, 1) ** 2
    eeg[6:8, mono] += 35e-6 * ramp * np.sin(2 * np.pi * 10 * t[mono])
    blinks(180, total, 4.0)
    blocks = [Block(0, 60, "eyes_open"), Block(60, 60, "eyes_closed"), Block(120, 60, "math"), Block(180, 600, "monotony")]
    return eeg, blocks


def test_alpha_rising_with_open_eyes_during_monotony():
    eeg, blocks = _night_recording()
    out = analyze_signals(eeg, blocks)
    assert out["eyes_closed_detected"] is True
    assert out["fast_late"] > out["fast_early"] + 2
    assert out["lapses_eyes_open"] >= 1 and out["lapses_eyes_closed"] == 0
    assert out["blinks_late"] > 5
    assert out["monotony_min"] == 10.0


def test_recording_without_monotony_is_skipped():
    eeg, blocks = _night_recording()
    assert analyze_signals(eeg[:, : 180 * SFREQ], blocks[:3]) is None


def test_task_parts():
    assert task_parts("wojtek-n1") == ("wojtek", "N1")
    assert task_parts("filip") is None


class _Frame:
    def __init__(self, name, **values):
        self.name = name
        self.values = values

    def get_value(self, key, fallback=None):
        return self.values.get(key, fallback)


def test_fit_frames_give_heart_rate_and_rr_and_rmssd_per_block():
    start = datetime(2026, 11, 15, 1, 0, tzinfo=timezone.utc)
    frames = [_Frame("record", timestamp=start + timedelta(seconds=s), heart_rate=60 + (s >= 60) * 10) for s in range(120)]
    # 60 beats summing to exactly 60 s, then a >20% jump (filtered as artefact) into the second block.
    rr = [(1.02 if i % 2 else 0.98) for i in range(60)] + [0.70, 0.69] * 40
    frames += [_Frame("hrv", time=tuple(rr[i : i + 5])) for i in range(0, len(rr), 5)]
    frames.append(_Frame("hrv", time=(65.535, None)))
    heart_rate, intervals = heart_from_frames(frames)
    assert len(heart_rate) == 120 and len(intervals) == len(rr)
    blocks = [Block(0, 60, "eyes_open"), Block(60, 60, "monotony")]
    per_block = heart_per_block(start, blocks, heart_rate, intervals)
    assert per_block["eyes_open"]["hr"] == 60 and per_block["monotony"]["hr"] == 70
    assert per_block["eyes_open"]["rmssd"] == 40.0
    assert per_block["monotony"]["rmssd"] == 10.0


def test_rmssd_drops_artefacts_and_needs_enough_beats():
    assert rmssd([800, 810] * 3) is None
    assert rmssd([800, 820] * 10 + [2500, 100]) == 20.0


def test_table_renders_without_heart_data():
    row = {"person": "wojtek", "checkpoint": "N1", "kss": 7, "pvt_lapses": 3, "median_rt_ms": 312.0,
           "fast_early": 0.1, "fast_late": 1.4, "fast_change": 1.3, "probes": 2,
           "lapses_eyes_open": 1, "lapses_eyes_closed": 0, "blinks_early": 14.0, "blinks_late": 9.0,
           "eyes_closed_detected": True}
    table = format_table([row])
    assert "| wojtek | N1 | 7 | 3 | 312 ms | 0,10 | 1,40 | +1,30 | 2 | 1 / 0 | 14 → 9 | — → — | — → — | tak |" in table


def test_minute_by_minute_course_of_monotony(tmp_path):
    from wachta.night import save_minutes_figure

    eeg, blocks = _night_recording()
    out = analyze_signals(eeg, blocks)
    minutes = out["minutes"]
    assert [m["minute"] for m in minutes] == list(range(1, 11))
    assert minutes[-1]["fast"] > minutes[0]["fast"] + 2
    assert any(m["lapse"] for m in minutes[-3:]) and not minutes[0]["lapse"]
    rows = [{"person": "wojtek", "checkpoint": "T1", **out, "hr_minutes": [60 + k for k in range(10)]}]
    assert save_minutes_figure(rows, tmp_path / "m.png").stat().st_size > 10_000


def test_heart_per_minute():
    from wachta.night import heart_per_minute

    start = datetime(2026, 11, 15, 1, 0, tzinfo=timezone.utc)
    hr = [(start + timedelta(seconds=s), 60.0 + s // 60) for s in range(180)]
    assert heart_per_minute(start, Block(60, 120, "monotony"), hr) == [61.0, 62.0]
