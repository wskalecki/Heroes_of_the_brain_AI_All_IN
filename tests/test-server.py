import asyncio

import numpy as np
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
            message = ws.receive_json()
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
