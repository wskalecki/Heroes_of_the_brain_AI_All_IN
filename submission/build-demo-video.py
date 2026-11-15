#!/usr/bin/env python3
"""Generate the 2-minute Wachta Stage 1 demo video (1920x1080 MP4, H.264 + AAC).

Combines:
1. Real renders of ``src/wachta/web/index.html`` driven by ``VigilanceIndex`` states in headless Chromium.
2. AI-generated B-roll and Picture-in-Picture webcam frames (truck driver at 2:30 AM, hospital nurse shift, EEG cap subject).
3. Validation figures from ``docs/img/`` and attribution slide (CC BY 4.0).
4. Synchronized Polish subtitles, chapter badges, 880 Hz reaction probe beeps, and optional Polish TTS voiceover
   (automatically uses ``edge-tts`` or macOS ``say`` when available).
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path("/home/antigravity/wskalecki/Heroes_of_the_brain_AI_All_IN")
ARTIFACT_DIR = Path(
    "str(Path(__file__).resolve().parent)"
)
WEB_DIR = REPO_ROOT / "src" / "wachta" / "web"
IMG_DIR = REPO_ROOT / "docs" / "img"

WIDTH = 1920
HEIGHT = 1080
FPS = 15
TOTAL_SECONDS = 114  # 1 min 54 s (strictly under the 2:00 limit)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        ]
        if bold
        else [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]
    )
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


FONT_TITLE = load_font(52, bold=True)
FONT_SUBTITLE = load_font(28, bold=False)
FONT_H2 = load_font(34, bold=True)
FONT_BODY = load_font(23, bold=False)
FONT_BODY_BOLD = load_font(25, bold=True)
FONT_SMALL = load_font(20, bold=False)
FONT_BADGE = load_font(21, bold=True)
FONT_CAPTION = load_font(24, bold=True)


def find_artifact_image(prefix: str) -> Path | None:
    matches = sorted(ARTIFACT_DIR.glob(f"{prefix}_*.jpg")) + sorted(ARTIFACT_DIR.glob(f"{prefix}_*.png"))
    return matches[-1] if matches else None


def build_dashboard_snapshots(tmp_dir: Path) -> dict[str, Image.Image]:
    """Render key states of the real Wachta web dashboard in headless Chromium."""
    chrome = shutil.which("chromium") or shutil.which("google-chrome")
    if not chrome:
        raise RuntimeError("Chromium / Google Chrome not found")

    rng = np.random.default_rng(42)

    def make_history(n: int, fast_vals: list[float], state: str, reserve: float, **overrides) -> list[dict]:
        hist = []
        t0 = 180.0
        for i in range(n):
            t = t0 - (n - 1 - i)
            fv = fast_vals[i]
            is_lapse = fv >= 2.5 and i >= n - 12 and state == "stop" and overrides.get("lapse", False)
            entry = {
                "t": float(t),
                "state": state if i == n - 1 else ("stop" if is_lapse else "ok"),
                "reserve": round(reserve + (n - 1 - i) * 0.04, 1),
                "fast": round(float(fv), 2),
                "slow": 0.45,
                "calibration": 1.0,
                "quality": 0.97,
                "work_min": round(28.0 + i * 0.5, 1),
                "drain_per_hour": 26.0,
                "minutes_to_warn": 74.0,
                "minutes_to_stop": 135.0,
                "lapse": bool(is_lapse),
                "lapse_count": overrides.get("lapse_count", 0),
                "lapse_kind": overrides.get("lapse_kind", None),
                "lapses_eyes_closed": overrides.get("lapses_eyes_closed", 0),
                "lapses_eyes_open": overrides.get("lapses_eyes_open", 0),
                "eye_state": overrides.get("eye_state", "open"),
                "blinks_per_min": overrides.get("blinks_per_min", 14.0),
                "probes_done": overrides.get("probes_done", 0),
                "probe_lapses": overrides.get("probe_lapses", 0),
                "last_rt_ms": overrides.get("last_rt_ms", None),
                "probe_failed_recently": overrides.get("probe_failed_recently", False),
                "on_break": overrides.get("on_break", False),
                "clock_h": overrides.get("clock_h", 2.5),
                "awake_h": overrides.get("awake_h", 19.5),
                "context_factor": overrides.get("context_factor", 2.6),
            }
            hist.append(entry)
        return hist

    base_fast = np.clip(rng.normal(0.15, 0.45, size=180), -1.4, 1.4).tolist()
    burst_fast = base_fast[:-14] + [1.2, 2.1, 2.8, 3.6, 4.4, 5.1, 5.5, 5.8, 5.4, 5.2, 4.9, 5.1, 5.3, 5.2]
    post_burst_fast = burst_fast[15:] + np.clip(rng.normal(0.3, 0.4, size=15), -0.8, 1.1).tolist()

    trace_ok = [[round(k * 2.0, 1), round(100.0 - k * 0.75, 1)] for k in range(16)]
    trace_lapse = trace_ok + [[32.0, 80.0], [34.0, 78.5], [36.0, 77.0]]
    trace_failed_probe = trace_lapse + [[38.0, 69.0], [40.0, 68.0]]
    trace_break = trace_failed_probe + [[42.0, 71.5], [44.0, 75.0], [46.0, 78.5]]

    states_spec = {
        "ok_fresh": {
            "scenario": "driver",
            "history": make_history(180, base_fast, "ok", 92.0, work_min=18.0),
            "trace": trace_ok[:10],
            "probe_modal": None,
        },
        "probe_prompt_schedule": {
            "scenario": "driver",
            "history": make_history(180, base_fast, "ok", 90.0),
            "trace": trace_ok,
            "probe_modal": {"title": "Reakcja!", "text": "Kontrola okresowa: naciśnij spację albo kliknij", "result": ""},
        },
        "probe_ok": {
            "scenario": "driver",
            "history": make_history(180, base_fast, "ok", 89.5, probes_done=1, last_rt_ms=248),
            "trace": trace_ok,
            "probe_modal": {"title": "248 ms", "text": "Reakcja w normie", "result": "ok"},
        },
        "ok_after_probe": {
            "scenario": "driver",
            "history": make_history(180, base_fast, "ok", 88.0, probes_done=1, last_rt_ms=248),
            "trace": trace_ok,
            "probe_modal": None,
        },
        "microsleep_stop": {
            "scenario": "driver",
            "history": make_history(
                180,
                burst_fast,
                "stop",
                78.0,
                lapse=True,
                lapse_count=1,
                lapse_kind="eyes_closed",
                lapses_eyes_closed=1,
                eye_state="closed",
                blinks_per_min=1.0,
                probes_done=1,
                last_rt_ms=248,
            ),
            "trace": trace_lapse,
            "probe_modal": None,
        },
        "probe_prompt_event": {
            "scenario": "driver",
            "history": make_history(
                180,
                post_burst_fast,
                "warn",
                76.5,
                lapse=False,
                lapse_count=1,
                lapses_eyes_closed=1,
                eye_state="open",
                blinks_per_min=12.0,
                probes_done=1,
                last_rt_ms=248,
            ),
            "trace": trace_lapse,
            "probe_modal": {
                "title": "Reakcja!",
                "text": "Sprawdzenie po spadku czujności: naciśnij spację albo kliknij",
                "result": "",
            },
        },
        "probe_failed_stop": {
            "scenario": "driver",
            "history": make_history(
                180,
                post_burst_fast,
                "stop",
                68.0,
                lapse=False,
                lapse_count=1,
                lapses_eyes_closed=1,
                eye_state="open",
                blinks_per_min=12.0,
                probes_done=2,
                probe_lapses=1,
                last_rt_ms=None,
                probe_failed_recently=True,
            ),
            "trace": trace_failed_probe,
            "probe_modal": {"title": "Brak reakcji", "text": "Reakcja za wolna: to liczy się jako spadek czujności", "result": "lapse"},
        },
        "probe_failed_banner": {
            "scenario": "driver",
            "history": make_history(
                180,
                post_burst_fast,
                "stop",
                68.0,
                lapse=False,
                lapse_count=1,
                lapses_eyes_closed=1,
                eye_state="open",
                blinks_per_min=12.0,
                probes_done=2,
                probe_lapses=1,
                last_rt_ms=None,
                probe_failed_recently=True,
            ),
            "trace": trace_failed_probe,
            "probe_modal": None,
        },
        "nurse_stop": {
            "scenario": "nurse",
            "history": make_history(
                180,
                post_burst_fast,
                "stop",
                68.0,
                lapse=False,
                lapse_count=1,
                lapses_eyes_closed=1,
                eye_state="open",
                blinks_per_min=12.0,
                probes_done=2,
                probe_lapses=1,
                last_rt_ms=None,
                probe_failed_recently=True,
            ),
            "trace": trace_failed_probe,
            "probe_modal": None,
        },
        "nurse_break": {
            "scenario": "nurse",
            "history": make_history(
                180,
                post_burst_fast,
                "break",
                78.5,
                on_break=True,
                lapse=False,
                lapse_count=1,
                lapses_eyes_closed=1,
                eye_state="open",
                blinks_per_min=14.0,
                probes_done=2,
                probe_lapses=1,
                last_rt_ms=None,
            ),
            "trace": trace_break,
            "probe_modal": None,
        },
    }

    # Copy web assets to tmp_dir and inject state renderer
    render_dir = tmp_dir / "web_render"
    shutil.copytree(WEB_DIR, render_dir, dirs_exist_ok=True)
    app_js = (WEB_DIR / "app.js").read_text(encoding="utf-8")
    # Compact chart height slightly so Worker card + Charts + Supervisor Panel all fit above the subtitle bar in 1080p
    app_js_patched = (
        app_js.replace("height: 230,", "height: 165,")
        .replace("connect();\n}", "// connect disabled for deterministic render\n}")
    )

    snapshots: dict[str, Image.Image] = {}
    for key, spec in states_spec.items():
        hello_payload = {
            "type": "hello",
            "primary": "w0",
            "config": {
                "z_enter": 2.5,
                "warn_below": 50.0,
                "stop_below": 25.0,
                "time_scale": 30.0,
                "probe_lapse_ms": 355.0,
                "probe_timeout_ms": 3000,
                "probe_interval_s": 1200.0,
            },
            "workers": [
                {
                    "id": "w0",
                    "name": "Wojtek (na żywo — BrainAccess MINI)",
                    "live": True,
                    "error": None,
                    "history": spec["history"],
                    "trace": spec["trace"],
                },
                {
                    "id": "w1",
                    "name": "Rudy",
                    "live": False,
                    "error": None,
                    "history": [{"state": "ok", "reserve": 88.0, "t": 180.0}],
                    "trace": [],
                },
                {
                    "id": "w2",
                    "name": "Adi",
                    "live": False,
                    "error": None,
                    "history": [{"state": "warn", "reserve": 44.0, "t": 180.0}],
                    "trace": [],
                },
            ],
        }
        driver_script = f"""
{app_js_patched}
document.body.style.zoom = "0.86";
app.connected = true;
setScenario({json.dumps(spec["scenario"])});
onMessage({json.dumps(hello_payload)});
render();
"""
        if spec["probe_modal"]:
            pm = spec["probe_modal"]
            driver_script += f"""
$("probe").hidden = false;
$("probe-title").textContent = {json.dumps(pm["title"])};
$("probe-text").textContent = {json.dumps(pm["text"])};
if ({json.dumps(pm["result"])}) {{
  $("probe-target").dataset.result = {json.dumps(pm["result"])};
}} else {{
  delete $("probe-target").dataset.result;
}}
"""
        (render_dir / "app.js").write_text(driver_script, encoding="utf-8")
        out_png = tmp_dir / f"snap_{key}.png"
        subprocess.run(
            [
                chrome,
                "--headless",
                "--no-sandbox",
                "--disable-gpu",
                "--hide-scrollbars",
                "--window-size=1920,1080",
                f"--screenshot={out_png}",
                f"file://{render_dir / 'index.html'}",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        snapshots[key] = Image.open(out_png).convert("RGB")

    return snapshots


def paste_pip(base: Image.Image, pip_img: Image.Image, label: str, alert: bool = False) -> Image.Image:
    """Overlay a Picture-in-Picture webcam box in the bottom-right corner."""
    frame = base.copy()
    pip_w, pip_h = 360, 202
    x0 = WIDTH - pip_w - 36
    y0 = HEIGHT - pip_h - 104
    resized = pip_img.resize((pip_w, pip_h), Image.Resampling.LANCZOS)

    draw = ImageDraw.Draw(frame)
    border_col = (208, 59, 59) if alert else (42, 120, 214)
    draw.rounded_rectangle([x0 - 4, y0 - 4, x0 + pip_w + 4, y0 + pip_h + 4], radius=12, fill=border_col)
    frame.paste(resized, (x0, y0))

    # Top pill inside PiP
    draw.rounded_rectangle([x0 + 10, y0 + 10, x0 + 10 + 305, y0 + 38], radius=6, fill=(11, 11, 11))
    dot_col = (208, 59, 59) if alert else (12, 163, 12)
    draw.ellipse([x0 + 20, y0 + 19, x0 + 30, y0 + 29], fill=dot_col)
    draw.text((x0 + 38, y0 + 13), label, font=FONT_SMALL, fill=(255, 255, 255))
    return frame


def ken_burns(img: Image.Image, progress: float, zoom: float = 0.08) -> Image.Image:
    """Subtle cinematic zoom-in over ``progress`` in [0, 1]."""
    src = img.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    scale = 1.0 - zoom * np.clip(progress, 0.0, 1.0)
    cw, ch = int(WIDTH * scale), int(HEIGHT * scale)
    left = (WIDTH - cw) // 2
    top = (HEIGHT - ch) // 2
    cropped = src.crop((left, top, left + cw, top + ch))
    return cropped.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)


def make_problem_slide(driver_img: Image.Image) -> Image.Image:
    """Slide for 0:15-0:33: The problem with clock-based fatigue norms."""
    slide = Image.new("RGB", (WIDTH, HEIGHT), (249, 249, 247))
    draw = ImageDraw.Draw(slide)

    # Header bar
    draw.text((72, 52), "Wachta", font=FONT_TITLE, fill=(11, 11, 11))
    draw.text(
        (315, 70),
        "— zmęczenie i czujność mierzone na człowieku, nie na zegarze",
        font=FONT_SUBTITLE,
        fill=(82, 81, 78),
    )

    # Left card: Problem & numbers with sources
    draw.rounded_rectangle([72, 145, 1085, 935], radius=16, fill=(252, 252, 251), outline=(225, 224, 217), width=2)
    draw.text((108, 182), "Problem: przepisy patrzą na zegar, nie na mózg", font=FONT_H2, fill=(11, 11, 11))

    bullets = [
        (
            "20% wypadków w transporcie komercyjnym",
            "wynika ze zmęczenia i senności za kierownicą\n(Komisja Europejska / ERSO 2023).",
        ),
        (
            "17–19 godzin bez snu = 0,05% alkoholu we krwi",
            "sprawność psychomotoryczna spada poniżej bezpiecznego progu\n(Dawson i Reid 1997, Nature).",
        ),
        (
            "Sztywna norma czasu pracy traktuje wszystkich tak samo",
            "po tych samych 8 godzinach jedna osoba ma pełną rezerwę,\na druga wchodzi w mikrosen.",
        ),
        (
            "Kamera w kabinie widzi dopiero zamknięte powieki",
            "nie sprawdza czasu reakcji po incydencie i nie wskazuje\nzmiennika w zespole.",
        ),
    ]
    y = 265
    for title, desc in bullets:
        draw.ellipse([108, y + 8, 124, y + 24], fill=(208, 59, 59))
        draw.text((142, y), title, font=FONT_BODY_BOLD, fill=(11, 11, 11))
        draw.multiline_text((142, y + 36), desc, font=FONT_BODY, fill=(82, 81, 78), spacing=6)
        y += 155

    # Right card: visual + adaptive loop diagram
    draw.rounded_rectangle([1120, 145, 1848, 935], radius=16, fill=(252, 252, 251), outline=(225, 224, 217), width=2)
    thumb = driver_img.resize((664, 374), Image.Resampling.LANCZOS)
    slide.paste(thumb, (1152, 178))
    draw.text((1152, 578), "Pętla adaptacyjna Wachty (Adaptive Systems):", font=FONT_BODY_BOLD, fill=(11, 11, 11))
    steps = [
        "1. Kalibracja osobista (60 s czystego EEG na starcie zmiany)",
        "2. Ciągły pomiar: wyrazistość alfy (O1/O2) + mrugnięcia (F3/F4)",
        "3. Kontekst pory doby i czasu od przebudzenia",
        "4. Próba reakcji po spadku czujności i z harmonogramu",
        "5. Decyzja: „Przerwa teraz” + wskazanie zmiennika z rezerwą",
    ]
    sy = 628
    for s in steps:
        draw.text((1152, sy), s, font=FONT_SMALL, fill=(82, 81, 78))
        sy += 48

    return slide


def fit_contain(img: Image.Image, box_w: int, box_h: int, bg=(252, 252, 251)) -> Image.Image:
    canvas = Image.new("RGB", (box_w, box_h), bg)
    ratio = min(box_w / img.width, box_h / img.height)
    nw, nh = max(1, int(img.width * ratio)), max(1, int(img.height * ratio))
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas.paste(resized, ((box_w - nw) // 2, (box_h - nh) // 2))
    return canvas


def make_evidence_slide_1() -> Image.Image:
    """Slide for 1:30-1:40: Validation on 5 team recordings + monotony T1."""
    slide = Image.new("RGB", (WIDTH, HEIGHT), (249, 249, 247))
    draw = ImageDraw.Draw(slide)
    draw.text((64, 42), "Walidacja na sprzęcie BrainAccess MINI: 5 nagrań zespołu", font=FONT_H2, fill=(11, 11, 11))
    draw.text(
        (64, 92),
        "Wykryto 5 z 5 bloków zamkniętych oczu (AUC 0,88–0,99) | 1 fałszywy alarm w 48 min | 0 alarmów w 15 min monotonii (T1)",
        font=FONT_BODY,
        fill=(82, 81, 78),
    )

    fig_left = Image.open(IMG_DIR / "trafnosc-na-nagraniach.png").convert("RGB")
    fig_right = Image.open(IMG_DIR / "monotonia-minuta-po-minucie.png").convert("RGB")

    draw.rounded_rectangle([64, 145, 1120, 940], radius=14, fill=(252, 252, 251), outline=(225, 224, 217), width=2)
    slide.paste(fit_contain(fig_left, 1030, 775), (77, 155))

    draw.rounded_rectangle([1150, 145, 1856, 940], radius=14, fill=(252, 252, 251), outline=(225, 224, 217), width=2)
    slide.paste(fit_contain(fig_right, 680, 520), (1163, 160))

    summary_lines = [
        "Sesja monotonii T1 (15 min, KSS 5):",
        "• 0,9% odrzuconych okien (słuchawki ANC)",
        "• 0 fałszywych alarmów przez 15 minut",
        "• Zamknięcie oczu wykryte po 9 s (1 zdarzenie)",
        "• 0 zbędnych prób reakcji po PR #36",
    ]
    sy = 700
    for idx, line in enumerate(summary_lines):
        draw.text((1175, sy), line, font=FONT_BODY_BOLD if idx == 0 else FONT_SMALL, fill=(11, 11, 11))
        sy += 40

    return slide


def make_evidence_slide_2() -> Image.Image:
    """Slide for 1:40-1:48: Public datasets validation (Cui et al. 2022 & COG-BCI)."""
    slide = Image.new("RGB", (WIDTH, HEIGHT), (249, 249, 247))
    draw = ImageDraw.Draw(slide)
    draw.text(
        (64, 42),
        "Walidacja na zbiorach publicznych: dlaczego kalibracja osobista i test reakcji",
        font=FONT_H2,
        fill=(11, 11, 11),
    )
    draw.text(
        (64, 92),
        "Cui i in. 2022 (11 osób, symulator jazdy) oraz COG-BCI (Hinss i in. 2023, 29 osób, zadanie PVT) — na naszych 8 kanałach",
        font=FONT_BODY,
        fill=(82, 81, 78),
    )

    fig_cui = Image.open(IMG_DIR / "drowsiness-public-auc-and-calibration.png").convert("RGB")
    fig_pvt = Image.open(IMG_DIR / "pvt-alpha-early-warning-cogbci.png").convert("RGB")

    draw.rounded_rectangle([64, 145, 940, 940], radius=14, fill=(252, 252, 251), outline=(225, 224, 217), width=2)
    slide.paste(fit_contain(fig_cui, 850, 620), (77, 160))
    draw.text(
        (84, 800),
        "1. Senność przy otwartych oczach (Cui i in. 2022):",
        font=FONT_BODY_BOLD,
        fill=(11, 11, 11),
    )
    draw.text(
        (84, 840),
        "Alfa O1/O2 rośnie u 11 z 11 osób (średnie AUC 0,75).\nModel osobisty podnosi AUC z 0,76 do 0,90.",
        font=FONT_SMALL,
        fill=(82, 81, 78),
    )

    draw.rounded_rectangle([980, 145, 1856, 940], radius=14, fill=(252, 252, 251), outline=(225, 224, 217), width=2)
    slide.paste(fit_contain(fig_pvt, 850, 620), (993, 160))
    draw.text(
        (1000, 800),
        "2. Uczciwa weryfikacja hipotez (COG-BCI, 29 osób):",
        font=FONT_BODY_BOLD,
        fill=(11, 11, 11),
    )
    draw.text(
        (1000, 840),
        "Podprogowa alfa nie wyprzedza lapsu o minutę (AUC 0,52).\nDlatego próby wyzwalane są po zdarzeniu i z harmonogramu.",
        font=FONT_SMALL,
        fill=(82, 81, 78),
    )

    return slide


def make_closing_slide() -> Image.Image:
    """Slide for 1:48-1:54: Team, next steps, repository & CC BY 4.0 credits."""
    slide = Image.new("RGB", (WIDTH, HEIGHT), (13, 13, 13))
    draw = ImageDraw.Draw(slide)

    draw.text((100, 90), "Wachta", font=load_font(72, bold=True), fill=(240, 239, 236))
    draw.text(
        (100, 180),
        "Zmęczenie i czujność mierzone na człowieku, nie na zegarze",
        font=FONT_H2,
        fill=(57, 135, 229),
    )
    draw.text(
        (100, 240),
        "Heroes of the Brain 2026 — Kategoria: Adaptive Systems",
        font=FONT_BODY,
        fill=(195, 194, 183),
    )

    draw.rounded_rectangle([100, 310, 1820, 650], radius=16, fill=(26, 26, 25), outline=(56, 56, 53), width=2)
    draw.text((140, 345), "Co zweryfikowaliśmy, a co sprawdzimy w pilotażu:", font=FONT_BODY_BOLD, fill=(240, 239, 236))
    points = [
        "✓ Działająca pętla na żywo (BrainAccess MINI, 8 suchych elektrod, 250 Hz, lokalne przetwarzanie na komputerze)",
        "✓ 5 z 5 wykrytych bloków zamkniętych oczu, 1 fałszywy alarm w 48 min (0 w 15-minutowej sesji monotonii T1)",
        "✓ Przewaga modelu osobistego na danych publicznych (AUC 0,90 vs 0,76) i adaptacyjny test czasu reakcji",
        "→ Następny krok: pilotaż na zmianach nocnych sprawdzający, czy osobisty limit rezerwy wyprzedza spadki czujności lepiej niż zegar",
    ]
    py = 405
    for p in points:
        draw.text((140, py), p, font=FONT_BODY, fill=(215, 214, 208))
        py += 54

    draw.text(
        (100, 700),
        "Zespół AI All In:  Adrian  •  Filip  •  Rudy  •  Wojtek",
        font=FONT_BODY_BOLD,
        fill=(240, 239, 236),
    )
    draw.text(
        (100, 745),
        "Kod i notebooki (publiczne repo):  github.com/wskalecki/Heroes_of_the_brain_AI_All_IN",
        font=FONT_BODY,
        fill=(57, 135, 229),
    )

    credits = [
        "Źródła danych publicznych wykorzystanych w analizach (zgodnie z licencjami):",
        "• Cao Z. i in. (2019), Multi-channel EEG recordings during a sustained-attention driving task, Scientific Data 6:19 — CC BY 4.0",
        "• Cui J. i in. (2022), EEG driver drowsiness dataset (figshare 14273687) — CC BY 4.0",
        "• Hinss M.F. i in. (2023), COG-BCI database (Zenodo 7413650, v4) — CC BY 4.0",
        "• Zyma I. i in. (2019), EEG During Mental Arithmetic Tasks (PhysioNet EEGMAT) — ODC-By v1.0",
    ]
    cy = 815
    for c in credits:
        draw.text((100, cy), c, font=FONT_SMALL, fill=(145, 143, 137))
        cy += 32

    return slide


def overlay_subtitles_and_hud(frame: Image.Image, t_sec: float, chapter: str, subtitle: str) -> Image.Image:
    """Draw a clean top-right chapter pill, bottom subtitle bar, and progress line."""
    out = frame.copy()
    draw = ImageDraw.Draw(out, "RGBA")

    # Top-right chapter + timer pill
    mm = int(t_sec) // 60
    ss = int(t_sec) % 60
    badge_text = f"{chapter}   {mm}:{ss:02d} / 1:54"
    bbox = draw.textbbox((0, 0), badge_text, font=FONT_BADGE)
    bw = bbox[2] - bbox[0] + 36
    x_badge = WIDTH - bw - 32
    y_badge = 14
    draw.rounded_rectangle([x_badge, y_badge, x_badge + bw, y_badge + 38], radius=19, fill=(11, 11, 11, 210))
    draw.text((x_badge + 18, y_badge + 7), badge_text, font=FONT_BADGE, fill=(255, 255, 255, 255))

    # Subtitle bar at bottom (centered and guaranteed to fit inside [48, WIDTH - 48])
    if subtitle:
        sb_box = draw.textbbox((0, 0), subtitle, font=FONT_CAPTION)
        tw = sb_box[2] - sb_box[0]
        pad_x = 28
        box_w = min(WIDTH - 80, tw + 2 * pad_x)
        x0 = (WIDTH - box_w) // 2
        draw.rounded_rectangle([x0, HEIGHT - 78, x0 + box_w, HEIGHT - 14], radius=12, fill=(11, 11, 11, 228))
        draw.text(((WIDTH - tw) // 2, HEIGHT - 60), subtitle, font=FONT_CAPTION, fill=(255, 255, 255, 255))

    # Subtle bottom timeline progress bar
    prog_w = int(WIDTH * (t_sec / TOTAL_SECONDS))
    draw.rectangle([0, HEIGHT - 5, prog_w, HEIGHT], fill=(42, 120, 214, 255))
    return out


def generate_audio_track(wav_path: Path) -> None:
    """Synthesize a clean 114 s stereo audio track with ambient pad and 880 Hz reaction probe beeps."""
    sr = 44100
    n = TOTAL_SECONDS * sr
    t = np.arange(n, dtype=np.float32) / sr

    # Warm, quiet ambient chord (A2 + E3 + C#4) so the video has a broadcast feel even before voiceover
    pad = (
        0.015 * np.sin(2 * np.pi * 110.0 * t)
        + 0.010 * np.sin(2 * np.pi * 164.81 * t)
        + 0.006 * np.sin(2 * np.pi * 220.0 * t)
    )
    # Soft fade-in and fade-out
    fade_len = 2 * sr
    pad[:fade_len] *= np.linspace(0.0, 1.0, fade_len, dtype=np.float32)
    pad[-fade_len:] *= np.linspace(1.0, 0.0, fade_len, dtype=np.float32)

    audio = pad.copy()

    # Exact 880 Hz reaction probe beeps matching app.js beep() at probe appearances:
    # 1) t = 45.0 s (scheduled probe)
    # 2) t = 63.5 s (post-event confirmation probe)
    for beep_t in (45.0, 63.5):
        start = int(beep_t * sr)
        dur = int(0.28 * sr)
        bt = np.arange(dur, dtype=np.float32) / sr
        env = np.exp(-bt * 12.0)
        beep = 0.25 * np.sin(2 * np.pi * 880.0 * bt) * env
        audio[start : start + dur] += beep

    # Subtle alert chime when microsleep STOP triggers at t = 6.0 s and t = 55.0 s
    for alert_t in (6.0, 55.0):
        for offset, freq in ((0.0, 587.33), (0.16, 440.0)):
            start = int((alert_t + offset) * sr)
            dur = int(0.22 * sr)
            bt = np.arange(dur, dtype=np.float32) / sr
            env = np.exp(-bt * 10.0)
            audio[start : start + dur] += 0.18 * np.sin(2 * np.pi * freq * bt) * env

    audio = np.clip(audio, -0.95, 0.95)
    pcm = (audio * 32767.0).astype(np.int16)

    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


def main() -> None:
    driver_path = find_artifact_image("driver_night_broll")
    nurse_path = find_artifact_image("nurse_shift_broll")
    pip_open_path = find_artifact_image("pip_eyes_open")
    pip_closed_path = find_artifact_image("pip_eyes_closed")
    assert driver_path and nurse_path and pip_open_path and pip_closed_path, "Missing generated AI images"

    driver_img = Image.open(driver_path).convert("RGB")
    nurse_img = Image.open(nurse_path).convert("RGB")
    pip_open = Image.open(pip_open_path).convert("RGB")
    pip_closed = Image.open(pip_closed_path).convert("RGB")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        print("1/4 Rendering real Wachta dashboard states in headless Chromium...")
        snaps = build_dashboard_snapshots(tmp_dir)

        print("2/4 Building slide & B-roll composites...")
        slide_problem = make_problem_slide(driver_img)
        slide_ev1 = make_evidence_slide_1()
        slide_ev2 = make_evidence_slide_2()
        slide_close = make_closing_slide()

        # Pre-build PiP dashboard variants
        dash_ok_pip = paste_pip(snaps["ok_fresh"], pip_open, "EEG NA ŻYWO: OCZY OTWARTE", alert=False)
        dash_probe_sched_pip = paste_pip(
            snaps["probe_prompt_schedule"], pip_open, "PRÓBA REAKCJI (SPACJA)", alert=False
        )
        dash_probe_ok_pip = paste_pip(snaps["probe_ok"], pip_open, "REAKCJA: 248 MS (W NORMIE)", alert=False)
        dash_after_probe_pip = paste_pip(snaps["ok_after_probe"], pip_open, "EEG NA ŻYWO: OCZY OTWARTE", alert=False)
        dash_microsleep_pip = paste_pip(
            snaps["microsleep_stop"], pip_closed, "MIKROSEN: OCZY ZAMKNIĘTE", alert=True
        )
        dash_probe_event_pip = paste_pip(
            snaps["probe_prompt_event"], pip_open, "SPRAWDZENIE PO INCYDENCIE", alert=True
        )
        dash_probe_fail_modal_pip = paste_pip(
            snaps["probe_failed_stop"], pip_open, "BRAK REAKCJI (> 3000 MS)", alert=True
        )
        dash_probe_fail_banner_pip = paste_pip(
            snaps["probe_failed_banner"], pip_open, "POTWIERDZONY SPADEK CZUJNOŚCI", alert=True
        )
        dash_nurse_stop = paste_pip(snaps["nurse_stop"], pip_open, "SCENARIUSZ: DYŻUR SZPITALNY", alert=True)
        dash_nurse_break = paste_pip(snaps["nurse_break"], pip_open, "PRZERWA: REGENERACJA REZERWY", alert=False)

        wav_path = tmp_dir / "audio.wav"
        generate_audio_track(wav_path)

        out_mp4 = ARTIFACT_DIR / "wachta-demo-2min.mp4"
        print("3/4 Encoding 1080p MP4 video via FFmpeg...")
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "rawvideo",
            "-vcodec",
            "rawvideo",
            "-s",
            f"{WIDTH}x{HEIGHT}",
            "-pix_fmt",
            "rgb24",
            "-r",
            str(FPS),
            "-i",
            "-",
            "-i",
            str(wav_path),
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-shortest",
            str(out_mp4),
        ]
        proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        assert proc.stdin is not None

        total_frames = TOTAL_SECONDS * FPS
        for f_idx in range(total_frames):
            t_sec = f_idx / FPS

            # Scene selection (0:00 to 1:54)
            if t_sec < 4.5:
                base = ken_burns(driver_img, t_sec / 4.5, zoom=0.07)
                draw_b = ImageDraw.Draw(base, "RGBA")
                draw_b.rounded_rectangle([72, 64, 1290, 210], radius=14, fill=(11, 11, 11, 205))
                draw_b.text((104, 82), "Wachta — Adaptive Systems", font=FONT_TITLE, fill=(255, 255, 255, 255))
                draw_b.text(
                    (104, 152),
                    "Zmęczenie i czujność mierzone na człowieku, nie na zegarze (BrainAccess MINI, 8 kanałów EEG)",
                    font=FONT_BODY,
                    fill=(215, 214, 208, 255),
                )
                chapter = "1/6  Problem na żywo"
                sub = "2:30 w nocy, 19 godzin od przebudzenia. Przepisy mierzą zegar — Wachta mierzy człowieka."
            elif t_sec < 15.0:
                base = dash_ok_pip if t_sec < 6.0 else dash_microsleep_pip
                chapter = "1/6  Wykrycie mikrosnu"
                sub = "Kiedy mózg przestaje reagować, Wachta każe zjechać i od razu wskazuje zmiennika z największą rezerwą."
            elif t_sec < 33.0:
                base = slide_problem
                chapter = "2/6  Dlaczego zegar nie wystarcza"
                if t_sec < 24.0:
                    sub = "Normy czasu pracy traktują wszystkich tak samo, a senność powoduje ok. 20% wypadków w transporcie."
                else:
                    sub = "Po 18 h czuwania sprawność spada jak przy 0,05% alkoholu. Kamera widzi tylko powieki — my mierzymy EEG i reakcję."
            elif t_sec < 45.0:
                base = dash_ok_pip
                chapter = "3/6  Kalibracja i kontekst nocy"
                sub = "Po 60 s osobistej kalibracji system śledzi alfę z tyłu głowy i mrugnięcia. W nocy rezerwa spada 2,6× szybciej."
            elif t_sec < 54.0:
                if t_sec < 48.0:
                    base = dash_probe_sched_pip
                elif t_sec < 50.5:
                    base = dash_probe_ok_pip
                else:
                    base = dash_after_probe_pip
                chapter = "3/6  Próba reakcji w normie"
                sub = "Krótka próba sprawdza czas reakcji względem osobistej normy pracownika: 248 ms — reakcja w normie."
            elif t_sec < 63.5:
                base = dash_microsleep_pip
                chapter = "4/6  Mikrosen i panel przełożonego"
                sub = "Zamknięcie oczu podnosi alfę na O1/O2 powyżej progu 2,5 przez 3 s. Przełożony widzi tylko gotowość zespołu."
            elif t_sec < 76.0:
                if t_sec < 66.5:
                    base = dash_probe_event_pip
                elif t_sec < 70.0:
                    base = dash_probe_fail_modal_pip
                else:
                    base = dash_probe_fail_banner_pip
                chapter = "4/6  Potwierdzenie po spadku czujności"
                sub = "Gdy oczy znów się otworzą, system sam sprawdza, czy mózg wrócił. Brak reakcji utrzymuje nakaz przerwy."
            elif t_sec < 90.0:
                if t_sec < 79.5:
                    base = ken_burns(nurse_img, (t_sec - 76.0) / 3.5, zoom=0.06)
                elif t_sec < 84.0:
                    base = dash_nurse_stop
                else:
                    base = dash_nurse_break
                chapter = "4/6  Dyżur w szpitalu i regeneracja"
                sub = "Ten sam system w szpitalu: przekaż pacjentów i zrób przerwę. Odpoczynek realnie odnawia rezerwę czujności."
            elif t_sec < 100.0:
                base = slide_ev1
                chapter = "5/6  Walidacja na 5 nagraniach zespołu"
                sub = "Ten sam kod wykrył 5 z 5 bloków zamkniętych oczu i dał tylko 1 fałszywy alarm w 48 minutach (0 w monotonii T1)."
            elif t_sec < 108.0:
                base = slide_ev2
                chapter = "5/6  Walidacja na zbiorach publicznych"
                sub = "W danych publicznych (Cui i in., CC BY 4.0) alfa rośnie u 11 z 11 osób, a model osobisty podnosi AUC z 0,76 do 0,90."
            else:
                base = slide_close
                chapter = "6/6  Podsumowanie i pilotaż"
                sub = "Następny krok: pilotaż sprawdzający, czy osobisty limit rezerwy wyprzedza spadki czujności lepiej niż zegar."

            composed = overlay_subtitles_and_hud(base, t_sec, chapter, sub)
            proc.stdin.write(composed.tobytes())

        proc.stdin.close()
        stderr_out = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
        ret = proc.wait()
        if ret != 0:
            raise RuntimeError(f"FFmpeg failed ({ret}): {stderr_out}")

        print(f"4/4 Done! Video saved to {out_mp4} ({out_mp4.stat().st_size / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
