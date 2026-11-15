#!/usr/bin/env python3
"""Build the Wachta stage 1 demo video (1080p, H.264 + AAC) from a live dashboard capture.

Inputs
  * a capture made by ``submission/capture-dashboard.js`` (frames, frames.json, events.json): the real dashboard
    replaying an EEG recording of the team, driven through the demo beats of ``docs/scenariusz-demo.md``;
  * AI visuals in ``submission/img`` (driver, nurse, operator picture-in-picture) and validation charts in ``docs/img``.

What it adds: dark canvas with a rounded dashboard card, eased camera moves and zooms from element rectangles
logged during the capture, a cursor and click ripples redrawn from the log, a state-coloured picture-in-picture HUD,
Ken Burns shots, staggered slides, callout badges, Polish subtitles, and an audio track (ambient pad plus the
probe beeps and alarm chimes at the moments they really happened).

    python submission/build-demo-video.py CAPTURE_DIR [--out-hq FILE] [--out FILE] [--preview T [T ...]]

Writes a high quality 30 fps file and a 24 fps file small enough for the repository (< 5 MB).
"""

from __future__ import annotations

import argparse
import bisect
import json
import math
import subprocess
import sys
import tempfile
import textwrap
import wave
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SUB = ROOT / "submission"
IMG = SUB / "img"
DOCS_IMG = ROOT / "docs" / "img"

W, H = 1920, 1080
FPS = 30
TOTAL = 114.0                      # 1:54, under the 2:00 limit
BG = (11, 17, 32)                  # #0B1120
CARD_BG = (17, 26, 46)
CARD_LINE = (36, 50, 80)
INK = (229, 231, 235)
MUTED = (148, 163, 184)
BLUE = (59, 130, 246)
GREEN = (22, 163, 74)              # #16A34A
AMBER = (217, 119, 6)              # #D97706
RED = (220, 38, 38)                # #DC2626
SLATE = (71, 85, 105)

# Dashboard card in canvas ("scene") coordinates; the capture viewport is 1920 x 1180 CSS px (the page is 1172 px tall).
VIEW_W, VIEW_H = 1920, 1180
CARD_X, CARD_Y, CARD_W = 32, 18, 1520
K = CARD_W / VIEW_W                # canvas px per CSS px
CARD_H = round(VIEW_H * K)

TEASER = (10.5, 15.0)
BEATS = {"A": (33.0, 44.0), "B": (44.0, 54.0), "C": (54.0, 64.0), "D": (64.0, 76.0), "E": (76.0, 90.0)}
LAPSE_OUT = (82.2, 90.0)           # time-lapse part of beat E
LAPSE_SPEED = 5.0


# ---------------------------------------------------------------- fonts

def _font_path(bold: bool) -> str | None:
    names = ["/usr/share/fonts/opentype/inter/Inter-Bold.otf" if bold else "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
             "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"]
    return next((n for n in names if Path(n).exists()), None)


_FONTS: dict = {}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    key = (size, bold)
    if key not in _FONTS:
        path = _font_path(bold)
        _FONTS[key] = ImageFont.truetype(path, size) if path else ImageFont.load_default()
    return _FONTS[key]


# ---------------------------------------------------------------- easing

def smooth(u: float) -> float:
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def spring(u: float) -> float:
    u = min(1.0, max(0.0, u))
    return 1.0 - math.exp(-7.0 * u) * math.cos(11.0 * u)


def lerp(a: float, b: float, u: float) -> float:
    return a + (b - a) * u


# ---------------------------------------------------------------- capture data

class Capture:
    def __init__(self, folder: Path) -> None:
        self.folder = folder
        data = json.loads((folder / "events.json").read_text())
        self.data = data
        self.frames = json.loads((folder / "frames.json").read_text())
        self.frame_t = [f[0] for f in self.frames]
        self.events = {e["name"]: e for e in data["events"]}
        self.updates = [u for u in data["updates"] if not u.get("team")]
        self.update_t = [u["t"] for u in self.updates]
        self.probes = data["probes"]
        self.cursor = data["cursor"]
        self.cursor_t = [c["t"] for c in self.cursor]
        self.clicks = [c for c in data["clicks"] if c["x"] >= 0]
        self.rects = data["rects"]
        self._cache: tuple[str, Image.Image] | None = None

    def t(self, name: str) -> float:
        return self.events[name]["t"]

    def frame(self, ts: float) -> Image.Image:
        i = bisect.bisect_right(self.frame_t, ts) - 1
        name = self.frames[max(0, i)][1]
        if self._cache is None or self._cache[0] != name:
            self._cache = (name, Image.open(self.folder / "frames" / name).convert("RGB"))
        return self._cache[1]

    def update_at(self, ts: float) -> dict | None:
        i = bisect.bisect_right(self.update_t, ts) - 1
        return self.updates[i] if i >= 0 else None

    def cursor_at(self, ts: float) -> tuple[float, float] | None:
        if not self.cursor or ts < self.cursor_t[0] or ts > self.cursor_t[-1] + 30:
            return None
        i = bisect.bisect_right(self.cursor_t, ts) - 1
        c = self.cursor[i]
        if i + 1 < len(self.cursor) and self.cursor[i + 1]["t"] - c["t"] < 0.5:
            n = self.cursor[i + 1]
            u = (ts - c["t"]) / max(1e-6, n["t"] - c["t"])
            return lerp(c["x"], n["x"], u), lerp(c["y"], n["y"], u)
        return c["x"], c["y"]

    def probe_windows(self) -> list[tuple[float, float]]:
        """Intervals in which the reaction prompt was on screen."""
        wins = []
        for p in self.probes:
            if p["reason"] == "manual" and "B_result" in self.events:
                end = self.t("B_result") + 1.2
            elif "D_fail" in self.events and p["reason"] == "event":
                end = self.t("D_fail") + 1.2
            else:
                end = p["t"] + 3.0
            wins.append((p["t"], end))
        return wins

    def css_rect(self, sel: str) -> tuple[float, float, float, float]:
        r = self.rects[sel]
        return r["x"], r["y"], r["w"], r["h"]


def scene_pt(x: float, y: float) -> tuple[float, float]:
    return CARD_X + x * K, CARD_Y + y * K


def scene_center(cap: Capture, *sels: str) -> tuple[float, float]:
    xs, ys = [], []
    for sel in sels:
        x, y, w, h = cap.css_rect(sel)
        xs += [x, x + w]
        ys += [y, y + h]
    return scene_pt((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)


# ---------------------------------------------------------------- timeline: output time -> capture time

class Timeline:
    """Segments (out0, out1, src0, speed) that map video time to capture time."""

    def __init__(self, cap: Capture) -> None:
        e = cap.t
        self.segments = [
            (TEASER[0], TEASER[1], e("C_lapse") - 0.35, 1.0),
            (BEATS["A"][0], BEATS["A"][1], e("A_start") - 0.4, 1.0),
            (BEATS["B"][0], BEATS["B"][1], e("B_start") - 0.3, 1.0),
            (BEATS["C"][0], BEATS["C"][1], e("C_lapse") - 4.5, 1.0),
            (BEATS["D"][0], BEATS["D"][1], e("D_probe") - 3.0, 1.0),
            (BEATS["E"][0], LAPSE_OUT[0], e("E_nurse") - 3.6, 1.0),
            (LAPSE_OUT[0], LAPSE_OUT[1], e("E_nurse") - 3.6 + (LAPSE_OUT[0] - BEATS["E"][0]), LAPSE_SPEED),
        ]

    def src(self, T: float) -> float | None:
        for out0, out1, src0, speed in self.segments:
            if out0 <= T < out1:
                return src0 + (T - out0) * speed
        return None

    def out_of(self, ts: float, beat: str | None = None) -> float | None:
        """Video time at which capture time ``ts`` is shown (the first segment containing it, or inside ``beat``)."""
        for out0, out1, src0, speed in self.segments:
            if beat and not (BEATS[beat][0] <= out0 < BEATS[beat][1]):
                continue
            if src0 <= ts < src0 + (out1 - out0) * speed:
                return out0 + (ts - src0) / speed
        return None


# ---------------------------------------------------------------- camera

def camera_keys(cap: Capture, tl: Timeline) -> list[tuple[float, float, float, float]]:
    """Keyframes (T, cx, cy, zoom) in scene coordinates; eased between consecutive keys."""
    full = (W / 2, H / 2)
    worker = scene_center(cap, ".worker")
    state = scene_center(cap, "#state")
    charts = scene_center(cap, ".charts")
    fast = scene_center(cap, "#chart-fast")
    team = scene_center(cap, ".team")
    probe = scene_center(cap, "#probe-target")
    btn_probe = scene_center(cap, "#btn-probe", "#state")
    keys: list[tuple[float, float, float, float]] = []

    def key(T, pos, z):
        keys.append((T, pos[0], pos[1], z))

    # Teaser: the alarm itself.
    a, b = TEASER
    key(a, scene_center(cap, ".worker", "#chart-fast"), 1.15)
    key(a + 2.2, state, 1.5)
    key(b, state, 1.55)

    # A: status card at 1.3x, then across both charts while the cursor hovers over them.
    a, b = BEATS["A"]
    key(a, full, 1.0)
    key(a + 1.1, worker, 1.3)
    key(a + 3.5, worker, 1.3)
    key(a + 4.7, charts, 1.15)
    key(b, charts, 1.15)

    # B: probe button, then a snap zoom onto the prompt and back.
    a, b = BEATS["B"]
    t_probe = tl.out_of(cap.probes[0]["t"]) or a + 4.0
    t_result = tl.out_of(cap.t("B_result")) or t_probe + 1.0
    key(a, full, 1.0)
    key(a + 0.9, btn_probe, 1.2)
    key(t_probe - 0.35, btn_probe, 1.2)
    key(t_probe - 0.05, probe, 1.4)
    key(t_result + 1.0, probe, 1.4)
    key(t_result + 2.0, state, 1.15)
    key(b, state, 1.15)

    # C: along the alpha trace as it crosses the threshold, to the alarm card, down to the supervisor panel.
    a, b = BEATS["C"]
    t_lapse = tl.out_of(cap.t("C_lapse"), "C") or a + 4.5
    team_left = scene_pt(*(lambda r: (r[0] + r[2] * 0.4, r[1] + r[3] * 0.5))(cap.css_rect(".team")))
    key(a, full, 1.0)
    key(a + 0.8, fast, 1.35)
    key(t_lapse + 0.5, fast, 1.35)
    key(t_lapse + 1.5, state, 1.35)
    key(t_lapse + 2.2, state, 1.35)
    key(t_lapse + 3.1, team_left, 1.3)
    key(b, team_left, 1.3)

    # D: wide, snap to the unanswered prompt, then to the reaction tile and the banner.
    a, b = BEATS["D"]
    t_probe = tl.out_of(cap.t("D_probe")) or a + 3.0
    t_fail = tl.out_of(cap.t("D_fail")) or t_probe + 3.2
    key(a, full, 1.0)
    key(t_probe - 0.4, full, 1.0)
    key(t_probe - 0.05, probe, 1.4)
    key(t_fail + 1.4, probe, 1.4)
    key(t_fail + 2.4, worker, 1.3)
    key(b, worker, 1.3)

    # E: scenario switch in the header, then the left card while the break restores the reserve.
    a, b = BEATS["E"]
    t_nurse = tl.out_of(cap.t("E_nurse")) or a + 3.6
    key(a, full, 1.0)
    key(t_nurse, full, 1.0)
    key(t_nurse + 1.0, worker, 1.3)
    key(b, worker, 1.3)
    return sorted(keys, key=lambda k: k[0])


def camera_at(keys: list[tuple[float, float, float, float]], T: float) -> tuple[float, float, float]:
    # Keys in the same beat are consecutive; across beats the hard cut falls at the beat boundary.
    prev = None
    for k in keys:
        if k[0] <= T:
            prev = k
            continue
        if prev is None:
            return k[1], k[2], k[3]
        if k[0] - prev[0] > 6.0 and prev[0] < T:          # a gap between beats: hold the last key
            return prev[1], prev[2], prev[3]
        u = smooth((T - prev[0]) / (k[0] - prev[0]))
        return lerp(prev[1], k[1], u), lerp(prev[2], k[2], u), lerp(prev[3], k[3], u)
    return prev[1], prev[2], prev[3]


# ---------------------------------------------------------------- drawing helpers

def rounded_mask(size: tuple[int, int], box: tuple[float, float, float, float], radius: float) -> Image.Image:
    s = 2
    mask = Image.new("L", (size[0] * s, size[1] * s), 0)
    ImageDraw.Draw(mask).rounded_rectangle([c * s for c in box], radius=radius * s, fill=255)
    return mask.resize(size, Image.LANCZOS)


def draw_text_wrapped(draw: ImageDraw.ImageDraw, xy, text: str, fnt, fill, width_px: int, spacing: int = 6) -> int:
    lines: list[str] = []
    for para in text.split("\n"):
        words, cur = para.split(), ""
        for w in words:
            trial = f"{cur} {w}".strip()
            if draw.textlength(trial, font=fnt) <= width_px:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    y = xy[1]
    for ln in lines:
        draw.text((xy[0], y), ln, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


def fit_contain(img: Image.Image, w: int, h: int) -> Image.Image:
    s = min(w / img.width, h / img.height)
    return img.resize((max(1, round(img.width * s)), max(1, round(img.height * s))), Image.LANCZOS)


def cover(img: Image.Image, zoom: float, pan: tuple[float, float] = (0.5, 0.5)) -> Image.Image:
    """Fill the 16:9 frame with ``img`` magnified by ``zoom`` (Ken Burns)."""
    base = max(W / img.width, H / img.height)
    vw, vh = W / (base * zoom), H / (base * zoom)
    x0 = (img.width - vw) * pan[0]
    y0 = (img.height - vh) * pan[1]
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + vw, y0 + vh))


def pasted_alpha(base: Image.Image, tile: Image.Image, pos: tuple[int, int], alpha: float) -> None:
    """Paste an RGBA tile with its alpha scaled by ``alpha``."""
    if alpha <= 0.003:
        return
    a = tile.getchannel("A").point(lambda v: int(v * min(1.0, alpha)))
    base.paste(tile.convert("RGB"), pos, a)


# ---------------------------------------------------------------- slides (dark, same canvas as the dashboard)

def plate(draw: ImageDraw.ImageDraw, box, fill=CARD_BG, line=CARD_LINE) -> None:
    draw.rounded_rectangle(box, radius=16, fill=fill, outline=line, width=2)


def white_plate(base: Image.Image, img: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    fig = fit_contain(img.convert("RGB"), x1 - x0 - 24, y1 - y0 - 24)
    px, py = x0 + (x1 - x0 - fig.width) // 2, y0 + (y1 - y0 - fig.height) // 2
    mask = rounded_mask(base.size, (px - 12, py - 12, px + fig.width + 12, py + fig.height + 12), 12)
    base.paste(Image.new("RGB", base.size, (250, 250, 249)), (0, 0), mask)
    base.paste(fig, (px, py))


def badge_tile(text: str, color, width: int, size: int = 24) -> Image.Image:
    """Callout badge: tinted rounded pill with a dot, as an RGBA tile."""
    fnt = font(size, True)
    probe = ImageDraw.Draw(Image.new("RGB", (4, 4)))
    lines = []
    cur = ""
    for w in text.split():
        trial = f"{cur} {w}".strip()
        if probe.textlength(trial, font=fnt) <= width - 84:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    h = 26 + len(lines) * (size + 8)
    tile = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    d.rounded_rectangle([0, 0, width - 1, h - 1], radius=h // 2 if len(lines) == 1 else 22, fill=(*color, 235))
    d.ellipse([22, h // 2 - 8, 38, h // 2 + 8], fill=(255, 255, 255, 255))
    y = 13
    for ln in lines:
        d.text((58, y), ln, font=fnt, fill=(255, 255, 255, 255))
        y += size + 8
    return tile


def title_block(draw: ImageDraw.ImageDraw, title: str, subtitle: str | None = None) -> None:
    draw.text((64, 40), title, font=font(38, True), fill=INK)
    if subtitle:
        draw.text((64, 94), subtitle, font=font(22), fill=MUTED)


class ProblemSlide:
    """0:15-0:33. The four problem points and the five loop steps spring in one after another."""

    def __init__(self, driver: Image.Image) -> None:
        self.base = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(self.base)
        d.text((72, 48), "Wachta", font=font(52, True), fill=INK)
        d.text((318, 68), "— zmęczenie i czujność mierzone na człowieku, nie na zegarze", font=font(26), fill=MUTED)
        plate(d, [72, 145, 1085, 935])
        plate(d, [1120, 145, 1848, 935])
        d.text((108, 180), "Problem: przepisy patrzą na zegar, nie na mózg", font=font(32, True), fill=INK)
        d.text((1152, 575), "Pętla adaptacyjna Wachty (Adaptive Systems):", font=font(24, True), fill=INK)
        bullets = [
            ("Do 20% wypadków drogowych wiąże się ze zmęczeniem", "zmęczenie i senność za kierownicą to jedna z głównych przyczyn\n(Komisja Europejska / ERSO 2023)."),
            ("17–19 godzin bez snu = 0,05% alkoholu we krwi", "sprawność psychomotoryczna spada poniżej bezpiecznego progu\n(Dawson i Reid 1997, Nature)."),
            ("Sztywna norma czasu pracy traktuje wszystkich tak samo", "po tych samych 8 godzinach jedna osoba ma pełną rezerwę,\na druga wchodzi w zamknięte oczy."),
            ("Kamera w kabinie widzi oczy i głowę", "Wachta dokłada osobisty profil, sprawdzenie reakcji\ni wskazanie zmiennika w zespole."),
        ]
        steps = [
            "1. Kalibracja osobista (60 s czystego EEG na starcie zmiany)",
            "2. Ciągły pomiar: wyrazistość alfy (O1/O2) + mrugnięcia (F3/F4)",
            "3. Kontekst pory doby i czasu od przebudzenia",
            "4. Próba reakcji po spadku czujności i z harmonogramu",
            "5. Decyzja: „Przerwa teraz” + wskazanie zmiennika z rezerwą",
        ]
        self.items: list[tuple[Image.Image, tuple[int, int]]] = []
        for i, (title, desc) in enumerate(bullets):
            tile = Image.new("RGBA", (960, 140), (0, 0, 0, 0))
            td = ImageDraw.Draw(tile)
            td.ellipse([0, 8, 16, 24], fill=(*RED, 255))
            td.text((34, 0), title, font=font(25, True), fill=(*INK, 255))
            td.multiline_text((34, 38), desc, font=font(22), fill=(*MUTED, 255), spacing=6)
            self.items.append((tile, (108, 262 + i * 155)))
        thumb = driver.resize((664, 374), Image.LANCZOS).convert("RGBA")
        self.items.append((thumb, (1152, 178)))
        for i, s in enumerate(steps):
            tile = Image.new("RGBA", (700, 40), (0, 0, 0, 0))
            ImageDraw.Draw(tile).text((0, 4), s, font=font(21), fill=(*MUTED, 255))
            self.items.append((tile, (1152, 624 + i * 48)))
        # Left points and right steps start in parallel, 0.3 s apart.
        self.starts = [0.3 + 0.3 * i for i in range(4)] + [0.3] + [0.7 + 0.3 * i for i in range(5)]
        self._final: Image.Image | None = None

    def at(self, t: float) -> Image.Image:
        if t > max(self.starts) + 0.5:
            if self._final is None:
                self._final = self._compose(99.0)
            return self._final
        return self._compose(t)

    def _compose(self, t: float) -> Image.Image:
        out = self.base.copy()
        for (tile, (x, y)), start in zip(self.items, self.starts):
            u = (t - start) / 0.25
            if u <= 0:
                continue
            p = spring(u)
            pasted_alpha(out, tile, (x, int(y + (1 - p) * 30)), min(1.0, u * 2.5))
        return out


class EvidenceSlides:
    """1:30-1:48. Validation charts with callout badges that pop in."""

    def __init__(self) -> None:
        self.s1 = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(self.s1)
        title_block(d, "Walidacja na sprzęcie BrainAccess MINI: 5 nagrań zespołu",
                    "Wykryto 5 z 5 bloków zamkniętych oczu (AUC 0,88–0,99) | 1 fałszywy alarm w 48 min | 0 alarmów w 15 min monotonii (T1)")
        plate(d, [64, 150, 790, 975])
        plate(d, [820, 150, 1856, 975])
        white_plate(self.s1, Image.open(DOCS_IMG / "trafnosc-na-nagraniach.png"), (84, 168, 770, 862))
        white_plate(self.s1, Image.open(DOCS_IMG / "monotonia-minuta-po-minucie.png"), (840, 168, 1836, 500))
        d = ImageDraw.Draw(self.s1)
        d.text((850, 530), "Sesja monotonii T1 (15 min, KSS 5):", font=font(26, True), fill=INK)
        y = 578
        for line in ("0,9% odrzuconych okien (słuchawki ANC)", "0 fałszywych alarmów przez 15 minut",
                     "Zamknięcie oczu wykryte po 9 s (1 zdarzenie)", "0 zbędnych prób reakcji po PR #36"):
            d.text((876, y), "•  " + line, font=font(23), fill=MUTED)
            y += 44
        self.b1 = (badge_tile("5 / 5 bloków zamkniętych oczu wykrytych (BrainAccess MINI)", GREEN, 676), (94, 880), 1.0)
        self.b2 = (badge_tile("1 fałszywy alarm w 48 min (0 w 15 min monotonii T1)", AMBER, 940), (860, 872), 2.4)

        self.s2 = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(self.s2)
        title_block(d, "Walidacja na zbiorach publicznych: dlaczego kalibracja osobista i test reakcji",
                    "Cui i in. 2022 (11 osób, symulator jazdy) oraz COG-BCI (Hinss i in. 2023, 29 osób, zadanie PVT), na naszych 8 kanałach")
        plate(d, [64, 150, 940, 975])
        plate(d, [980, 150, 1856, 975])
        white_plate(self.s2, Image.open(DOCS_IMG / "drowsiness-public-auc-and-calibration.png"), (84, 250, 920, 590))
        white_plate(self.s2, Image.open(DOCS_IMG / "pvt-alpha-early-warning-cogbci.png"), (1000, 250, 1836, 590))
        d = ImageDraw.Draw(self.s2)
        d.text((94, 172), "1. Senność przy otwartych oczach (Cui i in. 2022):", font=font(26, True), fill=INK)
        d.text((1010, 172), "2. Uczciwa weryfikacja hipotez (COG-BCI, 29 osób):", font=font(26, True), fill=INK)
        draw_text_wrapped(d, (94, 620), "Alfa O1/O2 rośnie u 11 z 11 osób (średnie AUC 0,75).\nModel osobisty podnosi AUC z 0,76 do 0,90.",
                          font(23), MUTED, 810, 8)
        draw_text_wrapped(d, (1010, 620), "Podprogowa alfa nie wyprzedza lapsu o minutę (AUC 0,52).\nDlatego próby wyzwalane są po zdarzeniu i z harmonogramu.",
                          font(23), MUTED, 810, 8)
        self.b3 = (badge_tile("Model osobisty: AUC 0,76 → 0,90 (Cui i in. 2022)", BLUE, 800), (104, 800), 1.2)
        self.b4 = (badge_tile("Podprogowa alfa nie wyprzedza lapsu: AUC 0,52 (COG-BCI)", SLATE, 800), (1020, 800), 2.6)

    @staticmethod
    def _badges(base: Image.Image, badges, t: float) -> Image.Image:
        out = base.copy()
        for tile, (x, y), start in badges:
            u = (t - start) / 0.45
            if u <= 0:
                continue
            p = spring(u)
            w, h = tile.size
            s = max(0.2, p)
            scaled = tile.resize((max(1, int(w * s)), max(1, int(h * s))), Image.BICUBIC)
            pasted_alpha(out, scaled, (x + (w - scaled.width) // 2, y + (h - scaled.height) // 2), min(1.0, u * 2.5))
        return out

    def slide1(self, t: float) -> Image.Image:
        return self._badges(self.s1, [self.b1, self.b2], t)

    def slide2(self, t: float) -> Image.Image:
        return self._badges(self.s2, [self.b3, self.b4], t)


def closing_slide() -> Image.Image:
    slide = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(slide)
    d.text((100, 80), "Wachta", font=font(76, True), fill=INK)
    d.text((100, 180), "Zmęczenie i czujność mierzone na człowieku, nie na zegarze", font=font(34, True), fill=BLUE)
    d.text((100, 240), "Heroes of the Brain 2026 — Kategoria: Adaptive Systems", font=font(24), fill=MUTED)
    plate(d, [100, 310, 1820, 650])
    d.text((140, 342), "Co zweryfikowaliśmy, a co sprawdzimy w pilotażu:", font=font(25, True), fill=INK)
    y = 400
    for p in ("✓ Działająca pętla (BrainAccess MINI, 8 suchych elektrod, 250 Hz, przetwarzanie lokalne na komputerze)",
              "✓ 5 z 5 wykrytych bloków zamkniętych oczu, 1 fałszywy alarm w 48 min (0 w 15-minutowej sesji monotonii T1)",
              "✓ Przewaga modelu osobistego na danych publicznych (AUC 0,90 vs 0,76) i adaptacyjny test czasu reakcji",
              "→ Następny krok: pilotaż na zmianach nocnych sprawdzający, czy osobisty limit rezerwy wyprzedza spadki czujności lepiej niż zegar"):
        draw_text_wrapped(d, (140, y), p, font(22), (215, 220, 228), 1640, 4)
        y += 56
    d.text((100, 690), "Zespół AI All In:  Adrian  •  Filip  •  Rudy  •  Wojtek", font=font(26, True), fill=INK)
    d.text((100, 738), "Kod i notebooki (publiczne repo):  github.com/wskalecki/Heroes_of_the_brain_AI_All_IN", font=font(24), fill=BLUE)
    cy = 800
    for c in ("Źródła danych publicznych wykorzystanych w analizach (zgodnie z licencjami):",
              "• Cao Z. i in. (2019), Multi-channel EEG recordings during a sustained-attention driving task, Scientific Data 6:19 — CC BY 4.0",
              "• Cui J. i in. (2022), EEG driver drowsiness dataset (figshare 14273687) — CC BY 4.0",
              "• Hinss M.F. i in. (2023), COG-BCI database (Zenodo 7413650, v4) — CC BY 4.0",
              "• Zyma I. i in. (2019), EEG During Mental Arithmetic Tasks (PhysioNet EEGMAT) — ODC-By v1.0"):
        d.text((100, cy), c, font=font(19), fill=(120, 134, 156))
        cy += 31
    return slide


# ---------------------------------------------------------------- dashboard view

def dashboard_view(cap: Capture, ts: float, cam: tuple[float, float, float], show_cursor: bool = True) -> Image.Image:
    frame = cap.frame(ts)
    cx, cy, z = cam
    vw, vh = W / z, H / z
    cy += 46 / z                       # keep zoomed content clear of the subtitle bar
    vx0 = min(max(cx - vw / 2, 0), W - vw)
    vy0 = min(max(cy - vh / 2, 0), H - vh)

    out = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(out)

    def to_view(x: float, y: float) -> tuple[float, float]:
        return (x - vx0) * z, (y - vy0) * z

    # Card: shadow, frame crop, rounded corners.
    x0, y0 = to_view(CARD_X, CARD_Y)
    x1, y1 = to_view(CARD_X + CARD_W, CARD_Y + CARD_H)
    small = (W // 4, H // 4)
    sh = Image.new("L", small, 0)
    ImageDraw.Draw(sh).rounded_rectangle([x0 / 4, (y0 + 10 * z) / 4, x1 / 4, (y1 + 10 * z) / 4], radius=16 * z / 4, fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(7 * z)).resize((W, H), Image.BILINEAR)
    out.paste(Image.new("RGB", (W, H), (2, 4, 10)), (0, 0), sh)

    ix0, iy0 = max(x0, 0), max(y0, 0)
    ix1, iy1 = min(x1, W), min(y1, H)
    if ix1 > ix0 and iy1 > iy0:
        fx = frame.width / (x1 - x0)
        fy = frame.height / (y1 - y0)
        box = ((ix0 - x0) * fx, (iy0 - y0) * fy, (ix1 - x0) * fx, (iy1 - y0) * fy)
        piece = frame.resize((round(ix1 - ix0), round(iy1 - iy0)), Image.LANCZOS, box=box)
        mask = rounded_mask((W, H), (x0, y0, x1, y1), 16 * z)
        layer = Image.new("RGB", (W, H), BG)
        layer.paste(piece, (round(ix0), round(iy0)))
        out.paste(layer, (0, 0), mask)

    draw = ImageDraw.Draw(out, "RGBA")

    # Ripple when the reaction turns green.
    if "B_result" in cap.events and "#probe-target" in cap.rects:
        r = cap.css_rect("#probe-target")
        age = ts - cap.t("B_result")
        if 0 <= age < 1.0:
            px, py = to_view(*scene_pt(r[0] + r[2] / 2, r[1] + r[3] / 2))
            for k in range(3):
                u = age - 0.18 * k
                if 0 < u < 0.8:
                    rad = (r[2] / 2 * K) * z * (1.0 + 0.9 * smooth(u / 0.8))
                    draw.ellipse([px - rad, py - rad, px + rad, py + rad], outline=(*GREEN, int(200 * (1 - u / 0.8))), width=max(2, round(5 * z)))

    # Click ripples and the cursor, redrawn from the log (headless Chromium records no pointer).
    for c in cap.clicks:
        age = ts - c["t"]
        if 0 <= age < 0.55:
            px, py = to_view(*scene_pt(c["x"], c["y"]))
            rad = (14 + 44 * smooth(age / 0.55)) * 1.0
            draw.ellipse([px - rad, py - rad, px + rad, py + rad], outline=(255, 255, 255, int(220 * (1 - age / 0.55))), width=3)
    pos = cap.cursor_at(ts) if show_cursor else None
    if pos:
        px, py = to_view(*scene_pt(*pos))
        if -20 < px < W + 20 and -20 < py < H + 20:
            arrow = [(0, 0), (0, 25), (6, 19), (10, 28), (14, 26), (10, 18), (18, 18)]
            pts = [(px + a, py + b) for a, b in arrow]
            draw.polygon([(a + 2, b + 3) for a, b in pts], fill=(0, 0, 0, 90))
            draw.polygon(pts, fill=(255, 255, 255, 255), outline=(15, 23, 42, 255))
    return out


# ---------------------------------------------------------------- PiP HUD

PIP = (1572, 764, 320, 180)


def pip_state(cap: Capture, ts: float) -> tuple[str, float, tuple, str]:
    """(image to show, closed amount 0..1, glow colour, label)."""
    def closed_at(t: float) -> bool:
        u = cap.update_at(t)
        return bool(u and u.get("lapse") and u.get("lapse_kind") != "eyes_open")

    amount = sum(closed_at(ts - 0.05 * i) for i in range(6)) / 6.0
    u = cap.update_at(ts) or {}
    for a, b in cap.probe_windows():
        if a <= ts <= b:
            return "probe", amount, AMBER, "PRÓBA REAKCJI"
    if closed_at(ts):
        return "closed", amount, RED, "OCZY ZAMKNIĘTE"
    state = u.get("state")
    if state == "stop":
        return "fail", amount, RED, "BRAK REAKCJI" if u.get("probe_failed_recently") else "PRZERWA TERAZ"
    if state == "warn":
        return "warn", amount, AMBER, "UWAGA"
    if state == "break":
        return "break", amount, BLUE, "PRZERWA"
    return "ok", amount, GREEN, "OCZY OTWARTE"


def draw_pip(frame: Image.Image, cap: Capture, ts: float, T: float, pip_open: Image.Image, pip_closed: Image.Image) -> None:
    _, amount, color, label = pip_state(cap, ts)
    x, y, w, h = PIP
    pic = Image.blend(pip_open, pip_closed, amount).resize((w, h), Image.LANCZOS)
    pad = 24
    glow = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle([pad, pad, pad + w, pad + h], radius=16, outline=(*color, 255), width=7)
    glow = glow.filter(ImageFilter.GaussianBlur(9))
    frame.paste(glow.convert("RGB"), (x - pad, y - pad), glow.getchannel("A"))
    mask = rounded_mask((w, h), (0, 0, w, h), 14)
    frame.paste(pic, (x, y), mask)
    d = ImageDraw.Draw(frame, "RGBA")
    d.rounded_rectangle([x, y, x + w, y + h], radius=14, outline=(*color, 255), width=3)
    # Top strip with REC dot and state, bottom-left disclaimer.
    d.rounded_rectangle([x + 10, y + 10, x + w - 10, y + 38], radius=10, fill=(8, 12, 24, 190))
    if int(T * 1.6) % 2 == 0:
        d.ellipse([x + 20, y + 18, x + 32, y + 30], fill=(*RED, 255))
    d.text((x + 42, y + 15), "REC", font=font(14, True), fill=(255, 255, 255, 255))
    lw = d.textlength(label, font=font(15, True))
    d.text((x + w - 20 - lw, y + 15), label, font=font(15, True), fill=(*color, 255) if color != GREEN else (74, 222, 128, 255))
    d.rounded_rectangle([x + 10, y + h - 30, x + 150, y + h - 10], radius=8, fill=(8, 12, 24, 170))
    d.text((x + 18, y + h - 27), "wizualizacja (AI)", font=font(13), fill=(203, 213, 225, 255))


# ---------------------------------------------------------------- subtitles, chapter, progress

def overlay(frame: Image.Image, T: float, chapter: str, subtitle: str, label: str | None = None, source_chip: bool = False) -> Image.Image:
    d = ImageDraw.Draw(frame, "RGBA")
    badge = f"{chapter}   {int(T) // 60}:{int(T) % 60:02d} / 1:54"
    fnt = font(19, True)
    bw = d.textlength(badge, font=fnt) + 36
    bx = W - bw - 28
    d.rounded_rectangle([bx, 14, bx + bw, 50], radius=18, fill=(8, 12, 24, 215))
    d.text((bx + 18, 22), badge, font=fnt, fill=(255, 255, 255, 255))
    if source_chip:
        chip = "ODTWORZENIE NAGRANIA EEG (BrainAccess MINI) · czas zmiany ×10"
        cw = d.textlength(chip, font=font(17, True)) + 32
        d.rounded_rectangle([(W - cw) / 2 - 120, 14, (W + cw) / 2 - 120, 50], radius=18, fill=(8, 12, 24, 215), outline=(*SLATE, 255), width=2)
        d.text(((W - cw) / 2 - 104, 23), chip, font=font(17, True), fill=(203, 213, 225, 255))
    if label:
        lw = d.textlength(label, font=font(18, True)) + 30
        d.rounded_rectangle([32, 14, 32 + lw, 50], radius=18, fill=(*AMBER, 235))
        d.text((47, 22), label, font=font(18, True), fill=(255, 255, 255, 255))
    if subtitle:
        sf = font(26, True)
        lines = textwrap.wrap(subtitle, width=96)
        tw = max(d.textlength(ln, font=sf) for ln in lines)
        bh = 22 + len(lines) * 36
        box_w = min(W - 80, tw + 56)
        x0 = (W - box_w) / 2
        y0 = H - 16 - bh
        d.rounded_rectangle([x0, y0, x0 + box_w, y0 + bh], radius=12, fill=(8, 12, 24, 232))
        for i, ln in enumerate(lines):
            d.text(((W - d.textlength(ln, font=sf)) / 2, y0 + 12 + i * 36), ln, font=sf, fill=(255, 255, 255, 255))
    d.rectangle([0, H - 5, int(W * T / TOTAL), H], fill=(*BLUE, 255))
    return frame


# ---------------------------------------------------------------- subtitles text

def subtitles(cap: Capture) -> list[tuple[float, float, str, str]]:
    a = cap.events["A_start"]["latest"] or {}
    cf = f"{a.get('context_factor', 2.4):.1f}".replace(".", ",")
    rt = (cap.events["B_result"].get("probeResult") or {}).get("title", "")
    rt_txt = rt if rt.endswith("ms") else "ok. 250 ms"
    return [
        (0.0, 6.0, "1/6  Problem", "2:30 w nocy, 19 godzin od przebudzenia. Przepisy mierzą zegar — Wachta mierzy człowieka."),
        (6.0, 15.0, "1/6  Problem", "Gdy oczy zamykają się na dłużej niż kilka sekund, Wachta każe zjechać i od razu wskazuje zmiennika z największą rezerwą."),
        (15.0, 24.0, "2/6  Dlaczego zegar nie wystarcza", "Normy czasu pracy traktują wszystkich tak samo, a ze zmęczeniem wiąże się do 20% wypadków drogowych."),
        (24.0, 33.0, "2/6  Dlaczego zegar nie wystarcza", "Po 18 h czuwania sprawność spada jak przy 0,05% alkoholu. Kamera widzi oczy. Wachta dokłada osobisty profil i próbę reakcji."),
        (33.0, 44.0, "3/6  Kalibracja i kontekst nocy", f"Po 60 s osobistej kalibracji system śledzi alfę z tyłu głowy i mrugnięcia. W nocy po długim czuwaniu zakładamy spadek rezerwy {cf}× szybszy (założenie modelu)."),
        (44.0, 54.0, "3/6  Próba reakcji w normie", f"Drugi sygnał to zachowanie: krótka próba sprawdza czas reakcji względem osobistej normy: {rt_txt}, w normie."),
        (54.0, 64.0, "4/6  Zamknięte oczy i panel przełożonego", "Zamknięcie oczu podnosi alfę na O1/O2 powyżej progu 2,5 przez 3 s. Przełożony widzi tylko gotowość zespołu."),
        (64.0, 76.0, "4/6  Potwierdzenie po spadku czujności", "Gdy oczy znów się otworzą, system sam sprawdza, czy człowiek reaguje. Brak reakcji utrzymuje nakaz przerwy."),
        (76.0, 90.0, "4/6  Dyżur w szpitalu i regeneracja", "Ten sam system w szpitalu: przekaż pacjentów i zrób przerwę. W modelu rezerwy odpoczynek ją odnawia."),
        (90.0, 99.0, "5/6  Walidacja na 5 nagraniach zespołu", "Ten sam kod wykrył 5 z 5 bloków zamkniętych oczu i dał tylko 1 fałszywy alarm w 48 minutach (0 w monotonii T1)."),
        (99.0, 108.0, "5/6  Walidacja na zbiorach publicznych", "W danych publicznych (Cui i in., CC BY 4.0) alfa rośnie u 11 z 11 osób, a model osobisty podnosi AUC z 0,76 do 0,90."),
        (108.0, 114.0, "6/6  Podsumowanie i pilotaż", "Następny krok: pilotaż sprawdzający, czy osobisty limit rezerwy wyprzedza spadki czujności lepiej niż zegar."),
    ]


# ---------------------------------------------------------------- frame renderer (runs in worker processes)

class Renderer:
    def __init__(self, capture_dir: Path) -> None:
        self.cap = Capture(capture_dir)
        self.tl = Timeline(self.cap)
        self.keys = camera_keys(self.cap, self.tl)
        self.driver = Image.open(IMG / "driver-night-broll.jpg").convert("RGB")
        self.nurse = Image.open(IMG / "nurse-shift-broll.jpg").convert("RGB")
        self.pip_open = Image.open(IMG / "pip-eyes-open.jpg").convert("RGB")
        self.pip_closed = Image.open(IMG / "pip-eyes-closed.jpg").convert("RGB")
        self.problem = ProblemSlide(self.driver)
        self.evidence = EvidenceSlides()
        self.closing = closing_slide()
        self.subs = subtitles(self.cap)

    def text_for(self, T: float) -> tuple[str, str]:
        for a, b, chapter, sub in self.subs:
            if a <= T < b:
                return chapter, sub
        return self.subs[-1][2], self.subs[-1][3]

    def frame(self, T: float) -> Image.Image:
        chapter, sub = self.text_for(T)
        label = None
        chip = False
        if T < 6.0:
            img = cover(self.driver, lerp(1.0, 1.08, T / 6.0), (0.5, 0.5))
            d = ImageDraw.Draw(img, "RGBA")
            u = smooth((T - 0.3) / 0.6)
            d.rounded_rectangle([72, 64, 1290, 214], radius=14, fill=(8, 12, 24, int(205 * u)))
            d.text((104, 80), "Wachta — Adaptive Systems", font=font(54, True), fill=(255, 255, 255, int(255 * u)))
            d.text((104, 152), "Zmęczenie i czujność mierzone na człowieku, nie na zegarze (BrainAccess MINI, 8 kanałów EEG)",
                   font=font(23), fill=(215, 220, 228, int(255 * u)))
        elif T < TEASER[0]:
            img = cover(self.nurse, lerp(1.0, 1.08, (T - 6.0) / (TEASER[0] - 6.0)), (0.5, 0.45))
            d = ImageDraw.Draw(img, "RGBA")
            u = smooth((T - 6.2) / 0.5)
            d.rounded_rectangle([72, 64, 900, 130], radius=14, fill=(8, 12, 24, int(205 * u)))
            d.text((104, 80), "Ten sam problem na nocnym dyżurze", font=font(32, True), fill=(255, 255, 255, int(255 * u)))
        elif T < TEASER[1] or (BEATS["A"][0] <= T < BEATS["E"][1]):
            ts = self.tl.src(T)
            cam = camera_at(self.keys, T)
            img = dashboard_view(self.cap, ts, cam)
            draw_pip(img, self.cap, ts, T, self.pip_open, self.pip_closed)
            chip = True
            if T < TEASER[1]:
                label = "PODGLĄD: SCENA 4/6"
            if LAPSE_OUT[0] <= T < LAPSE_OUT[1]:
                d = ImageDraw.Draw(img, "RGBA")
                txt = f"przyspieszono ×{LAPSE_SPEED:.0f}"
                tw = d.textlength(txt, font=font(18, True)) + 32
                d.rounded_rectangle([W - 28 - tw, 62, W - 28, 98], radius=18, fill=(*AMBER, 235))
                d.text((W - 12 - tw, 69), txt, font=font(18, True), fill=(255, 255, 255, 255))
        elif T < BEATS["A"][0]:
            img = self.problem.at(T - TEASER[1])
        elif T < 99.0:
            img = self.evidence.slide1(T - 90.0)
        elif T < 108.0:
            img = self.evidence.slide2(T - 99.0)
        else:
            img = self.closing.copy()
        return overlay(img, T, chapter, sub, label, chip)


_R: Renderer | None = None


def _init(capture_dir: str) -> None:
    global _R
    _R = Renderer(Path(capture_dir))


def _render(i: int) -> bytes:
    assert _R is not None
    return _R.frame(i / FPS).tobytes()


# ---------------------------------------------------------------- audio

def audio_track(cap: Capture, tl: Timeline, path: Path) -> None:
    sr = 44100
    n = int(TOTAL * sr)
    t = np.arange(n, dtype=np.float32) / sr
    pad = 0.014 * np.sin(2 * np.pi * 110.0 * t) + 0.009 * np.sin(2 * np.pi * 164.81 * t) + 0.005 * np.sin(2 * np.pi * 220.0 * t)
    fade = 2 * sr
    pad[:fade] *= np.linspace(0, 1, fade, dtype=np.float32)
    pad[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)
    audio = pad.copy()

    def tone(at: float, freq: float, dur: float, gain: float, decay: float = 12.0) -> None:
        s = int(at * sr)
        m = int(dur * sr)
        if s < 0 or s + m > n:
            return
        bt = np.arange(m, dtype=np.float32) / sr
        audio[s:s + m] += gain * np.sin(2 * np.pi * freq * bt) * np.exp(-bt * decay)

    for p in cap.probes:                                  # the 880 Hz prompt beep, as in app.js
        at = tl.out_of(p["t"])
        if at is not None:
            tone(at, 880.0, 0.28, 0.25)
    for name in ("C_lapse",):                             # alarm chime when "Przerwa teraz" appears (also in the teaser)
        ts = cap.t(name)
        for out0, out1, src0, speed in tl.segments:
            at = out0 + (ts - src0) / speed
            if out0 <= at < out1:
                tone(at, 587.33, 0.22, 0.18, 10.0)
                tone(at + 0.16, 440.0, 0.22, 0.18, 10.0)
    if "B_result" in cap.events:
        at = tl.out_of(cap.t("B_result"))
        if at is not None:
            tone(at, 1318.5, 0.18, 0.14, 14.0)
    if "D_fail" in cap.events:
        at = tl.out_of(cap.t("D_fail"))
        if at is not None:
            tone(at, 196.0, 0.4, 0.2, 5.0)
    audio = np.clip(audio, -0.95, 0.95)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((audio * 32767).astype(np.int16).tobytes())


# ---------------------------------------------------------------- main

def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode:
        raise RuntimeError(f"{' '.join(cmd[:3])} failed: {proc.stderr[-1500:]}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("capture", type=Path, help="folder written by capture-dashboard.js")
    ap.add_argument("--out", type=Path, default=SUB / "wachta-demo-2min.mp4", help="repository version (24 fps, < 5 MB)")
    ap.add_argument("--out-hq", type=Path, default=None, help="high quality 30 fps version")
    ap.add_argument("--preview", type=float, nargs="*", help="write PNG previews of these video times and exit")
    ap.add_argument("--target-kbps", type=int, default=270, help="video bitrate of the repository version")
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()

    if args.preview is not None:
        r = Renderer(args.capture)
        for T in args.preview:
            out = args.capture / f"preview_{T:06.2f}.png"
            r.frame(T).save(out)
            print(out)
        return

    out_hq = args.out_hq or args.capture / "wachta-demo-hq.mp4"
    cap = Capture(args.capture)
    tl = Timeline(cap)
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "audio.wav"
        audio_track(cap, tl, wav)
        enc = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
             "-i", str(wav), "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
             "-t", f"{TOTAL}", "-movflags", "+faststart", str(out_hq)],
            stdin=subprocess.PIPE)
        total = int(TOTAL * FPS)
        with Pool(args.jobs, initializer=_init, initargs=(str(args.capture),)) as pool:
            for i, raw in enumerate(pool.imap(_render, range(total), chunksize=4)):
                enc.stdin.write(raw)
                if i % 150 == 0:
                    print(f"frame {i}/{total}", file=sys.stderr, flush=True)
        enc.stdin.close()
        if enc.wait():
            raise RuntimeError("ffmpeg failed on the high quality encode")

        # Repository version: 24 fps, two-pass at a fixed bitrate so it stays below the 5 MB limit.
        log = str(Path(tmp) / "pass")
        common = ["-i", str(out_hq), "-vf", "fps=24", "-c:v", "libx264", "-preset", "slow", "-b:v", f"{args.target_kbps}k",
                  "-maxrate", f"{int(args.target_kbps * 1.6)}k", "-bufsize", f"{args.target_kbps * 2}k", "-pix_fmt", "yuv420p", "-passlogfile", log]
        run(["ffmpeg", "-y", "-loglevel", "error", *common, "-pass", "1", "-an", "-f", "mp4", "/dev/null"])
        run(["ffmpeg", "-y", "-loglevel", "error", *common, "-pass", "2", "-c:a", "aac", "-b:a", "48k", "-ac", "1", "-movflags", "+faststart", str(args.out)])
    print(f"repo version: {args.out} ({args.out.stat().st_size / 1e6:.2f} MB)\nhigh quality: {out_hq} ({out_hq.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
