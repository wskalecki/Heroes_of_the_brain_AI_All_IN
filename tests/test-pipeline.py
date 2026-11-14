import numpy as np
import pytest

from wachta.pipeline import Pipeline, run_offline
from wachta.recordings import find_recordings, load_annotations, load_eeg

SFREQ = 250


def _synthetic(seconds, alpha_from=None, alpha_to=None, seed=0):
    """Noise in volts with a 50 mV offset; optional 10 Hz burst on O1/O2."""
    rng = np.random.default_rng(seed)
    n = seconds * SFREQ
    eeg = rng.normal(0.0, 10e-6, size=(8, n)) + 0.05
    if alpha_from is not None:
        t = np.arange(n) / SFREQ
        burst = (t >= alpha_from) & (t < alpha_to)
        eeg[6:8, burst] += 30e-6 * np.sin(2 * np.pi * 10.0 * t[burst])
    return eeg


def test_alpha_burst_after_calibration_is_detected_as_one_lapse():
    results = run_offline(_synthetic(120, alpha_from=90, alpha_to=105))
    starts = [r["t"] for r in results if r["new_lapse"]]
    assert len(starts) == 1
    assert 92 <= starts[0] <= 100
    assert all(r["state"] != "stop" for r in results if r["t"] < 90)


def test_plain_noise_gives_no_lapse_and_a_clean_signal():
    results = run_offline(_synthetic(180, seed=3))
    assert not any(r["new_lapse"] for r in results)
    assert results[-1]["state"] == "ok"
    assert results[-1]["quality"] == 1.0


def test_calibration_takes_about_a_minute():
    results = run_offline(_synthetic(90))
    ready_at = next(r["t"] for r in results if r["calibrated"])
    assert 60 <= ready_at <= 66


def test_large_artifact_marks_windows_as_bad():
    eeg = _synthetic(90)
    eeg[2, 70 * SFREQ : 71 * SFREQ] += 500e-6
    bad_times = [r["t"] for r in run_offline(eeg) if r["bad"]]
    assert bad_times and all(69 <= t <= 75 for t in bad_times)


def test_chunk_size_does_not_change_the_result():
    eeg = _synthetic(80, seed=5)
    whole = run_offline(eeg)
    pipeline, pieces = Pipeline(), []
    for start in range(0, eeg.shape[1], 37):
        pieces.extend(pipeline.push(eeg[:, start : start + 37]))
    assert [r["t"] for r in pieces] == [r["t"] for r in whole]
    assert pieces[-1]["features"]["alpha_prom"] == pytest.approx(whole[-1]["features"]["alpha_prom"], abs=1e-6)


def test_wrong_channel_count_is_rejected():
    with pytest.raises(ValueError):
        Pipeline().push(np.zeros((4, 100)))


@pytest.mark.parametrize("name", ["adi", "filip", "rudy", "wojtek"])
def test_eyes_closed_block_is_detected_in_team_recordings(name):
    recordings = find_recordings()
    if name not in recordings:
        pytest.skip("team recordings are not available")
    eeg, _ = load_eeg(recordings[name])
    block = next(b for b in load_annotations(recordings[name]) if b.label == "eyes_closed")
    starts = [r["t"] for r in run_offline(eeg) if r["new_lapse"]]
    assert any(block.onset <= t <= block.end for t in starts)


def test_new_shift_keeps_calibration_and_restores_the_reserve():
    import dataclasses

    from wachta.config import Config

    cfg = dataclasses.replace(Config(), time_scale=3600.0)
    pipeline = Pipeline(cfg)
    eeg = _synthetic(70)
    results = []
    for start in range(0, eeg.shape[1], 250):
        results.extend(pipeline.push(eeg[:, start : start + 250]))
    last = results[-1]
    assert last["calibrated"] and last["reserve"] < 100
    pipeline.new_shift()
    result = pipeline.push(_synthetic(1, seed=9))[-1]
    assert result["calibrated"] and result["state"] != "calibrating"
    assert result["reserve"] == pytest.approx(100 - cfg.drain_per_hour)   # one window = one shift hour
    assert result["work_min"] == pytest.approx(60)
