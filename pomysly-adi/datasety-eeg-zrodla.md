# Otwarte zbiory EEG dla projektu Wachta (senność i przeciążenie)

Wszystkie zbiory nagrano na laboratoryjnych elektrodach żelowych. Służą do sprawdzenia pipeline'u cech i do walidacji na slajdzie. Progi w demo muszą pochodzić z kalibracji na BrainAccess MINI.

Nasz montaż: F3, F4, C3, C4, P3, P4, O1, O2.

---

## 1. EEG During Mental Arithmetic Tasks (PhysioNet), przeciążenie

- **Co zawiera:** 36 zdrowych osób, układ 10/20 (23-kanałowy system Neurocom), na osobę 180 s spoczynku i 60 s liczenia w pamięci (odejmowanie). Artefakty usunięte przez ICA. Format EDF, struktura BIDS.
- **Pokrywa nasze kanały:** tak, wszystkie osiem.
- **Licencja:** Open Data Commons Attribution v1.0.
- **Rozmiar:** mały, do pobrania od razu.

Linki:
- Strona zbioru (PhysioNet, DOI): https://doi.org/10.13026/C2JQ1P
- Archiwalna strona PhysioNet z opisem plików: https://archive.physionet.org/physiobank/database/eegmat
- Kopia na AWS (bez konta): `aws s3 ls --no-sign-request s3://physionet-open/eegmat/` ([opis](https://registry.opendata.aws/eegmat/))
- Artykuł opisujący zbiór: Zyma I. i in., *Electroencephalograms during Mental Arithmetic Task Performance*, Data 2019, 4(1):14. https://doi.org/10.3390/data4010014 ([pełny tekst](https://www.mdpi.com/2306-5729/4/1/14))

---

## 2. Multi-channel EEG recordings during a sustained-attention driving task, senność

- **Co zawiera:** 27 osób, 62 sesje po ok. 90 min jazdy w symulatorze VR (nocna autostrada, losowe zjazdy z pasa, mierzony czas reakcji). 32 elektrody Ag/AgCl w zmodyfikowanym układzie 10/20, 500 Hz. Sesje po obiedzie (13:00–14:00), bez przerw, więc senność narasta naturalnie.
- **Pokrywa nasze kanały:** sprawdzić listę kanałów w plikach (zmodyfikowany 10/20).
- **Licencja:** CC BY 4.0.
- **Rozmiar:** duży.

Linki:
- Dane surowe (figshare): https://figshare.com/articles/Multi-channel_EEG_recordings_during_a_sustained-attention_driving_task/6427334/5
- Artykuł: Cao Z., Chuang C.-H., King J.-K., Lin C.-T., *Multi-channel EEG recordings during a sustained-attention driving task*, Scientific Data 6, 19 (2019). https://doi.org/10.1038/s41597-019-0027-4
- Pełny tekst (PMC): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6472414/
- Preprint (arXiv): https://arxiv.org/abs/1809.06534

---

## 3. COG-BCI database, przeciążenie i czujność (najbliżej scenariusza operatora)

- **Co zawiera:** 29 osób, 3 sesje w odstępach tygodniowych, 4 zadania: MATB-II (symulacja pracy operatora od NASA), N-Back (0/1/2-back), PVT (czujność i zmęczenie), Flanker. Łącznie ponad 100 h EEG i EKG oraz kwestionariusze (RSME, KSS). Format BIDS.
- **Najbardziej przydatne:** MATB i N-Back (poziomy obciążenia) oraz PVT (spadek czujności).
- **Rozmiar:** 31,7 GB w całości, ok. 1,1 GB na plik, więc pobierać pojedyncze osoby.
- **Uwaga:** wersja 4 poprawia błąd w nazwach elektrod, więc używać najnowszej.

Linki:
- Dane (Zenodo, wersja 4): https://zenodo.org/record/7413650
- Opis zbioru (PDF w Zenodo): https://zenodo.org/records/7413650/files/COG-BCI_info.pdf
- Artykuł: Hinss M.F. i in., *Open multi-session and multi-task EEG cognitive Dataset for passive brain-computer Interface Applications*, Scientific Data 10 (2023). https://doi.org/10.1038/s41597-022-01898-y
- Pełny tekst (PMC): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9918545/

---

## 4. EEG Alpha Waves dataset (GIPSA-lab), test detektora alfy

- **Co zawiera:** 20 osób, 16 elektrod (m.in. P3, P4, O1, O2, Pz, Oz), 512 Hz. Na osobę 10 bloków po 10 s: 5 z oczami zamkniętymi i 5 z otwartymi, na przemian.
- **Pokrywa nasze kanały:** P3, P4, O1, O2 tak; F3, F4, C3, C4 nie.
- **Najprostszy start:** w Pythonie przez MOABB jako `moabb.datasets.Rodrigues2017`.

Linki:
- Dane (Zenodo): https://zenodo.org/record/2348892
- Wersja z opisem ID ALPHA.EEG.2017-GIPSA: https://zenodo.org/records/2605110
- Pełny opis eksperymentu (HAL): https://hal.archives-ouvertes.fr/hal-02086581
- Kod w Pythonie: https://github.com/plcrodrigues/Alpha-Waves-Dataset
- Dokumentacja w MOABB: https://neurotechx.github.io/moabb/generated/moabb.datasets.Rodrigues2017.html

---

## 5. STEW: Simultaneous Task EEG Workload Dataset, przeciążenie

- **Co zawiera:** 48 osób, Emotiv EPOC (14 kanałów, 128 Hz), po 2,5 min spoczynku i testu wielozadaniowego SIMKAP. Każda osoba oceniła obciążenie w skali 1–9 (brak ocen dla osób 5, 24 i 42).
- **Pokrywa nasze kanały:** F3, F4, O1, O2 tak; C3, C4, P3, P4 nie (są P7/P8).
- **Licencja:** CC BY.
- **Dostęp:** wymaga darmowego konta IEEE. Plik ok. 52 MB.

Linki:
- Dane (IEEE DataPort, DOI): https://doi.org/10.21227/44r8-ya50
- Strona zbioru: https://ieee-dataport.org/open-access/stew-simultaneous-task-eeg-workload-dataset
- Artykuł: Lim W.L., Sourina O., Wang L.P., *STEW: Simultaneous Task EEG Workload Data Set*, IEEE TNSRE 26(11):2106–2114 (2018). https://doi.org/10.1109/TNSRE.2018.2872924

---

## Dodatkowo (znalezione w bibliografii COG-BCI, niesprawdzone)

- *An EEG dataset for cross-session mental workload estimation: Passive BCI competition of the Neuroergonomics Conference 2021*, Zenodo: https://doi.org/10.5281/zenodo.5055046

---

## Kolejność pracy

1. **Mental Arithmetic:** czy theta na F3/F4 odróżnia spoczynek od liczenia.
2. **Alpha Waves:** czy detektor alfy na O1/O2 odróżnia oczy zamknięte od otwartych.
3. **COG-BCI:** 1–2 osoby z zadania MATB jako walidacja w scenariuszu operatora.
4. **Zbiór z jazdy:** walidacja senności, jeśli zostanie czas.
