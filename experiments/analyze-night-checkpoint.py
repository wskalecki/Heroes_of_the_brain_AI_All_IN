"""Night checkpoint analysis: vigilance index during monotony, KSS, PVT-B and heart (task C4).

Usage:
    python experiments/analyze-night-checkpoint.py
    python experiments/analyze-night-checkpoint.py --fit wojtek-n1=~/Downloads/activity.fit --figure docs/img/noc-vs-dzien.png

Protocol: docs/protokol-nocny.md.
"""

import argparse
from pathlib import Path

from wachta.config import Config
from wachta.night import (
    analyze_signals, format_table, heart_per_block, heart_per_minute, load_fit, parse_started_at, save_figure,
    save_minutes_figure, task_parts,
)
from wachta.recordings import DEFAULT_DIR, find_recordings, load_annotations, load_eeg
from wachta.summary import load_and_merge


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--recordings", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--fit", nargs="*", default=[], metavar="TASK=PLIK",
                        help="Garmin FIT file for a recording, e.g. wojtek-n1=activity.fit")
    parser.add_argument("--figure", type=Path, help="save a PNG comparing checkpoints (KSS, PVT, alpha)")
    parser.add_argument("--minutes-figure", type=Path, help="save a PNG with the minute-by-minute monotony course")
    args = parser.parse_args()

    fits = {}
    for item in args.fit:
        task, _, path = item.partition("=")
        if not path:
            raise SystemExit(f"--fit expects TASK=FILE, got {item!r}")
        fits[task.lower()] = Path(path).expanduser()

    merged = {(r["person"], r["checkpoint"]): r for r in load_and_merge(
        args.recordings / "checkpoints.csv", args.recordings / "pvt.csv")}
    cfg = Config()
    rows = []
    for task, path in find_recordings(args.recordings).items():
        parts = task_parts(task)
        blocks = load_annotations(path)
        if parts is None or not any(b.label == "monotony" for b in blocks):
            continue
        eeg, _ = load_eeg(path)
        row = {"person": parts[0], "checkpoint": parts[1], **analyze_signals(eeg, blocks, cfg)}
        info = merged.get(parts, {})
        row.update(kss=info.get("kss"), pvt_lapses=info.get("lapses"), median_rt_ms=info.get("median_rt_ms"))
        if task in fits:
            started = parse_started_at(info.get("started_at", ""))
            if started is None:
                print(f"{task}: brak started_at w checkpoints.csv, pomijam plik FIT")
            else:
                heart_rate, rr = load_fit(fits[task])
                row["heart"] = heart_per_block(started, blocks, heart_rate, rr)
                monotony = next(b for b in blocks if b.label == "monotony")
                row["hr_minutes"] = heart_per_minute(started, monotony, heart_rate)
                if not rr:
                    print(f"{task}: plik FIT nie ma odstępów R–R, liczę tylko tętno")
        rows.append(row)

    if not rows:
        raise SystemExit(f"Brak nagrań z blokiem 'monotony' w {args.recordings}. Protokół: docs/protokol-nocny.md")
    rows.sort(key=lambda r: (r["person"], r["checkpoint"][0] != "T", r["checkpoint"]))
    print(format_table(rows))
    if args.figure:
        print(f"\nWykres: {save_figure(rows, args.figure)}")
    if args.minutes_figure:
        print(f"Wykres minuta po minucie: {save_minutes_figure(rows, args.minutes_figure)}")


if __name__ == "__main__":
    main()
