# Zadania

Podział pracy z [`plan-projektu.md`](plan-projektu.md) na zadania, które można brać od razu.
Plik jest dla ludzi i dla agentów AI. Stan na 14.11.2026, godz. 14:30: do oddania zostało mniej niż 12 h.

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
| B. Dane i dowody | Adrian (z agentem) | `data/analysis/`, `docs/datasety-eeg-zrodla.md`, `docs/img/` |
| C. Pomiary | Filip | nowe pliki w `data/recordings/` (nagrania, adnotacje, `checkpoints.csv`) |
| D. Pitch i demo | Rudy | `docs/pitch.md`, `docs/scenariusz-demo.md`, `docs/rynek-*.md` |

Role Filipa i Rudego to propozycja, mogą się zamienić.

Pliki wspólne (zmiany małe i celowe): `README.md`, `AGENTS.md`, `.gitignore`, `docs/README.md`, `docs/decyzje.md`,
`docs/plan-projektu.md`, `docs/zadania.md`.

## A. Sygnał i aplikacja

| ID | Priorytet | Zadanie | Wynik | Gotowe, gdy | Status |
|---|---|---|---|---|---|
| A1 | MUST | Rdzeń: filtr strumieniowy, cechy okna, kalibracja na osobę, wskaźnik, stany, rezerwa | `src/wachta/`, `tests/`, `pyproject.toml` | `pytest` przechodzi | w toku: `claude/sleepy-lamport-v2kzl7` |
| A2 | MUST | Trafność pipeline'u na 4 nagraniach z adnotacjami | `experiments/validate-on-recordings.py`, `docs/trafnosc-na-nagraniach.md` | tabela na osobę: wykrycie `eyes_closed` i fałszywe alarmy poza nim | do zrobienia |
| A3 | MUST | Odtwarzanie nagrania, serwer i dashboard | `src/wachta/sources.py`, `src/wachta/server.py`, `src/wachta/web/` | dashboard działa w trybie odtwarzania i zmienia stan w bloku `eyes_closed` | do zrobienia |
| A4 | MUST | Tryb na żywo z BrainAccess Board | źródło `board` w `sources.py`, `docs/uruchomienie.md` | na laptopie ze sprzętem płyną próbki, a zamknięcie oczu zmienia stan | do zrobienia (wymaga sprzętu, uruchamia Wojtek) |
| A5 | SHOULD | Narzędzie punktu pomiarowego: odlicza kroki, zapisuje znaczniki i KSS | `src/wachta/session.py` | zapisuje adnotacje i wiersz w `checkpoints.csv` w formatach z sekcji „Kontrakty” | do zrobienia |
| A6 | COULD | Prognoza czasu do progu, test czasu reakcji w przeglądarce, krzywe z Garmin Connect | — | — | do zrobienia |

## B. Dane i dowody

| ID | Priorytet | Zadanie | Wynik | Gotowe, gdy | Status |
|---|---|---|---|---|---|
| B1 | MUST | Notebook 03 na prawdziwych etykietach: bloki z adnotacji zamiast epizodów wykrytych z sygnału; kontrast `reading` i `math` wobec `neutral` | `data/analysis/` (notebook 03 albo nowy), poprawka w `data/analysis/README.md` | wnioski nie są już „kołowe”; jest wykres na slajd | do zrobienia |
| B2 | SHOULD | Czujny kontra senny na naszych 8 kanałach, zbiór Cui i in. (figshare, 172 MB) | `data/analysis/04-drowsiness-public-dataset.ipynb`, wykres w `docs/img/` | AUC na osobę; porównanie: kalibracja osobista kontra jeden próg dla wszystkich | do zrobienia |
| B3 | COULD | EEG a serce: HRV z EKG w COG-BCI wobec wskaźnika EEG. Zamiennie ds004902 (wyspani kontra po deprywacji snu) | kolejny notebook, wykres w `docs/img/` | jeden wykres i dwa zdania wniosku | do zrobienia |
| B4 | SHOULD | Dopisać zbiory o zmęczeniu z planu do listy zbiorów | `docs/datasety-eeg-zrodla.md` | link, zawartość, rozmiar i licencja każdego zbioru | do zrobienia |

## C. Pomiary

| ID | Priorytet | Zadanie | Wynik | Gotowe, gdy | Status |
|---|---|---|---|---|---|
| C1 | SHOULD | Punkt pomiarowy T0 czterech osób wg protokołu z planu | `.fif` z adnotacjami w `data/recordings/`, wiersze w `checkpoints.csv` | 4 osoby, każda z KSS | do zrobienia |
| C2 | SHOULD | Punkty T1 (w połowie) i T2 (przed zamrożeniem kodu) | jak wyżej | po 4 osoby na punkt | do zrobienia |
| C3 | MUST | Operator demo: dwie próby, jedna na żywo i jedna w trybie odtwarzania | uwagi w `docs/scenariusz-demo.md` | próby odbyte, lista problemów przekazana do A i D | do zrobienia |

C1 nie czeka na A5. Kroki mają stałą długość, więc wystarczy stoper uruchomiony razem z nagraniem,
a adnotacje wpisuje się z tabeli w sekcji „Kontrakty”.

## D. Pitch i demo

| ID | Priorytet | Zadanie | Wynik | Gotowe, gdy | Status |
|---|---|---|---|---|---|
| D1 | MUST | Treść slajdów: problem, luka, rozwiązanie, dowody, rynek, prawo, zespół | `docs/pitch.md` | 10 slajdów, na każdym jedno zdanie i źródło każdej liczby | do zrobienia |
| D2 | MUST | Segment wejścia i różnica względem SmartCap (punkt otwarty 1 w decyzjach) | wpis w `docs/decyzje.md`, slajd w `docs/pitch.md` | zespół wybrał segment | do zrobienia |
| D3 | MUST | Scenariusz demo co do kroku i plan awaryjny | `docs/scenariusz-demo.md` | wiadomo, kto co klika i co mówimy; jest wariant bez sprzętu | do zrobienia |
| D4 | SHOULD | Slajd „co zweryfikowane, a co założone” | w `docs/pitch.md` | wstawione liczby z A2 i B2 | do zrobienia (czeka na A2, B2) |

Zasady dla treści pitchu: mówimy „zmęczenie i czujność”, nie „stres”, „wypalenie” ani „przeciążenie”
(uzasadnienie w [`rynek-wielkosc-i-kierunek.md`](rynek-wielkosc-i-kierunek.md) §3). Przełożony widzi tylko gotowość.

## Zależności

- A1 → A2 i A3 → A4. A4 wymaga laptopa ze sprzętem.
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
`state` (`calibrating`, `ok`, `warn`, `stop`, `no_signal`), `reserve` (0–100), `fast` (wskaźnik szybki, z-score),
`slow` (wskaźnik wolny), `quality` (0–1), `t` (sekundy od startu).

**Stałe i definicje cech:** źródłem prawdy jest `src/wachta/config.py`. Notebooki mogą je importować po scaleniu A1.

**Wykresy na slajdy:** PNG do 300 kB w `docs/img/`, nazwa mówi, co jest na wykresie.

## Co już jest

- Cztery nagrania z adnotacjami protokołu w `data/recordings/`.
- Analiza jakości nagrań i wskaźnika w `data/analysis/` (notebooki 01–03).
- Research konkurencji, rynku i prawa w `docs/rynek-*.md`.
- Decyzja o kierunku i plan projektu w `docs/`.
