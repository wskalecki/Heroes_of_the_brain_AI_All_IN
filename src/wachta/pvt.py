"""Brief psychomotor vigilance test (PVT-B) in the browser.

A 3-minute reaction time test used as a behavioural vigilance label next to KSS at
checkpoints. Parameters follow Basner, Mollicone & Dinges (2011), Acta Astronautica
69:949-959 (PMC3197786):

* test duration 3 min;
* response-to-stimulus interval 1-4 s, including 1 s of reaction time feedback;
* lapse: reaction time >= 355 ms (PVT-B threshold; 500 ms is used for the 10-min PVT);
* false start: response without a stimulus or reaction time < 100 ms;
* no response within 30 s counts as a lapse with a 30 s reaction time.

Run ``python -m wachta.pvt --person wojtek --checkpoint T1``. The command starts a
local web server (127.0.0.1 only), opens the test page and appends one row per test
to ``data/recordings/pvt.csv``. Scoring happens here, in Python, so the browser page
only measures and sends raw reaction times.

Browser timing adds a roughly constant delay (display and keyboard latency, typically
tens of ms). Results are comparable within one person on one computer, not with
published absolute norms.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import csv
import json
import math
from pathlib import Path
import statistics
import sys
import threading
from typing import Any, Sequence
from urllib.parse import urlencode, urlsplit
import webbrowser

from .session import normalize_checkpoint, normalize_person

DEFAULT_RESULTS_FILE = Path("data/recordings/pvt.csv")
DEFAULT_PORT = 8765
PAGE_PATH = Path(__file__).with_name("pvt.html")
CONFIG_PLACEHOLDER = "/*__PVT_CONFIG__*/"
MAX_BODY_BYTES = 256 * 1024
MAX_RESPONSES = 2000

PVT_FIELDS = (
    "person",
    "checkpoint",
    "started_at",
    "duration_s",
    "n_stimuli",
    "false_starts",
    "lapses",
    "mean_rt_ms",
    "median_rt_ms",
    "mean_speed",
    "slowest10_speed",
    "performance_score",
    "rts_ms",
)


@dataclass(frozen=True)
class PvtConfig:
    duration_s: float = 180.0
    isi_min_s: float = 1.0      # response-to-stimulus interval, feedback included
    isi_max_s: float = 4.0
    feedback_s: float = 1.0
    lapse_ms: float = 355.0
    false_start_ms: float = 100.0
    timeout_ms: float = 30000.0


def _mean(values: Sequence[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _round(value: float | None, digits: int) -> float | None:
    return None if value is None else round(value, digits)


def score_pvt(
    rts_ms: Sequence[float],
    anticipations: int = 0,
    cfg: PvtConfig = PvtConfig(),
) -> dict[str, Any]:
    """Score one PVT run.

    Parameters
    ----------
    rts_ms : reaction times to stimuli in ms, one per stimulus; a timeout is ``cfg.timeout_ms``.
    anticipations : responses made while no stimulus was shown.
    """
    rts = [float(r) for r in rts_ms]
    valid = [r for r in rts if r >= cfg.false_start_ms]
    false_starts = int(anticipations) + (len(rts) - len(valid))
    lapses = sum(1 for r in valid if r >= cfg.lapse_ms)
    speeds = sorted(1000.0 / r for r in valid)
    n_slowest = max(1, math.ceil(0.1 * len(speeds))) if speeds else 0

    # Basner & Dinges (2011): 1 - (lapses + false starts) / valid stimuli including false starts.
    denominator = len(rts) + int(anticipations)
    performance = 1.0 - (lapses + false_starts) / denominator if denominator else None

    return {
        "n_stimuli": len(rts),
        "false_starts": false_starts,
        "lapses": lapses,
        "mean_rt_ms": _round(_mean(valid), 1),
        "median_rt_ms": _round(statistics.median(valid) if valid else None, 1),
        "mean_speed": _round(_mean(speeds), 3),
        "slowest10_speed": _round(_mean(speeds[:n_slowest]), 3),
        "performance_score": _round(performance, 3),
    }


def _parse_started_at(value: Any) -> str:
    if value in (None, ""):
        return datetime.now().astimezone().isoformat(timespec="seconds")
    raw = str(value).strip()
    if len(raw) > 64:
        raise ValueError("started_at is too long")
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError(f"started_at must be an ISO-8601 timestamp, got {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.astimezone()
    return parsed.astimezone().isoformat(timespec="seconds")


def _parse_rts(value: Any, cfg: PvtConfig) -> list[float]:
    if not isinstance(value, list):
        raise ValueError("rts_ms must be a list of numbers")
    if len(value) > MAX_RESPONSES:
        raise ValueError(f"too many responses ({len(value)})")
    rts = []
    for item in value:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise ValueError(f"reaction time must be a number, got {item!r}")
        rt = float(item)
        if not math.isfinite(rt) or rt < 0 or rt > cfg.timeout_ms:
            raise ValueError(f"reaction time out of range: {item!r}")
        rts.append(round(rt, 1))
    return rts


def _parse_count(value: Any, name: str) -> int:
    if value in (None, ""):
        return 0
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value != int(value)
    ):
        raise ValueError(f"{name} must be a non-negative integer, got {value!r}")
    count = int(value)
    if not 0 <= count <= MAX_RESPONSES:
        raise ValueError(f"{name} out of range: {count}")
    return count


def build_row(payload: dict[str, Any], cfg: PvtConfig = PvtConfig()) -> dict[str, Any]:
    """Validate a result sent by the browser and turn it into a ``pvt.csv`` row."""
    if not isinstance(payload, dict):
        raise ValueError("result must be a JSON object")
    raw_person = payload.get("person")
    raw_checkpoint = payload.get("checkpoint")
    if not isinstance(raw_person, str) or not isinstance(raw_checkpoint, str):
        raise ValueError("person and checkpoint must be strings")
    person = normalize_person(raw_person)
    checkpoint = normalize_checkpoint(raw_checkpoint)
    rts = _parse_rts(payload.get("rts_ms"), cfg)
    anticipations = _parse_count(payload.get("anticipations"), "anticipations")

    duration = payload.get("duration_s", cfg.duration_s)
    if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not 1 <= duration <= 3600:
        raise ValueError(f"duration_s out of range: {duration!r}")

    metrics = score_pvt(rts, anticipations, cfg)
    row: dict[str, Any] = {
        "person": person,
        "checkpoint": checkpoint,
        "started_at": _parse_started_at(payload.get("started_at")),
        "duration_s": round(float(duration), 1),
        **metrics,
        "rts_ms": ";".join(f"{r:g}" for r in rts),
    }
    return row


def append_result(results_path: Path | str, row: dict[str, Any]) -> Path:
    """Create or append one row to ``pvt.csv`` (header checked against ``PVT_FIELDS``)."""
    path = Path(results_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not path.exists() or path.stat().st_size == 0
    if not needs_header:
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            header = next(csv.reader(handle), None)
        if header is None:
            needs_header = True
        elif tuple(header) != PVT_FIELDS:
            raise ValueError(f"{path} has unexpected columns {header!r}; expected {list(PVT_FIELDS)!r}")

    with path.open("w" if needs_header else "a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=PVT_FIELDS, lineterminator="\n")
        if needs_header:
            writer.writeheader()
        writer.writerow({field: "" if row.get(field) is None else row.get(field) for field in PVT_FIELDS})
    return path


def render_page(cfg: PvtConfig, person: str = "", checkpoint: str = "") -> str:
    """Return the test page with the configuration embedded."""
    page = PAGE_PATH.read_text(encoding="utf-8")
    settings = {**asdict(cfg), "person": person, "checkpoint": checkpoint, "save_url": "/api/result"}
    script = "window.PVT_CONFIG = " + json.dumps(settings, ensure_ascii=False).replace("</", "<\\/") + ";"
    return page.replace(CONFIG_PLACEHOLDER, script, 1)


class PvtServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(
        self,
        address: tuple[str, int],
        results_path: Path | str = DEFAULT_RESULTS_FILE,
        cfg: PvtConfig = PvtConfig(),
        person: str = "",
        checkpoint: str = "",
        once: bool = False,
        out=sys.stdout,
    ) -> None:
        super().__init__(address, PvtRequestHandler)
        self.results_path = Path(results_path)
        self.cfg = cfg
        self.person = person
        self.checkpoint = checkpoint
        self.once = once
        self.out = out
        self.saved_rows: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    def save(self, payload: dict[str, Any]) -> dict[str, Any]:
        row = build_row(payload, self.cfg)
        with self._lock:
            append_result(self.results_path, row)
            self.saved_rows.append(row)
        self.out.write(
            f"Zapisano PVT: {row['person']} {row['checkpoint']} | lapsy {row['lapses']}, "
            f"falstarty {row['false_starts']}, mediana {row['median_rt_ms']} ms -> {self.results_path}\n"
        )
        self.out.flush()
        if self.once:
            threading.Thread(target=self.shutdown, daemon=True).start()
        return row


class PvtRequestHandler(BaseHTTPRequestHandler):
    server: PvtServer

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - stdlib signature
        return

    def _send(self, status: HTTPStatus, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: HTTPStatus, data: dict[str, Any]) -> None:
        self._send(status, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802 - stdlib naming
        path = urlsplit(self.path).path
        if path in ("/", "/index.html"):
            page = render_page(self.server.cfg, self.server.person, self.server.checkpoint)
            self._send(HTTPStatus.OK, page.encode("utf-8"), "text/html; charset=utf-8")
        elif path == "/favicon.ico":
            self._send(HTTPStatus.NO_CONTENT, b"", "image/x-icon")
        else:
            self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:  # noqa: N802 - stdlib naming
        if urlsplit(self.path).path != "/api/result":
            self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if not 0 < length <= MAX_BODY_BYTES:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid body size"})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            row = self.server.save(payload)
        except (ValueError, UnicodeDecodeError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
            return
        self._send_json(HTTPStatus.OK, {"ok": True, "result": row, "saved_to": str(self.server.results_path)})


def import_result(json_path: Path | str, results_path: Path | str, cfg: PvtConfig = PvtConfig()) -> dict[str, Any]:
    """Score and save a raw result downloaded from the page when no server was running."""
    payload = json.loads(Path(json_path).read_text(encoding="utf-8"))
    row = build_row(payload, cfg)
    append_result(results_path, row)
    return row


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m wachta.pvt",
        description="Test czasu reakcji PVT-B (3 min) w przeglądarce; wynik trafia do pvt.csv.",
    )
    parser.add_argument("--person", default="", help="Imię uczestnika (wpisane z góry na stronie testu)")
    parser.add_argument("--checkpoint", default="", help="Punkt pomiarowy, np. T0, T1, T2")
    parser.add_argument("--results-file", default=str(DEFAULT_RESULTS_FILE), help="Plik wyników (domyślnie: data/recordings/pvt.csv)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port lokalnego serwera (domyślnie: {DEFAULT_PORT})")
    parser.add_argument("--duration", type=float, default=PvtConfig.duration_s, help="Czas testu w sekundach (domyślnie: 180)")
    parser.add_argument("--no-browser", action="store_true", help="Nie otwieraj przeglądarki automatycznie")
    parser.add_argument("--once", action="store_true", help="Zakończ po zapisaniu pierwszego wyniku")
    parser.add_argument("--import", dest="import_json", metavar="PLIK_JSON", help="Wczytaj surowy wynik pobrany ze strony testu i zapisz go do pliku wyników")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not 10 <= args.duration <= 3600:
        sys.stderr.write("Błąd: --duration musi mieć od 10 do 3600 s\n")
        return 2
    cfg = PvtConfig(duration_s=float(args.duration))

    if args.import_json:
        try:
            row = import_result(args.import_json, args.results_file, cfg)
        except (OSError, ValueError) as exc:
            sys.stderr.write(f"Błąd: {exc}\n")
            return 2
        print(f"Zapisano wynik {row['person']} {row['checkpoint']} do {args.results_file}")
        return 0

    try:
        person = normalize_person(args.person) if args.person else ""
        checkpoint = normalize_checkpoint(args.checkpoint) if args.checkpoint else ""
        server = PvtServer(("127.0.0.1", args.port), args.results_file, cfg, person, checkpoint, args.once)
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"Błąd: {exc}\n")
        return 2

    query = urlencode({k: v for k, v in (("person", person), ("checkpoint", checkpoint)) if v})
    url = f"http://127.0.0.1:{server.server_address[1]}/" + (f"?{query}" if query else "")
    print(f"Test PVT-B: {url}\nWyniki: {args.results_file}\nZakończ: Ctrl+C", flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
