# Otwarte zbiory EEG dla projektu Wachta (zmęczenie i czujność)

Kierunek projektu to zmęczenie i spadek czujności, czyli senność ([`decyzje.md`](decyzje.md), [`plan-projektu.md`](plan-projektu.md)). Zbiory 1–5 zebraliśmy wcześniej, gdy w grze był też wariant „przeciążenie”. Zostają na liście: EEGMAT (1) i COG-BCI (3) posłużyły do porównania sygnału w notebooku 02, a zbiór z jazdy (2) i COG-BCI pasują też do obecnego kierunku. Produkt nie wykrywa przeciążenia; etykiety „przeciążenie” przy zbiorach opisują tylko to, co mierzy sam zbiór. Nowe zbiory o zmęczeniu i senności są w punktach 6–10.

Zbiory 1–4 i 6–7 nagrano na laboratoryjnych elektrodach żelowych, a 5 i 8–10 na urządzeniach konsumenckich. Służą do sprawdzenia pipeline'u cech i do walidacji na slajdzie. Progi w demo muszą pochodzić z kalibracji na BrainAccess MINI.

Nasz montaż: F3, F4, C3, C4, P3, P4, O1, O2.

Fakty przy zbiorach 6–10 sprawdzone 14.11.2026 w API i na stronach repozytoriów (figshare, OpenNeuro, Zenodo, Borealis, Mendeley Data) oraz w artykułach (PubMed/PMC, arXiv). Czego nie dało się potwierdzić, jest oznaczone jako **niesprawdzone**.

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
- **Pokrywa nasze kanały:** sprawdzić listę kanałów w plikach (zmodyfikowany 10/20). **Sprawdzone:** 30 kanałów EEG (Fp1, Fp2, F7, F3, Fz, F4, F8, FT7, FC3, FCz, FC4, FT8, T3, C3, Cz, C4, T4, TP7, CP3, CPz, CP4, TP8, T5, P3, Pz, P4, T6, O1, Oz, O2), więc wszystkie osiem nasze są. Lista pochodzi z kodu Cui i in. do zbioru pochodnego (punkt 6), nie z plików `.set`.
- **Licencja:** CC BY 4.0.
- **Rozmiar:** duży. **Sprawdzone:** dane surowe to 64 pliki `.set` (jedna sesja w pliku, ok. 200–420 MB), razem 19,6 GB, więc da się pobrać pojedyncze sesje. Wersja wstępnie przetworzona (figshare 7666055, CC BY 4.0) to 64 pliki `.zip`, razem 16,6 GB.
- **Pochodne:** z tego zbioru powstał gotowy do użycia zbiór Cui i in. z oknami „czujny / senny” (punkt 6).

Linki:
- Dane surowe (figshare): https://figshare.com/articles/Multi-channel_EEG_recordings_during_a_sustained-attention_driving_task/6427334/5
- Dane wstępnie przetworzone (figshare, DOI): https://doi.org/10.6084/m9.figshare.7666055.v3
- Artykuł: Cao Z., Chuang C.-H., King J.-K., Lin C.-T., *Multi-channel EEG recordings during a sustained-attention driving task*, Scientific Data 6, 19 (2019). https://doi.org/10.1038/s41597-019-0027-4
- Pełny tekst (PMC): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6472414/
- Preprint (arXiv): https://arxiv.org/abs/1809.06534

---

## 3. COG-BCI database, przeciążenie i czujność (najbliżej scenariusza operatora)

- **Co zawiera:** 29 osób, 3 sesje w odstępach tygodniowych, 4 zadania: MATB-II (symulacja pracy operatora od NASA), N-Back (0/1/2-back), PVT (czujność i zmęczenie), Flanker. Łącznie ponad 100 h EEG i EKG oraz kwestionariusze (RSME, KSS). Format BIDS.
- **Najbardziej przydatne:** MATB i N-Back (poziomy obciążenia) oraz PVT (spadek czujności).
- **Rozmiar:** 31,7 GB w całości, ok. 1,1 GB na plik, więc pobierać pojedyncze osoby.
- **Uwaga:** wersja 4 poprawia błąd w nazwach elektrod, więc używać najnowszej.
- **Dla kierunku zmęczenie i czujność (sprawdzone w artykule i w Zenodo):**
  - EEG: 64 aktywne elektrody Ag/AgCl (ActiCap), 500 Hz, układ 10–20. Elektrodę TP9 przeznaczono na EKG (w danych kanał `ECG`), więc EEG i EKG są nagrane jednocześnie tym samym wzmacniaczem. U osób 1–9 brak Cz.
  - PVT: 90 prób na sesję, ok. 10 min, zapisane czasy reakcji.
  - KSS: na początku sesji, po każdym PVT i na końcu sesji; wyniki w osobnym pliku `KSS.txt` (kolumny: osoba, sesja, wynik, moment).
  - Pliki: jeden `sub-XX.zip` na osobę (ok. 1,0–1,1 GB), więc da się pobrać jedną osobę.
  - Licencja: CC BY 4.0. Najnowsza wersja to nadal 4.
  - **Znane problemy (sprawdzone w notebookach 07 i 10):** (1) dwie pary osób to identyczne pliki EEG (sub-27 = sub-17, sub-28 = sub-25), więc liczymy 27 niezależnych osób zamiast 29; (2) pliki `behavioral/PVT.mat` we wszystkich 87 folderach to kopie zachowania jednej osoby (sub-29, S3), więc czasy reakcji bierzemy ze znaczników w plikach EEG, nie z `PVT.mat`. Do zgłoszenia autorom zbioru (Zenodo 7413650).
  - Pełnej listy 64 kanałów nie sprawdzałem w plikach; O1 i O2 są używane w notebooku 02.

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

## 6. EEG driver drowsiness dataset (Cui i in.), senność

- **Pochodzenie:** wycinek zbioru z jazdy z punktu 2 (Cao i in. 2019), przygotowany przez Cui i in. do własnych badań. Opis na figshare każe cytować także zbiór Cao i in.
- **Co zawiera:** 11 osób (z 27 w zbiorze źródłowym), 2022 okna po 3 s, 128 Hz (zbiór źródłowy ma 500 Hz). Etykiety: 0 = czujny, 1 = senny. Jeden plik MATLAB `dataset.mat` z trzema zmiennymi: `EEGsample` (okna), `substate` (etykieta), `subindex` (numer osoby 1–11). Wersja zbalansowana: podobna liczba okien w obu klasach u każdej osoby.
- **Pokrywa nasze kanały:** tak, wszystkie osiem. 30 kanałów EEG, ta sama lista co w punkcie 2 (kolejność w kodzie autorów, licząc od 0: F3 to indeks 3, F4 5, C3 13, C4 15, P3 23, P4 25, O1 27, O2 29).
- **Uwaga:** opis na figshare podaje rozmiar okna „20x384”, a jednocześnie 30 kanałów. Kod autorów zakłada 30 × 384 (30 kanałów × 3 s × 128 Hz). Kształt sprawdzić po wczytaniu pliku.
- **Jak powstały etykiety:** **niesprawdzone.** Abstrakt tego nie opisuje, a pełny tekst jest płatny. Najpewniej z czasu reakcji na zjazd z pasa (jedyna miara zachowania w zbiorze źródłowym), ale progi i okno przed zdarzeniem trzeba sprawdzić w artykule, zanim opiszemy etykiety na slajdzie.
- **Wynik w artykule (abstrakt):** 73,22% trafności między osobami (leave-one-subject-out) z jednego kanału (Oz). Model rozpoznaje senność po wrzecionach alfa i wybuchach theta.
- **Licencja:** CC BY 4.0.
- **Rozmiar:** 180,8 MB (172 MiB), jeden plik. Nie da się pobrać pojedynczej osoby, ale całość jest mała. Bez konta.
- **Wersja niezbalansowana:** ten sam zbiór bez wyrównania liczby okien, 264 MB, CC BY 4.0.

Linki:
- Dane (figshare, DOI): https://doi.org/10.6084/m9.figshare.14273687.v3 ([strona](https://figshare.com/articles/dataset/EEG_driver_drowsiness_dataset/14273687))
- Wersja niezbalansowana: https://doi.org/10.6084/m9.figshare.16586957.v1
- Artykuł: Cui J. i in., *A compact and interpretable convolutional neural network for cross-subject driver drowsiness detection from single-channel EEG*, Methods 202:173–184 (2022). https://doi.org/10.1016/j.ymeth.2021.04.017 ([PubMed](https://pubmed.ncbi.nlm.nih.gov/33901644/))
- Kod autorów (PyTorch, wczytanie danych i lista kanałów): https://github.com/cuijiancorbin/A-Compact-and-Interpretable-Convolutional-Neural-Network-for-Single-Channel-EEG
- Nasza analiza (w toku): `data/analysis/04-drowsiness-public-dataset.ipynb`

---

## 7. OpenNeuro ds004902: A Resting-state EEG Dataset for Sleep Deprivation, senność

- **Co zawiera:** 71 osób (34 kobiety, 37 mężczyzn, średnio 20 lat), dwie sesje w układzie wewnątrzosobniczym: po normalnym śnie (`ses-1`) i po 24–30 h bez snu (`ses-2`). Kolejność sesji zrównoważona między osobami (kolumna `SessionOrder`), odstęp 7 dni do miesiąca. W każdej sesji 5 min EEG spoczynkowego z oczami otwartymi i 5 min z oczami „częściowo” zamkniętymi.
- **EEG:** 61 elektrod Brain Products, rozszerzony układ 10–20, 500 Hz, referencja FCz, sieć 50 Hz. Dane bez żadnego przetwarzania. Format BIDS (EEGLAB `.set`/`.fdt`).
- **Pokrywa nasze kanały:** tak, wszystkie osiem (sprawdzone w `channels.tsv`).
- **Etykiety:** warunek (wyspany / po deprywacji) oraz w `participants.tsv`: PVT (liczba lapsów, mediana i odchylenie czasu reakcji), KSS, SSS, PANAS, kwestionariusze cech (PSQI, Buss-Perry i in.). Surowe próby PVT w `beh/*_task-pvt_beh.tsv`.
- **Uwaga, braki danych (policzone w `participants.tsv`):** KSS ma tylko 33 z 71 osób (w obu sesjach), PVT ma 30 osób z wynikiem w obu sesjach. Oczy zamknięte nagrano u 38 osób (artykuł), oczy otwarte u wszystkich 71. Plan zakłada „71 osób z KSS i PVT”, a to prawda tylko dla etykiety warunku.
- **Licencja:** CC0 (zbiór na OpenNeuro). Artykuł: CC BY 4.0.
- **Rozmiar:** 8,9 GB, 1228 plików, wersja 1.0.8. Pojedyncze osoby da się pobrać osobno (jedna osoba to ok. 140 MB, np. `sub-01`). Bez konta.

Linki:
- Dane (OpenNeuro, DOI): https://doi.org/10.18112/openneuro.ds004902.v1.0.8 ([strona](https://openneuro.org/datasets/ds004902))
- Kopia na AWS (bez konta): `aws s3 ls --no-sign-request s3://openneuro.org/ds004902/`
- Mirror w GitHub (DataLad): https://github.com/OpenNeuroDatasets/ds004902
- Artykuł: Xiang C., Fan X., Bai D., Lv K., Lei X., *A resting-state EEG dataset for sleep deprivation*, Scientific Data 11, 427 (2024). https://doi.org/10.1038/s41597-024-03268-2
- Pełny tekst (PMC): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11043390/

---

## Na slajd „co dalej”: zbiory z czujników noszonych

Zbiory 8–10 nie pasują do naszego montażu (EEG z 1–4 elektrod czołowych lub skroniowych). Przydają się jako dowód, że EEG konsumenckie i czujniki noszone (EKG, PPG, EDA) da się nagrywać razem. To argument za mapą „EEG kalibruje, zegarek pilnuje”, a nie dane do naszego pipeline'u.

## 8. CL-Drive, obciążenie poznawcze kierowcy (nie zmęczenie)

- **Co zawiera:** 21 osób w immersyjnym symulatorze jazdy, 9 poziomów trudności po 3 min, każdy z nagraniem bazowym. Etykieta: subiektywna ocena obciążenia poznawczego co 10 s.
- **Czujniki:** EEG z opaski Muse S (4 kanały: AF7, AF8, TP9, TP10, 256 Hz), EKG z Shimmer (3 odprowadzenia, 512 Hz), EDA z Shimmer (128 Hz), eye tracking Tobii.
- **Pokrywa nasze kanały:** nie, żadnego.
- **Uwaga:** zbiór mierzy obciążenie poznawcze, nie zmęczenie ani senność. Na slajd tylko jako przykład zestawu „opaska EEG + EKG + EDA” u kierowcy.
- **Licencja:** CC BY-NC 4.0 (tylko użycie niekomercyjne).
- **Rozmiar:** 1,29 GB, po jednym archiwum `.rar` na modalność (EEG 151 MB, EKG 679 MB, EDA 157 MB, wzrok 299 MB, etykiety 5 kB). Nie da się pobrać jednej osoby, za to da się pobrać samo EEG. Pliki bez ograniczeń dostępu.

Linki:
- Dane (Borealis, DOI): https://doi.org/10.5683/SP3/JJ2YZZ
- Repozytorium z opisem: https://github.com/prithila05/cl-drive
- Artykuł: Angkan P. i in., *Multimodal Brain-Computer Interface for In-Vehicle Driver Cognitive Load Measurement: Dataset and Baselines*, IEEE Transactions on Intelligent Transportation Systems (przyjęty 2023). Preprint: https://arxiv.org/abs/2304.04273

---

## 9. FatigueSet (Nokia Bell Labs), zmęczenie psychiczne

- **Co zawiera:** ok. 13 h danych z 36 sesji (po 12 sesji o niskiej, średniej i wysokiej aktywności fizycznej). Każda osoba ma trzy sesje, więc wychodzi 12 osób (wniosek ze struktury opisanej na stronie, liczby osób wprost nie sprawdziłem). Etykiety: subiektywne oceny zmęczenia oraz wyniki męczliwości w dwóch zadaniach (czas reakcji z wyborem i 2-back).
- **Czujniki:** 14 czujników na czterech urządzeniach: prototyp słuchawki dousznej Nokia Bell Labs (akcelerometr, żyroskop, PPG), opaska EEG Muse S (EEG, akcelerometr, żyroskop), pas piersiowy Zephyr BioHarness 3.0 (EKG, oddech, akcelerometr, postawa), opaska Empatica E4 (BVP i IBI, EDA, temperatura skóry, akcelerometr).
- **Pokrywa nasze kanały:** nie. Muse S ma 4 elektrody czołowo-skroniowe; **niesprawdzone**, które kanały i jaka częstotliwość są w plikach FatigueSet.
- **Licencja:** **niesprawdzona.** Strona nie podaje licencji, link „Terms of Use” jest pusty, a stopka mówi „© Nokia Bell Labs 2021. All Rights Reserved”. Przed użyciem na slajdzie poza samą wzmianką trzeba to wyjaśnić z autorami.
- **Rozmiar:** jeden plik `fatigueset.zip` na Google Drive, 612 MB (z komunikatu Google Drive). Nie da się pobrać jednej osoby. Bez konta.
- **Artykuł:** zamknięty dostęp, abstraktu nie udało się pobrać (Springer i EUDL odrzucają zapytania). Fakty powyżej są ze strony zbioru.

Linki:
- Strona zbioru: https://www.esense.io/datasets/fatigueset/
- Artykuł: Kalanadhabhatta M., Min C., Montanari A., Kawsar F., *FatigueSet: A Multi-modal Dataset for Modeling Mental Fatigue and Fatigability*, Pervasive Health 2021, LNICST (Springer, 2022). https://doi.org/10.1007/978-3-030-99194-4_14 ([EUDL](https://eudl.eu/doi/10.1007/978-3-030-99194-4_14))

---

## 10. MEFAR, zmęczenie psychiczne w pracy

- **Co zawiera:** 23 osoby z czterech grup zawodowych (nauczyciele akademiccy, technicy, inżynierowie komputerowi, pracownicy kuchni), nagrane w trakcie pracy w dwóch sesjach: rano i wieczorem. Etykieta: Skala Zmęczenia Chaldera (wynik 12 i więcej oznacza zmęczenie psychiczne), w obu sesjach. Dane surowe i przetworzone (wersje 1, 32 i 64 Hz: `MEFAR_DOWN`, `MEFAR_MID`, `MEFAR_UP`) oraz arkusz `general_info` z demografią.
- **Czujniki:** EEG z NeuroSky MindWave (jeden kanał), BVP, EDA, tętno, temperatura skóry i akcelerometr z opaski Empatica E4 (BVP 64 Hz, EDA 4 Hz).
- **Uwaga:** EEG zapisano z częstotliwością 1 Hz (artykuł), czyli są to wartości wyliczone przez aplikację NeuroSky, a nie surowy sygnał. Analizy widma, jaką robimy, nie da się na nim powtórzyć.
- **Pokrywa nasze kanały:** nie.
- **Licencja:** CC BY 4.0.
- **Rozmiar:** dane surowe 25,7 MB, przetworzone 64,6 MB (dwa pliki `.zip`, wersja 5). Bez konta.

Linki:
- Dane (Mendeley Data, DOI): https://doi.org/10.17632/z3g26tphnv.5 ([strona](https://data.mendeley.com/datasets/z3g26tphnv/5))
- Artykuł: Derdiyok S., Patlar Akbulut F., Catal C., *Neurophysiological and biosignal data for investigating occupational mental fatigue: MEFAR dataset*, Data in Brief 52, 109896 (2024). https://doi.org/10.1016/j.dib.2023.109896
- Pełny tekst (PMC): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10762351/

---

## Kolejność pracy

Zgodna z [`plan-projektu.md`](plan-projektu.md), sekcja „Zbiory publiczne, w kolejności”.

**Zrobione:**
- `data/analysis/01-recordings-quality.ipynb`: jakość naszych nagrań z BrainAccess MINI.
- `data/analysis/02-public-datasets-comparison.ipynb`: porównanie naszych nagrań z EEGMAT (punkt 1) i COG-BCI (punkt 3).
- `data/analysis/03-wachta-indicator-on-recordings.ipynb`: wskaźnik Wachty na naszych nagraniach.

**Dalej:**
1. **Cui i in. (punkt 6):** wykres czujny kontra senny na O1/O2 i pozostałych naszych kanałach. W toku: `data/analysis/04-drowsiness-public-dataset.ipynb`.
2. **ds004902 (punkt 7):** wyspany kontra po deprywacji snu, z PVT i KSS tam, gdzie są (KSS tylko u 33 osób).
3. **COG-BCI (punkt 3):** EEG i EKG jednocześnie, PVT i KSS. Jedyny szybki sposób, by pokazać związek EEG z sercem.
4. **Slajd „co dalej”:** CL-Drive, FatigueSet, MEFAR (punkty 8–10), tylko jako opis, bez analizy.

Poprzednia kolejność (z czasu wariantu „senność i przeciążenie”), zostawiona dla porządku:

1. **Mental Arithmetic:** czy theta na F3/F4 odróżnia spoczynek od liczenia.
2. **Alpha Waves:** czy detektor alfy na O1/O2 odróżnia oczy zamknięte od otwartych.
3. **COG-BCI:** 1–2 osoby z zadania MATB jako walidacja w scenariuszu operatora.
4. **Zbiór z jazdy:** walidacja senności, jeśli zostanie czas.

---

## Literatura do slajdu o zegarku: do sprawdzenia przed slajdem

Stan na 14.11.2026. Sprawdzone w abstraktach, pełnych tekstów tych trzech prac nie czytałem.

- **Fujiwara i in. 2019, HRV i senność potwierdzona EEG.** **Potwierdzone w abstrakcie:** 34 osoby w symulatorze jazdy, zasypianie oceniał specjalista snu z EEG. Wykryto senność w 12 z 13 epizodów przed fazą N1, fałszywe alarmy 1,7 na godzinę. Fujiwara K. i in., *Heart Rate Variability-Based Driver Drowsiness Detection and Its Validation With EEG*, IEEE Trans Biomed Eng 66(6):1769–1778. https://doi.org/10.1109/TBME.2018.2879346 ([PubMed](https://pubmed.ncbi.nlm.nih.gov/30403616/))
- **Persson i in. 2019, HRV słabo uogólnia się w realnych warunkach.** **Potwierdzone w abstrakcie, ale inaczej niż w planie:** 86 kierowców na prawdziwych drogach, wyspani i po deprywacji snu, etykiety z KSS (trzy klasy), klasyfikator SVM na 24 cechach HRV osiąga średnio 61% trafności. Autorzy piszą, że wysokich wyników z kontrolowanych badań nie udało się powtórzyć w realnej jeździe, i wskazują czynniki zakłócające. Abstrakt nie mówi wprost o „uogólnianiu między osobami”; tego sformułowania nie dawać na slajd bez pełnego tekstu (**niesprawdzone**). Persson A. i in., *Heart Rate Variability for Driver Sleepiness Classification in Real Road Driving Conditions*, EMBC 2019:6537–6540. https://doi.org/10.1109/EMBC.2019.8857229 ([PubMed](https://pubmed.ncbi.nlm.nih.gov/31947339/))
- **Lu i in. 2022 (Chalmers), kontekst podnosi AUC.** **Potwierdzone w abstrakcie:** 43 osoby na prawdziwych drogach, jazda ręczna i częściowo zautomatyzowana, wyspani i po deprywacji snu. Tętno z konsumenckich pasów piersiowych, KSS co 5 min jako etykieta. Klasyfikator AdaBoost na cechach HRV: AUC 0,76, po dodaniu czasu jazdy i pory dnia/nocy AUC 0,88. Lu K., Karlsson J.G., Sjörs A., Sjöqvist B.-A., Candefjord S., *Detecting Driver Sleepiness Using Consumer Wearable Devices in Manual and Partial Automated Real-Road Driving*, IEEE Trans Intell Transp Syst 23(5):4801–4810 (2022). https://doi.org/10.1109/TITS.2021.3127944 ([Chalmers](https://research.chalmers.se/en/publication/527879))
