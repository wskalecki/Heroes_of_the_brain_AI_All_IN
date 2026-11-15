import asyncio
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from wachta.config import Config
from wachta.server import CLIENT_FIELDS, Worker, create_app
from wachta.sources import ReplaySource

SFREQ = 250.0


def _noise(seconds, seed=0):
    rng = np.random.default_rng(seed)
    return rng.normal(0.0, 10e-6, size=(8, int(seconds * SFREQ))) + 0.05


def test_replay_source_yields_eight_channel_chunks_and_loops():
    source = ReplaySource(_noise(2), SFREQ, speed=1000.0, chunk_s=0.5)

    async def take(n):
        out = []
        async for chunk in source.chunks():
            out.append(chunk)
            if len(out) == n:
                break
        return out

    chunks = asyncio.run(take(6))
    assert all(c.shape == (8, 125) for c in chunks)
    assert np.array_equal(chunks[0], chunks[4])      # 2 s of data in 0.5 s chunks, then it loops


def test_replay_source_without_loop_stops_at_the_end():
    source = ReplaySource(_noise(1), SFREQ, speed=1000.0, chunk_s=0.5, loop=False)

    async def count():
        return sum([1 async for _ in source.chunks()])

    assert asyncio.run(count()) == 2


def test_replay_segment_loops_inside_its_bounds():
    eeg = np.tile(np.arange(10, dtype=float), (8, 1)) * 1e-3          # 10 samples, value = index (SFREQ 1 Hz here)
    source = ReplaySource(eeg, 1.0, speed=1000.0, chunk_s=1.0, start_s=2.0, end_s=5.0)

    async def take(n):
        out = []
        async for chunk in source.chunks():
            out.append(float(chunk[0, 0] * 1e3))
            if len(out) == n:
                break
        return out

    assert asyncio.run(take(8)) == [2, 3, 4, 2, 3, 4, 2, 3]
    with pytest.raises(ValueError):
        ReplaySource(eeg, 1.0, start_s=5.0, end_s=5.0)


def test_team_spec_accepts_a_segment_and_hyphenated_recording_names(monkeypatch):
    from wachta import server

    seen = {}

    class Spy:
        @classmethod
        def from_file(cls, path, **kwargs):
            seen.update(kwargs, path=path)
            return ReplaySource(_noise(1), SFREQ, name=kwargs["name"])

    monkeypatch.setattr(server, "ReplaySource", Spy)
    monkeypatch.setattr(server, "resolve_recording", lambda name: Path(f"x/task-{name}_run.fif"))
    server._replay_worker("w1", "wojtek-t1:380-520", Config(), 1.0, 0.0)
    assert seen["start_s"] == 380.0 and seen["end_s"] == 520.0 and str(seen["path"]).endswith("task-wojtek-t1_run.fif")
    server._replay_worker("w1", "rudy", Config(), 1.0, 7.0)
    assert seen["start_s"] == 7.0 and seen["end_s"] is None


def _app(seconds=80):
    cfg = Config()
    worker = Worker("w0", ReplaySource(_noise(seconds), SFREQ, name="Test", speed=200.0), cfg)
    return create_app([worker], cfg), worker


def test_page_and_static_files_are_served():
    app, _ = _app()
    with TestClient(app) as client:
        page = client.get("/")
        assert page.status_code == 200 and "Wachta" in page.text
        assert client.get("/app.js").status_code == 200
        assert client.get("/style.css").status_code == 200


def test_websocket_sends_hello_then_updates_with_the_contract_fields():
    app, _ = _app()
    with TestClient(app) as client, client.websocket_connect("/ws") as ws:
        hello = ws.receive_json()
        assert hello["type"] == "hello" and hello["primary"] == "w0"
        assert {"z_enter", "warn_below", "stop_below", "time_scale"} <= set(hello["config"])
        update = ws.receive_json()
        while update["type"] != "update":
            update = ws.receive_json()
        assert set(CLIENT_FIELDS) <= set(update["data"])
        assert update["data"]["state"] == "calibrating"


def test_actions_change_the_worker_pipeline():
    app, worker = _app()
    with TestClient(app) as client, client.websocket_connect("/ws") as ws:
        ws.receive_json()
        ws.send_json({"action": "break_start", "worker": "w0"})
        for _ in range(200):
            ws.receive_json()
            if worker.pipeline.index.on_break:
                break
        assert worker.pipeline.index.on_break
        baseline = worker.pipeline.baseline
        ws.send_json({"action": "recalibrate", "worker": "w0"})
        for _ in range(200):
            ws.receive_json()
            if worker.pipeline.baseline is not baseline:
                break
        assert worker.pipeline.baseline is not baseline


def test_state_endpoint_reports_the_latest_result():
    app, _ = _app()
    with TestClient(app) as client, client.websocket_connect("/ws") as ws:
        ws.receive_json()
        ws.receive_json()
        state = client.get("/api/state").json()
        assert state["w0"]["name"] == "Test"
        assert state["w0"]["latest"]["t"] > 0


class _FakeBoardDB:
    """Mimics brainaccess_board.ReadDB: the handle is closed after construction."""

    def __init__(self):
        self.open = False
        self.calls = 0

    def _connect(self):
        self.open = True

    def _close(self):
        self.open = False

    def _list_devices(self, only_lsl=False):
        if not self.open:
            return {"data": {}, "markers": {}}
        channels = ["O2", "O1", "P4", "P3", "C4", "C3", "F4", "F3", "Accel_x"]
        return {"data": {"dev-1": {"channels": channels, "channels_unit": ["uV"] * 8 + ["g"], "srate": 250.0}},
                "markers": {}}

    def get_data_since(self, device, last_timestamp=0.0):
        self.calls += 1
        if self.calls == 1:
            return {"data": np.zeros((9, 10)), "last_timestamp": 1.0}
        data = np.arange(9 * 5, dtype=float).reshape(9, 5)
        return {"data": data, "last_timestamp": float(self.calls)}


def test_board_source_reopens_the_database_and_reorders_channels(monkeypatch):
    from wachta.sources import BoardSource

    fake = _FakeBoardDB()
    monkeypatch.setattr(BoardSource, "_connect", staticmethod(lambda: fake))
    source = BoardSource(poll_s=0.0)

    async def first():
        async for chunk in source.chunks():
            return chunk

    chunk = asyncio.run(first())
    assert chunk.shape == (8, 5)
    # F3 is row 7 in the Board order; microvolts are converted to volts.
    assert np.allclose(chunk[0], np.arange(35, 40) * 1e-6)
    assert not fake.open


class _SilentBoardDB(_FakeBoardDB):
    """Delivers the backlog and then nothing: the headset was switched off."""

    def get_data_since(self, device, last_timestamp=0.0):
        self.calls += 1
        return {"data": np.zeros((9, 10)), "last_timestamp": 1.0} if self.calls == 1 else None


def test_board_source_reports_a_stalled_stream(monkeypatch):
    import pytest

    from wachta.sources import BoardSource

    monkeypatch.setattr(BoardSource, "_connect", staticmethod(lambda: _SilentBoardDB()))
    source = BoardSource(poll_s=0.01, stale_s=0.1)

    async def drain():
        async for _ in source.chunks():
            pass

    with pytest.raises(RuntimeError, match="Brak nowych próbek"):
        asyncio.run(drain())


def test_context_settings_from_wake_and_clock():
    from wachta.server import context_settings

    assert context_settings(None, None) == {}
    settings = context_settings("23:30", "05:00")
    assert settings["start_clock_h"] == 5.0
    assert settings["awake_at_start_h"] == 5.5


def test_probe_reaches_the_page_and_the_answer_is_recorded():
    app, worker = _app(120)
    worker.primary = True
    with TestClient(app) as client, client.websocket_connect("/ws") as ws:
        ws.receive_json()
        while True:                                   # wait until calibrated
            message = ws.receive_json()
            if message["type"] == "update" and message["data"]["state"] != "calibrating":
                break
        ws.send_json({"action": "probe_now", "worker": "w0"})
        probe = ws.receive_json()
        while probe["type"] != "probe":
            probe = ws.receive_json()
        ws.send_json({"action": "probe_response", "worker": "w0", "id": probe["id"], "rt_ms": 512})
        for _ in range(400):
            message = ws.receive_json()
            if message["type"] == "update" and message["data"]["probes_done"] == 1:
                break
        assert message["data"]["probe_lapses"] == 1 and message["data"]["last_rt_ms"] == 512
        # A second answer to the same probe is ignored.
        assert not worker.probe_response(probe["id"], 100)


def test_garbage_probe_answers_are_ignored_without_breaking_the_worker():
    app, worker = _app(5)
    for bad in ("abc", {"x": 1}, [1]):
        probe_id = worker.new_probe()
        assert not worker.probe_response(probe_id, bad)
        assert worker.pending_probe is None
    assert worker.pipeline.index.probes_done == 0


def test_answer_without_a_pending_probe_is_rejected():
    # Regression: probe_response(None, None) used to match pending_probe = None and cost the worker 8 points.
    app, worker = _app(5)
    index = worker.pipeline.index
    reserve, done = index.reserve, index.probes_done
    assert worker.pending_probe is None
    assert not worker.probe_response(None, None)
    assert not worker.probe_response(None, 250)
    assert index.probes_done == done
    assert index.reserve == reserve


def test_new_shift_resets_the_whole_team():
    cfg = Config()
    workers = [Worker(f"w{i}", ReplaySource(_noise(80, seed=i), SFREQ, name=f"T{i}", speed=200.0), cfg) for i in range(2)]
    app = create_app(workers, cfg)
    with TestClient(app) as client, client.websocket_connect("/ws") as ws:
        ws.receive_json()
        for _ in range(300):
            ws.receive_json()
            if all(w.history and w.history[-1]["state"] != "calibrating" for w in workers):
                break
        before = [w.pipeline.index for w in workers]
        stale_probe_id = workers[0].new_probe()
        ws.send_json({"action": "reset", "worker": "w0"})
        message = ws.receive_json()
        while message["type"] != "hello":
            message = ws.receive_json()
        assert all(w.pipeline.index is not b for w, b in zip(workers, before))
        assert all(w.pipeline.baseline.ready for w in workers)
        assert workers[0].pending_probe is None
        assert not workers[0].probe_response(stale_probe_id, None)
