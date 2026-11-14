"""Merge and summarize team checkpoints (KSS + Garmin Venu 2) and PVT-B results.

Combines ``data/recordings/checkpoints.csv`` (written by ``python -m wachta.session``)
and ``data/recordings/pvt.csv`` (written by ``python -m wachta.pvt``) by
``(person, checkpoint)``, computes within-person changes relative to ``T0``, prints a
slide-ready Markdown table in Polish and optionally writes a merged CSV and PNG chart.

Run with:
    python -m wachta.summary
    python experiments/summarize-checkpoints.py --figure docs/img/checkpoints-summary.png
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys
from typing import Any, Sequence, TextIO

from .pvt import DEFAULT_RESULTS_FILE as DEFAULT_PVT_FILE
from .session import DEFAULT_RECORDINGS_DIR, VALID_CHECKPOINTS, normalize_checkpoint, normalize_person

DEFAULT_CHECKPOINTS_FILE = DEFAULT_RECORDINGS_DIR / "checkpoints.csv"

MERGED_FIELDS = (
    "person",
    "checkpoint",
    "started_at",
    "kss",
    "delta_kss",
    "median_rt_ms",
    "delta_median_rt_ms",
    "mean_rt_ms",
    "lapses",
    "false_starts",
    "mean_speed",
    "performance_score",
    "body_battery",
    "delta_body_battery",
    "stress",
    "heart_rate",
    "hrv_ms",
    "delta_hrv_ms",
    "recording_file",
    "notes",
)


def _opt_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(round(float(str(value).strip().replace(",", "."))))


def _opt_float(value: Any, digits: int = 3) -> float | None:
    if value in (None, ""):
        return None
    return round(float(str(value).strip().replace(",", ".")), digits)


def _checkpoint_sort_key(cp: str) -> tuple[int, str]:
    if cp in VALID_CHECKPOINTS:
        return (VALID_CHECKPOINTS.index(cp), cp)
    if cp.startswith("T") and cp[1:].isdigit():
        return (int(cp[1:]), cp)
    return (999, cp)


def _read_keyed_csv(path: Path | str) -> dict[tuple[str, str], dict[str, str]]:
    file_path = Path(path)
    if not file_path.exists() or file_path.stat().st_size == 0:
        return {}
    records: dict[tuple[str, str], dict[str, str]] = {}
    with file_path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            raw_person = (row.get("person") or "").strip()
            raw_cp = (row.get("checkpoint") or "").strip()
            if not raw_person or not raw_cp:
                continue
            key = (normalize_person(raw_person), normalize_checkpoint(raw_cp))
            records[key] = row
    return records


def _diff_int(current: int | None, base: int | None) -> int | None:
    if current is None or base is None:
        return None
    return current - base


def _diff_float(current: float | None, base: float | None, digits: int = 1) -> float | None:
    if current is None or base is None:
        return None
    return round(current - base, digits)


def load_and_merge(
    checkpoints_path: Path | str = DEFAULT_CHECKPOINTS_FILE,
    pvt_path: Path | str = DEFAULT_PVT_FILE,
) -> list[dict[str, Any]]:
    """Load ``checkpoints.csv`` and ``pvt.csv``, outer-join on ``(person, checkpoint)`` and compute deltas vs ``T0``."""
    cp_rows = _read_keyed_csv(checkpoints_path)
    pvt_rows = _read_keyed_csv(pvt_path)

    all_keys = sorted(
        set(cp_rows) | set(pvt_rows),
        key=lambda item: (item[0], _checkpoint_sort_key(item[1])),
    )

    merged: list[dict[str, Any]] = []
    for person, checkpoint in all_keys:
        cp = cp_rows.get((person, checkpoint), {})
        pv = pvt_rows.get((person, checkpoint), {})
        merged.append(
            {
                "person": person,
                "checkpoint": checkpoint,
                "started_at": (cp.get("started_at") or pv.get("started_at") or "").strip(),
                "kss": _opt_int(cp.get("kss")),
                "delta_kss": None,
                "median_rt_ms": _opt_float(pv.get("median_rt_ms"), 1),
                "delta_median_rt_ms": None,
                "mean_rt_ms": _opt_float(pv.get("mean_rt_ms"), 1),
                "lapses": _opt_int(pv.get("lapses")),
                "false_starts": _opt_int(pv.get("false_starts")),
                "mean_speed": _opt_float(pv.get("mean_speed"), 3),
                "performance_score": _opt_float(pv.get("performance_score"), 3),
                "body_battery": _opt_int(cp.get("body_battery")),
                "delta_body_battery": None,
                "stress": _opt_int(cp.get("stress")),
                "heart_rate": _opt_int(cp.get("heart_rate")),
                "hrv_ms": _opt_float(cp.get("hrv_ms"), 1),
                "delta_hrv_ms": None,
                "recording_file": (cp.get("recording_file") or "").strip(),
                "notes": (cp.get("notes") or "").strip(),
            }
        )

    t0_by_person = {row["person"]: row for row in merged if row["checkpoint"] == "T0"}
    for row in merged:
        base = t0_by_person.get(row["person"])
        if base is None:
            continue
        row["delta_kss"] = _diff_int(row["kss"], base["kss"])
        row["delta_median_rt_ms"] = _diff_float(row["median_rt_ms"], base["median_rt_ms"], 1)
        row["delta_body_battery"] = _diff_int(row["body_battery"], base["body_battery"])
        row["delta_hrv_ms"] = _diff_float(row["hrv_ms"], base["hrv_ms"], 1)

    return merged


def _pl_num(value: int | float | None, digits: int | None = None, signed: bool = False) -> str:
    if value is None:
        return "—"
    if digits is None or isinstance(value, int):
        fmt = f"{int(value):+d}" if signed else f"{int(value):d}"
        return fmt
    fmt = f"{float(value):+.{digits}f}" if signed else f"{float(value):.{digits}f}"
    return fmt.replace(".", ",")


def _with_delta(
    value: int | float | None,
    delta: int | float | None,
    *,
    checkpoint: str,
    digits: int | None = None,
) -> str:
    if value is None:
        return "—"
    base_str = _pl_num(value, digits=digits, signed=False)
    if checkpoint == "T0" or delta is None:
        return base_str
    return f"{base_str} ({_pl_num(delta, digits=digits, signed=True)})"


def format_markdown_table(rows: Sequence[dict[str, Any]]) -> str:
    """Format merged checkpoint rows as a Markdown table in Polish."""
    lines = [
        "| Osoba | Punkt | KSS (1–9) | PVT mediana [ms] | PVT lapsy | PVT 1/RT [1/s] | "
        "Body Battery | Stress | Tętno [bpm] | HRV [ms] |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        cp = row["checkpoint"]
        lines.append(
            f"| {row['person']} | {cp} | "
            f"{_with_delta(row['kss'], row['delta_kss'], checkpoint=cp)} | "
            f"{_with_delta(row['median_rt_ms'], row['delta_median_rt_ms'], checkpoint=cp, digits=1)} | "
            f"{_pl_num(row['lapses'])} | "
            f"{_pl_num(row['mean_speed'], digits=2)} | "
            f"{_with_delta(row['body_battery'], row['delta_body_battery'], checkpoint=cp)} | "
            f"{_pl_num(row['stress'])} | "
            f"{_pl_num(row['heart_rate'])} | "
            f"{_with_delta(row['hrv_ms'], row['delta_hrv_ms'], checkpoint=cp, digits=1)} |"
        )
    return "\n".join(lines)


def write_merged_csv(path: Path | str, rows: Sequence[dict[str, Any]]) -> Path:
    """Write merged rows to a CSV file with ``MERGED_FIELDS`` columns."""
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=MERGED_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {field: "" if row.get(field) is None else row.get(field) for field in MERGED_FIELDS}
            )
    return out_path


def _load_pil_font(size: int, bold: bool = False):
    from PIL import ImageFont

    candidates = (
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        )
        if bold
        else (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        )
    )
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size), True
            except OSError:
                continue
    return ImageFont.load_default(), False


_PL_ASCII = str.maketrans("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ–—", "acelnoszzACELNOSZZ--")


def _save_figure_pillow(rows: Sequence[dict[str, Any]], path: Path) -> None:
    from PIL import Image, ImageDraw

    width, height = 1080, 420
    img = Image.new("RGB", (width, height), (252, 252, 251))
    draw = ImageDraw.Draw(img)
    font_title, has_utf8 = _load_pil_font(15, bold=True)
    font_panel, _ = _load_pil_font(12, bold=True)
    font_body, _ = _load_pil_font(11, bold=False)

    def txt(s: str) -> str:
        return s if has_utf8 else s.translate(_PL_ASCII)

    ink = (15, 15, 15)
    muted = (115, 113, 108)
    grid = (225, 224, 217)
    palette = [
        (42, 120, 214),
        (208, 59, 59),
        (39, 150, 92),
        (214, 134, 32),
    ]

    draw.text(
        (28, 16),
        txt("Punkty pomiarowe zespołu (T0 / T1 / T2): KSS, PVT-B i Garmin Venu 2"),
        fill=ink,
        font=font_title,
    )
    draw.text(
        (28, 38),
        txt("Każda linia to jedna osoba; porównanie zmian w trakcie pracy"),
        fill=muted,
        font=font_body,
    )

    panels = [
        ("Senność KSS (1–9)", "kss", 1.0, 9.0),
        ("PVT-B mediana RT [ms]", "median_rt_ms", 180.0, 500.0),
        ("Garmin Body Battery (0–100)", "body_battery", 0.0, 100.0),
    ]
    checkpoints = list(VALID_CHECKPOINTS)
    people = sorted({r["person"] for r in rows})
    by_key = {(r["person"], r["checkpoint"]): r for r in rows}

    panel_w = 290
    top, bottom = 90, 355
    for idx, (title, field, vmin, vmax) in enumerate(panels):
        left = 54 + idx * (panel_w + 54)
        right = left + panel_w
        draw.text((left, top - 24), txt(title), fill=ink, font=font_panel)
        for frac in (0.0, 0.5, 1.0):
            y = int(bottom - frac * (bottom - top))
            draw.line([(left, y), (right, y)], fill=grid, width=1)
            val = vmin + frac * (vmax - vmin)
            draw.text((left - 36, y - 7), f"{val:.0f}", fill=muted, font=font_body)

        xs = [int(left + i * (panel_w // max(1, len(checkpoints) - 1))) for i in range(len(checkpoints))]
        for x, cp in zip(xs, checkpoints):
            draw.text((x - 8, bottom + 8), cp, fill=muted, font=font_body)

        for p_idx, person in enumerate(people):
            color = palette[p_idx % len(palette)]
            pts: list[tuple[int, int]] = []
            for x, cp in zip(xs, checkpoints):
                rec = by_key.get((person, cp))
                val = rec.get(field) if rec else None
                if val is None:
                    continue
                norm = max(0.0, min(1.0, (float(val) - vmin) / max(1e-6, vmax - vmin)))
                y = int(bottom - norm * (bottom - top))
                pts.append((x, y))
            if len(pts) >= 2:
                draw.line(pts, fill=color, width=3)
            for x, y in pts:
                draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=color)

    for p_idx, person in enumerate(people):
        color = palette[p_idx % len(palette)]
        lx = 54 + p_idx * 140
        draw.rectangle((lx, height - 26, lx + 16, height - 16), fill=color)
        draw.text((lx + 22, height - 28), txt(person), fill=ink, font=font_body)

    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", optimize=True)


def save_summary_figure(rows: Sequence[dict[str, Any]], path: Path | str) -> Path:
    """Save a compact 3-panel PNG chart (< 300 kB) of KSS, PVT median RT and Garmin Body Battery."""
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        _save_figure_pillow(rows, out_path)
        return out_path

    checkpoints = list(VALID_CHECKPOINTS)
    people = sorted({r["person"] for r in rows})
    by_key = {(r["person"], r["checkpoint"]): r for r in rows}
    palette = ["#2a78d6", "#d03b3b", "#27965c", "#d68620"]

    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.6), facecolor="#fcfcfb")
    specs = [
        ("Senność KSS (1–9)", "kss", (1, 9)),
        ("PVT-B mediana RT [ms]", "median_rt_ms", None),
        ("Garmin Body Battery (0–100)", "body_battery", (0, 100)),
    ]
    for ax, (title, field, ylim) in zip(axes, specs):
        ax.set_facecolor("#fcfcfb")
        for p_idx, person in enumerate(people):
            xs, ys = [], []
            for idx, cp in enumerate(checkpoints):
                rec = by_key.get((person, cp))
                val = rec.get(field) if rec else None
                if val is not None:
                    xs.append(idx)
                    ys.append(float(val))
            if xs:
                ax.plot(xs, ys, marker="o", lw=1.8, color=palette[p_idx % len(palette)], label=person)
        ax.set_xticks(range(len(checkpoints)), checkpoints)
        ax.set_title(title, loc="left", fontsize=9.5, fontweight="bold")
        if ylim:
            ax.set_ylim(*ylim)
        ax.grid(axis="y", color="#e1e0d9", lw=0.8)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)

    if people:
        axes[0].legend(frameon=False, fontsize=8.5)
    fig.suptitle(
        "Punkty pomiarowe zespołu (T0 / T1 / T2): KSS, PVT-B i Garmin Venu 2",
        x=0.01,
        y=0.98,
        ha="left",
        fontsize=11.5,
        fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.91))
    fig.savefig(out_path, dpi=120, facecolor="#fcfcfb")
    plt.close(fig)
    return out_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m wachta.summary",
        description="Podsumowanie punktów pomiarowych (checkpoints.csv + pvt.csv): tabela Markdown, CSV i wykres.",
    )
    parser.add_argument(
        "--checkpoints",
        default=str(DEFAULT_CHECKPOINTS_FILE),
        help="Ścieżka do checkpoints.csv (domyślnie: data/recordings/checkpoints.csv)",
    )
    parser.add_argument(
        "--pvt",
        default=str(DEFAULT_PVT_FILE),
        help="Ścieżka do pvt.csv (domyślnie: data/recordings/pvt.csv)",
    )
    parser.add_argument("--out-csv", help="Zapisz połączoną tabelę do pliku CSV")
    parser.add_argument("--figure", help="Zapisz wykres PNG (np. docs/img/checkpoints-summary.png)")
    return parser


def main(argv: Sequence[str] | None = None, *, out: TextIO = sys.stdout) -> int:
    args = build_parser().parse_args(argv)
    rows = load_and_merge(args.checkpoints, args.pvt)
    if not rows:
        out.write(
            f"Brak danych w {args.checkpoints} i {args.pvt}. "
            "Uruchom najpierw `python -m wachta.session` lub `python -m wachta.pvt`.\n"
        )
        return 0

    out.write(format_markdown_table(rows) + "\n")
    if args.out_csv:
        write_merged_csv(args.out_csv, rows)
        out.write(f"\nZapisano połączony CSV: {args.out_csv}\n")
    if args.figure:
        save_summary_figure(rows, args.figure)
        out.write(f"Zapisano wykres: {args.figure}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
