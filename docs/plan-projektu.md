# Plan projektu: Wachta (nazwa robocza)

Zmęczenie mierzone na człowieku, nie na zegarze. Plan na hackathon Heroes of the Brain 2026
(do oddania mniej niż 12 h od spisania) i krótki zarys tego, co dalej.

Decyzja o kierunku jest zapisana w [`decyzje.md`](decyzje.md). Ten plik mówi, co budujemy, kto co robi i w jakiej kolejności.

## Produkt w jednym zdaniu

Przepisy mierzą czas pracy, a nie człowieka. Wachta mierzy człowieka: **EEG kalibruje, zegarek pilnuje.**

1. Krótka sesja z EEG uczy osobistego wzorca zmęczenia danej osoby.
2. Na co dzień wystarcza tani czujnik (zegarek) i kontekst: czas pracy, pora doby, sen.
3. Wynik: rezerwa czujności 0–100 i rekomendacja (pracuj / zaplanuj przerwę / przerwa teraz).
4. Adaptacja: system zmienia plan przerw i obsadę, a nie tylko alarmuje. Przełożony widzi wyłącznie gotowość.

Odbiorcy: pracownicy zmianowi, u których błąd ze zmęczenia jest kosztowny (kierowca zawodowy, pielęgniarka, lekarz).
Zamiast jednej normy czasu pracy dla wszystkich firma dostaje limit liczony dla konkretnej osoby w konkretnym dniu.

Na hackathonie pokazujemy na żywo punkty 1, 3 i 4 z EEG. Punkt 2 pokazujemy jako dowód z danych
publicznych i literatury oraz studium jednej osoby z zegarkiem Garmin Venu 2.

## Co już wiemy i co z tego wynika

| Ustalenie | Źródło | Wniosek dla planu |
|---|---|---|
| Alfa potyliczna (zamknięte oczy / senność) działa u 4/4 osób po 60 s kalibracji | `data/analysis/` notebooki 01 i 03 | To jest rdzeń demo |
| Epizody alfy z notebooka 01 pokrywają się z blokami `eyes_closed` z protokołu | `data/recordings/README.md` | Mamy prawdziwe etykiety, można policzyć trafność |
| Reguła „przeciążenie” nie zadziałała ani razu; w zadaniu MATB alfa ciemieniowa rośnie zamiast spadać | notebooki 02 i 03 | Przeciążenia nie obiecujemy |
| Odrzucanie artefaktów i kalibracja na osobę są konieczne; flaga kontaktu elektrod nic nie mówi | notebooki 01–03 | Jakość sygnału oceniamy sami |
| Zmęczenie i senność to stan fizyczny, dozwolony w celach bezpieczeństwa; obciążenie poznawcze to szara strefa, a stres i wypalenie są zakazane | [`rynek-wielkosc-i-kierunek.md`](rynek-wielkosc-i-kierunek.md) §3, AI Act motyw 18 | Mówimy „zmęczenie i czujność”, nie „przeciążenie kognitywne” |
| W zarządzaniu zmęczeniem działa już SmartCap (EEG w czapce); research rynku rekomendował wejście przez IT ops | [`rynek-eeg-wearables.md`](rynek-eeg-wearables.md), [`rynek-wielkosc-i-kierunek.md`](rynek-wielkosc-i-kierunek.md) | Na slajdzie musi być różnica względem SmartCap; segment wejścia jest punktem otwartym |
| Logowanie bibliotek do Garmin Connect jest zepsute od marca 2026; HRV z nadgarstka bywa niewiarygodne | źródła na końcu | Odczyty z Venu 2 wpisujemy ręcznie; API tylko jako próba na 20 min |

**Cel produktu definiujemy jako zmęczenie i spadek czujności.** Obciążenie zadaniem zostaje jako kierunek
badawczy „co dalej”. Pipeline i demo są wspólne dla obu wariantów pitchu (pracownicy zmianowi albo dyżurni IT),
różni się scenariusz i slajdy.

## Zakres na hackathon

| Priorytet | Co | Kto |
|---|---|---|
| MUST | Pipeline: okna 2 s, odrzucanie artefaktów, kalibracja 60 s, wskaźnik czujności, stany i rekomendacja. Tryb odtwarzania z pliku i tryb na żywo z BrainAccess Board | Claude, Wojtek |
| MUST | Dashboard: widok pracownika (rezerwa, trend, rekomendacja, jakość sygnału), mini-panel przełożonego (tylko gotowość), przełącznik scenariusza kierowca / pielęgniarka | Claude |
| MUST | Trafność na naszych nagraniach z adnotacjami: `eyes_closed` kontra reszta, na osobę | Claude, Adrian |
| MUST | Pitch i scenariusz demo | Rudy, Filip |
| SHOULD | Jeden wykres z danych publicznych o zmęczeniu (czujny kontra senny na naszych 8 kanałach) | Adrian |
| SHOULD | Trzy punkty pomiarowe zespołu (T0, T1, T2) z protokołem i KSS; u Wojtka odczyty z Venu 2 | Filip, Wojtek |
| COULD | EEG a tętno/HRV w COG-BCI (ma EKG) albo „zmiana w 90 sekund” z nagrania jazdy | Adrian |
| COULD | Prognoza „czas do progu”, test czasu reakcji (PVT) w przeglądarce, pobranie krzywych z Garmin Connect | Claude |
| Nie teraz | Tętno i HRV na żywo, model uczony między osobami, EEG w kasku, integracje z systemami firm | — |

## Architektura

```
BrainAccess MINI → BrainAccess Board → BoardSource ─┐
plik .fif z data/recordings → ReplaySource ─────────┼→ bufor → cechy (okna 2 s) → kalibracja (z-score)
                                                    │        → wskaźnik + stan + rezerwa → WebSocket → dashboard
odczyty Venu 2 i KSS (ręcznie, punkty pomiarowe) ───┘
```

Kod powstaje w `src/wachta/`, testy w `tests/`, skrypty analityczne w `experiments/`. Instrukcja uruchomienia pojawi się
w `uruchomienie.md` razem z kodem.

Logika cech i stałe pochodzą z notebooków w `data/analysis/` (okna 2 s z krokiem 1 s, próg artefaktu 300 µV,
kalibracja z pierwszych 60 czystych okien, mediana z 5 okien, próg z-score 2).

**Wskaźnik v0** jest jawny i prosty, a jego parametry są w `src/wachta/config.py` i opisane jako założenia:

- szybki: wyrazistość alfy na O1/O2 jako z-score względem kalibracji; powyżej progu przez co najmniej 3 s to „spadek czujności”;
- wolny: średnia z 60 s z-score stosunku (theta+alfa)/beta, czyli znany z literatury znacznik zmęczenia;
- rezerwa 0–100: ubywa z czasem pracy, szybciej przy rosnącym wskaźniku wolnym i po każdym spadku czujności, a wraca w przerwie;
- jakość: gdy ponad połowa okien z ostatnich 30 s jest odrzucona, system pokazuje „brak wiarygodnego sygnału” i nie zgaduje.

## Dane i dowody

### Punkt pomiarowy (4 min na osobę)

Trzy razy w trakcie pracy: T0 na starcie, T1 w połowie, T2 przed zamrożeniem kodu.

| Krok | Czas | Po co |
|---|---|---|
| Oczy otwarte, patrzenie w punkt | 60 s | kalibracja |
| Oczy zamknięte | 60 s | alfa potyliczna |
| Liczenie w pamięci (odejmowanie 7 od 1000) | 60 s | obciążenie zadaniem, tylko do obserwacji |
| Ocena senności KSS 1–9 | 10 s | etykieta zmęczenia |

U Wojtka w tych samych 2 minutach spoczynku Health Snapshot na Venu 2 oraz odczyt Body Battery, stresu i tętna.
Znaczniki zapisuje narzędzie punktu pomiarowego (`python -m wachta.session`). Nowe nagrania zapisujemy jako `.fif`
z adnotacjami, bez kopii CSV.

### Zbiory publiczne, w kolejności

1. **EEG driver drowsiness dataset** (Cui i in., figshare, 172 MB): okna 3 s, czujny kontra senny. To pochodna zbioru jazdy
   z [`datasety-eeg-zrodla.md`](datasety-eeg-zrodla.md). Najszybszy wykres.
2. **OpenNeuro ds004902**: 71 osób wyspanych i po deprywacji snu, EEG spoczynkowe, KSS i PVT.
3. **COG-BCI**: EEG i EKG jednocześnie, PVT i KSS. Jedyny szybki sposób, by pokazać związek EEG z sercem.
4. Na slajd „co dalej” (EEG konsumenckie z czujnikami noszonymi): CL-Drive, FatigueSet, MEFAR.

### Literatura do slajdu o zegarku

- Wykrywanie senności z HRV potwierdzone EEG: 12 z 13 epizodów przed zaśnięciem, 1,7 fałszywego alarmu na godzinę (Fujiwara i in. 2019).
- Samo HRV słabo uogólnia się między osobami (Persson i in.), a kontekst (czas jazdy, pora doby) podnosi AUC z 0,76 do 0,88
  (Chalmers/Autoliv 2022). To argument za personalizacją.

Liczby trzeba sprawdzić w pełnych tekstach przed wstawieniem na slajd.

## Podział pracy i harmonogram

| Blok | Claude | Wojtek | Adrian | Filip | Rudy |
|---|---|---|---|---|---|
| 0–0,5 h | plan i decyzja do repo | scala PR, akceptuje plan | — | przygotowuje punkt T0 | szkielet slajdów |
| 0,5–3 h | pakiet, pipeline offline, trafność na adnotacjach | test odczytu na żywo z Board, odczyty Venu 2 | notebook 03 z prawdziwymi etykietami, start zbioru 1 | pomiary T0 czterech osób | problem, rynek, prawo |
| 3–6 h | strumień, serwer, dashboard w trybie odtwarzania | podpięcie trybu na żywo | wykres czujny kontra senny | pomiary T1 | rozwiązanie, różnica względem SmartCap |
| 6–8,5 h | rezerwa, panel przełożonego, poprawki | próba demo na żywo | COULD albo liczby do slajdów | pomiary T2, operator demo | model biznesowy, ryzyka |
| ostatnie 2 h | tylko poprawki błędów | dwie próby demo, nagranie zapasowe | wykresy na slajdy | próby demo | finalny pitch |

Role Filipa i Rudego to propozycja, do zamiany między nimi. Kod zamrażamy 2 h przed oddaniem.

## Demo i pitch

1. Osoba z zespołu skalibrowana przed wejściem. Dashboard: rezerwa wysoka, „możesz pracować”.
2. Zamyka oczy na 5–10 s (symulowany mikrosen): „przerwa teraz, zjedź na parking”, a panel przełożonego proponuje zmianę obsady.
3. Slajdy: trafność na naszych nagraniach, wykres z danych publicznych, studium Venu 2 (jedna osoba, ilustracja), mapa „EEG kalibruje, zegarek pilnuje”.
4. Plan awaryjny: ten sam dashboard w trybie odtwarzania nagrania i nagrane wideo.

**Co zweryfikowane, a co założone** (osobny slajd):

| Zweryfikowane | Założone |
|---|---|
| Wykrywanie zamkniętych oczu i alfy na naszym sprzęcie, z etykietami | Parametry rezerwy czujności |
| Kontrast czujny/senny w danych publicznych (po wykonaniu wykresu) | Przeniesienie wzorca z EEG na zegarek |

**Różnica względem SmartCap:** EEG nie musi być na głowie całą zmianę, limit jest osobisty, system zmienia plan pracy,
a zakres obejmuje też ochronę zdrowia.

**Kontekst prawny:** UE wymaga ostrzegania o senności kierowcy we wszystkich nowych autach od lipca 2024,
a AI Act wprost wyłącza wykrywanie zmęczenia z zakazu rozpoznawania emocji. Lotnictwo ma już systemy zarządzania
ryzykiem zmęczenia (FRMS), ale opierają się głównie na limitach czasu i samoocenie.

## Ryzyka

| Ryzyko | Odpowiedź |
|---|---|
| Tryb na żywo nie był testowany poza laptopem ze sprzętem | Wojtek testuje w pierwszym bloku; demo zawsze działa w trybie odtwarzania |
| Mało czasu | Zamrożenie kodu 2 h przed oddaniem; COULD wypada pierwsze |
| Rozjazd zespołu co do segmentu (IT ops kontra pracownicy zmianowi) | Punkt otwarty w `decyzje.md`; technika jest wspólna |
| Sygnał z suchych elektrod przy ruchu | Odrzucanie okien, wskaźnik jakości, stan „brak sygnału” |
| Dane z zegarka jednej osoby | Opisane jako ilustracja, bez wniosków statystycznych |
| Dane o zdrowiu pracownika (RODO art. 9, Kodeks pracy) | Surowe dane zostają u pracownika, przełożony widzi tylko gotowość; do konsultacji prawnej po hackathonie |

## Po hackathonie

- Pilotaż na jednej zmianie u jednego klienta, z pomiarem przed i po.
- Własny zbiór EEG + zegarek z etykietami KSS i PVT.
- Model osobisty uczony z EEG jako wzorca.
- Oficjalny dostęp do danych Garmina (program dla firm).
- EEG w czapce lub kasku dla ról wysokiego ryzyka.

## Źródła

- Zbiory: [Cui i in., drowsiness](https://figshare.com/articles/dataset/EEG_driver_drowsiness_dataset/14273687) ·
  [ds004902](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11043390/) · [COG-BCI](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9918545/) ·
  [CL-Drive](https://github.com/prithila05/cl-drive) · [FatigueSet](https://eudl.eu/doi/10.1007/978-3-030-99194-4_14) ·
  [MEFAR](https://data.mendeley.com/datasets/z3g26tphnv/5)
- Literatura: [Fujiwara 2019](https://www.pubmed.gov/30403616/) · [Persson 2019](https://pubmed.ncbi.nlm.nih.gov/31947339/) ·
  [Chalmers 2022](https://research.chalmers.se/en/publication/527879) · [PVT-B](https://pmc.ncbi.nlm.nih.gov/articles/PMC3197786)
- Prawo i rynek: [AI Act, motyw 18](https://artificialintelligenceact.eu/recital/18/) ·
  [GSR2, ostrzeganie o senności](https://rsa.ie/road-safety/road-users/car-drivers/general-safety-regulation-(gsr2)) ·
  [SmartCap](https://www.equipmentworld.com/smartcap-integrates-camera-free-worker-fatigue-monitoring-into-hard-hats-ball-caps-and-more/) ·
  [IATA, FRMS 2025](https://www.iata.org/contentassets/5f976bb3ca2446f3a40e88b18dd61fbb/frms_white-paper_2025.pdf)
- Sprzęt: [brainaccess-board](https://pypi.org/project/brainaccess-board/) · [garminconnect 0.3.2](https://pypi.org/project/garminconnect/0.3.2/) ·
  [Health Snapshot](https://www.wareable.com/garmin/what-is-garmin-health-snapshot-how-to-use) ·
  [dokładność HRV z zegarków](https://discovery.ucl.ac.uk/10186376/1/CinC2023-237.pdf)
