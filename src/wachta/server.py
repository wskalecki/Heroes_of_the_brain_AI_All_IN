"""Web server: runs the pipeline on each source and streams results to the dashboard.

Examples:
    python -m wachta.server --file filip --start 540 --team rudy:230 adi:240
    python -m wachta.server --file filip --team rudy:380-520 adi:370-500   # team members loop over a calm segment
    python -m wachta.server --source board --team rudy:230 adi:240

The first source is the worker shown in the main view. ``--team`` adds replayed
recordings so the supervisor panel has more than one row.
"""

import argparse
import asyncio
import contextlib
import dataclasses
import logging
import time
from collections import deque
from datetime import datetime
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
    "drain_per_hour", "bad", "on_break", "lapse_kind", "lapses_eyes_closed", "lapses_eyes_open",
    "eye_state", "blinks_per_min", "probes_done", "probe_lapses", "last_rt_ms", "context_factor",
    "clock_h", "awake_h", "probe_threshold_ms", "probe_failed_recently",
)


def _client_entry(result: dict) -> dict:
    entry = {key: result[key] for key in CLIENT_FIELDS}
    for key in ("minutes_to_warn", "minutes_to_stop"):
        if entry[key] is not None:
            entry[key] = round(entry[key], 1)
    return entry


class Worker:
    """One person: a source of samples, a pipeline and the recent results."""

    def __init__(self, worker_id: str, source, cfg: Config, primary: bool = False) -> None:
        self.id = worker_id
        self.primary = primary
        self.source = source
        self.cfg = cfg
        self.pipeline = Pipeline(cfg)
        self.history: deque[dict] = deque(maxlen=HISTORY_S)
        self.trace: deque[list[float]] = deque(maxlen=4000)   # [work_min, reserve]
        self.error: str | None = None
        self._windows = 0
        self.pending_probe: int | None = None
        self._probe_seq = 0
        self._probe_sent = 0.0
        self.last_t = 0.0

    def new_probe(self) -> int:
        self._probe_seq += 1
        self.pending_probe = self._probe_seq
        self._probe_sent = time.monotonic()
        return self._probe_seq

    def drop_stale_probe(self) -> None:
        """Forget a probe nobody answered (e.g. the page was closed); it does not count as a lapse."""
        if self.pending_probe is not None and time.monotonic() - self._probe_sent > self.cfg.probe_timeout_ms / 1000 + 5:
            self.pending_probe = None

    def probe_response(self, probe_id, rt_ms) -> bool:
        """Accept the first answer to the pending probe; later or stale answers are ignored."""
        if probe_id != self.pending_probe:
            return False
        self.pending_probe = None
        try:
            value = None if rt_ms is None else float(rt_ms)
        except (TypeError, ValueError):
            return False                      # garbage from the page: forget the probe, count nothing
        self.pipeline.index.record_probe(self.last_t, value)
        return True

    def record(self, result: dict) -> dict:
        entry = _client_entry(result)
        self.last_t = entry["t"]
        self.history.append(entry)
        if entry["state"] != "calibrating" and self._windows % TRACE_EVERY == 0:
            self.trace.append([entry["work_min"], entry["reserve"]])
        self._windows += 1
        return entry

    def handle(self, action: str) -> None:
        if action == "probe_now":
            self.pipeline.index.request_probe()
        elif action == "break_start":
            self.pipeline.index.start_break()
        elif action == "break_end":
            self.pipeline.index.end_break()
        elif action == "recalibrate":
            self.pipeline.recalibrate()
            self.pending_probe = None
        elif action == "reset":
            # New shift, same person: keep the calibration and blink threshold.
            self.pipeline.new_shift()
            self.pending_probe = None
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
                    # Probes go to the person in the main view only, and only if someone can answer.
                    worker.drop_stale_probe()
                    if result["probe"] and worker.primary and hub.clients and worker.pending_probe is None:
                        await hub.broadcast({"type": "probe", "worker": worker.id, "id": worker.new_probe(),
                                             "timeout_ms": worker.cfg.probe_timeout_ms,
                                             "threshold_ms": result["probe_threshold_ms"],
                                             "reason": result["probe_reason"]})
            return
        except asyncio.CancelledError:
            raise
        except Exception as error:
            worker.error = str(error)
            worker.pipeline.reset_stream()      # the stream has a gap now; do not trust windows across it
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
                "probe_lapse_ms": cfg.probe_lapse_ms,
                "probe_timeout_ms": cfg.probe_timeout_ms,
                "probe_interval_s": cfg.probe_interval_s,
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
                if message.get("action") == "probe_response":
                    worker.probe_response(message.get("id"), message.get("rt_ms"))
                    continue
                if message.get("action") == "reset":
                    # "Nowa zmiana" starts a new shift for the whole team at once, calibrations kept.
                    for member in workers:
                        member.handle("reset")
                    await hub.broadcast(hello())
                    continue
                worker.handle(str(message.get("action")))
        except WebSocketDisconnect:
            pass
        finally:
            hub.clients.discard(websocket)

    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
    return app


def _replay_worker(worker_id: str, spec: str, cfg: Config, speed: float, start_s: float) -> Worker:
    """Build a replayed worker from ``name``, ``name:start`` or ``name:start-end`` (seconds, end loops back to start)."""
    name, _, offset = spec.partition(":")
    offset, _, end = offset.partition("-")
    path = resolve_recording(name)
    label = path.name.split("task-")[1].split("_")[0] if "task-" in path.name else path.stem
    source = ReplaySource.from_file(
        path, name=f"{label.capitalize()} (nagranie)", speed=speed, start_s=float(offset) if offset else start_s,
        end_s=float(end) if end else None,
    )
    return Worker(worker_id, source, cfg)


def build_workers(args: argparse.Namespace, cfg: Config) -> list[Worker]:
    if args.source == "board":
        workers = [Worker("w0", BoardSource(name=args.name or "Na żywo"), cfg, primary=True)]
    else:
        spec = args.file or next(iter(find_recordings()), None)
        if spec is None:
            raise SystemExit("Brak nagrań w data/recordings. Podaj --file albo użyj --source board.")
        workers = [_replay_worker("w0", spec, cfg, args.speed, args.start)]
        workers[0].primary = True
        if args.name:
            workers[0].source.name = args.name
    for i, spec in enumerate(args.team, start=1):
        workers.append(_replay_worker(f"w{i}", spec, cfg, args.speed, 0.0))
    return workers


def _hours(text: str) -> float:
    hours, _, minutes = text.partition(":")
    value = int(hours) + int(minutes or 0) / 60.0
    if not 0 <= value < 24:
        raise ValueError(f"Niepoprawna godzina: {text}")
    return value


def context_settings(wake: str | None, clock: str | None) -> dict:
    """Config fields for the context model from ``--wake`` and ``--clock`` (HH:MM)."""
    if wake is None and clock is None:
        return {}
    start = _hours(clock) if clock else datetime.now().hour + datetime.now().minute / 60.0
    settings = {"start_clock_h": start}
    if wake is not None:
        settings["awake_at_start_h"] = (start - _hours(wake)) % 24.0
    return settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Wachta dashboard server")
    parser.add_argument("--source", choices=("replay", "board"), default="replay",
                        help="replay a recording (default) or read BrainAccess Board live")
    parser.add_argument("--file", help="recording to replay: a .fif path or a team recording name, e.g. filip")
    parser.add_argument("--start", type=float, default=0.0, help="replay start offset in seconds")
    parser.add_argument("--speed", type=float, default=1.0, help="replay speed, 1 is real time")
    parser.add_argument("--name", help="display name of the main worker")
    parser.add_argument("--team", nargs="*", default=[], metavar="NAME[:START[-END]]",
                        help="extra replayed recordings for the supervisor panel")
    parser.add_argument("--time-scale", type=float, default=60.0,
                        help="shift seconds per real second; 60 means one minute of demo is one hour of work")
    parser.add_argument("--wake", metavar="HH:MM", help="wake-up time of the main worker; turns on the context model")
    parser.add_argument("--clock", metavar="HH:MM", help="time of day at shift start (default: now); use with --wake")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    import uvicorn

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        cfg = dataclasses.replace(Config(), time_scale=args.time_scale, **context_settings(args.wake, args.clock))
        workers = build_workers(args, cfg)
    except (ValueError, FileNotFoundError) as error:
        parser.error(str(error))               # a readable message instead of a traceback
    log.info("Wachta: http://%s:%s  (%s)", args.host, args.port, ", ".join(w.source.name for w in workers))
    uvicorn.run(create_app(workers, cfg), host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
