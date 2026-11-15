"""Accuracy of the streaming pipeline on the annotated team recordings.

Runs each recording in ``data/recordings`` through the same pipeline the demo
uses and compares detected vigilance lapses with the ``eyes_closed`` block from
the protocol annotations. Voluntary eye closure stands in for a real lapse.

Usage:
    python experiments/validate-on-recordings.py
    python experiments/validate-on-recordings.py --figure docs/img/trafnosc-na-nagraniach.png
"""

import argparse
from pathlib import Path

import numpy as np

from wachta.config import Config
from wachta.pipeline import run_offline
from wachta.recordings import DEFAULT_DIR, find_recordings, load_annotations, load_eeg

BLOCK_NAMES = {
    "neutral": "spoczynek",
    "eyes_open": "oczy otwarte",
    "eyes_closed": "oczy zamknięte",
    "reading": "czytanie",
    "math": "liczenie",
    "control": "kontrolne",
    "monotony": "monotonia",
}


def auc(positive: list[float], negative: list[float]) -> float:
    """Probability that a positive window scores above a negative one."""
    if not positive or not negative:
        return float("nan")
    values = np.concatenate([positive, negative])
    ranks = values.argsort().argsort() + 1
    n_pos, n_neg = len(positive), len(negative)
    return float((ranks[:n_pos].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def block_label(t_end: float, blocks, win_s: float) -> str:
    """Label of the block that fully contains the window ending at ``t_end``."""
    for block in blocks:
        if t_end - win_s >= block.onset and t_end <= block.end:
            return block.label
    return "transition"


def evaluate(name: str, path: Path, cfg: Config) -> dict:
    eeg, _ = load_eeg(path)
    blocks = load_annotations(path)
    results = run_offline(eeg, cfg)
    target = next((b for b in blocks if b.label == "eyes_closed"), None)
    if target is None:
        raise ValueError(f"{name}: no eyes_closed block in the annotations")

    calibrated = [r for r in results if r["calibrated"]]
    labels = [block_label(r["t"], blocks, cfg.win_s) for r in calibrated]
    inside = [r for r, lab in zip(calibrated, labels) if lab == "eyes_closed"]
    outside = [r for r, lab in zip(calibrated, labels) if lab not in ("eyes_closed", "transition")]

    starts = [r["t"] for r in calibrated if r["new_lapse"]]
    hits = [t for t in starts if target.onset <= t <= target.end]
    false_alarms = [t for t in starts if not target.onset <= t <= target.end + cfg.win_s]
    outside_minutes = len(outside) * cfg.step_s / 60.0

    # Eye state (A7) and reaction probes (A8).
    lapse_in_block = [r for r in inside if r["lapse"]]
    eyes_closed_share = (
        100.0 * np.mean([r["lapse_kind"] == "eyes_closed" for r in lapse_in_block]) if lapse_in_block else float("nan")
    )
    # Issues #11 and #14: one event per block, "stop" ends soon after the block, probe after the event only.
    events_in_block = [r["t"] for r in calibrated if r["new_lapse"] and target.onset <= r["t"] <= target.end]
    stop_after = [r["t"] for r in calibrated if r["state"] == "stop" and target.end < r["t"] <= target.end + 60]
    probes = [r for r in calibrated if r["probe"]]
    event_times = [r["t"] for r in calibrated if r["new_lapse"]]
    probe_after_block = next((r["t"] for r in probes if target.end <= r["t"] <= target.end + 40), None)
    probes_without_event = [
        r["t"] for r in probes if r["probe_reason"] != "event" or not any(0 < r["t"] - e <= 90 for e in event_times)
    ]

    return {
        "name": name,
        "results": results,
        "blocks": blocks,
        "rejected_pct": 100.0 * np.mean([r["bad"] for r in results]),
        "calibrated_at": calibrated[0]["t"] if calibrated else float("nan"),
        "detected": bool(hits),
        "delay_s": hits[0] - target.onset if hits else float("nan"),
        "coverage_pct": 100.0 * np.mean([r["lapse"] for r in inside]) if inside else float("nan"),
        "false_alarms": len(false_alarms),
        "false_alarms_per_10min": len(false_alarms) / outside_minutes * 10.0 if outside_minutes else float("nan"),
        "false_time_pct": 100.0 * np.mean([r["lapse"] for r in outside]) if outside else float("nan"),
        "outside_minutes": outside_minutes,
        "eyes_closed_share": eyes_closed_share,
        "events_in_block": len(events_in_block),
        "stop_ends_after_s": (max(stop_after) - target.end) if stop_after else 0.0,
        "probe_after_block_s": None if probe_after_block is None else probe_after_block - target.end,
        "probes_without_event": len(probes_without_event),
        "auc": auc(
            [r["fast"] for r in inside if r["fast"] is not None],
            [r["fast"] for r in outside if r["fast"] is not None],
        ),
    }


def print_table(rows: list[dict]) -> None:
    def pl(value: float, digits: int = 1) -> str:
        return "—" if np.isnan(value) else f"{value:.{digits}f}".replace(".", ",")

    print("| Osoba | Okna odrzucone | Oczy zamknięte wykryte | Opóźnienie | Pokrycie bloku | "
          "Fałszywe alarmy | Czas w fałszywym alarmie | AUC |")
    print("|---|---|---|---|---|---|---|---|")
    for row in rows:
        print(
            f"| {row['name']} | {pl(row['rejected_pct'])}% | {'tak' if row['detected'] else 'nie'} | "
            f"{pl(row['delay_s'], 0)} s | {pl(row['coverage_pct'], 0)}% | "
            f"{row['false_alarms']} w {pl(row['outside_minutes'], 1)} min | "
            f"{pl(row['false_time_pct'])}% | {pl(row['auc'], 2)} |"
        )
    detected = sum(r["detected"] for r in rows)
    minutes = sum(r["outside_minutes"] for r in rows)
    alarms = sum(r["false_alarms"] for r in rows)
    print()
    if alarms == 1:
        alarms_text = "1 fałszywy alarm"
    elif alarms % 10 in (2, 3, 4) and alarms % 100 not in (12, 13, 14):
        alarms_text = f"{alarms} fałszywe alarmy"
    else:
        alarms_text = f"{alarms} fałszywych alarmów"
    print(f"Razem: wykryto {detected} z {len(rows)} bloków, {alarms_text} "
          f"w {pl(minutes, 0)} min poza blokiem (po kalibracji).")
    print()
    print("| Osoba | Spadek w bloku oznaczony jako „oczy zamknięte” | Zdarzenia w bloku | „Stop” trwa po bloku | "
          "Próba reakcji po bloku | Próby bez wcześniejszego zdarzenia |")
    print("|---|---|---|---|---|---|")
    for row in rows:
        after = "brak" if row["probe_after_block_s"] is None else f"po {pl(row['probe_after_block_s'], 0)} s"
        print(f"| {row['name']} | {pl(row['eyes_closed_share'], 0)}% okien | {row['events_in_block']} | "
              f"{pl(row['stop_ends_after_s'], 0)} s | {after} | {row['probes_without_event']} |")


def save_figure(rows: list[dict], cfg: Config, path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    surface, ink, ink2, muted = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
    grid, axis = "#e1e0d9", "#c3c2b7"
    series, critical, band = "#2a78d6", "#d03b3b", "#ecebe6"
    y_min, y_max, y_cap = -3.5, 10.5, 6.6

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    fig, axes = plt.subplots(len(rows), 1, figsize=(10, 2.05 * len(rows) + 1.0), facecolor=surface)
    for ax, row in zip(np.atleast_1d(axes), rows):
        results, blocks = row["results"], row["blocks"]
        t = np.array([r["t"] for r in results])
        fast = np.array([np.nan if r["fast"] is None else r["fast"] for r in results])
        ax.set_facecolor(surface)

        for block in blocks:
            if block.label == "eyes_closed":
                ax.axvspan(block.onset, block.end, color=band, lw=0, zorder=0)
            else:
                ax.axvline(block.onset, color=grid, lw=1, zorder=0)
            # The highlighted block sits one row lower so narrow neighbours never collide with it.
            highlighted = block.label == "eyes_closed"
            last = block is blocks[-1]
            ax.text(
                min(block.end, t[-1]) if last else (block.onset + block.end) / 2,
                y_max - (1.7 if highlighted else 0.35),
                BLOCK_NAMES.get(block.label, block.label),
                ha="right" if last else "center", va="top", fontsize=8,
                color=ink if highlighted else muted,
                fontweight="bold" if highlighted else "normal",
            )
        if not np.isnan(row["calibrated_at"]):
            ax.plot([0, row["calibrated_at"]], [y_min + 0.7] * 2, color=axis, lw=3, solid_capstyle="butt")
            ax.text(row["calibrated_at"] / 2, y_min + 1.3, "kalibracja", ha="center", va="bottom", fontsize=7.5, color=muted)

        ax.axhline(cfg.z_enter, color=ink2, lw=0.8, zorder=1)
        ax.text(t[-1], cfg.z_enter + 0.3, f"próg {cfg.z_enter:g}".replace(".", ","), ha="right", va="bottom", fontsize=7.5, color=ink2)
        ax.plot(t, np.clip(fast, y_min, y_cap), color=series, lw=1.6, solid_joinstyle="round", zorder=3)

        lapse = np.array([r["lapse"] for r in results])
        edges = np.flatnonzero(np.diff(np.r_[False, lapse, False].astype(int)))
        for start, stop in zip(edges[::2], edges[1::2]):
            ax.plot([t[start], t[stop - 1]], [y_cap + 0.5] * 2, color=critical, lw=4, solid_capstyle="butt", zorder=4)

        ax.set_xlim(0, t[-1])
        ax.set_ylim(y_min, y_max)
        ax.set_yticks([0, 5])
        ax.grid(axis="y", color=grid, lw=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(colors=muted, length=0, labelsize=8)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(axis)
        verdict = "wykryte" if row["detected"] else "niewykryte"
        ax.set_title(
            f"{row['name']}: oczy zamknięte {verdict}, fałszywe alarmy: {row['false_alarms']}",
            loc="left", fontsize=9.5, color=ink, fontweight="bold", pad=4,
        )
    np.atleast_1d(axes)[-1].set_xlabel("czas nagrania [s]", color=ink2, fontsize=8.5)

    fig.suptitle("Wskaźnik czujności na nagraniach zespołu", x=0.012, y=0.995, ha="left", fontsize=12.5, fontweight="bold", color=ink)
    fig.text(
        0.012, 0.962, "Wyrazistość alfy na O1/O2 jako z-score względem własnej kalibracji. Ten sam kod liczy wskaźnik w demo.",
        ha="left", va="top", fontsize=9, color=ink2,
    )
    fig.legend(
        handles=[
            Line2D([0], [0], color=series, lw=1.6, label="wskaźnik (z-score)"),
            Line2D([0], [0], color=critical, lw=4, label="wykryty spadek czujności"),
            Patch(facecolor=band, edgecolor="none", label="blok „oczy zamknięte” wg protokołu"),
        ],
        loc="upper left", bbox_to_anchor=(0.004, 0.94), ncol=3, frameon=False, fontsize=8.5, labelcolor=ink2,
        handlelength=1.6, columnspacing=1.4,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.905))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=115, facecolor=surface)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--recordings", type=Path, default=DEFAULT_DIR, help="folder with *-raw.fif files")
    parser.add_argument("--figure", type=Path, help="save a timeline figure to this PNG path")
    args = parser.parse_args()

    cfg = Config()
    recordings = {n: p for n, p in find_recordings(args.recordings).items() if load_annotations(p)}
    if not recordings:
        raise SystemExit(f"No annotated recordings found in {args.recordings}")
    rows = [evaluate(name, path, cfg) for name, path in recordings.items()]
    print_table(rows)
    if args.figure:
        save_figure(rows, cfg, args.figure)
        print(f"\nFigure saved to {args.figure}")


if __name__ == "__main__":
    main()
