# Analiza dotychczasowych wyników i projekt adaptacji v2

Stan na 14.11.2026, wieczór. Dokument zbiera to, co ustaliliśmy w notebookach 01–06, w literaturze
([`podstawy-naukowe.md`](podstawy-naukowe.md)), w kodzie `src/wachta/` i w kryteriach oceny
([`pytania-i-odpowiedzi.md`](pytania-i-odpowiedzi.md)), a potem proponuje, jak system ma adaptować się lepiej.
Zadania wynikające z tej analizy są w issues na GitHubie (zbiorczy issue „Adaptacja v2”).

**Czego ten dokument nie jest.** To propozycja do uzgodnienia w zespole, a nie decyzja. Fragmenty oznaczone
**„założenie”** to moja ocena, nieoparta na danych. Kod i dokumenty cudzych strumieni nie były zmieniane.

## 1. Co wiemy i na ile to pewne

### Potwierdzone

| # | Ustalenie | Źródło |
|---|---|---|
| S1 | Wyrazistość alfy na O1/O2 wykrywa zamknięcie oczu na suchych elektrodach: 4 z 4 osób, opóźnienie 7–13 s, 1 fałszywy alarm w 32 min poza blokiem. Próg 2,5 dobrano na tych samych nagraniach | `trafnosc-na-nagraniach.md`, notebook 03 |
| S2 | Wyrazistość alfy jest lepsza od surowej mocy alfy (AUC 0,92 kontra 0,80 łącznie dla czterech osób, u Adiego moc nie dała alarmu wcale) | notebook 03 |
| S3 | Na publicznym zbiorze z jazdy alfa potyliczna rośnie ze zmęczeniem u 11 z 11 osób, AUC 0,75 (0,52–0,91), także przy referencji Fp1 | notebook 04 |
| S4 | Model uczony na tej samej osobie daje ok. 81% po ok. 1 min na klasę (83% w pełnym teście), a jeden model dla wszystkich 66–72%. Więcej osób w treningu pomaga coraz mniej po ok. 5 osobach | notebook 04, krzywa uczenia |
| S5 | Nasz sprzęt jest bardziej zaszumiony niż zbiory laboratoryjne (mediana amplitudy okna 115 µV wobec 53–75 µV, odrzucane 5–21% okien), ale referencja Fp1 prawie nie zmienia wskaźników alfy | notebooki 01, 02 |
| S6 | Kontekst (czas jazdy, pora doby) podnosi AUC wykrywania senności z 0,76 do 0,88, a poprzedni czas reakcji jest lepszym predyktorem lapsu niż EEG | Lu 2022, notebook 06 |
| S7 | Ludzie różnią się podatnością na zmęczenie w sposób stabilny | Van Dongen 2004 |

### Słabe albo obalone

| # | Ustalenie | Źródło |
|---|---|---|
| N1 | **Alfa przy otwartych oczach nie przewiduje lapsu w następnej minucie** (AUC 0,52, żadnego wyprzedzenia, ostrzeżenia na poziomie losowym) | notebook 06 |
| N2 | Wskaźnik wolny (θ+α)/β jest zakłócany przez mięśnie (r ≈ −0,5 u dwóch osób) i nie ma spójnego trendu w zadaniu czujności | notebooki 03, 05 |
| N3 | Theta czołowa nie działa przy referencji Fp1 (AUC 0,58, u 3 z 11 osób odwrotny kierunek) | notebook 04 |
| N4 | Reguła „przeciążony” nie zadziałała ani razu, a w zadaniu MATB alfa ciemieniowa rośnie zamiast spadać | notebooki 02, 03 |
| N5 | Serce i EEG nie idą w parze minuta po minucie (|r| ≤ 0,16). Zmienność rytmu serca (RMSSD) i szybkość reakcji spadają razem (r = 0,18, ten kierunek u 22 z 29 osób), ale głównie dlatego, że obie zmieniają się z czasem zadania; po jego uwzględnieniu zostaje +0,05 (CI −0,03 do 0,17), więc wcześniejsze „r = −0,23, 16 z 16” nie przetrwało przeliczenia (notebook 10). Tętno rośnie w 10-minutowym zadaniu, czyli odwrotnie niż przy senności | notebooks 05, 10 |
| N6 | Próg 300 µV łapie ruch głowy (74–100% okien), ale tylko 33–60% okien z napięciem mięśni | notebook 03 |

### Czego jeszcze nie wiemy

- Czy wskaźnik wykrywa **prawdziwą senność na naszym sprzęcie**. Nikt w nagraniach nie był senny, a zamknięte oczy to nie senność.
- Czy drugi sygnał (akcelerometr, tętno) podnosi pewność oceny. Nie sprawdziliśmy tego na danych.
- Jak działa osobista kalibracja z oczami otwartymi i zamkniętymi.
- Jak długo kalibracja pozostaje ważna w ciągu nocy (u Wojtka dryf alfy 0,94 σ w rozmowie).

## 2. Co robi dziś system i co ma wady

Stan kodu na `main` po scaleniu A1–A9 (analiza przepływu nagrań przez pipeline, 4 nagrania):

1. **Tryb demo jest napędzany zegarem, nie człowiekiem.** Przy `--time-scale 60` rezerwa spada o 12 punktów na minutę ekranu.
   U Filipa jest zerowa jeszcze przed jego zamknięciem oczu, a w blokach czytania, liczenia i ruchu stan „stop” wynika w 100% z
   wyczerpania rezerwy. Stan jest zgodny z modelem „tylko zegar” przez 53–83% czasu.
2. **Jedno zamknięcie oczu liczy się jako dwa spadki.** U Adiego i Wojtka w jednym bloku są dwa początki spadku. Reguła
   „dwa spadki w 120 s → stop” trzyma wtedy „Przerwa teraz” długo po otwarciu oczu (Adi w czytaniu: 96% czasu w stanie stop
   bez aktualnego spadku).
3. **Próba reakcji (A8) jest wywoływana wzrostem alfy poniżej progu** (`probe_z` 1,5). Notebook 06 pokazał, że taki sygnał nie
   wyprzedza lapsów (ostrzeżenia na poziomie losowym, ok. 17 fałszywych na godzinę przy z > 1,5). Na nagraniach zespołu daje
   to 0–8 prób na 10 minut poza blokiem zamkniętych oczu.
4. **Adaptacja ogranicza się do komunikatu**: napis stanu, rada, pasek rezerwy, panel przełożonego z propozycją, kto ma najwięcej
   rezerwy. Interfejs się nie zmienia, nic nie jest blokowane, a jedyny sygnał poza EEG to zegar.
5. **Wskaźnik wolny nadal przyspiesza odpływ rezerwy** (`slow_gain` 0,5), mimo N2.
6. **Kalibracja to pierwsze 60 czystych okien z otwartymi oczami.** Nie sprawdza, czy marker działa u danej osoby
   (Adi: czułość 49%, w danych publicznych AUC spadało do 0,52 u niektórych).

## 3. Rozbieżności w dokumentach i kodzie

| Gdzie | Problem |
|---|---|
| `docs/plan-projektu.md` (harmonogram) i `docs/zadania.md` | oddanie „za mniej niż 12 h” od 14:30, czyli ok. 2:30. Strona hackathonu: koniec prac w niedzielę 10:30, ocena wstępna 10:30–12:30, finał 13:00–15:00 |
| `data/recordings/README.md` | `neutral` opisany jako spoczynek z otwartymi oczami, a to była swobodna rozmowa. `control` to mruganie, zaciskanie szczęki i ruch głowy, nie „zdejmowanie czapki” |
| `docs/zadania.md` | B5 nadal „do zrobienia”, a jest zrobione z wynikiem negatywnym. Opis A8 zakłada wywoływanie próby wskaźnikiem „zbliżającym się do progu” |
| `src/wachta/index.py` (docstring) | opisuje wskaźnik szybki jako wykrywanie „spadków czujności” i próbę jako reakcję na wzrost wskaźnika |
| `docs/podstawy-naukowe.md` §1 | zdanie, że alfa przy otwartych oczach rośnie przy wtargnięciach senności, nie ma potwierdzenia w notebooku 06 |
| `AGENTS.md`, `README.md` | zasada „surowych nagrań EEG nie commitujemy” kontra nagrania zespołu w `data/recordings/` (punkt otwarty 4 w `decyzje.md`) |

## 4. Zasady projektu adaptacji v2

Wnioski z sekcji 1 prowadzą do kilku zasad:

1. **EEG robi tylko to, co umie: wykrywa teraz, nie przewiduje.** Zamknięcie oczu i fale alfy w sekundach (S1, S2). Żadnych haseł o
   przewidywaniu spadku czujności (N1).
2. **To, co przewiduje, to kontekst i zachowanie** (S6): pora doby, czas od przebudzenia, czas zadania i wynik próby reakcji. System ma
   z nich korzystać jawnie, a nie ukrywać ich w jednej liczbie.
3. **Trzy skale czasu, trzy pętle.** Pasuje to do literatury (EEG w sekundach, zachowanie w minutach, rytm dobowy w godzinach).
4. **System adaptuje też sposób monitorowania, nie tylko komunikat.** Częstość prób reakcji zależy od ryzyka. Jest to adaptacja,
   której nie trzeba uzasadniać przewidywaniem.
5. **Osoba jest wzorcem dla siebie.** Kalibracja, próg i model są osobiste (S4), a system mówi, kiedy marker u tej osoby nie działa.
6. **Pokazujemy, skąd bierze się stan.** Rozbicie na dowody (EEG teraz, próba reakcji, kontekst) zamiast jednej nieprzejrzystej rezerwy.
7. **Każdy parametr, którego nie dopasowano do danych, jest oznaczony jako założenie** (rezerwa, kary, progi okien).

## 5. Projekt: pętle, stany i zachowania

### 5.1 Trzy pętle

| Pętla | Skala | Sygnał | Co robi |
|---|---|---|---|
| Ostra | sekundy | EEG: wyrazistość alfy O1/O2 po bramce artefaktów (amplituda, EMG, akcelerometr) | wykrywa „oczy zamknięte / fala alfy” teraz, zmienia interfejs natychmiast |
| Zachowania | minuty | próba reakcji (PVT-B, krótka wersja: lapsy i 1/RT, nie średni czas) | potwierdza lub odrzuca podejrzenie, dostarcza etykiety, aktualizuje osobistą linię bazową |
| Kontekstu | godziny | czas od przebudzenia, pora doby, czas zadania (uproszczony model dwuprocesowy) | ustawia poziom ryzyka bazowego i częstość prób reakcji |

### 5.2 Stany i przejścia (specyfikacja do uzgodnienia)

| Stan | Wejście | Wyjście | Zmiana w systemie |
|---|---|---|---|
| **OK** | baza: poziom ryzyka niski, brak zdarzeń ostrych | zdarzenie ostre, próba niezaliczona, ryzyko ≥ średnie | pełny interfejs, próba co ok. 20 min **(założenie)** |
| **UWAGA** | ryzyko średnie z kontekstu albo jedno zdarzenie ostre w ostatnich N minutach | dwa zdarzenia ostre, próba niezaliczona | uproszczony widok (jedno zadanie), potwierdzanie czynności ryzykownych, próba co ok. 10 min **(założenie)** |
| **SPRAWDZENIE** | zdarzenie ostre (po jego zakończeniu) lub termin próby | wynik próby | nakładka z próbą, bez blokowania zadań krytycznych |
| **STOP / PRZEKAZANIE** | próba niezaliczona albo dwa odrębne zdarzenia ostre | co najmniej dwie próby zaliczone w osobistej normie i brak zdarzeń przez M minut | blokada czynności ryzykownych, odliczanie przerwy, propozycja przekazania (przełożony widzi tylko gotowość) |
| **BRAK SYGNAŁU** | jakość sygnału poniżej progu | jakość powyżej progu | system nie zgaduje; zostaje kontekst i próby |

Zasady, które naprawiają wady z sekcji 2:

- **Scalanie zdarzeń:** zdarzenia ostre w odstępie poniżej ok. 15–20 s to jedno zdarzenie (jedno zamknięcie oczu to jedno zdarzenie).
- **Rozdzielenie „teraz” od „niedawno”:** baner ostry znika po otwarciu oczu. Pamięć o zdarzeniach obniża rezerwę i podnosi poziom ryzyka,
  ale nie trzyma stanu „Przerwa teraz” przez 2 minuty.
- **Próba tylko po zdarzeniu ostrym albo z harmonogramu**, nigdy z podprogowego wzrostu alfy (N1).
- **Zaliczenie próby względem osobistej normy** (np. czas reakcji powyżej 1,5-krotności własnej mediany z kalibracji, jak w pracy Cui),
  a nie stałej wartości dla wszystkich **(założenie do sprawdzenia)**.

### 5.3 Co system konkretnie zmienia (widoczne w demo)

1. **Interfejs:** trzy różne widoki (OK, UWAGA, STOP). W UWAGA widok upraszcza się do jednego zadania i prosi o potwierdzenie
   działań ryzykownych. W STOP blokuje je i pokazuje przekazanie. Scenariusz kierowcy: większe elementy, mniej danych. Scenariusz
   dyżuru medycznego: dwustopniowe potwierdzenie.
2. **Częstość monitorowania:** odstęp między próbami reakcji skraca się wraz z ryzykiem (np. 20 → 10 → 5 min, **założenie**).
3. **Plan przerw:** długość przerwy zależy od zmierzonego powrotu do normy (próby w osobistej normie), a nie ustalona z góry.
4. **Warstwa zespołu:** panel przełożonego pokazuje wyłącznie gotowość i propozycję przekazania.
5. **Personalizacja:** próg alarmu osobisty, a próby reakcji jako etykiety uczą model osobisty (po ok. 20 próbkach, **COULD**).

### 5.4 Drugi sygnał biologiczny

Kategoria wymaga „EEG i innych sygnałów biologicznych”, a samo tętno słabo wykrywa senność (N5, Persson 2019).
Proponuję więc:

- **Akcelerometr z czapki** (już w nagraniach): bramka artefaktów oraz sygnał dodatkowy (ruch głowy, opadanie głowy). To jedyny
  drugi sygnał, który na pewno mamy. **Nie jest zwalidowany**, więc w pitchu opisujemy go jako demonstrator.
- **Tętno z zegarka** (jeśli da się podpiąć na żywo, nie sprawdzono, czy Venu 2 przesyła odstępy RR): podnosi lub obniża **pewność** oceny,
  nie decyduje o stanie. Przy zgodności EEG i tętna pewność wysoka. Przy rozbieżności system prosi o próbę reakcji.
- **Próba reakcji** jest trzecim, behawioralnym sygnałem i jedynym ze złotym standardem w literaturze (lapsy w PVT).

### 5.5 Kalibracja z reaktywnością alfy

Kalibracja: ok. 30 s oczy otwarte i ok. 15 s oczy zamknięte. Z tego powstaje osobisty współczynnik reaktywności alfy (stosunek alfy przy
oczach zamkniętych do otwartych) i test „marker działa u tej osoby: tak, słabo, nie”. Próg alarmu ustawiany jako ułamek skoku
(**założenie**: senna alfa jest słabsza niż przy zamkniętych oczach). Gdy marker jest słaby, system opiera się na próbach i kontekście
i mówi o tym wprost.

**Po sprawdzeniu w B7 (notebook 07) ten punkt wymaga korekt:** (1) próg alarmu jako ułamek skoku podnosi fałszywe alarmy z 1 do 20 na nagraniach zespołu, więc zostaje stałe `z_enter` = 2,5; (2) 30 s oczu otwartych to za mało (zgodność werdyktu 78%), potrzeba 60 s oczu otwartych (bez rozmowy) i ok. 40 s zamkniętych, z pominięciem pierwszych 10 s; (3) werdykt jest cechą sesji, nie osoby (tydzień później ten sam werdykt u 44–56% osób), więc liczymy go przy każdym założeniu czepka, a „nie” znaczy „dziś, przy tym dopasowaniu”; (4) założenie o słabszej alfie senności nadal niesprawdzone. Progi robocze R_z: tak ≥ 2,5, słabo 1,5–2,5, nie < 1,5 (27 osób z elektrodami żelowymi, wstępne).

## 6. Plan walidacji (żeby adaptacja nie była tylko ilustracją)

1. **Nocne punkty pomiarowe T0, T1, T2 z testem reakcji i KSS** (zadania C1, C2, C4). Trenować na T0/T1, testować na T2.
2. **Zdarzenia ostre kontra lapsy z próby** na naszych nocnych danych: czy fale alfy przy otwartych oczach pokrywają się z wolnymi reakcjami.
3. **Model osobisty kontra wspólny** na naszych danych (potwierdzenie S4 na suchych elektrodach).
4. **Adaptacyjny harmonogram prób kontra stały:** ile prób na godzinę i jaki odsetek lapsów jest „zauważony” (symulacja offline).
5. **Powtórzenie B3 na lapsach i odwrotności czasu reakcji** (Basner i Dinges 2011) zamiast mediany RT.

## 7. Co wycinamy

- Wskaźnik wolny jako sterownik rezerwy (zostaje jako „eksperymentalny” bez wpływu na stan).
- Wszystko o „obciążeniu poznawczym”, stresie i wypaleniu.
- Wariant dyżurnych IT, potwierdzanie zaciśnięciem szczęki (nie zwalidowane), integracje z cudzymi systemami.
- Haseł „EEG ostrzega przed spadkiem czujności” i „przewidujemy mikrosen”.

## 8. Co wolno powiedzieć w pitchu (po zmianach)

- **Wolno:** wykrywamy zamknięcie oczu i fale alfy w czasie rzeczywistym na suchych elektrodach (4 z 4, 7–13 s). System zmienia interfejs,
  częstość kontroli i plan przerw. Na danych publicznych alfa rośnie ze zmęczeniem u 11 z 11 osób (AUC 0,75), a model osobisty
  daje ok. 80% wobec 66–72% dla wspólnego.
- **Trzeba zaznaczyć jako założenia:** parametry rezerwy i harmonogramu prób, kalibracja z reaktywnością alfy, drugi sygnał.
- **Nie wolno:** przewidywanie lapsu z alfy, „zegarek zastąpi EEG”, trafność na senności bez własnych nocnych danych.

## 9. Mapa zadań

Zadania są w issues repozytorium (zbiorczy issue „Adaptacja v2”). Kolejność ważności: scalanie zdarzeń i rozdzielenie „teraz” od
„niedawno”, tryby interfejsu, przebudowa próby reakcji, rozbicie rezerwy na dowody, nocne pomiary, film demo.
