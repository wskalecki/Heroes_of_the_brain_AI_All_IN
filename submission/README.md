# Paczka zgłoszeniowa — Heroes of the Brain 2026 (Adaptive Systems)

Ten folder zawiera gotowe pliki do formularza zgłoszeniowego na `https://hotb.pl` (termin: 15.11.2026 przed 11:00):

1. **[`wachta-demo-2min.mp4`](wachta-demo-2min.mp4)**: film demo (`1:54`, `1920x1080`, `24 fps`, ok. 4,5 MB). Prawdziwy dashboard Wachty odtwarzający nagranie EEG zespołu (nagrany skryptem [`capture-dashboard.js`](capture-dashboard.js), zmontowany przez [`build-demo-video.py`](build-demo-video.py)), przebitki AI i wykresy walidacyjne z [`docs/img/`](../docs/img/). Opis powstawania, tekst lektora i polecenia do odtworzenia: punkt 4.
2. **[`wachta-prezentacja-10-slajdow.pdf`](wachta-prezentacja-10-slajdow.pdf)** — 10-slajdowa prezentacja PDF (format `16:9`) wygenerowana na podstawie [`docs/pitch.md`](../docs/pitch.md).
3. **[`wachta-prezentacja-10-slajdow.html`](wachta-prezentacja-10-slajdow.html)** — źródłowa wersja HTML prezentacji (można otworzyć w przeglądarce, wprowadzić poprawki i zapisać jako PDF przez `Cmd+P` / `Ctrl+P`).
4. **[`wideo-demo-scenariusz-i-lektor.md`](wideo-demo-scenariusz-i-lektor.md)** — rozkład czasowy 6 sekcji filmu demo, pełny tekst polskiego lektora do wklejenia w Google AI Studio (`Generate Speech` / Gemini TTS) oraz komenda `ffmpeg` do zmiksowania głosu z wideo.
5. **[`wachta-repo-dla-ai-studio.txt`](wachta-repo-dla-ai-studio.txt)** — pojedynczy plik tekstowy z całą dokumentacją (`README.md`, `docs/*.md`) i kodem (`src/wachta/*`), gotowy do przeciągnięcia (*drag & drop*) do Google AI Studio lub Google NotebookLM.
6. **Publiczny link do repozytorium GitHub:** `https://github.com/wskalecki/Heroes_of_the_brain_AI_All_IN`
