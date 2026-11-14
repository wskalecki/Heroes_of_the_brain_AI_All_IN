"""Analysis of checkpoint recordings with a monotony block (night protocol, task C4).

For every recording whose annotations contain a ``monotony`` block, the recording
goes through the same pipeline as the demo (calibration on the ``eyes_open``
block) and we summarise how the vigilance index behaves during monotonous
sitting with open eyes: early versus late minutes, reaction probes the system
would ask for, lapses and their kind, blink rate. Results are joined with KSS and
PVT-B from ``checkpoints.csv`` and ``pvt.csv``. A Garmin FIT file recorded in
parallel (chest strap paired with the watch) adds heart rate and, if the file
contains beat-to-beat intervals, RMSSD per block.

Run with:
    python experiments/analyze-night-checkpoint.py
    python experiments/analyze-night-checkpoint.py --fit wojtek-n1=~/Downloads/activity.fit --figure docs/img/noc-vs-dzien.png
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np

from .config import Config
from .pipeline import run_offline
from .recordings import Block

EARLY_LATE_S = 120.0          # compare the first and the last two minutes of monotony
RR_MIN_MS, RR_MAX_MS = 300.0, 2000.0


def _mean(values: Iterable[float | None]) -> float | None:
    kept = [v for v in values if v is not None and not (isinstance(v, float) and math.isnan(v))]
    return float(np.mean(kept)) if kept else None


def task_parts(task: str) -> tuple[str, str] | None:
    """``wojtek-n1`` -> (``wojtek``, ``N1``); None when the task name has no checkpoint."""
    person, sep, checkpoint = task.rpartition("-")
    if not sep or not person or not checkpoint:
        return None
    return person.lower(), checkpoint.upper()


def analyze_signals(eeg_volts: np.ndarray, blocks: Sequence[Block], cfg: Config | None = None) -> dict[str, Any] | None:
    """Summarise one recording; returns None when it has no ``monotony`` block."""
    cfg = cfg or Config()
    monotony = next((b for b in blocks if b.label == "monotony"), None)
    if monotony is None:
        return None
    results = run_offline(eeg_volts, cfg)
    calibrated = [r for r in results if r["calibrated"]]

    def window_in(r: dict, start: float, end: float) -> bool:
        return start + cfg.win_s <= r["t"] <= end

    closed = next((b for b in blocks if b.label == "eyes_closed"), None)
    eyes_closed_detected = None
    if closed is not None:
        eyes_closed_detected = any(r["new_lapse"] and closed.onset <= r["t"] <= closed.end for r in calibrated)

    inside = [r for r in results if window_in(r, monotony.onset, monotony.end)]
    early = [r for r in inside if r["t"] <= monotony.onset + EARLY_LATE_S]
    late = [r for r in inside if r["t"] >= monotony.end - EARLY_LATE_S]

    # One kind per lapse: the kind most windows of that lapse had.
    lapses, current = [], []
    for r in inside:
        if r["lapse"]:
            current.append(r["lapse_kind"] or "unknown")
        elif current:
            lapses.append(max(set(current), key=current.count))
            current = []
    if current:
        lapses.append(max(set(current), key=current.count))

    def blink_rate_at(t: float) -> float | None:
        before = [r for r in results if r["t"] <= t]
        return before[-1]["blinks_per_min"] if before else None

    # Minute-by-minute course of the monotony block (the main view for a single person).
    minutes = []
    n_minutes = int(round(monotony.duration / 60.0))
    for k in range(n_minutes):
        start, end = monotony.onset + 60.0 * k, monotony.onset + 60.0 * (k + 1)
        in_minute = [r for r in results if start < r["t"] <= end]
        fast = _mean(r["fast"] for r in in_minute)
        minutes.append({
            "minute": k + 1,
            "fast": None if fast is None else round(fast, 2),
            "blinks": blink_rate_at(end),
            "rejected_pct": round(100.0 * np.mean([r["bad"] for r in in_minute]), 1) if in_minute else None,
            "lapse": any(r["lapse"] for r in in_minute),
        })

    fast_early = _mean(r["fast"] for r in early)
    fast_late = _mean(r["fast"] for r in late)
    return {
        "calibrated": bool(calibrated),
        "eyes_closed_detected": eyes_closed_detected,
        "monotony_min": round(monotony.duration / 60.0, 1),
        "rejected_pct": round(100.0 * np.mean([r["bad"] for r in inside]), 1) if inside else None,
        "fast_early": None if fast_early is None else round(fast_early, 2),
        "fast_late": None if fast_late is None else round(fast_late, 2),
        "fast_change": None if fast_early is None or fast_late is None else round(fast_late - fast_early, 2),
        "probes": sum(1 for r in inside if r["probe"]),
        "lapses": len(lapses),
        "lapses_eyes_open": lapses.count("eyes_open"),
        "lapses_eyes_closed": lapses.count("eyes_closed"),
        "blinks_early": blink_rate_at(monotony.onset + EARLY_LATE_S),
        "blinks_late": blink_rate_at(monotony.end),
        "minutes": minutes,
    }


# -- Garmin FIT (chest strap paired with the watch) ---------------------------------


def heart_from_frames(frames: Iterable[Any]) -> tuple[list[tuple[datetime, float]], list[tuple[datetime, float]]]:
    """Extract (time, bpm) and (time, RR ms) from decoded FIT data messages.

    ``record`` messages give heart rate with timestamps. ``hrv`` messages give
    beat-to-beat intervals without timestamps; they are placed by accumulating the
    intervals from the first record timestamp, which is accurate to a few seconds.
    """
    heart_rate: list[tuple[datetime, float]] = []
    intervals: list[float] = []
    for frame in frames:
        name = getattr(frame, "name", None)
        if name == "record":
            stamp = frame.get_value("timestamp", fallback=None)
            bpm = frame.get_value("heart_rate", fallback=None)
            if stamp is not None and bpm is not None:
                heart_rate.append((stamp, float(bpm)))
        elif name == "hrv":
            values = frame.get_value("time", fallback=None)
            if values is None:
                continue
            for value in values if isinstance(values, (list, tuple)) else [values]:
                if value is not None and value < 60:          # seconds; 65.535 marks "invalid"
                    intervals.append(float(value) * 1000.0)
    rr: list[tuple[datetime, float]] = []
    if intervals and heart_rate:
        clock = heart_rate[0][0]
        for ms in intervals:
            clock = clock + timedelta(milliseconds=ms)
            rr.append((clock, ms))
    return heart_rate, rr


def load_fit(path: Path | str) -> tuple[list[tuple[datetime, float]], list[tuple[datetime, float]]]:
    try:
        import fitdecode
    except ImportError as error:
        raise RuntimeError('Brak biblioteki fitdecode. Zainstaluj: pip install -e ".[analysis]"') from error
    with fitdecode.FitReader(str(path)) as reader:
        frames = [f for f in reader if isinstance(f, fitdecode.FitDataMessage)]
    return heart_from_frames(frames)


def rmssd(rr_ms: Sequence[float]) -> float | None:
    """RMSSD of plausible intervals; successive jumps over 20% are treated as artefacts."""
    clean = [v for v in rr_ms if RR_MIN_MS <= v <= RR_MAX_MS]
    diffs = [b - a for a, b in zip(clean, clean[1:]) if abs(b - a) <= 0.2 * a]
    if len(diffs) < 10:
        return None
    return float(np.sqrt(np.mean(np.square(diffs))))


def heart_per_block(
    started_at: datetime,
    blocks: Sequence[Block],
    heart_rate: Sequence[tuple[datetime, float]],
    rr: Sequence[tuple[datetime, float]],
) -> dict[str, dict[str, float | None]]:
    """Mean heart rate and RMSSD for every protocol block, by wall-clock time."""
    out = {}
    for block in blocks:
        start = started_at + timedelta(seconds=block.onset)
        end = started_at + timedelta(seconds=block.end)
        hr = [v for t, v in heart_rate if start <= t < end]
        beats = [v for t, v in rr if start <= t < end]
        out[block.label] = {
            "hr": None if not hr else round(float(np.mean(hr)), 1),
            "rmssd": None if (value := rmssd(beats)) is None else round(value, 1),
        }
    return out


def heart_per_minute(
    started_at: datetime, block: Block, heart_rate: Sequence[tuple[datetime, float]]
) -> list[float | None]:
    """Mean heart rate in each minute of one block."""
    out = []
    for k in range(int(round(block.duration / 60.0))):
        start = started_at + timedelta(seconds=block.onset + 60.0 * k)
        values = [v for t, v in heart_rate if start <= t < start + timedelta(seconds=60)]
        out.append(None if not values else round(float(np.mean(values)), 1))
    return out


def parse_started_at(text: str) -> datetime | None:
    try:
        stamp = datetime.fromisoformat(text)
    except (TypeError, ValueError):
        return None
    return stamp if stamp.tzinfo else stamp.astimezone()


# -- report ---------------------------------------------------------------------------


def _pl(value: Any, digits: int = 1, signed: bool = False) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "tak" if value else "nie"
    if isinstance(value, int):
        return f"{value:+d}" if signed else str(value)
    text = f"{value:+.{digits}f}" if signed else f"{value:.{digits}f}"
    return text.replace(".", ",")


def format_table(rows: Sequence[dict[str, Any]]) -> str:
    head = ("| Osoba | Punkt | KSS | PVT: lapsy | PVT: mediana RT | Alfa (z) min. 1–2 | Alfa (z) ostatnie 2 min | Zmiana | "
            "Próby reakcji | Spadki (oczy otwarte / zamknięte) | Mrugnięcia/min początek → koniec | "
            "Tętno spoczynek → monotonia | RMSSD spoczynek → monotonia | Oczy zamknięte wykryte |")
    lines = [head, "|" + "---|" * (head.count("|") - 1)]
    for r in rows:
        heart = r.get("heart") or {}
        rest, mono = heart.get("eyes_open", {}), heart.get("monotony", {})
        lines.append(
            f"| {r['person']} | {r['checkpoint']} | {_pl(r.get('kss'))} | {_pl(r.get('pvt_lapses'))} | "
            f"{_pl(r.get('median_rt_ms'), 0)} ms | {_pl(r.get('fast_early'), 2)} | {_pl(r.get('fast_late'), 2)} | "
            f"{_pl(r.get('fast_change'), 2, signed=True)} | {_pl(r.get('probes'))} | "
            f"{r.get('lapses_eyes_open', '—')} / {r.get('lapses_eyes_closed', '—')} | "
            f"{_pl(r.get('blinks_early'), 0)} → {_pl(r.get('blinks_late'), 0)} | "
            f"{_pl(rest.get('hr'), 0)} → {_pl(mono.get('hr'), 0)} | {_pl(rest.get('rmssd'), 0)} → {_pl(mono.get('rmssd'), 0)} | "
            f"{_pl(r.get('eyes_closed_detected'))} |"
        )
    return "\n".join(lines)


def save_figure(rows: Sequence[dict[str, Any]], path: Path | str) -> Path:
    """Three small panels per checkpoint, one line per person: KSS, PVT lapses, late-monotony alpha."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    surface, ink, ink2, muted, grid = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
    palette = ["#2a78d6", "#eb6834", "#1baf7a", "#6250d6"]
    people = sorted({r["person"] for r in rows})
    order = sorted({r["checkpoint"] for r in rows}, key=lambda c: (c[0] != "T", c))
    panels = [("kss", "Senność (KSS, 1–9)"), ("pvt_lapses", "Lapsy w teście reakcji"), ("fast_late", "Alfa w monotonii (z), ostatnie 2 min")]

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6), facecolor=surface)
    for ax, (key, title) in zip(axes, panels):
        ax.set_facecolor(surface)
        for i, person in enumerate(people):
            series = [(order.index(r["checkpoint"]), r.get(key)) for r in rows if r["person"] == person and r.get(key) is not None]
            series.sort()
            if not series:
                continue
            xs, ys = zip(*series)
            color = palette[i % len(palette)]
            ax.plot(xs, ys, color=color, lw=2, marker="o", ms=6, mec=surface, mew=2)
            ax.annotate(person, (xs[-1], ys[-1]), xytext=(6, 0), textcoords="offset points", va="center", fontsize=8, color=ink2)
        ax.set_xticks(range(len(order)), order)
        if key != "fast_late":
            from matplotlib.ticker import MaxNLocator
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_title(title, loc="left", fontsize=9.5, color=ink, fontweight="bold")
        ax.grid(axis="y", color=grid, lw=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(colors=muted, length=0)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color("#c3c2b7")
        ax.set_xlim(-0.3, len(order) - 0.4)
    fig.suptitle("Dzień (T) a noc (N): ocena senności, test reakcji i EEG", x=0.01, ha="left", fontsize=12, fontweight="bold", color=ink)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=130, facecolor=surface)
    plt.close(fig)
    return out


def save_minutes_figure(rows: Sequence[dict[str, Any]], path: Path | str) -> Path:
    """Minute-by-minute monotony course, one line per session: alpha index, blinks and heart rate."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    surface, ink, ink2, muted, grid = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
    palette = ["#2a78d6", "#eb6834", "#1baf7a", "#6250d6"]
    sessions = sorted(rows, key=lambda r: (r["person"], r["checkpoint"][0] != "T", r["checkpoint"]))
    several_people = len({r["person"] for r in rows}) > 1
    has_heart = any(r.get("hr_minutes") for r in rows)
    panels = [("fast", "Wskaźnik alfy (z-score względem kalibracji)"), ("blinks", "Mrugnięcia na minutę")]
    if has_heart:
        panels.append(("hr", "Tętno z paska [bpm]"))

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    fig, axes = plt.subplots(1, len(panels), figsize=(3.9 * len(panels), 3.7), facecolor=surface)
    for ax, (key, title) in zip(axes, panels):
        ax.set_facecolor(surface)
        for i, row in enumerate(sessions[: len(palette)]):
            label = f"{row['person']} {row['checkpoint']}" if several_people else row["checkpoint"]
            if key == "hr":
                values = list(enumerate(row.get("hr_minutes") or [], start=1))
            else:
                values = [(m["minute"], m[key]) for m in row.get("minutes", [])]
            points = [(x, y) for x, y in values if y is not None]
            if not points:
                continue
            xs, ys = zip(*points)
            color = palette[i]
            ax.plot(xs, ys, color=color, lw=2, marker="o", ms=5, mec=surface, mew=1.5)
            ax.annotate(label, (xs[-1], ys[-1]), xytext=(6, 0), textcoords="offset points", va="center", fontsize=8, color=ink2)
            if key == "fast":
                for m in row.get("minutes", []):
                    if m["lapse"] and m["fast"] is not None:
                        ax.plot(m["minute"], m["fast"], marker="o", ms=9, mfc="none", mec="#d03b3b", mew=1.8)
        if key == "fast":
            ax.axhline(0, color="#c3c2b7", lw=1)
            threshold = Config().z_enter
            ax.axhline(threshold, color=ink2, lw=1)
            ax.annotate(f"próg alarmu {threshold:g}".replace(".", ","), (1, threshold), xytext=(0, 4),
                        textcoords="offset points", fontsize=8, color=ink2)
            low, high = ax.get_ylim()
            ax.set_ylim(min(low, -0.5), max(high, threshold + 0.8))
        if key == "blinks":
            ax.set_ylim(bottom=0, top=max(10.0, ax.get_ylim()[1] * 1.1))
        ax.set_title(title, loc="left", fontsize=9.5, color=ink, fontweight="bold")
        ax.set_xlabel("minuta monotonii", color=ink2, fontsize=8.5)
        ax.grid(axis="y", color=grid, lw=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(colors=muted, length=0)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color("#c3c2b7")
    fig.suptitle("Monotonia minuta po minucie", x=0.01, ha="left", fontsize=12, fontweight="bold", color=ink)
    fig.text(0.01, 0.885, "Czerwone kółko: minuta z wykrytym spadkiem czujności.", fontsize=8.5, color=ink2)
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=130, facecolor=surface)
    plt.close(fig)
    return out
