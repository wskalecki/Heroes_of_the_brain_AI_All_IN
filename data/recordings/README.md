# Nagrania testowe (14.11.2026)

Cztery nagrania z południa (oraz nagranie T1 z wieczora, opisane niżej) z BrainAccess MINI (8 kanałów: F3, F4, C3, C4, P3, P4, O1, O2, 250 Hz),
zrobione na członkach zespołu za ich zgodą. Służą do budowy i sprawdzenia pipeline'u.

Każde nagranie ma cztery pliki o wspólnym prefiksie:

| Plik | Zawartość |
|---|---|
| `*-raw.fif` | surowy sygnał w formacie MNE |
| `*-raw.csv` | ten sam sygnał jako CSV (kanały EEG, kontakt elektrod, akcelerometr, bateria) |
| `*-raw_montage.json` | montaż i ustawienia urządzenia |
| `*-raw_annotations.csv` | bloki protokołu (opis niżej) |

## Protokół

Każda osoba przechodziła te same bloki, w tej kolejności:

| Etykieta | Co robił uczestnik |
|---|---|
| `neutral` | **swobodna rozmowa i normalne funkcjonowanie** (mówienie, ruch), nie cichy spoczynek |
| `eyes_closed` | oczy zamknięte (punkt odniesienia dla alfy) |
| `reading` | czytanie tekstu |
| `math` | liczenie w pamięci (obciążenie poznawcze) |
| `control` | **otwieranie i zamykanie oczu, zaciskanie szczęki i machanie głową** (bez osobnych znaczników czasu wewnątrz bloku) |

## Timeline (sekundy od początku nagrania)

| Osoba | neutral | eyes_closed | reading | math | control |
|---|---|---|---|---|---|
| adi | 0–300 | 300–360 | 360–435 | 435–505 | 505–548 |
| filip | 0–600 | 600–660 | 660–740 | 740–840 | 840–881 |
| rudy | 0–300 | 300–360 | 420–450 | 450–524 | 524–544 |
| wojtek | 0–300 | 300–363 | 363–425 | 430–484 | 484–509 |

Odcinki bez etykiety (przerwy między blokami): rudy 360–420 s, wojtek 425–430 s.

Źródło: timeline spisany przez zespół podczas nagrań. Zgodność z sygnałem sprawdzona zgrubnie:
w bloku `eyes_closed` rośnie alfa na O1/O2 względem `neutral` (wyraźnie u filipa i rudego,
słabiej u adi i wojtka).

## Format adnotacji

`onset,duration,description`, czasy w sekundach od początku nagrania. Pliki `.fif` nie zawierają
tych adnotacji. W MNE można je dołączyć tak:

```python
import mne
import pandas as pd

raw = mne.io.read_raw_fif("...-raw.fif")
ann = pd.read_csv("...-raw_annotations.csv")
raw.set_annotations(mne.Annotations(ann.onset, ann.duration, ann.description))
```

## Uwagi o jakości

- Kontakt elektrod 100% na wszystkich kanałach we wszystkich nagraniach.
- Silny brum sieci 50 Hz w nagraniu adi (wszystkie kanały) i punktowo na P4 (filip) i P3 (rudy).
  Przed analizą potrzebny filtr notch 50 Hz.
- Bloki `control` są krótkie (20–43 s) i widać w nich wzrost mocy we wszystkich pasmach: to celowe ruchy (mruganie, szczęka, głowa),
  a nie zdejmowanie czapki. Przy referencji Fp1 artefakty oczu trafiają na wszystkie 8 kanałów naraz.
- Ponieważ `neutral` to rozmowa, jest hałaśliwą bazą (mięśnie, ruch). Czysty spoczynek z oczami otwartymi ma dopiero nagranie `wojtek-t1`.

## Nagranie T1 (wojtek-t1, wieczór)

Plik `subj-1_ses-S001_task-wojtek-t1_...` (tylko `.fif` i adnotacje): 60 s oczy otwarte, 60 s oczy zamknięte, 60 s liczenie, 15 min monotonii
(oczy otwarte, słuchawki z ANC i biały szum). Adnotacje są przesunięte o 3 s (nagranie ruszyło przed narzędziem sesji, sprawdzone na alfie).
Opis i wyniki: [`docs/sesja-monotonii-wojtek.md`](../../docs/sesja-monotonii-wojtek.md). Wpis w `checkpoints.csv`.
