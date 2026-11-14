# Analiza nagrań BrainAccess

Notebooki analizujące nagrania z `data/recordings/` i porównujące je z otwartymi zbiorami EEG. Działają lokalnie (uruchamiane z tego folderu) oraz w Google Colab (same pobiorą repo i dane publiczne). Mają zapisane wyniki, więc można je czytać bez uruchamiania.

Uruchamiajcie po kolei, bo notebook 02 i 03 korzystają z `alpha-episodes.csv` zapisanego przez 01.

| Notebook | Pytanie |
|---|---|
| [`01-recordings-quality.ipynb`](01-recordings-quality.ipynb) | Jak dobre są nasze nagrania? Artefakty, szum sieciowy, epizody alfy |
| [`02-public-datasets-comparison.ipynb`](02-public-datasets-comparison.ipynb) | Czym różni się nasz sprzęt od zbiorów laboratoryjnych? Wpływ referencji Fp1 na wskaźniki |
| [`03-wachta-indicator-on-recordings.ipynb`](03-wachta-indicator-on-recordings.ipynb) | Jak zachowuje się wskaźnik w stylu Wachty? Kalibracja, artefakty, napięcie mięśni, protokół następnego nagrania |

**Główne ograniczenie:** nagrania nie mają znaczników (puste adnotacje), więc stany są wnioskowane z samego sygnału. Wyniki nie są walidacją detektora.

Zbiory publiczne notebook 02 pobiera sam (EEGMAT z PhysioNet, COG-BCI z Zenodo, tylko potrzebne pliki). Nic z nich nie trafia do repo.
