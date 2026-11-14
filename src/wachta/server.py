"""Web server: runs the pipeline on each source and streams results to the dashboard.

Examples:
    python -m wachta.server --file filip --start 540 --team rudy:230 adi:240
    python -m wachta.server --source board --team rudy:230 adi:240

The first source is the worker shown in the main view. ``--team`` adds replayed
recordings so the supervisor panel has more than one row.
"""

import argparse
import asyncio
import contextlib
import dataclasses
import logging
from collections import deque
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from .config import Config
from .pipeline import Pipeline
from .recordings import find_recordings
from .sources import BoardSource, ReplaySource, resolve_recording

log = logging.getLogger("wachta")

WEB_DIR = Path(__file__).parent / "web"
RETRY_S = 3.0
HISTORY_S = 900            # seconds of per-window history kept for new clients
TRACE_EVERY = 5            # keep every n-th window in the long reserve trace

# Fields of a pipeline result that the dashboard needs.
CLIENT_FIELDS = (
    "t", "state", "reserve", "fast", "slow", "quality", "lapse", "new_lapse", "lapses_recent",
    "lapse_count", "calibration", "minutes_to_warn", "minutes_to_stop", "work_min",
    "drain_per_hour", "bad", "on_break",
)


def _client_entry(result: dict) -> dict:
    entry = {key: result[key] for key in CLIENT_FIELDS}
    for key in ("minutes_to_warn", "minutes_to_stop"):
        if entry[key] is not None:
            entry[key] = round(entry[key], 1)
    return entry


class Worker:
    """One person: a source of samples, a pipeline and the recent results."""

    def __init__(self, worker_id: str, source, cfg: Config) -> None:
        self.id = worker_id
        self.source = source
        self.cfg = cfg
        self.pipeline = Pipeline(cfg)
        self.history: deque[dict] = deque(maxlen=HISTORY_S)
        self.trace: deque[list[float]] = deque(maxlen=4000)   # [work_min, reserve]
        self.error: str | None = None
        self._windows = 0

    def record(self, result: dict) -> dict:
        entry = _client_entry(result)
        self.history.append(entry)
        if entry["state"] != "calibrating" and self._windows % TRACE_EVERY == 0:
            self.trace.append([entry["work_min"], entry["reserve"]])
        self._windows += 1
        return entry

    def handle(self, action: str) -> None:
        if action == "break_start":
            self.pipeline.index.start_break()
        elif action == "break_end":
            self.pipeline.index.end_break()
        elif action == "recalibrate":
            self.pipeline.recalibrate()
        elif action == "reset":
            self.pipeline = Pipeline(self.cfg)
            self.history.clear()
            self.trace.clear()

    def describe(self) -> dict:
        return {
            "id": self.id,
            "name": self.source.name,
            "live": self.source.live,
            "error": self.error,
            "history": list(self.history),
            "trace": list(self.trace),
        }


class Hub:
    """Connected dashboards."""

    def __init__(self) -> None:
        self.clients: set[WebSocket] = set()

    async def broadcast(self, message: dict) -> None:
        for client in list(self.clients):
            try:
                await client.send_json(message)
            except Exception:
                self.clients.discard(client)


async def _run_worker(worker: Worker, hub: Hub) -> None:
    """Pump one source through its pipeline; live sources reconnect after errors."""
    while True:
        try:
            async for chunk in worker.source.chunks():
                if worker.error:
                    worker.error = None
                    await hub.broadcast({"type": "status", "worker": worker.id, "error": None})
                for result in worker.pipeline.push(chunk):
                    await hub.broadcast({"type": "update", "worker": worker.id, "data": worker.record(result)})
            return
        except asyncio.CancelledError:
            raise
        except Exception as error:
            worker.error = str(error)
            log.warning("%s: %s", worker.source.name, error)
            await hub.broadcast({"type": "status", "worker": worker.id, "error": worker.error})
            if not worker.source.live:
                return
            await asyncio.sleep(RETRY_S)


def create_app(workers: list[Worker], cfg: Config) -> FastAPI:
    if not workers:
        raise ValueError("At least one worker is required")
    hub = Hub()
    by_id = {worker.id: worker for worker in workers}

    @contextlib.asynccontextmanager
    async def lifespan(_: FastAPI):
        tasks = [asyncio.create_task(_run_worker(worker, hub)) for worker in workers]
        yield
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    app = FastAPI(title="Wachta", lifespan=lifespan)

    def hello() -> dict:
        return {
            "type": "hello",
            "primary": workers[0].id,
            "config": {
                "z_enter": cfg.z_enter,
                "warn_below": cfg.warn_below,
                "stop_below": cfg.stop_below,
                "time_scale": cfg.time_scale,
                "step_s": cfg.step_s,
                "drain_per_hour": cfg.drain_per_hour,
            },
            "workers": [worker.describe() for worker in workers],
        }

    @app.get("/api/state")
    def state() -> dict:
        """Latest result per worker, for scripts and quick checks."""
        return {
            worker.id: {"name": worker.source.name, "error": worker.error,
                        "latest": worker.history[-1] if worker.history else None}
            for worker in workers
        }

    @app.websocket("/ws")
    async def stream(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_json(hello())
        hub.clients.add(websocket)
        try:
            while True:
                message = await websocket.receive_json()
                worker = by_id.get(message.get("worker"), workers[0])
                worker.handle(str(message.get("action")))
                if message.get("action") == "reset":
                    await websocket.send_json(hello())
        except WebSocketDisconnect:
            pass
        finally:
            hub.clients.discard(websocket)

    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
    return app


def _replay_worker(worker_id: str, spec: str, cfg: Config, speed: float, start_s: float) -> Worker:
    """Build a replayed worker from ``name`` or ``name:start_seconds``."""
    name, _, offset = spec.partition(":")
    path = resolve_recording(name)
    label = path.name.split("task-")[1].split("_")[0] if "task-" in path.name else path.stem
    source = ReplaySource.from_file(
        path, name=f"{label.capitalize()} (nagranie)", speed=speed, start_s=float(offset) if offset else start_s
    )
    return Worker(worker_id, source, cfg)


def build_workers(args: argparse.Namespace, cfg: Config) -> list[Worker]:
    if args.source == "board":
        workers = [Worker("w0", BoardSource(name=args.name or "Na żywo"), cfg)]
    else:
        spec = args.file or next(iter(find_recordings()), None)
        if spec is None:
            raise SystemExit("Brak nagrań w data/recordings. Podaj --file albo użyj --source board.")
        workers = [_replay_worker("w0", spec, cfg, args.speed, args.start)]
        if args.name:
            workers[0].source.name = args.name
    for i, spec in enumerate(args.team, start=1):
        workers.append(_replay_worker(f"w{i}", spec, cfg, args.speed, 0.0))
    return workers


def main() -> None:
    parser = argparse.ArgumentParser(description="Wachta dashboard server")
    parser.add_argument("--source", choices=("replay", "board"), default="replay",
                        help="replay a recording (default) or read BrainAccess Board live")
    parser.add_argument("--file", help="recording to replay: a .fif path or a team recording name, e.g. filip")
    parser.add_argument("--start", type=float, default=0.0, help="replay start offset in seconds")
    parser.add_argument("--speed", type=float, default=1.0, help="replay speed, 1 is real time")
    parser.add_argument("--name", help="display name of the main worker")
    parser.add_argument("--team", nargs="*", default=[], metavar="NAME[:START]",
                        help="extra replayed recordings for the supervisor panel")
    parser.add_argument("--time-scale", type=float, default=60.0,
                        help="shift seconds per real second; 60 means one minute of demo is one hour of work")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    import uvicorn

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    cfg = dataclasses.replace(Config(), time_scale=args.time_scale)
    workers = build_workers(args, cfg)
    log.info("Wachta: http://%s:%s  (%s)", args.host, args.port, ", ".join(w.source.name for w in workers))
    uvicorn.run(create_app(workers, cfg), host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
