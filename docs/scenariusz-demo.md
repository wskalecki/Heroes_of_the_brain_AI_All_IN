# Scenariusz demo

Zadanie D3 z [`zadania.md`](zadania.md). Treść slajdów: [`pitch.md`](pitch.md). Szkic do przejrzenia przez osoby od pitchu i demo (strumienie C i D).
Czasy w tym pliku zmierzono 14.11 na odtworzeniu nagrania Filipa. Na żywo trzeba je sprawdzić w próbach (zadanie C3).

## Dwa formaty, dwa cele

| | Film demo | Demo na scenie |
|---|---|---|
| Kiedy | etap 1, ocena **bez nas** (prezentacja + film, maks. 50 pkt) | finał, przy jury (maks. 20 pkt) |
| Co musi pokazać | całą pętlę: sygnał → stan → **zmiana zachowania systemu**, w pierwszych 15 s | to samo na żywo i odpowiedzi na pytania |
| Na czym | najlepsze ujęcie na żywo, a jeśli się nie uda, odtworzenie nagrania | na żywo, a plan awaryjny gotowy w drugim terminalu |

Za zgodność z tematem jest 20 z 50 punktów etapu 1 ([`jury-i-kryteria.md`](jury-i-kryteria.md) §1). Temat to system,
który **zmienia zachowanie** na podstawie EEG i innych sygnałów biologicznych. Dlatego demo nie kończy się na wykresie:
pokazujemy rekomendację, próbę reakcji, zmianę obsady w panelu przełożonego i przerwę.

**Do sprawdzenia:** limitu długości filmu nie znalazłem na stronie hackathonu. Zapytajcie organizatorów
(heroesofthebrain@gmail.com) albo poszukajcie w materiałach dla uczestników. Scenariusz filmu niżej trwa ok. 2 min.

## Role (propozycja)

| Rola | Kto | Co robi |
|---|---|---|
| Osoba w czepku | Wojtek (jego laptop i czepek, sprawdzony tryb na żywo) | siedzi spokojnie, reaguje na próby, zamyka oczy na znak |
| Operator | Filip (zadanie C3) | klika na dashboardzie, pilnuje terminala, decyduje o przejściu na plan awaryjny |
| Narrator | Rudy | mówi tekst ze scenariusza, trzyma czas |
| Odpowiedzi na pytania | Adrian | dane, walidacja, literatura |

## Przygotowanie (30 min przed)

- [ ] Laptop na zasilaniu, powiadomienia wyłączone, dźwięk włączony (próba reakcji ma sygnał dźwiękowy).
- [ ] BrainAccess Board uruchomiony, czepek naładowany i połączony, w Board widać płynący sygnał.
- [ ] Repo zaktualizowane (`git pull`), pakiet zainstalowany (`pip install -e ".[live]"`).
- [ ] Dwa terminale z wpisanymi komendami: na żywo i plan awaryjny (niżej). Port 8000 bywa zajęty, dlatego komendy używają 8001 i 8002.
- [ ] Przeglądarka na pełnym ekranie, strona dashboardu otwarta, scenariusz „Kierowca” wybrany. Internet nie jest potrzebny.
- [ ] Na drugim ekranie albo w drugiej karcie slajd z dowodami (`docs/img/trafnosc-na-nagraniach.png`).

## Komendy

**A. Na żywo** (noc, kierowca wstał o 7:00, jest 2:30; 1 minuta na ekranie to 30 minut zmiany):

```bash
python -m wachta.server --source board --name Wojtek --port 8001 --time-scale 30 --wake 07:00 --clock 02:30 --team rudy:380-520 adi:370-500
```

Strona: http://127.0.0.1:8001

**B. Plan awaryjny bez sprzętu** (odtworzenie nagrania Filipa, te same ustawienia):

```bash
python -m wachta.server --file filip --start 480 --port 8002 --time-scale 30 --wake 07:00 --clock 02:30 --team rudy:380-520 adi:370-500
```

Strona: http://127.0.0.1:8002

`--team` dodaje do panelu przełożonego nagrania Rudego i Adiego. Zapis `rudy:380-520` zapętla je na spokojnym odcinku
(spokojne czytanie i liczenie, bez bloku zamkniętych oczu), więc przez pierwsze ok. 3 min po „Nowej zmianie” mają stan „Może pracować”,
a rezerwa spada im tak samo jak innym. Nie uruchamiajcie serwera wcześniej niż 5 min przed wejściem.

Ile zostaje rezerwy w tych ustawieniach (bez spadków czujności; każdy spadek i każda nieudana próba zabiera 8 pkt):

| Od „Nowej zmiany” | 60 s | 90 s | 120 s | 180 s |
|---|---|---|---|---|
| Noc (×30, 2:30, wstał 7:00) | 85% | 77% | 69% | 52% |

## Demo na scenie, krok po kroku (ok. 2,5 min)

**Przed wejściem (3–5 min wcześniej):** operator uruchamia komendę A. Osoba w czepku przez ok. 60 s patrzy spokojnie
przed siebie, aż baner zmieni się z „Kalibracja” na „Możesz pracować”. Kalibracja zostaje zapamiętana. Serwer działa dalej.

| Czas | Kto | Co się dzieje | Co mówimy |
|---|---|---|---|
| 0:00 | narrator | dashboard na ekranie | „Przepisy mierzą czas pracy, a nie człowieka. Dwie osoby po tej samej zmianie mają różną rezerwę czujności.” |
| 0:10 | operator | klika **Nowa zmiana**. Rezerwa 100%, kafelek: 19,5 h od przebudzenia, godz. 02:30 | „Jest 2:30 w nocy. Kierowca nie śpi od 19 godzin. System zna jego wzorzec z minutowej kalibracji EEG i liczy, ile rezerwy mu zostało.” |
| 0:25 | narrator | wskazuje kafelki „Tempo zużycia” i „Oczy” | „W nocy i po długim czuwaniu rezerwa spada ponad dwa razy szybciej niż w dzień (założenie modelu). Na żywo patrzymy na dwie rzeczy: alfę z tyłu głowy i mrugnięcia.” |
| 0:45 | operator | klika **Sprawdź reakcję**. Osoba w czepku od razu naciska spację | „Kamera w aucie sprawdza, czy oczy są otwarte. My sprawdzamy, czy człowiek jeszcze reaguje. Tu: reakcja w normie.” |
| 1:00 | osoba w czepku | na znak narratora **zamyka oczy na 15 s** | „Teraz zamykam oczy.” |
| 1:07–1:13 | — | baner: **„Przerwa teraz. Oczy zamknięte dłużej niż kilka sekund. Zjedź na najbliższy parking.”** Widok sam się upraszcza: wykresy i kafelki znikają, zostaje duży komunikat i czerwony przycisk „Rozpocznij przerwę” (adaptacja interfejsu, #13). Nie pokazujemy wtedy wykresu, bo go nie ma | „Po kilku sekundach system nie tylko alarmuje, ale zmienia plan: kierowca ma zjechać.” |
| 1:20 | narrator | wskazuje panel przełożonego: „Najwięcej rezerwy ma Rudy” | „Przełożony nie widzi fal mózgowych, tylko gotowość. I od razu wie, kto może przejąć kurs.” |
| 1:30 | — | ok. 12–20 s po otwarciu oczu **system sam prosi o reakcję** („Sprawdzenie po spadku czujności”). Osoba w czepku **celowo nie reaguje** | „Po każdym spadku czujności system sprawdza, czy mózg wrócił. Oczy są już otwarte, a reakcji brak. Tu ją symulujemy.” |
| 1:40 | — | „Brak reakcji”, rezerwa spada o 8 pkt, stan „Przerwa teraz: reakcja za wolna albo jej brak” | „Brak reakcji to potwierdzony spadek czujności, niezależnie od tego, jak wyglądają oczy. Stan zostaje, dopóki kolejna próba nie wypadnie w normie.” |
| 1:55 | operator | przełącza na **Pielęgniarka** | „Ten sam system w szpitalu: przekaż pacjentów i zrób przerwę.” |
| 2:05 | operator | klika **Rozpocznij przerwę**. Stan „Przerwa trwa”, rezerwa rośnie | „Przerwa naprawdę odnawia rezerwę, a limit jest liczony dla tej osoby, nie dla zegara.” |
| 2:20 | narrator | slajd z dowodami | „Zamknięte oczy wykryliśmy w 5 z 5 nagrań, z jednym fałszywym alarmem w 48 minutach. Senność przy otwartych oczach pokazują dane publiczne: alfa rośnie u 11 z 11 osób, a model osobisty rozróżnia stany wyraźnie lepiej niż jeden dla wszystkich. Dlatego liczymy normy dla człowieka, nie dla zegara.” |

**Kiedy system sam prosi o reakcję:** tylko po spadku czujności (12–20 s po otwarciu oczu) i z harmonogramu co 20 min.
Rosnący wskaźnik sam w sobie już jej nie wywołuje (issue #14), więc w demo nie pojawi się przypadkowo. Gdy próba pojawi się sama, osoba w czepku reaguje normalnie, a narrator mówi „system sam sprawdza reakcję”. To dobry moment, nie błąd. Nie mówimy, że wskaźnik „zapowiada” spadek czujności: alfa przy otwartych oczach go nie zapowiada (notebook 06).

**Jeśli alarm nie przyjdzie po 15 s zamkniętych oczu:** osoba w czepku trzyma oczy zamknięte jeszcze 10 s. U dwóch osób
w naszych nagraniach alarm przychodził z przerwami. Jeśli dalej nic, przejdźcie na plan B.

## Plan awaryjny

**Kiedy przełączyć na B:** Board nie widzi czepka, baner przez ponad 20 s pokazuje „Brak wiarygodnego sygnału”
mimo poprawienia czepka, albo alarm nie przychodzi po 25 s zamkniętych oczu.

**Przebieg B** (komenda B, zmierzony 15.11 rano po zmianach z issues #11, #14 i po wyłączeniu wskaźnika wolnego z rezerwy; czasy od kliknięcia „Nowa zmiana”, kalibracja trwa ok. 62 s od startu serwera):

| Od „Nowej zmiany” | Co się dzieje | Co robi operator |
|---|---|---|
| przed kliknięciem (0–62 s od startu serwera) | kalibracja na nagraniu Filipa | narrator: „To nagranie Filipa z dzisiejszego dnia, przetwarzane tym samym kodem co na żywo.” |
| 0 s | „Możesz pracować”, rezerwa 100%, rezerwa spada ok. 29 pkt/h czasu zmiany | klika **Nowa zmiana** |
| ok. 70 s | „Przerwa teraz. Oczy zamknięte dłużej niż kilka sekund”, rezerwa ok. 74%, panel: „Najwięcej rezerwy ma Rudy” | narrator jak w scenariuszu na żywo od 1:20 |
| ok. 124 s | Filip otwiera oczy, „stop” znika, stan „Zaplanuj przerwę” | — |
| ok. 136 s | próba reakcji „Sprawdzenie po spadku czujności” | **nie reaguje**; po 3 s (ok. 140 s) „Przerwa teraz: reakcja za wolna albo jej brak”, rezerwa ok. 48% |
| ok. 190 s | Rudy i Adi dochodzą do „Zaplanuj przerwę” (ok. 50%) | koniec planu B |

Kalibrację planu B najlepiej zrobić w tle zawczasu: uruchomić komendę B razem z A i przełączyć kartę przeglądarki.
Wtedy „Nowa zmiana” na B daje zamknięcie oczu Filipa ok. 70 s później.

**Plan C:** nagrany film demo odtworzony z laptopa.

## Film demo (etap 1), ok. 2 min

Nagranie ekranu w 1080p (QuickTime albo OBS) i kamera telefonu na osobę w czepku, wklejona w rogu obrazu.
Nagrajcie jedno ujęcie na żywo i jedno na planie B, potem wybierzcie lepsze. Narracja z offu, napisy z kluczowymi zdaniami.

| Czas | Obraz | Narracja / napis |
|---|---|---|
| 0:00–0:15 | osoba w czepku zamyka oczy, baner zmienia się na „Przerwa teraz”, panel przełożonego wskazuje zmiennika | „Wachta zmienia plan pracy na podstawie EEG: gdy oczy zamykają się na dłużej niż kilka sekund, system każe zjechać i wskazuje zmiennika.” |
| 0:15–0:35 | slajd: problem | „Normy mierzą czas pracy, a nie człowieka.” Jedna liczba ze źródłem (z `rynek-*.md`) |
| 0:35–1:05 | „Nowa zmiana” w nocy, kafelki kontekstu, próba reakcji z szybką odpowiedzią | „Minuta kalibracji EEG, potem system śledzi alfę, mrugnięcia i reakcję. W nocy rezerwa spada szybciej.” |
| 1:05–1:30 | brak reakcji przy otwartych oczach, rezerwa spada, przełączenie na „Pielęgniarka”, przerwa | „Kamera widzi, czy oczy są otwarte. My sprawdzamy, czy człowiek jeszcze reaguje.” |
| 1:30–1:50 | wykres `trafnosc-na-nagraniach.png`, wykres z danych publicznych | „5 z 5 nagrań, jeden fałszywy alarm w 48 minutach. W danych publicznych alfa rośnie z sennością u 11 z 11 osób.” |
| 1:50–2:00 | zespół, nazwa, „co dalej” | „Następny krok: pilotaż, który sprawdzi, czy osobisty limit przewiduje spadki czujności lepiej niż norma czasu.” Źródła danych w napisach końcowych (CC BY wymaga podania) |

## Co mówimy, a czego nie

Na podstawie [`podstawy-naukowe.md`](podstawy-naukowe.md) §6 i [`jury-i-kryteria.md`](jury-i-kryteria.md) §3.

| Mówimy | Nie mówimy |
|---|---|
| „zmęczenie”, „czujność”, „reakcja” | „stres”, „wypalenie”, „przeciążenie”, „skupienie” |
| „zamknięte oczy wykryliśmy w 5 z 5 nagrań (4 osoby)” | „wykrywamy senność z trafnością X%” |
| „senność przy otwartych oczach pokazują dane publiczne” | że wykryliśmy ją na naszych nagraniach (nikt w nich nie był senny) |
| „brak reakcji tu symulujemy” | że próba w demo była prawdziwym spadkiem czujności |
| „HRV i EEG reagują na to samo, ale nie są zamienne” | „zegarek zastąpi EEG” |
| „parametry rezerwy to założenia” | że rezerwa jest zmierzona albo zwalidowana |

## Pytania, na które trzeba mieć odpowiedź

Pełna lista: [`jury-i-kryteria.md`](jury-i-kryteria.md) §4. Dwa nowe po zmianach z 14.11:

| Pytanie | Odpowiedź |
|---|---|
| Czym to się różni od kamery? | Kamera widzi zamknięte oczy. My dodatkowo odróżniamy zamknięcie oczu od wzrostu alfy przy mrugających oczach i sprawdzamy reakcję. Senności przy otwartych oczach na własnych danych jeszcze nie zmierzyliśmy (sesja T1: KSS 5, bez senności), więc tego nie twierdzimy. Alarm zmienia plan pracy i obsadę, a nie tylko piszczy |
| Jak często system przerywa próbą reakcji? | Tylko po spadku czujności (12–20 s po otwarciu oczu) i z harmonogramu co 20 min, nigdy z samego wzrostu alfy poniżej progu: sprawdziliśmy, że taki wzrost nie zapowiada lapsu (notebook 06, AUC 0,52), a w 15 minutach monotonii dałby 11 prób bez żadnego spadku czujności (issue #14). Odstęp 20 min to założenie |

## Próby (zadanie C3)

| Data, godz. | Wariant | Czy przeszło do końca | Co nie działało | Kto poprawia |
|---|---|---|---|---|
| | na żywo | | | |
| | plan B | | | |
