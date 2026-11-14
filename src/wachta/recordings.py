"""Loading team recordings (``data/recordings``) and their protocol annotations."""

import csv
from pathlib import Path
from typing import NamedTuple

import numpy as np

from .config import CHANNELS

DEFAULT_DIR = Path("data/recordings")


class Block(NamedTuple):
    onset: float
    duration: float
    label: str

    @property
    def end(self) -> float:
        return self.onset + self.duration


def find_recordings(folder: Path | str = DEFAULT_DIR) -> dict[str, Path]:
    """Map the task name embedded in each file name (e.g. ``filip``) to its ``.fif`` path."""
    found = {}
    for path in sorted(Path(folder).glob("*-raw.fif")):
        name = path.name.split("task-")[1].split("_")[0] if "task-" in path.name else path.stem
        found[name] = path
    return found


def load_eeg(path: Path | str) -> tuple[np.ndarray, float]:
    """Return the 8 EEG channels in volts, ordered as ``CHANNELS``, and the sampling rate."""
    import mne

    raw = mne.io.read_raw_fif(path, preload=True, verbose="ERROR")
    missing = [ch for ch in CHANNELS if ch not in raw.ch_names]
    if missing:
        raise ValueError(f"{path}: missing channels {missing}")
    return raw.get_data(picks=list(CHANNELS)), float(raw.info["sfreq"])


def annotations_path(fif_path: Path | str) -> Path:
    fif_path = Path(fif_path)
    return fif_path.with_name(fif_path.name.replace("-raw.fif", "-raw_annotations.csv"))


def load_annotations(fif_path: Path | str) -> list[Block]:
    """Read protocol blocks stored next to a recording; empty list if there are none."""
    path = annotations_path(fif_path)
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            Block(float(row["onset"]), float(row["duration"]), row["description"])
            for row in csv.DictReader(handle)
            if row.get("duration")
        ]
