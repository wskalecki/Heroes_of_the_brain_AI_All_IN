"""Checkpoint protocol runner and metadata logger for team EEG sessions.

Guides a participant through the fixed 3-minute EEG checkpoint protocol
(``eyes_open``, ``eyes_closed``, ``math``) followed by KSS (1-9) and optional
Garmin Venu 2 readings, then writes:

* ``<recording>-raw_annotations.csv`` in MNE-compatible ``onset,duration,description``
  format next to the ``.fif`` recording;
* a row in ``data/recordings/checkpoints.csv``.

Run with ``python -m wachta.session``.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
import math
from pathlib import Path
import sys
import time
from typing import Callable, Sequence, TextIO

DEFAULT_RECORDINGS_DIR = Path("data/recordings")
DEFAULT_STEP_SECONDS = 60.0
VALID_CHECKPOINTS = ("T0", "T1", "T2")

CHECKPOINT_FIELDS = (
    "person",
    "checkpoint",
    "started_at",
    "kss",
    "body_battery",
    "stress",
    "heart_rate",
    "hrv_ms",
    "recording_file",
    "notes",
)

KSS_GUIDE = (
    "Skala senności KSS (1–9):\n"
    "  1 = skrajnie czujny  | 3 = czujny | 5 = ani czujny, ani senny\n"
    "  7 = senny, bez walki ze snem | 9 = bardzo senny, walka ze snem"
)


@dataclass(frozen=True)
class ProtocolStep:
    label: str
    duration_s: float
    instruction: str


DEFAULT_STEPS: tuple[ProtocolStep, ...] = (
    ProtocolStep(
        label="eyes_open",
        duration_s=DEFAULT_STEP_SECONDS,
        instruction="Oczy otwarte, patrz spokojnie w jeden punkt (kalibracja)",
    ),
    ProtocolStep(
        label="eyes_closed",
        duration_s=DEFAULT_STEP_SECONDS,
        instruction="Zamknij oczy, rozluźnij się (alfa potyliczna)",
    ),
    ProtocolStep(
        label="math",
        duration_s=DEFAULT_STEP_SECONDS,
        instruction="Liczenie w pamięci: odejmuj 7 od 1000 (oczy otwarte)",
    ),
)


def build_steps(step_seconds: float = DEFAULT_STEP_SECONDS) -> tuple[ProtocolStep, ...]:
    """Return the fixed checkpoint steps with the requested per-step duration."""
    if step_seconds <= 0:
        raise ValueError(f"step_seconds must be positive, got {step_seconds}")
    return tuple(
        ProtocolStep(step.label, float(step_seconds), step.instruction)
        for step in DEFAULT_STEPS
    )


def normalize_person(value: str) -> str:
    cleaned = value.strip().lower()
    if not cleaned:
        raise ValueError("person cannot be empty")
    if any(sep in cleaned for sep in ("/", "\\", "\n", "\r")):
        raise ValueError(f"invalid person name: {value!r}")
    return cleaned


def normalize_checkpoint(value: str) -> str:
    cleaned = value.strip().upper()
    if not cleaned:
        raise ValueError("checkpoint cannot be empty")
    return cleaned


def parse_kss(value: str | int) -> int:
    raw = str(value).strip()
    try:
        score = int(raw)
    except ValueError as exc:
        raise ValueError(f"KSS must be an integer 1..9, got {value!r}") from exc
    if not 1 <= score <= 9:
        raise ValueError(f"KSS must be between 1 and 9, got {score}")
    return score


def parse_optional_number(
    value: str | float | int | None,
    field_name: str,
    *,
    min_value: float | None = None,
    max_value: float | None = None,
    integer: bool = False,
) -> str:
    if value is None:
        return ""
    raw = str(value).strip()
    if not raw:
        return ""
    raw_normalized = raw.replace(",", ".")
    try:
        num = int(raw_normalized) if integer else float(raw_normalized)
    except ValueError as exc:
        kind = "integer" if integer else "number"
        raise ValueError(f"{field_name} must be a valid {kind}, got {value!r}") from exc
    if min_value is not None and num < min_value:
        raise ValueError(f"{field_name} must be >= {min_value}, got {num}")
    if max_value is not None and num > max_value:
        raise ValueError(f"{field_name} must be <= {max_value}, got {num}")
    if isinstance(num, float) and num.is_integer():
        return str(int(num))
    return str(num)


def annotations_path_for(recording_path: Path | str) -> Path:
    """Return the companion annotations CSV path for a ``.fif`` recording."""
    path = Path(recording_path)
    if path.name.endswith("-raw.fif"):
        return path.with_name(path.name.replace("-raw.fif", "-raw_annotations.csv"))
    return path.with_name(f"{path.stem}-raw_annotations.csv")


def write_annotations(
    path: Path | str,
    steps: Sequence[ProtocolStep] = DEFAULT_STEPS,
) -> Path:
    """Write ``onset,duration,description`` CSV for the checkpoint blocks."""
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    onset = 0.0
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["onset", "duration", "description"])
        for step in steps:
            writer.writerow([f"{onset:.3f}", f"{step.duration_s:.3f}", step.label])
            onset += step.duration_s
    return out_path


def find_candidate_recordings(
    recordings_dir: Path | str,
    person: str,
    checkpoint: str,
    *,
    started_epoch: float | None = None,
) -> list[Path]:
    """Return ``.fif`` files in ``recordings_dir`` ordered by relevance and recency."""
    folder = Path(recordings_dir)
    if not folder.exists():
        return []

    person_lc = person.lower()
    cp_lc = checkpoint.lower()
    task_token = f"{person_lc}-{cp_lc}"
    alt_token = f"{person_lc}_{cp_lc}"

    candidates: list[tuple[int, float, Path]] = []
    for path in folder.rglob("*.fif"):
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        name_lc = path.name.lower()
        score = 0
        if task_token in name_lc or alt_token in name_lc:
            score += 4
        elif person_lc in name_lc:
            score += 2
        if started_epoch is not None and mtime >= started_epoch - 5.0:
            score += 3
        candidates.append((score, mtime, path))

    candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [item[2] for item in candidates]


def format_recording_ref(recording_path: Path | str, recordings_dir: Path | str) -> str:
    """Format recording path relative to ``recordings_dir`` when located inside it."""
    rec = Path(recording_path)
    base = Path(recordings_dir)
    try:
        return rec.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return rec.as_posix()


def existing_checkpoints(checkpoints_path: Path | str) -> set[tuple[str, str]]:
    """Return recorded ``(person, checkpoint)`` pairs from ``checkpoints.csv``."""
    path = Path(checkpoints_path)
    if not path.exists() or path.stat().st_size == 0:
        return set()
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return set()
        return {
            (row["person"].strip().lower(), row["checkpoint"].strip().upper())
            for row in reader
            if row.get("person") and row.get("checkpoint")
        }


def append_checkpoint_row(checkpoints_path: Path | str, row: dict[str, str]) -> Path:
    """Create or append a validated row to ``checkpoints.csv``."""
    path = Path(checkpoints_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not path.exists() or path.stat().st_size == 0

    if not needs_header:
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.reader(handle)
            header = next(reader, None)
        if header is None:
            needs_header = True
        elif tuple(header) != CHECKPOINT_FIELDS:
            raise ValueError(
                f"{path} has unexpected columns {header!r}; expected {list(CHECKPOINT_FIELDS)!r}"
            )

    normalized_row = {field: row.get(field, "") for field in CHECKPOINT_FIELDS}
    mode = "w" if needs_header else "a"
    with path.open(mode, newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CHECKPOINT_FIELDS, lineterminator="\n")
        if needs_header:
            writer.writeheader()
        writer.writerow(normalized_row)
    return path


def _ring_bell(out: TextIO, enabled: bool) -> None:
    if enabled:
        out.write("\a")
        out.flush()


def _format_mm_ss(seconds: float) -> str:
    total = max(0, int(round(seconds)))
    minutes, secs = divmod(total, 60)
    return f"{minutes:02d}:{secs:02d}"


def run_countdown(
    steps: Sequence[ProtocolStep],
    *,
    out: TextIO = sys.stdout,
    bell: bool = True,
    clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> None:
    """Run an interactive second-by-second countdown through all protocol steps."""
    is_tty = hasattr(out, "isatty") and out.isatty()
    for idx, step in enumerate(steps, start=1):
        _ring_bell(out, bell)
        out.write(
            f"\n[{idx}/{len(steps)}] {step.label.upper()} ({int(round(step.duration_s))} s): "
            f"{step.instruction}\n"
        )
        out.flush()

        step_start = clock()
        step_end = step_start + step.duration_s
        last_shown: int | None = None
        while True:
            remaining = step_end - clock()
            if remaining <= 0:
                break
            rem_sec = max(1, math.ceil(remaining - 0.01))
            if rem_sec != last_shown:
                last_shown = rem_sec
                if is_tty:
                    out.write(f"\r  Pozostało: {_format_mm_ss(rem_sec)} ")
                    out.flush()
                elif rem_sec == int(round(step.duration_s)) or rem_sec in (30, 15, 5):
                    out.write(f"  Pozostało: {_format_mm_ss(rem_sec)}\n")
                    out.flush()
            sleep(min(0.25, remaining))

        if is_tty:
            out.write("\r  Pozostało: 00:00 — koniec kroku\n")
        else:
            out.write("  Koniec kroku.\n")
        out.flush()

    _ring_bell(out, bell)
    out.write("\nKoniec protokołu EEG. Możesz zatrzymać nagrywanie w BrainAccess Board.\n")
    out.flush()


def _prompt_until_valid(
    prompt: str,
    parser: Callable[[str], object],
    *,
    input_fn: Callable[[str], str],
    out: TextIO,
    default: str | None = None,
) -> object:
    while True:
        raw = input_fn(prompt)
        if not raw.strip() and default is not None:
            raw = default
        try:
            return parser(raw)
        except ValueError as exc:
            out.write(f"  Błąd: {exc}\n")
            out.flush()


def run_session(
    args: argparse.Namespace,
    *,
    input_fn: Callable[[str], str] = input,
    out: TextIO = sys.stdout,
    clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
    now_fn: Callable[[], datetime] | None = None,
) -> dict[str, Path | dict[str, str] | None]:
    """Execute one checkpoint session and persist annotations + checkpoints row."""
    now_provider = now_fn or (lambda: datetime.now().astimezone())
    recordings_dir = Path(args.recordings_dir)
    checkpoints_path = (
        Path(args.checkpoints_file)
        if args.checkpoints_file
        else recordings_dir / "checkpoints.csv"
    )
    steps = build_steps(args.step_seconds)

    person = (
        normalize_person(args.person)
        if args.person
        else _prompt_until_valid(
            "Imię uczestnika (np. adi, filip, rudy, wojtek): ",
            normalize_person,
            input_fn=input_fn,
            out=out,
        )
    )
    checkpoint = (
        normalize_checkpoint(args.checkpoint)
        if args.checkpoint
        else _prompt_until_valid(
            "Punkt pomiarowy (T0 / T1 / T2): ",
            normalize_checkpoint,
            input_fn=input_fn,
            out=out,
        )
    )
    if checkpoint not in VALID_CHECKPOINTS:
        out.write(
            f"Uwaga: nietypowy punkt {checkpoint!r} (standardowe: {', '.join(VALID_CHECKPOINTS)}).\n"
        )

    prior = existing_checkpoints(checkpoints_path)
    if (person, checkpoint) in prior:
        out.write(
            f"Uwaga: w {checkpoints_path} istnieje już wpis dla ({person}, {checkpoint}).\n"
        )

    task_hint = f"{person}-{checkpoint.lower()}"
    include_watch = (person == "wojtek" and not args.no_watch) or args.watch

    kss: int | None = parse_kss(args.kss) if args.kss is not None else None
    body_battery = parse_optional_number(
        args.body_battery, "body_battery", min_value=0, max_value=100, integer=True
    )
    stress = parse_optional_number(
        args.stress, "stress", min_value=0, max_value=100, integer=True
    )
    heart_rate = parse_optional_number(
        args.heart_rate, "heart_rate", min_value=20, max_value=250, integer=True
    )
    hrv_ms = parse_optional_number(args.hrv_ms, "hrv_ms", min_value=1, max_value=500)

    out.write(
        "\n=== Punkt pomiarowy Wachta ===\n"
        f"Uczestnik: {person} | Punkt: {checkpoint}\n"
        f"Nazwa zadania w BrainAccess Board: {task_hint}\n"
        "Pamiętaj: w BrainAccess Board zapisz tylko plik .fif (bez kopii CSV).\n"
    )
    if include_watch:
        out.write(
            "Garmin Venu 2: uruchom Health Snapshot podczas 2 min spoczynku "
            "(eyes_open + eyes_closed).\n"
        )
    out.flush()

    started_epoch: float | None = None
    if args.no_countdown:
        started_at = args.started_at or now_provider().isoformat(timespec="seconds")
    else:
        input_fn(
            f"\nWłącz nagrywanie w BrainAccess Board (zadanie '{task_hint}') "
            "i naciśnij Enter dokładnie w momencie startu..."
        )
        started_dt = now_provider()
        started_at = args.started_at or started_dt.isoformat(timespec="seconds")
        started_epoch = started_dt.timestamp()
        run_countdown(
            steps,
            out=out,
            bell=not args.no_bell,
            clock=clock,
            sleep=sleep,
        )

    if kss is None:
        out.write(f"\n{KSS_GUIDE}\n")
        out.flush()
        kss = _prompt_until_valid(
            "Ocena senności KSS (1–9): ",
            parse_kss,
            input_fn=input_fn,
            out=out,
        )

    if include_watch:
        if args.body_battery is None:
            body_battery = _prompt_until_valid(
                "Garmin Body Battery (0–100, Enter aby pominąć): ",
                lambda v: parse_optional_number(
                    v, "body_battery", min_value=0, max_value=100, integer=True
                ),
                input_fn=input_fn,
                out=out,
            )
        if args.stress is None:
            stress = _prompt_until_valid(
                "Garmin Stress (0–100, Enter aby pominąć): ",
                lambda v: parse_optional_number(
                    v, "stress", min_value=0, max_value=100, integer=True
                ),
                input_fn=input_fn,
                out=out,
            )
        if args.heart_rate is None:
            heart_rate = _prompt_until_valid(
                "Garmin Tętno [bpm] (Enter aby pominąć): ",
                lambda v: parse_optional_number(
                    v, "heart_rate", min_value=20, max_value=250, integer=True
                ),
                input_fn=input_fn,
                out=out,
            )
        if args.hrv_ms is None:
            hrv_ms = _prompt_until_valid(
                "Garmin HRV [ms] (Enter aby pominąć): ",
                lambda v: parse_optional_number(v, "hrv_ms", min_value=1, max_value=500),
                input_fn=input_fn,
                out=out,
            )

    recording_path: Path | None = Path(args.recording) if args.recording else None
    if recording_path is None and not args.no_prompt_recording:
        candidates = find_candidate_recordings(
            recordings_dir, person, checkpoint, started_epoch=started_epoch
        )
        default_rec = str(candidates[0]) if candidates else ""
        hint = f" [domyślnie: {candidates[0].name}]" if candidates else ""
        entered = input_fn(
            f"Ścieżka do pliku .fif{hint} (Enter = domyślny / brak): "
        ).strip()
        if entered:
            recording_path = Path(entered)
        elif default_rec:
            recording_path = Path(default_rec)

    annotations_written: Path | None = None
    if args.annotations_out:
        annotations_written = write_annotations(args.annotations_out, steps)
    elif recording_path is not None:
        annotations_written = write_annotations(
            annotations_path_for(recording_path), steps
        )

    notes = args.notes
    if notes is None and not args.no_prompt_notes:
        notes = input_fn("Uwagi (Enter aby pominąć): ").strip()

    row = {
        "person": person,
        "checkpoint": checkpoint,
        "started_at": started_at,
        "kss": str(kss),
        "body_battery": str(body_battery),
        "stress": str(stress),
        "heart_rate": str(heart_rate),
        "hrv_ms": str(hrv_ms),
        "recording_file": (
            format_recording_ref(recording_path, recordings_dir)
            if recording_path is not None
            else ""
        ),
        "notes": (notes or "").strip(),
    }
    saved_checkpoints = append_checkpoint_row(checkpoints_path, row)

    out.write("\nZapisano:\n")
    out.write(f"  - {saved_checkpoints}\n")
    if annotations_written is not None:
        out.write(f"  - {annotations_written}\n")
    else:
        out.write(
            "  - (adnotacje nie zostały zapisane — brak ścieżki do .fif; "
            "użyj --recording lub --annotations-out)\n"
        )
    out.flush()

    return {
        "checkpoints_path": saved_checkpoints,
        "annotations_path": annotations_written,
        "row": row,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m wachta.session",
        description="Narzędzie punktu pomiarowego Wachty (protokół 3x60 s, KSS, adnotacje i checkpoints.csv).",
    )
    parser.add_argument("--person", help="Imię uczestnika (np. adi, filip, rudy, wojtek)")
    parser.add_argument("--checkpoint", help="Punkt pomiarowy (np. T0, T1, T2)")
    parser.add_argument("--kss", type=int, help="Ocena senności KSS 1–9")
    parser.add_argument("--body-battery", help="Garmin Body Battery (0–100)")
    parser.add_argument("--stress", help="Garmin Stress (0–100)")
    parser.add_argument("--heart-rate", help="Tętno [bpm]")
    parser.add_argument("--hrv-ms", help="HRV [ms]")
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Pytaj o odczyty z zegarka Garmin nawet poza profilem Wojtka",
    )
    parser.add_argument(
        "--no-watch",
        action="store_true",
        help="Pomiń interaktywne pytania o odczyty z zegarka Garmin",
    )
    parser.add_argument("--recording", help="Ścieżka do pliku nagrania .fif")
    parser.add_argument(
        "--annotations-out",
        help="Jawna ścieżka wyjściowa dla pliku adnotacji CSV",
    )
    parser.add_argument(
        "--recordings-dir",
        default=str(DEFAULT_RECORDINGS_DIR),
        help="Folder z nagraniami (domyślnie: data/recordings)",
    )
    parser.add_argument(
        "--checkpoints-file",
        help="Ścieżka do checkpoints.csv (domyślnie: <recordings-dir>/checkpoints.csv)",
    )
    parser.add_argument(
        "--step-seconds",
        type=float,
        default=DEFAULT_STEP_SECONDS,
        help="Czas trwania każdego z 3 bloków EEG w sekundach (domyślnie: 60)",
    )
    parser.add_argument(
        "--started-at",
        help="Znacznik czasu rozpoczęcia ISO-8601 (przydatne z --no-countdown)",
    )
    parser.add_argument(
        "--notes",
        default=None,
        help="Dodatkowe uwagi do wiersza w checkpoints.csv",
    )
    parser.add_argument(
        "--no-countdown",
        action="store_true",
        help="Pomiń odliczanie w czasie rzeczywistym (np. przy uzupełnianiu po nagraniu)",
    )
    parser.add_argument(
        "--no-bell",
        action="store_true",
        help="Wyłącz sygnał dźwiękowy terminala przy zmianie kroku",
    )
    parser.add_argument(
        "--no-prompt-recording",
        action="store_true",
        help="Nie pytaj interaktywnie o plik .fif, gdy --recording nie jest podane",
    )
    parser.add_argument(
        "--no-prompt-notes",
        action="store_true",
        help="Nie pytaj interaktywnie o uwagi, gdy --notes nie jest podane",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_session(args)
    except KeyboardInterrupt:
        sys.stdout.write("\nPrzerwano sesję pomiarową (nic nie zapisano).\n")
        return 130
    except ValueError as exc:
        sys.stderr.write(f"Błąd: {exc}\n")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
