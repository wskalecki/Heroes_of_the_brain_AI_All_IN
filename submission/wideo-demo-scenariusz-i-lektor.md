# Wideo Demo (1:54) — Scenariusz i Lektor AI

Gotowy film **[`wachta-demo-2min.mp4`](wachta-demo-2min.mp4)** (`1920x1080`, `24 fps`, `1 min 54 s` — z bezpiecznym zapasem poniżej limitu `2:00` na `hotb.pl`) został wygenerowany automatycznie w **Wariancie B**:

- **Prawdziwy interfejs Wachty** wyrenderowany w 1080p w bezgłowym Chromium bezpośrednio z plików [`index.html`](../src/wachta/web/index.html), [`style.css`](../src/wachta/web/style.css) i [`app.js`](../src/wachta/web/app.js).
- **4 fotorealistyczne ujęcia AI (Google Imagen)** w folderze [`img/`](img/): kierowca ciężarówki o 2:30 w nocy w opasce EEG, pielęgniarka na nocnym dyżurze w szpitalu oraz okienko kamery PiP (oczy otwarte / oczy zamknięte przy mikrosnie).
- **Prawdziwe wykresy walidacyjne** z repozytorium ([`trafnosc-na-nagraniach.png`](../docs/img/trafnosc-na-nagraniach.png), [`monotonia-minuta-po-minucie.png`](../docs/img/monotonia-minuta-po-minucie.png), [`drowsiness-public-auc-and-calibration.png`](../docs/img/drowsiness-public-auc-and-calibration.png), [`pvt-alpha-early-warning-cogbci.png`](../docs/img/pvt-alpha-early-warning-cogbci.png)).
- **Wbudowane napisy po polsku** na dole ekranu oraz wygenerowana ścieżka audio (ambient + sygnały próby reakcji i alarmu mikrosnu).

---

## Rozkład scen i tekst lektora (1:54)

| Przedział | Sekcja w wideo | Tekst lektora (PL) |
| :--- | :--- | :--- |
| **0:00 – 0:15** | **1/6 Problem na żywo i wykrycie mikrosnu** (nocna trasa + natychmiastowy pokaz alarmu) | *„Druga trzydzieści w nocy, dziewiętnasta godzina od przebudzenia. Przepisy patrzą na zegar, a Wachta mierzy człowieka. Kiedy mózg przestaje reagować, system każe zjechać i od razu wskazuje zmiennika z największą rezerwą czujności.”* |
| **0:15 – 0:33** | **2/6 Dlaczego zegar nie wystarcza** (20% wypadków, 17–19 h bez snu = 0,05% alkoholu, 5 kroków pętli Wachty) | *„Sztywne normy czasu pracy traktują wszystkich tak samo, a senność powoduje dwadzieścia procent wypadków w transporcie. Po osiemnastu godzinach czuwania sprawność spada jak przy pół promila alkoholu. Kamera widzi dopiero opadającą powiekę — my mierzymy fale mózgowe i czas reakcji.”* |
| **0:33 – 0:54** | **3/6 Kalibracja, kontekst nocy i próba reakcji w normie** (`92%` -> próba `248 ms`) | *„Po sześćdziesięciu sekundach osobistej kalibracji na starcie zmiany system śledzi fale alfa z tyłu głowy i mrugnięcia. W nocy rezerwa czujności spada ponaddwukrotnie szybciej. Krótka próba dźwiękowa sprawdza czas reakcji względem osobistej normy pracownika: dwieście czterdzieści osiem milisekund — reakcja w normie.”* |
| **0:54 – 1:16** | **4/6 Mikrosen, panel przełożonego i brak reakcji** (`78%` -> `Brak reakcji` -> `68%`) | *„Gdy zamknięcie oczu podnosi falę alfa na elektrodach potylicznych powyżej progu przez trzy sekundy, włącza się czerwony alarm, a przełożony widzi wyłącznie gotowość zespołu. Po otwarciu oczu system sam weryfikuje, czy pracownik może wrócić — brak reakcji utrzymuje nakaz przerwy.”* |
| **1:16 – 1:30** | **4/6 Dyżur w szpitalu i regeneracja** (przekazanie pacjentów + tryb `Przerwa trwa 79%`) | *„Ten sam system działa na nocnym dyżurze w szpitalu: przekaż pacjentów zmiennikowi i zrób przerwę. Odpoczynek z zamkniętymi oczami realnie odnawia rezerwę czujności na wykresie.”* |
| **1:30 – 1:48** | **5/6 Walidacja na sprzęcie BrainAccess MINI i zbiorach publicznych** (5/5 bloków, Cui 2022, COG-BCI) | *„Ten sam kod wykrył pięć z pięciu bloków zamkniętych oczu na naszych nagraniach z BrainAccess MINI przy zaledwie jednym fałszywym alarmie na czterdzieści osiem minut. W danych publicznych model osobisty podnosi pole pod krzywą ROC z siedemdziesięciu sześciu do dziewięćdziesięciu setnych.”* |
| **1:48 – 1:54** | **6/6 Podsumowanie i pilotaż** | *„Wachta. Zmęczenie i czujność mierzone na człowieku, nie na zegarze.”* |

---

## Opcjonalnie: Jak w 60 sekund dołożyć głos lektora AI z Google AI Studio (Gemini TTS)

Plik **[`wachta-demo-2min.mp4`](wachta-demo-2min.mp4)** ma już wbudowane napisy PL oraz kompletną ścieżkę dźwiękową z sygnałami próby reakcji i alarmów, więc **nadaje się do wysłania na `hotb.pl` od razu**.

Jeśli chcesz dograć naturalny polski głos lektora z **Google AI Studio**:

1. Wejdź na **Google AI Studio** (`aistudio.google.com`) -> **Generate speech** (model `gemini-2.5-flash-preview-tts`, głos np. `Charon` lub `Puck`).
2. Wklej powyższy tekst lektora jednym ciągiem:
   ```text
   Druga trzydzieści w nocy, dziewiętnasta godzina od przebudzenia. Przepisy patrzą na zegar, a Wachta mierzy człowieka. Kiedy mózg przestaje reagować, system każe zjechać i od razu wskazuje zmiennika z największą rezerwą czujności. Sztywne normy czasu pracy traktują wszystkich tak samo, a senność powoduje dwadzieścia procent wypadków w transporcie. Po osiemnastu godzinach czuwania sprawność spada jak przy pół promila alkoholu. Kamera widzi dopiero opadającą powiekę — my mierzymy fale mózgowe i czas reakcji. Po sześćdziesięciu sekundach osobistej kalibracji na starcie zmiany system śledzi fale alfa z tyłu głowy i mrugnięcia. W nocy rezerwa czujności spada ponaddwukrotnie szybciej. Krótka próba dźwiękowa sprawdza czas reakcji względem osobistej normy pracownika: dwieście czterdzieści osiem milisekund — reakcja w normie. Gdy zamknięcie oczu podnosi falę alfa na elektrodach potylicznych powyżej progu przez trzy sekundy, włącza się czerwony alarm, a przełożony widzi wyłącznie gotowość zespołu. Po otwarciu oczu system sam weryfikuje, czy pracownik może wrócić — brak reakcji utrzymuje nakaz przerwy. Ten sam system działa na nocnym dyżurze w szpitalu: przekaż pacjentów zmiennikowi i zrób przerwę. Odpoczynek z zamkniętymi oczami realnie odnawia rezerwę czujności na wykresie. Ten sam kod wykrył pięć z pięciu bloków zamkniętych oczu na naszych nagraniach z BrainAccess MINI przy zaledwie jednym fałszywym alarmie na czterdzieści osiem minut. W danych publicznych model osobisty podnosi pole pod krzywą ROC z siedemdziesięciu sześciu do dziewięćdziesięciu setnych. Wachta. Zmęczenie i czujność mierzone na człowieku, nie na zegarze.
   ```
3. Pobierz wygenerowany plik jako `lektor.wav` i połącz go z wideo jednym poleceniem `ffmpeg` w folderze `submission/`:
   ```bash
   ffmpeg -y -i wachta-demo-2min.mp4 -i lektor.wav \
     -filter_complex "[0:a]volume=0.45[bg];[1:a]volume=1.25[vo];[bg][vo]amix=inputs=2:duration=first[aout]" \
     -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k wachta-demo-2min-z-lektorem.mp4
   ```
