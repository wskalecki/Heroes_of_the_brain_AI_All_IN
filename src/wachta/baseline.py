"""Personal calibration: z-scores against the person's own first clean windows."""

import numpy as np


class Baseline:
    """Collects the first ``n_windows`` clean windows and z-scores later ones.

    The centre and spread are robust (median and scaled MAD), so a few blinks
    during calibration do not shift the baseline.
    """

    def __init__(self, keys: tuple[str, ...], n_windows: int) -> None:
        self.keys = keys
        self.n_windows = n_windows
        self._rows: list[list[float]] = []
        self._centre: np.ndarray | None = None
        self._spread: np.ndarray | None = None

    @property
    def ready(self) -> bool:
        return self._centre is not None

    @property
    def progress(self) -> float:
        return 1.0 if self.ready else len(self._rows) / self.n_windows

    def add(self, features: dict[str, float]) -> None:
        """Feed one clean window; ignored once the baseline is ready."""
        if self.ready:
            return
        self._rows.append([features[k] for k in self.keys])
        if len(self._rows) >= self.n_windows:
            rows = np.asarray(self._rows)
            centre = np.median(rows, axis=0)
            spread = np.median(np.abs(rows - centre), axis=0) * 1.4826
            # Guard against a degenerate (flat) calibration signal.
            fallback = rows.std(axis=0)
            spread = np.where(spread > 1e-6, spread, np.where(fallback > 1e-6, fallback, 1.0))
            self._centre, self._spread = centre, spread

    def z(self, features: dict[str, float]) -> dict[str, float]:
        if not self.ready:
            raise RuntimeError("Baseline is not ready yet")
        values = np.array([features[k] for k in self.keys])
        scores = (values - self._centre) / self._spread
        return dict(zip(self.keys, scores.tolist()))
