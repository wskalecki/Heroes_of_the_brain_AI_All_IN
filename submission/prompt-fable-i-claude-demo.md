# Prompty: Claude (żywe wyklikanie demo) + Fable (motion design i montaż)

Poniżej masz dwa gotowe prompty:
1. **Prompt dla Claude (Computer Use / Claude Code z przeglądarką)** — żeby uruchomił prawdziwy serwer Wachty, wyklikał cały scenariusz na żywo (z płynnym ruchem wykresów i kursora) i zapisał surowe nagranie ekranu `.mp4`.
2. **Prompt pod Fable** — żeby z nagrania dashboardu oraz przebitek z `submission/img/` i wykresów z `docs/img/` zmontował dynamiczny, dopieszczony wizualnie film `≤ 1:55` (1080p, 16:9) z najazdami kamery (zoom-in na alerty i wykresy), płynnymi przejściami i typografią kinetyczną.

---

## Krok 1: Prompt dla Claude (żeby wyklikał żywe demo na ekranie)

Wklej ten prompt do **Claude Code / Claude z dostępem do przeglądarki** w katalogu naszego repozytorium:

```text
Chcę nagrać 75-sekundowe, płynne wideo (1920x1080, 30 lub 60 fps) z żywej interakcji z naszym dashboardem Wachty do wstawienia w montażu w Fable.

Wykonaj po kolei:
1. Uruchom serwer Wachty w tle w przyspieszonym trybie odtwarzania z nocnym kontekstem:
   `python -m wachta --source replay --file data/recordings/wojtek_1-raw.fif --speed 4 --wake 19 --clock 02:30 --no-browser`
   (lub użyj `--source sim --wake 19 --clock 02:30` + endpointów WebSocket, jeśli chcesz precyzyjnie sterować czasem każdego przejścia).
2. Otwórz `http://127.0.0.1:8765` w oknie przeglądarki o wymiarach dokładnie `1920x1080` (bez paska zakładek) i rozpocznij nagrywanie ekranu (Playwright `record_video_dir` w 1920x1080 lub `ffmpeg` z Xvfb/ekranu) do pliku `submission/live-dashboard-capture.mp4`.
3. Wyklikaj na żywo z widocznym, płynnym ruchem kursora dokładnie 5 scen ze `scenariusz-demo.md`:
   - Scena A (0:00–0:12): Kalibracja kończy się -> zielony stan „Możesz pracować”, rezerwa czujności ~92%, w karcie kontekstu widać „19 h od przebudzenia” i „02:30 (noc)”. Przejedź płynnie kursorem po wykresie „Wskaźnik czujności, ostatnie 3 minuty” oraz „Rezerwa czujności w czasie zmiany”.
   - Scena B (0:12–0:25): Kliknij przycisk „Sprawdź reakcję”. Gdy pojawi się pomarańczowe koło „Reakcja!”, odczekaj ~250 ms i naciśnij `Space` -> pokaż przez 3 sekundy zielone koło z wynikiem w normie (np. „248 ms — Reakcja w normie”).
   - Scena C (0:25–0:42): Wejście w blok zamkniętych oczu (`eyes_closed`) -> wykres wskaźnika czujności rośnie powyżej czerwonej linii progu 2,5, karta „Oczy” zmienia się na „zamknięte”, a główny status zmienia się na czerwony „Przerwa teraz”. Zjedź kursorem na dół na „Panel przełożonego”, gdzie przy Wojtku świeci „Przerwa teraz”, a przy Rudym i Adim „Możesz pracować”.
   - Scena D (0:42–0:58): Po wyjściu z bloku zamkniętych oczu pojawia się automatyczna próba weryfikacyjna „Reakcja! (sprawdzenie po spadku czujności)”. NIE klikaj spacji przez 3 sekundy -> pozwól, by pojawiło się czerwone koło „Brak reakcji”, które utrzymuje status „Przerwa teraz” i obniża rezerwę czujności.
   - Scena E (0:58–1:12): Kliknij przycisk „Rozpocznij przerwę” -> status zmienia się na niebieski „Przerwa trwa — Odpocznij. W tym czasie rezerwa wraca”, a krzywa rezerwy czujności zaczyna rosnąć.
4. Zatrzymaj nagrywanie i przekonwertuj plik wyjściowy przez `ffmpeg` do `submission/live-dashboard-capture.mp4` (H.264, `yuv420p`, `1920x1080`).
```

---

## Krok 2: Zoptymalizowany prompt pod Fable (motion design i uładnienie wideo)

Wgraj do projektu w **Fable** pliki:
- `submission/wachta-demo-2min.mp4` (oraz `submission/live-dashboard-capture.mp4`, jeśli wygenerujesz żywy przebieg z Kroku 1),
- przebitki z `submission/img/` (`driver-night-broll.jpg`, `nurse-shift-broll.jpg`, `pip-eyes-open.jpg`, `pip-eyes-closed.jpg`),
- wykresy z `docs/img/` (`trafnosc-na-nagraniach.png`, `drowsiness-public-auc-and-calibration.png`, `pvt-alpha-early-warning-cogbci.png`),

a następnie wklej poniższy prompt (po angielsku — Fable najlepiej rozumie dyrektywy kompozycji i kamery po angielsku, z nakazem zachowania polskich napisów):

```text
Polish and animate this 1:54 hackathon product demo video ("Wachta — Adaptive Systems", 1920x1080, 16:9, 24fps) into a sleek, high-contrast tech product reel while strictly keeping total duration under 1:55 and preserving all Polish UI text and captions verbatim.

VISUAL STYLE & MOTION DESIGN INSTRUCTIONS:
1. Smooth 2.5D Camera Moves on Dashboard UI:
   - Instead of flat static full-screen captures of the web dashboard, place the dashboard on a clean dark-slate canvas (#0B1120) with a subtle drop shadow and rounded corners (16px), and animate smooth ease-in-out camera pans and 1.35x zoom-ins onto the active UI region at each beat:
     * [0:33–0:44] Zoom 1.3x into the top-left status card ("Możesz pracować", "92% Rezerwa czujności", "19 h od przebudzenia / 26% / h").
     * [0:45–0:53] Snap-zoom 1.4x to the center orange reaction probe modal ("Reakcja!") -> pulse ripple effect when it turns green ("248 ms — Reakcja w normie").
     * [0:54–1:03] Pan right to follow the rising blue EEG alpha line crossing the red threshold (2.5) on the top chart, then pan left to the red alert card ("Przerwa teraz") with a subtle red glow pulse, and pan down to highlight the "Panel przełożonego" row showing the replacement teammate ("Rudy — Możesz pracować").
     * [1:04–1:15] Zoom into the post-incident reaction probe timing out into the red circle ("Brak reakcji").
     * [1:20–1:29] Zoom into the blue recovery state ("Przerwa trwa — 79%") after clicking "Rozpocznij przerwę".

2. Picture-in-Picture (PiP) Operator Feed Polish:
   - Style the bottom-right PiP operator camera (`pip-eyes-open.jpg` / `pip-eyes-closed.jpg`) as a live HUD overlay with a rounded border, subtle REC indicator dot, and a glowing border color that matches the current state (emerald #16A34A when alert, amber #D97706 during probe, crimson #DC2626 during eyes-closed microsleep).

3. B-Roll & Problem Hook [0:00–0:32]:
   - Add a slow cinematic Ken Burns push-in (1.00x -> 1.08x) on the night truck driver (`driver-night-broll.jpg`) and hospital night-shift nurse (`nurse-shift-broll.jpg`) with subtle film grain and a clean lower-third glassmorphism title bar.
   - On the problem/loop comparison slide [0:15–0:32], stagger-animate the 4 problem bullet points on the left and the 5 numbered adaptive-loop steps on the right with a 0.25s spring fade-up.

4. Scientific Validation Charts [1:30–1:47]:
   - Animate a clean highlight callout badge over the key metrics on the validation figures (`trafnosc-na-nagraniach.png` and `drowsiness-public-auc-and-calibration.png`):
     * "5 / 5 bloków zamkniętych oczu wykrytych (BrainAccess MINI)"
     * "1 fałszywy alarm w 48 min (0 w 15 min monotonii T1)"
     * "Kalibracja osobista: AUC 0,76 → 0,90 (Cui i in. 2022)"

5. Subtitles & Audio Cues:
   - Keep the Polish subtitles in a clean, high-contrast pill at the bottom safe-area (font: Inter/Plus Jakarta Sans SemiBold, 24px, white on #0F172A at 88% opacity).
   - Keep the audio cues (660 Hz reaction probe beep at 0:45 and 1:04, and 880/660 Hz two-tone alarm at 0:06 and 0:55) synced to the visual modal popups.
```
