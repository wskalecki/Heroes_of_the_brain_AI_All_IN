# Zadania

Podział pracy z [`plan-projektu.md`](plan-projektu.md) na zadania, które można brać od razu.
Plik jest dla ludzi i dla agentów AI. Termin oddania: niedziela 15.11.2026 do 11:00, cel zespołu: gotowe ok. 10:00 (kod zamrożony ok. 8:00).

## Jak z tego korzystać

1. Zrób `git pull origin main`, potem przeczytaj [`decyzje.md`](decyzje.md) i [`plan-projektu.md`](plan-projektu.md).
2. Bierz zadania tylko ze strumienia osoby, z którą pracujesz. Każdy strumień ma właściciela i własne pliki.
3. Zaczynasz zadanie: zmień status na `w toku` i dopisz gałąź. Kończysz: `zrobione` i numer PR.
   Status zmieniaj w tym samym PR co pracę.
4. Poza plikami swojego strumienia zmieniaj tylko to, co konieczne, małymi commitami.
5. Zadanie stoi: status `zablokowane: powód` i wiadomość na czacie zespołu.
6. Kod zamrażamy 2 h przed oddaniem. Potem tylko poprawki błędów.

Statusy: `do zrobienia`, `w toku`, `zrobione`, `zablokowane`.
Priorytety: **MUST** (bez tego nie ma demo), **SHOULD** (wzmacnia pitch), **COULD** (tylko gdy zostanie czas).

## Strumienie

| Strumień | Właściciel | Pliki strumienia |
|---|---|---|
| A. Sygnał i aplikacja | Wojtek (z agentem) | `src/wachta/`, `tests/`, `experiments/`, `pyproject.toml`, `docs/uruchomienie.md`, `docs/trafnosc-na-nagraniach.md` |
| B. Dane i dowody | Adrian (z agentem) | `data/analysis/`, `docs/datasety-eeg-zrodla.md` |
| C. Pomiary | Filip | nowe pliki w `data/recordings/` (nagrania, adnotacje, `checkpoints.csv`) |
| D. Pitch i demo | Rudy | `docs/pitch.md`, `docs/scenariusz-demo.md`, `docs/rynek-*.md` |

Role Filipa i Rudego to propozycja, mogą się zamienić.

Pliki wspólne (zmiany małe i celowe): `README.md`, `AGENTS.md`, `.gitignore`, `docs/README.md`, `docs/decyzje.md`,
`docs/plan-projektu.md`, `docs/zadania.md`. Wspólny jest też folder `docs/img/` z wykresami na slajdy.

## A. Sygnał i aplikacja

| ID | Priorytet | Zadanie | Wynik | Gotowe, gdy | Status |
|---|---|---|---|---|---|
| A1 | MUST | Rdzeń: filtr strumieniowy, cechy okna, kalibracja na osobę, wskaźnik, stany, rezerwa | `src/wachta/`, `tests/`, `pyproject.toml` | `pytest` przechodzi | zrobione |
| A2 | MUST | Trafność pipeline'u na 4 nagraniach z adnotacjami | `experiments/validate-on-recordings.py`, `docs/trafnosc-na-nagraniach.md` | tabela na osobę: wykrycie `eyes_closed` i fałszywe alarmy poza nim | zrobione: 4 z 4 bloków, 1 fałszywy alarm |
| A3 | MUST | Odtwarzanie nagrania, serwer i dashboard | `src/wachta/sources.py`, `src/wachta/server.py`, `src/wachta/web/` | dashboard działa w trybie odtwarzania i zmienia stan w bloku `eyes_closed` | zrobione |
| A4 | MUST | Tryb na żywo z BrainAccess Board | źródło `board` w `sources.py`, `docs/uruchomienie.md` | na laptopie ze sprzętem płyną próbki, a zamknięcie oczu zmienia stan | zrobione: test na sprzęcie 14.11 (kalibracja, zamknięcie oczu → „Przerwa teraz”) |
| A5 | SHOULD | Narzędzie punktu pomiarowego: odlicza kroki, zapisuje znaczniki i KSS | `src/wachta/session.py` | zapisuje adnotacje i wiersz w `checkpoints.csv` w formatach z sekcji „Kontrakty” | zrobione: `feat/checkpoint-session` |
| A6 | COULD | Prognoza czasu do progu, test czasu reakcji w przeglądarce, krzywe z Garmin Connect | `src/wachta/pvt.py`, `src/wachta/pvt.html` (`minutes_to_warn` / `minutes_to_stop` w `src/wachta/index.py`) | test PVT-B działa w przeglądarce i zapisuje wynik do `data/recordings/pvt.csv` | zrobione: `feat/pvt-test` (PVT-B + prognoza w `index.py`; odczyty Garmin w `checkpoints.csv`) |
| A7 | MUST | Stan oczu z EEG: mrugnięcia na F3/F4, rozdzielenie spadku czujności na „oczy zamknięte” i „senność przy otwartych oczach” | `src/wachta/blinks.py`, `src/wachta/index.py`, dashboard | na nagraniach zespołu blok `eyes_closed` jest klasyfikowany jako „oczy zamknięte”; tabela w `docs/trafnosc-na-nagraniach.md` | zrobione |
| A8 | MUST | Próba reakcji wywoływana przez EEG: gdy wskaźnik zbliża się do progu, dashboard prosi o reakcję; > 355 ms albo brak = potwierdzony spadek | `src/wachta/index.py`, `src/wachta/server.py`, `src/wachta/web/` | próba pojawia się przy rosnącym wskaźniku i ręcznie, czas reakcji wpływa na stan i rezerwę | zrobione |
| A9 | SHOULD | Kontekst w rezerwie: czas od przebudzenia, pora doby (model dwuprocesowy, uproszczony) | `src/wachta/config.py`, `src/wachta/index.py`, `--wake`, `--clock` | rezerwa spada szybciej w nocy i po długim czuwaniu; parametry opisane jako założenia | zrobione |

## B. Dane i dowody

| ID | Priorytet | Zadanie | Wynik | Gotowe, gdy | Status |
|---|---|---|---|---|---|
| B1 | MUST | Notebook 03 na prawdziwych etykietach: bloki z adnotacji zamiast epizodów wykrytych z sygnału; kontrast `reading` i `math` wobec `neutral` | `data/analysis/` (notebook 03 albo nowy), poprawka w `data/analysis/README.md` | wnioski nie są już „kołowe”; jest wykres na slajd | zrobione: `claude/charming-tesla-jkdhq5` |
| B2 | SHOULD | Czujny kontra senny na naszych 8 kanałach, zbiór Cui i in. (figshare, 172 MB) | `data/analysis/04-drowsiness-public-dataset.ipynb`, wykres w `docs/img/` | AUC na osobę; porównanie: kalibracja osobista kontra jeden próg dla wszystkich | zrobione: `claude/charming-tesla-jkdhq5` |
| B3 | COULD | EEG a serce: HRV z EKG w COG-BCI wobec wskaźnika EEG. Zamiennie ds004902 (wyspani kontra po deprywacji snu) | kolejny notebook, wykres w `docs/img/` | jeden wykres i dwa zdania wniosku | zrobione: `claude/charming-tesla-jkdhq5` |
| B4 | SHOULD | Dopisać zbiory o zmęczeniu z planu do listy zbiorów | `docs/datasety-eeg-zrodla.md` | link, zawartość, rozmiar i licencja każdego zbioru | zrobione: `claude/charming-tesla-jkdhq5` |
| B5 | SHOULD | COG-BCI, zadanie PVT: czy alfa O1/O2 przy otwartych oczach przewiduje lapsy (RT > 500 ms) w kolejnej minucie | kolejny notebook, wykres w `docs/img/` | jedna liczba na slajd (np. AUC na osobę) i dwa zdania wniosku | zrobione: wynik negatywny, alfa nie przewiduje lapsu (AUC 0,52), notebook 06 |
| B6 | MUST | Spójność dowodów przed filmem: slajdy 7–8 w `pitch.md`, `podstawy-naukowe.md` §1, `data/recordings/README.md`, wyjaśnienie w `scenariusz-demo.md`, issues #27 i #30 | `docs/pitch.md`, `docs/podstawy-naukowe.md`, `data/recordings/README.md`, `docs/scenariusz-demo.md`, `docs/plan-projektu.md` | nic nie twierdzi, że alfa przy otwartych oczach ostrzega przed spadkiem; `neutral` opisany jako rozmowa; D przejrzał zmiany w pitchu | zrobione: `claude/charming-tesla-jkdhq5` (do przejrzenia przez D) |
| B7 | MUST | Reaktywność alfy jako test „marker działa u tej osoby” na 5 nagraniach i 29 osobach COG-BCI; progi tak / słabo / nie; ile sekund zamkniętych oczu wystarczy do kalibracji | `data/analysis/07-alpha-reactivity-marker-check.ipynb`, wykres w `docs/img/` | tabela parametrów do `config.py` (issue #18) | w toku: `claude/charming-tesla-jkdhq5` |
| B8 | SHOULD | Symulacja harmonogramu prób reakcji na COG-BCI (PVT): stała co X min, po zdarzeniu ostrym, z podprogowej alfy; liczba prób na godzinę kontra odsetek złapanych lapsów (issue #23) | `data/analysis/08-probe-schedule-simulation.ipynb`, wykres w `docs/img/` | odstępy do issues #14 i #15 | zrobione: wynik nierozstrzygający co do odstępu, parametry wg kosztu prób, notebook 08 |
| B9 | SHOULD | T1 jako kontrola negatywna: tabela „ciche warunki kontra sala” (artefakty, brum, EMG, ruch, rozkład wskaźnika alfy, fałszywe alarmy i próby na godzinę), zawęża issue #21 | `data/analysis/09-t1-negative-control.ipynb`, wykres w `docs/img/` | tabela i wnioski dla issues #11, #12, #14, #18; oddech i stres z pliku `.fit` Wojtka poza repo, nie analizowane | zrobione: `claude/charming-tesla-jkdhq5` |
| B10 | COULD | Serce a EEG na lapsach i 1/RT oraz rozbieżność plików `PVT.mat` w COG-BCI (issue #22) | `data/analysis/10-heart-vs-eeg-lapses-and-response-speed.ipynb`, wykres w `docs/img/` | wniosek o RMSSD i czujności sprawdzony na lapsach i 1/RT, poprawione zdanie na slajd | zrobione (wynik negatywny: ponad czas zadania RMSSD nie dodaje informacji); poprawione zdanie w pitch, jury, podstawy, analiza; pliki `PVT.mat` w COG-BCI zgłosić autorom (Zenodo 7413650) |

## C. Pomiary

| ID | Priorytet | Zadanie | Wynik | Gotowe, gdy | Status |
|---|---|---|---|---|---|
| C1 | SHOULD | Punkt pomiarowy T0 czterech osób wg protokołu z planu | `.fif` z adnotacjami w `data/recordings/`, wiersze w `checkpoints.csv` | 4 osoby, każda z KSS | do zrobienia |
| C2 | SHOULD | Punkty T1 (w połowie) i T2 (przed zamrożeniem kodu) | jak wyżej | po 4 osoby na punkt | do zrobienia |
| C3 | MUST | Operator demo: dwie próby, jedna na żywo i jedna w trybie odtwarzania | uwagi w `docs/scenariusz-demo.md` | próby odbyte, lista problemów przekazana do A i D | do zrobienia |
| C4 | SHOULD | Nocny punkt pomiarowy z testem PVT-B (`wachta.pvt`) zaraz po nagraniu, żeby mieć własne dane senności przy otwartych oczach | jak C1, plus wiersze w `pvt.csv` | min. 2 osoby po północy | protokół i analiza gotowe (`protokol-nocny.md`, `experiments/analyze-night-checkpoint.py`), czeka na pomiar |

C1 nie czeka na A5. Kroki mają stałą długość, więc wystarczy stoper uruchomiony razem z nagraniem,
a adnotacje wpisuje się z tabeli w sekcji „Kontrakty”.

## D. Pitch i demo

| ID | Priorytet | Zadanie | Wynik | Gotowe, gdy | Status |
|---|---|---|---|---|---|
| D1 | MUST | Treść slajdów: problem, luka, rozwiązanie, dowody, rynek, prawo, zespół | `docs/pitch.md` | 10 slajdów, na każdym jedno zdanie i źródło każdej liczby | szkic gotowy (pozycjonowanie: personalizacja norm zmęczenia), do przejrzenia przez D |
| D2 | MUST | Segment wejścia i różnica względem SmartCap (punkt otwarty 1 w decyzjach) | wpis w `docs/decyzje.md`, slajd w `docs/pitch.md` | zespół wybrał segment | do zrobienia |
| D3 | MUST | Scenariusz demo co do kroku i plan awaryjny | `docs/scenariusz-demo.md` | wiadomo, kto co klika i co mówimy; jest wariant bez sprzętu | szkic gotowy, do przejrzenia przez D i próby C3 |
| D4 | SHOULD | Slajd „co zweryfikowane, a co założone” | w `docs/pitch.md` | wstawione liczby z A2 i B2 | szkic w `pitch.md` slajd 8, liczby z A2 i B2 wstawione |
| D5 | MUST | Slajd „Kamera a Wachta”: kamera widzi, czy oczy są otwarte, my sprawdzamy, czy mózg jeszcze reaguje. Złagodzone hasło o zegarku (HRV i EEG reagują na to samo, ale nie są zamienne) | `docs/pitch.md` | slajd z liczbami z A7, B2 i B5; zgodny z `podstawy-naukowe.md` §6 | do zrobienia |

Zasady dla treści pitchu: mówimy „zmęczenie i czujność”, nie „stres”, „wypalenie” ani „przeciążenie”
(uzasadnienie w [`rynek-wielkosc-i-kierunek.md`](rynek-wielkosc-i-kierunek.md) §3). Przełożony widzi tylko gotowość.

## Zależności

- A1 → A2 i A3 → A4. A4 wymaga laptopa ze sprzętem.
- A7 → A8 (próba korzysta ze stanu oczu). D5 czeka na liczby z A7 i B5.
- D4 czeka na liczby z A2 i B2. Do tego czasu zostaw na slajdzie miejsce, nie wpisuj szacunków.
- D1 w wersji finalnej czeka na D2.
- Pozostałe zadania są niezależne i mogą iść równolegle.

## Kontrakty między strumieniami

**Adnotacje nagrania** (`<nagranie>-raw_annotations.csv`, opis w `data/recordings/README.md`):
`onset,duration,description`, czasy w sekundach od początku nagrania.
Etykiety: `eyes_open`, `eyes_closed`, `math`, a w starszych nagraniach także `neutral`, `reading`, `control`.

**Punkt pomiarowy** ma stałe kroki, więc adnotacje nowego nagrania to zawsze:

```
onset,duration,description
0.000,60.000,eyes_open
60.000,60.000,eyes_closed
120.000,60.000,math
```

W BrainAccess Board jako nazwę zadania wpisz `<imie>-t0`, `<imie>-t1` albo `<imie>-t2`. Zapisuj tylko `.fif`, bez kopii CSV.

**`data/recordings/checkpoints.csv`**, jeden wiersz na osobę i punkt:
`person,checkpoint,started_at,kss,body_battery,stress,heart_rate,hrv_ms,recording_file,notes`.
Kolumny z zegarka wypełnia tylko osoba z Garminem, reszta zostawia je puste. KSS to skala senności 1–9.

**Wynik pipeline'u** (jedna wiadomość na sekundę, JSON przez WebSocket):
`state` (`calibrating`, `ok`, `warn`, `stop`, `break`, `no_signal`), `reserve` (0–100), `fast` (wskaźnik szybki, z-score),
`slow` (wskaźnik wolny), `quality` (0–1), `t` (sekundy od startu). Pełna lista pól: `src/wachta/index.py`.

**Stałe i definicje cech:** źródłem prawdy jest `src/wachta/config.py`. Notebooki mogą je importować (`pip install -e .`).
Próg wskaźnika szybkiego to 2,5, a nie 2,0 jak w notebooku 03: uzasadnienie w [`trafnosc-na-nagraniach.md`](trafnosc-na-nagraniach.md).

**Wykresy na slajdy:** PNG do 300 kB w `docs/img/`, nazwa mówi, co jest na wykresie.

## Co już jest

- Cztery nagrania z adnotacjami protokołu w `data/recordings/`.
- Analiza jakości nagrań i wskaźnika w `data/analysis/` (notebooki 01–03).
- Research konkurencji, rynku i prawa w `docs/rynek-*.md`.
- Decyzja o kierunku i plan projektu w `docs/`.
- Rdzeń pipeline'u w `src/wachta/` z testami i wynik trafności w [`trafnosc-na-nagraniach.md`](trafnosc-na-nagraniach.md).
