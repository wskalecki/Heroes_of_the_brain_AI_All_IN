# Analiza nagrań BrainAccess

Notebooki analizujące nagrania z `data/recordings/` i porównujące je z otwartymi zbiorami EEG. Działają lokalnie (uruchamiane z tego folderu) oraz w Google Colab (same pobiorą repo i dane publiczne). Mają zapisane wyniki, więc można je czytać bez uruchamiania.

Uruchamiajcie po kolei, bo notebook 02 i 03 korzystają z `alpha-episodes.csv` zapisanego przez 01.

| Notebook | Pytanie |
|---|---|
| [`01-recordings-quality.ipynb`](01-recordings-quality.ipynb) | Jak dobre są nasze nagrania? Artefakty, szum sieciowy, epizody alfy |
| [`02-public-datasets-comparison.ipynb`](02-public-datasets-comparison.ipynb) | Czym różni się nasz sprzęt od zbiorów laboratoryjnych? Wpływ referencji Fp1 na wskaźniki |
| [`03-wachta-indicator-on-recordings.ipynb`](03-wachta-indicator-on-recordings.ipynb) | Jak działa wskaźnik czujności na blokach z adnotacji? Wykrywanie `eyes_closed`, fałszywe alarmy, czytanie i liczenie wobec rozmowy, blok z mruganiem, szczęką i ruchem głowy |
| [`04-drowsiness-public-dataset.ipynb`](04-drowsiness-public-dataset.ipynb) | Czujny kontra senny na naszych 8 kanałach (zbiór Cui i in., symulator jazdy). AUC na osobę, kalibracja osobista kontra jeden próg dla wszystkich |
| [`05-eeg-vs-heart-cogbci.ipynb`](05-eeg-vs-heart-cogbci.ipynb) | Czy serce (EKG) idzie w parze ze wskaźnikiem EEG w zadaniu czujności PVT? (COG-BCI, 16 osób) |
| [`06-pvt-alpha-early-warning.ipynb`](06-pvt-alpha-early-warning.ipynb) | Czy alfa potyliczna przy otwartych oczach ostrzega przed lapsem w kolejnej minucie? (COG-BCI, 29 osób). Wynik negatywny: nie ostrzega, nic nie dodaje do czasu zadania i poprzedniego czasu reakcji |
| [`07-alpha-reactivity-marker-check.ipynb`](07-alpha-reactivity-marker-check.ipynb) | Test „marker działa u tej osoby”: reaktywność alfy (zamknięte vs otwarte oczy) na 5 nagraniach zespołu i 27 osobach COG-BCI, progi tak / słabo / nie, ile sekund wystarczy |
| [`08-probe-schedule-simulation.ipynb`](08-probe-schedule-simulation.ipynb) | Symulacja harmonogramów prób reakcji na COG-BCI (PVT): stały, po zdarzeniu ostrym, z podprogowej alfy, adaptacyjny. Wynik: żaden wyzwalacz nie łapie lapsów lepiej niż losowe próby przy tej samej liczbie |
| [`09-t1-negative-control.ipynb`](09-t1-negative-control.ipynb) | T1 (15 min monotonii, KSS 5) jako kontrola negatywna: cisza kontra sala, fałszywe alarmy i próby reakcji na godzinę, stabilność kalibracji |
| [`10-heart-vs-eeg-lapses-and-response-speed.ipynb`](10-heart-vs-eeg-lapses-and-response-speed.ipynb) | Czy RMSSD niesie informację o czujności ponad czas zadania? Lapsy i szybkość 1/RT, 29 osób COG-BCI; poprawia wcześniejsze „r = −0,23, 16 z 16” |

**Etykiety:** notebooki 01 i 03 korzystają z bloków protokołu z `data/recordings/*-raw_annotations.csv`. Blok `neutral` to swobodna rozmowa (nie cichy spoczynek), a `control` to mruganie, zaciskanie szczęki i ruch głowy bez osobnych znaczników czasu. Próba to 4 osoby i jedno nagranie na osobę, więc liczby pokazują, że pipeline działa na naszym sprzęcie, a nie trafność na populacji.

Wykresy na slajdy są w [`docs/img/`](../../docs/img/).

Zbiory publiczne notebooki 02, 04, 05 i 06 pobierają same (EEGMAT z PhysioNet, COG-BCI z Zenodo, zbiór Cui z figshare), do katalogu poza repo. Nic z nich nie trafia do repo.
