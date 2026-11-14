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

**Etykiety:** notebooki 01 i 03 korzystają z bloków protokołu z `data/recordings/*-raw_annotations.csv`. Blok `neutral` to swobodna rozmowa (nie cichy spoczynek), a `control` to mruganie, zaciskanie szczęki i ruch głowy bez osobnych znaczników czasu. Próba to 4 osoby i jedno nagranie na osobę, więc liczby pokazują, że pipeline działa na naszym sprzęcie, a nie trafność na populacji.

Wykresy na slajdy są w [`docs/img/`](../../docs/img/).

Zbiory publiczne notebooki 02, 04 i 05 pobierają same (EEGMAT z PhysioNet, COG-BCI z Zenodo, zbiór Cui z figshare), do katalogu poza repo. Nic z nich nie trafia do repo.
