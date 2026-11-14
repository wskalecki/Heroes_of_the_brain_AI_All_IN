"""Where EEG samples come from: a recording played back, or BrainAccess Board live.

Every source exposes ``chunks()``, an async iterator of arrays shaped (8, n) in
volts with channels ordered as ``config.CHANNELS``, plus ``name`` and ``live``.
"""

import asyncio
import time
from pathlib import Path
from typing import AsyncIterator

import numpy as np

from .config import CHANNELS
from .recordings import find_recordings, load_eeg

# Unit names used by BrainAccess Board metadata, mapped to volts.
_UNIT_TO_VOLTS = {"microvolts": 1e-6, "uV": 1e-6, "millivolts": 1e-3, "mV": 1e-3, "volts": 1.0, "V": 1.0}


class ReplaySource:
    """Plays an array of samples at ``speed`` times real time, optionally in a loop."""

    live = False

    def __init__(
        self,
        eeg_volts: np.ndarray,
        sfreq: float,
        name: str = "nagranie",
        speed: float = 1.0,
        start_s: float = 0.0,
        loop: bool = True,
        chunk_s: float = 0.25,
    ) -> None:
        if speed <= 0:
            raise ValueError("speed must be positive")
        self.eeg = eeg_volts
        self.sfreq = sfreq
        self.name = name
        self.speed = speed
        self.start_s = start_s
        self.loop = loop
        self.chunk = max(1, int(round(chunk_s * sfreq)))

    @classmethod
    def from_file(cls, path: Path | str, **kwargs) -> "ReplaySource":
        eeg, sfreq = load_eeg(path)
        return cls(eeg, sfreq, **kwargs)

    async def chunks(self) -> AsyncIterator[np.ndarray]:
        position = min(int(self.start_s * self.sfreq), max(self.eeg.shape[1] - self.chunk, 0))
        interval = self.chunk / self.sfreq / self.speed
        due = time.monotonic()
        while True:
            if position >= self.eeg.shape[1]:
                if not self.loop:
                    return
                position = 0
            yield self.eeg[:, position : position + self.chunk]
            position += self.chunk
            due += interval
            await asyncio.sleep(max(0.0, due - time.monotonic()))


class BoardSource:
    """Reads new samples from the database of a running BrainAccess Board session.

    Needs the ``live`` extra (``pip install -e ".[live]"``), the Board app running
    and the headset streaming. Not exercised by the test suite: it needs hardware.
    """

    live = True

    def __init__(self, name: str = "na żywo", poll_s: float = 0.25, sfreq: float = 250.0) -> None:
        self.name = name
        self.poll_s = poll_s
        self.sfreq = sfreq

    @staticmethod
    def _connect():
        try:
            import brainaccess_board as bb
        except ImportError as error:
            raise RuntimeError('Brak biblioteki brainaccess-board. Zainstaluj: pip install -e ".[live]"') from error
        database, ok = bb.db_connect()
        if not ok or database is None:
            raise RuntimeError("Nie widzę aktywnej sesji BrainAccess Board. Uruchom Board i połącz czepek.")
        return database

    @staticmethod
    def _pick_device(database) -> tuple[str, list[int], np.ndarray, float]:
        """Find the device that has all eight channels; return its id, row order and unit scale."""
        devices = database._list_devices()["data"]
        seen = {}
        for device, info in devices.items():
            names = [str(ch).strip() for ch in info["channels"]]
            seen[device] = names
            lookup = {ch.upper(): i for i, ch in enumerate(names)}
            if all(ch.upper() in lookup for ch in CHANNELS):
                rows = [lookup[ch.upper()] for ch in CHANNELS]
                units = [str(info["channels_unit"][i]) for i in rows]
                scale = np.array([_UNIT_TO_VOLTS.get(u, 1.0) for u in units]).reshape(-1, 1)
                return device, rows, scale, float(info["srate"])
        raise RuntimeError(f"Żadne urządzenie w Board nie ma kanałów {CHANNELS}. Znalezione: {seen}")

    async def chunks(self) -> AsyncIterator[np.ndarray]:
        database = await asyncio.to_thread(self._connect)
        device, rows, scale, srate = await asyncio.to_thread(self._pick_device, database)
        if abs(srate - self.sfreq) > 0.5:
            raise RuntimeError(f"Board podaje {srate} Hz, a pipeline oczekuje {self.sfreq} Hz.")

        # Skip whatever was recorded before we connected.
        backlog = await asyncio.to_thread(database.get_data_since, device, 0.0)
        last = backlog["last_timestamp"] if backlog else 0.0
        while True:
            fresh = await asyncio.to_thread(database.get_data_since, device, last)
            if fresh:
                last = fresh["last_timestamp"]
                yield np.asarray(fresh["data"], dtype=float)[rows] * scale
            await asyncio.sleep(self.poll_s)


def resolve_recording(spec: str) -> Path:
    """Accept a path to a ``.fif`` file or the task name of a team recording (e.g. ``filip``)."""
    path = Path(spec)
    if path.exists():
        return path
    recordings = find_recordings()
    if spec in recordings:
        return recordings[spec]
    raise FileNotFoundError(f"Nie znam nagrania '{spec}'. Dostępne: {', '.join(recordings) or 'brak'}")
