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
