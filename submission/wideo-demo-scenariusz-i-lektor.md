# Wideo Demo (1:54) — Scenariusz i Lektor AI

Gotowy film **[`wachta-demo-2min.mp4`](wachta-demo-2min.mp4)** (`1920x1080`, `24 fps`, `1 min 54 s`, ok. 4,5 MB, z zapasem poniżej limitu `2:00` na `hotb.pl`) składa się z:

- **Nagrania prawdziwego dashboardu Wachty.** Serwer z `src/wachta/` odtwarza nagranie EEG Wojtka z BrainAccess MINI (`data/recordings`, od 200 s, czas zmiany ×10, `--wake 07:00 --clock 02:30`), a skrypt [`capture-dashboard.js`](capture-dashboard.js) przechodzi przez sceny z [`docs/scenariusz-demo.md`](../docs/scenariusz-demo.md) w prawdziwej przeglądarce i zapisuje klatki oraz log zdarzeń. Wszystkie stany, liczby i próby reakcji na ekranie pochodzą z tego przebiegu, nic nie jest wstrzyknięte. Na filmie jest podpis „odtworzenie nagrania EEG”, bo to nie jest tryb na żywo.
- **Montażu** w [`build-demo-video.py`](build-demo-video.py): ciemne tło z zaokrągloną kartą dashboardu, płynne najazdy kamery (1,3–1,4×) na kartę stanu, okno próby reakcji, wykres wskaźnika, panel przełożonego i kafelek reakcji, kursor i fale kliknięć odtworzone z logu, ramka PiP zmieniająca kolor wraz ze stanem (zielony: oczy otwarte, bursztynowy: próba reakcji, czerwony: oczy zamknięte), przebitki Ken Burns, slajdy z animowanymi punktami, plakietki na wykresach walidacyjnych i napisy po polsku.
- **Czterech obrazów AI** w [`img/`](img/): kierowca ciężarówki, pielęgniarka i dwa ujęcia okienka PiP. To wizualizacje, nie nagranie osoby z czepkiem, więc okienko PiP ma podpis „wizualizacja (AI)”. Zamknięte oczy w PiP pokazuje stan wykryty przez kod (`lapse`), a nie kamera.
- **Wykresów walidacyjnych** z repozytorium ([`trafnosc-na-nagraniach.png`](../docs/img/trafnosc-na-nagraniach.png), [`monotonia-minuta-po-minucie.png`](../docs/img/monotonia-minuta-po-minucie.png), [`drowsiness-public-auc-and-calibration.png`](../docs/img/drowsiness-public-auc-and-calibration.png), [`pvt-alpha-early-warning-cogbci.png`](../docs/img/pvt-alpha-early-warning-cogbci.png)).
- **Ścieżki dźwiękowej**: ambient oraz sygnały próby reakcji i alarmu w chwilach, w których naprawdę wystąpiły.

Jak odtworzyć (potrzebne: Node z Playwrightem, Python z pakietem `wachta[analysis]`, `ffmpeg`, nagrania z `data/recordings`; nagranie trwa ok. 4 minuty):

```bash
node submission/capture-dashboard.js /tmp/wachta-capture python3 wojtek 200
```

```bash
python submission/build-demo-video.py /tmp/wachta-capture
```

Drugi skrypt zapisuje wersję do repozytorium (`24 fps`, poniżej 5 MB, limit w `check-repo.py`) oraz wersję wysokiej jakości (`30 fps`, ok. 20 MB) w folderze nagrania. Wersję wysoką warto wgrać na `hotb.pl`, jeśli formularz przyjmuje większy plik.

---

## Rozkład scen i tekst lektora (1:54)

| Przedział | Sekcja w wideo | Tekst lektora (PL) |
| :--- | :--- | :--- |
| **0:00 – 0:15** | **1/6 Problem i zapowiedź alarmu** (kierowca, pielęgniarka, podgląd sceny „Przerwa teraz”) | *„Druga trzydzieści w nocy, dziewiętnasta godzina od przebudzenia. Przepisy patrzą na zegar, a Wachta patrzy na człowieka. Gdy oczy zamykają się na dłużej niż kilka sekund, system każe zjechać i od razu wskazuje zmiennika z największą rezerwą czujności.”* |
| **0:15 – 0:33** | **2/6 Dlaczego zegar nie wystarcza** (do 20% wypadków, 17–19 h bez snu = 0,05% alkoholu, 5 kroków pętli Wachty) | *„Sztywne normy czasu pracy traktują wszystkich tak samo, a ze zmęczeniem wiąże się do dwudziestu procent wypadków drogowych. Po osiemnastu godzinach czuwania sprawność spada jak przy pół promila alkoholu. Kamera widzi oczy. Wachta dokłada to, czego kamera nie zobaczy: osobisty profil i sprawdzenie, czy człowiek naprawdę reaguje.”* |
| **0:33 – 0:54** | **3/6 Kalibracja, kontekst nocy i próba reakcji w normie** (`99%` -> próba `325 ms`) | *„Po sześćdziesięciu sekundach osobistej kalibracji system śledzi fale alfa z tyłu głowy i mrugnięcia. Po długim czuwaniu w nocy zakładamy, że rezerwa czujności spada ponad dwa razy szybciej; to założenie, które zweryfikuje pilotaż. Drugi sygnał to zachowanie: krótka próba dźwiękowa sprawdza czas reakcji względem osobistej normy: trzysta dwadzieścia pięć milisekund, w normie.”* |
| **0:54 – 1:16** | **4/6 Zamknięte oczy, panel przełożonego i brak reakcji** (`87%` -> `Brak reakcji` -> `74%`) | *„Gdy zamknięcie oczu podnosi falę alfa na elektrodach potylicznych powyżej progu przez trzy sekundy, włącza się czerwony alarm, a przełożony widzi wyłącznie gotowość zespołu. Po otwarciu oczu system sam sprawdza, czy człowiek reaguje; brak reakcji utrzymuje nakaz przerwy.”* |
| **1:16 – 1:30** | **4/6 Dyżur w szpitalu i regeneracja** (przekazanie pacjentów + `Przerwa trwa`, rezerwa `74%` -> `82%`, przyspieszone ×5) | *„Ten sam system działa na nocnym dyżurze w szpitalu: przekaż pacjentów zmiennikowi i zrób przerwę. W modelu rezerwy odpoczynek ją odnawia, co widać na wykresie.”* |
| **1:30 – 1:48** | **5/6 Walidacja na sprzęcie BrainAccess MINI i zbiorach publicznych** (5/5 bloków, Cui 2022, COG-BCI) | *„Ten sam kod wykrył pięć z pięciu bloków zamkniętych oczu na naszych nagraniach z BrainAccess MINI przy zaledwie jednym fałszywym alarmie na czterdzieści osiem minut. W danych publicznych model uczony na danych danej osoby podnosi pole pod krzywą ROC z siedemdziesięciu sześciu do dziewięćdziesięciu setnych.”* |
| **1:48 – 1:54** | **6/6 Podsumowanie i pilotaż** | *„Wachta. Zmęczenie i czujność mierzone na człowieku, nie na zegarze.”* |

---

## Opcjonalnie: Jak w 60 sekund dołożyć głos lektora AI z Google AI Studio (Gemini TTS)

Plik **[`wachta-demo-2min.mp4`](wachta-demo-2min.mp4)** ma już wbudowane napisy PL oraz kompletną ścieżkę dźwiękową z sygnałami próby reakcji i alarmów, więc **nadaje się do wysłania na `hotb.pl` od razu**.

Jeśli chcesz dograć naturalny polski głos lektora z **Google AI Studio**:

1. Wejdź na **Google AI Studio** (`aistudio.google.com`) -> **Generate speech** (model `gemini-2.5-flash-preview-tts`, głos np. `Charon` lub `Puck`).
2. Wklej powyższy tekst lektora jednym ciągiem:
   ```text
   Druga trzydzieści w nocy, dziewiętnasta godzina od przebudzenia. Przepisy patrzą na zegar, a Wachta patrzy na człowieka. Gdy oczy zamykają się na dłużej niż kilka sekund, system każe zjechać i od razu wskazuje zmiennika z największą rezerwą czujności. Sztywne normy czasu pracy traktują wszystkich tak samo, a ze zmęczeniem wiąże się do dwudziestu procent wypadków drogowych. Po osiemnastu godzinach czuwania sprawność spada jak przy pół promila alkoholu. Kamera widzi oczy. Wachta dokłada to, czego kamera nie zobaczy: osobisty profil i sprawdzenie, czy człowiek naprawdę reaguje. Po sześćdziesięciu sekundach osobistej kalibracji system śledzi fale alfa z tyłu głowy i mrugnięcia. Po długim czuwaniu w nocy zakładamy, że rezerwa czujności spada ponad dwa razy szybciej; to założenie, które zweryfikuje pilotaż. Drugi sygnał to zachowanie: krótka próba dźwiękowa sprawdza czas reakcji względem osobistej normy: trzysta dwadzieścia pięć milisekund, w normie. Gdy zamknięcie oczu podnosi falę alfa na elektrodach potylicznych powyżej progu przez trzy sekundy, włącza się czerwony alarm, a przełożony widzi wyłącznie gotowość zespołu. Po otwarciu oczu system sam sprawdza, czy człowiek reaguje; brak reakcji utrzymuje nakaz przerwy. Ten sam system działa na nocnym dyżurze w szpitalu: przekaż pacjentów zmiennikowi i zrób przerwę. W modelu rezerwy odpoczynek ją odnawia, co widać na wykresie. Ten sam kod wykrył pięć z pięciu bloków zamkniętych oczu na naszych nagraniach z BrainAccess MINI przy zaledwie jednym fałszywym alarmie na czterdzieści osiem minut. W danych publicznych model uczony na danych danej osoby podnosi pole pod krzywą ROC z siedemdziesięciu sześciu do dziewięćdziesięciu setnych. Wachta. Zmęczenie i czujność mierzone na człowieku, nie na zegarze.
   ```
3. Pobierz wygenerowany plik jako `lektor.wav` i połącz go z wideo jednym poleceniem `ffmpeg` w folderze `submission/`:
   ```bash
   ffmpeg -y -i wachta-demo-2min.mp4 -i lektor.wav \
     -filter_complex "[0:a]volume=0.45[bg];[1:a]volume=1.25[vo];[bg][vo]amix=inputs=2:duration=first[aout]" \
     -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k wachta-demo-2min-z-lektorem.mp4
   ```
