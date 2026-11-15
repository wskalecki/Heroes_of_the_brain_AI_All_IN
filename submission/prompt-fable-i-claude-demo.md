# Prompty z dokładnymi ścieżkami w repozytorium (bez lokalnego pullowania)

Repozytorium publiczne: `https://github.com/wskalecki/Heroes_of_the_brain_AI_All_IN`
Gałąź z gotowymi plikami wideo, obrazami i prezentacją: **`submission-assets`**

---

## 1. Jeden wspólny prompt dla Claude / Fable (działającego na repozytorium GitHub)

Skopiuj i wklej w całości:

```text
Work directly on the public GitHub repository:
Repository: https://github.com/wskalecki/Heroes_of_the_brain_AI_All_IN
Branch with all existing video/image/presentation assets: `submission-assets`

If your workspace is currently checked out on `main`, first fetch and switch to `submission-assets`:
`git fetch origin submission-assets:submission-assets && git checkout submission-assets`

### EXISTING FILES IN THE REPOSITORY (branch `submission-assets`):
1. Current 1:54 demo video (1920x1080, 24fps, H.264 + AAC):
   - Path: `submission/wachta-demo-2min.mp4`
   - Raw URL: https://raw.githubusercontent.com/wskalecki/Heroes_of_the_brain_AI_All_IN/submission-assets/submission/wachta-demo-2min.mp4
2. Video generator script & timeline / voiceover script:
   - Path: `submission/build-demo-video.py`
   - Path: `submission/wideo-demo-scenariusz-i-lektor.md`
   - Path: `docs/scenariusz-demo.md`
   - Path: `docs/pitch.md`
3. AI B-Roll & Picture-in-Picture (PiP) operator images:
   - `submission/img/driver-night-broll.jpg` (https://raw.githubusercontent.com/wskalecki/Heroes_of_the_brain_AI_All_IN/submission-assets/submission/img/driver-night-broll.jpg)
   - `submission/img/nurse-shift-broll.jpg` (https://raw.githubusercontent.com/wskalecki/Heroes_of_the_brain_AI_All_IN/submission-assets/submission/img/nurse-shift-broll.jpg)
   - `submission/img/pip-eyes-open.jpg` (https://raw.githubusercontent.com/wskalecki/Heroes_of_the_brain_AI_All_IN/submission-assets/submission/img/pip-eyes-open.jpg)
   - `submission/img/pip-eyes-closed.jpg` (https://raw.githubusercontent.com/wskalecki/Heroes_of_the_brain_AI_All_IN/submission-assets/submission/img/pip-eyes-closed.jpg)
4. Validation charts in `docs/img/`:
   - `docs/img/trafnosc-na-nagraniach.png` (https://raw.githubusercontent.com/wskalecki/Heroes_of_the_brain_AI_All_IN/submission-assets/docs/img/trafnosc-na-nagraniach.png)
   - `docs/img/drowsiness-public-auc-and-calibration.png` (https://raw.githubusercontent.com/wskalecki/Heroes_of_the_brain_AI_All_IN/submission-assets/docs/img/drowsiness-public-auc-and-calibration.png)
   - `docs/img/pvt-alpha-early-warning-cogbci.png` (https://raw.githubusercontent.com/wskalecki/Heroes_of_the_brain_AI_All_IN/submission-assets/docs/img/pvt-alpha-early-warning-cogbci.png)
   - `docs/img/monotonia-minuta-po-minucie.png` (https://raw.githubusercontent.com/wskalecki/Heroes_of_the_brain_AI_All_IN/submission-assets/docs/img/monotonia-minuta-po-minucie.png)
5. Real web dashboard source code & EEG replay recordings:
   - Web UI: `src/wachta/web/index.html`, `src/wachta/web/style.css`, `src/wachta/web/app.js`
   - Server & DSP pipeline: `src/wachta/server.py`, `src/wachta/index.py`, `src/wachta/blinks.py`
   - Real EEG recordings: `data/recordings/wojtek_1-raw.fif`, `data/recordings/wojtek-monotonia_1-raw.fif`

---

### TASK PART 1 — LIVE INTERACTIVE DASHBOARD CAPTURE (for Claude / Browser Agent):
Instead of static screenshots of the dashboard, launch the real Wachta server from `src/wachta/` and record a smooth 30/60fps 1920x1080 browser interaction with visible cursor movements and live scrolling charts:
1. Start the server:
   `python -m wachta --source replay --file data/recordings/wojtek_1-raw.fif --speed 4 --wake 19 --clock 02:30 --no-browser`
   (or `--source sim --wake 19 --clock 02:30` for deterministic state transitions).
2. Open `http://127.0.0.1:8765` in a `1920x1080` viewport and click through the 5 demo beats from `docs/scenariusz-demo.md`:
   - Beat A [0:33–0:44]: Calibration finishes -> green status `"Możesz pracować"`, `"92% Rezerwa czujności"`, `"19 h od przebudzenia"`, `"26% / h"`. Hover cursor smoothly over the two live charts (`#chart-index` and `#chart-reserve`).
   - Beat B [0:45–0:53]: Click `"Sprawdź reakcję"` (`#btn-probe`). When the orange modal `"Reakcja!"` (`#probe`) appears, wait ~250 ms and press `Space` -> show the green confirmation circle `"248 ms — Reakcja w normie"`.
   - Beat C [0:54–1:03]: Enter the `eyes_closed` block -> live alpha prominence line crosses the red threshold `2.5` for 3 seconds, `"Oczy"` changes to `"zamknięte"`, main status switches to red `"Przerwa teraz"`. Move cursor down to `"Panel przełożonego"` (`#team-rows`) showing `"Wojtek — Przerwa teraz"` and `"Rudy — Możesz pracować"`.
   - Beat D [1:04–1:15]: Eyes reopen -> automatic post-event verification probe `"Reakcja! (sprawdzenie po spadku czujności)"` pops up. Do NOT press space for 3 seconds -> show red timeout circle `"Brak reakcji"`, keeping `"Przerwa teraz"` active.
   - Beat E [1:20–1:29]: Click `"Rozpocznij przerwę"` (`#btn-break`) -> status changes to blue `"Przerwa trwa — Odpocznij. W tym czasie rezerwa wraca"`, and the reserve curve begins recovering.

---

### TASK PART 2 — MOTION DESIGN & VIDEO POLISH (for Fable / Video Renderer):
Upgrade `submission/wachta-demo-2min.mp4` into a sleek 1080p (16:9, 24/30fps) hackathon product demo reel while keeping total duration strictly under `1:55` (hard limit `2:00`) and preserving all Polish UI labels and captions verbatim:

1. Smooth 2.5D Camera Moves on the Dashboard (`src/wachta/web/`):
   - Place the dashboard on a dark slate canvas (`#0B1120`) with rounded corners (`16px`) and soft shadow.
   - Animate smooth ease-in-out camera pans and `1.35x` zoom-ins onto the active UI region at each timestamp:
     * `[0:33–0:44]` Zoom `1.3x` into the top-left status card (`#state-card`: `"Możesz pracować"`, `"92%"`, `"19 h od przebudzenia"`).
     * `[0:45–0:53]` Snap-zoom `1.4x` to the center orange reaction probe modal (`#probe`: `"Reakcja!"`) -> pulse ripple effect when it turns green (`"248 ms — Reakcja w normie"`).
     * `[0:54–1:03]` Pan across `#chart-index` as the blue EEG alpha line crosses the red threshold (`2.5`), then pan left to the red alert card (`"Przerwa teraz"`) and down to `"Panel przełożonego"` (`#team-rows`).
     * `[1:04–1:15]` Zoom into the post-incident reaction probe timing out into the red circle (`"Brak reakcji"`).
     * `[1:20–1:29]` Zoom into the blue recovery state (`"Przerwa trwa — 79%"`) after clicking `"Rozpocznij przerwę"`.

2. Picture-in-Picture (PiP) Operator Feed Polish:
   - Style the bottom-right PiP operator feed (`submission/img/pip-eyes-open.jpg` and `submission/img/pip-eyes-closed.jpg`) as a live HUD overlay with rounded corners, a subtle `REC` dot, and a border glow matching the current state (emerald `#16A34A` when alert, amber `#D97706` during probe, crimson `#DC2626` during eyes-closed microsleep).

3. B-Roll & Problem Hook `[0:00–0:32]`:
   - Apply a slow cinematic Ken Burns push-in (`1.00x -> 1.08x`) on `submission/img/driver-night-broll.jpg` and `submission/img/nurse-shift-broll.jpg`.
   - On the problem vs. adaptive loop comparison slide `[0:15–0:32]`, stagger-animate the 4 problem points on the left and the 5 adaptive loop steps on the right with a `0.25s` spring fade-up.

4. Scientific Validation Charts `[1:30–1:47]`:
   - Display `docs/img/trafnosc-na-nagraniach.png`, `docs/img/monotonia-minuta-po-minucie.png`, `docs/img/drowsiness-public-auc-and-calibration.png`, and `docs/img/pvt-alpha-early-warning-cogbci.png` with animated callout badges highlighting:
     * `"5 / 5 bloków zamkniętych oczu wykrytych (BrainAccess MINI)"`
     * `"1 fałszywy alarm w 48 min (0 w 15 min monotonii T1)"`
     * `"Kalibracja osobista: AUC 0,76 → 0,90 (Cui i in. 2022)"`

5. Output:
   - Save and commit the final polished video back to `submission/wachta-demo-2min.mp4` on branch `submission-assets` (keep file size `< 5 MB` so `.github/scripts/check-repo.py` passes).
```
