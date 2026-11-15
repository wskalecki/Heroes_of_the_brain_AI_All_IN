# Jury, kryteria oceny i opakowanie use case'u

Stan na 14.11.2026. Fakty o jury i regulaminie pochodzą ze stron publicznych (linki na dole). Fragmenty oznaczone
**„wniosek”** to interpretacja, nie informacja ze źródła.

## 1. Jak będziemy oceniani (regulamin, §8)

Każdą kategorię ocenia **osobna, 3-osobowa grupa jurorów** (sponsorzy i Politechnika Wrocławska). Ocena ma dwa etapy.

| Etap | Co oceniają | Punkty |
|---|---|---|
| 1. Ocena wstępna | **nadesłana prezentacja i film demo** (bez nas na scenie). Do finału przechodzi maksymalnie 5 zespołów z kategorii | maks. 50 |
| 2. Finał | prezentacja na scenie i pytania jury | maks. 20 |

Kryteria etapu 1:

| Kryterium | Punkty |
|---|---|
| **Zgodność z tematem** | **1–20** |
| Innowacyjność | 1–10 |
| Użyteczność | 1–10 |
| Jakość implementacji | 1–10 |

Etap 2: odpowiedzi na pytania (1–10) i jakość prezentacji (1–10).

Co z tego wynika (**wniosek**):

- **40% punktów etapu 1 to zgodność z tematem.** Temat kategorii „Systemy adaptacyjne” brzmi: *oprogramowanie, które
  zmienia swoje zachowanie w oparciu o EEG **i inne sygnały biologiczne**, np. interfejsy, samouczki, muzykę czy oświetlenie
  dopasowujące się do stanu użytkownika*. Pomiar sam w sobie nie wystarczy. Musi być widać **adaptację** (system coś zmienia)
  oraz **drugi sygnał biologiczny** obok EEG (u nas tętno i zmienność rytmu serca z zegarka).
- **Etap 1 nie widzi demo na żywo.** Film demo i prezentacja muszą bronić się same. Film musi pokazać pętlę od początku do końca:
  sygnał, stan, zmiana zachowania systemu.
- Projekt trzeba **zdeponować w repozytorium wskazanym przez organizatorów** przed oceną (§10). Autorskie prawa majątkowe
  zostają przy uczestnikach, organizatorzy dostają niewyłączną licencję na promocję. To nie blokuje komercjalizacji.
- Regulamin dopuszcza biblioteki open source, o ile ich licencje pozwalają na takie użycie. Warto sprawdzić licencje
  zależności (`pyproject.toml`) i licencje zbiorów w notebookach (CC BY wymaga podania źródła). Przegląd: [`licencje.md`](licencje.md).

**Do sprawdzenia przez zespół.** Plan projektu liczy „do oddania mniej niż 12 h” od godz. 14:30, czyli do ok. 2:30 w nocy.
Strona hackathonu podaje inny harmonogram: **koniec prac w niedzielę 10:30**, ocena wstępna 10:30–12:30, finał 13:00–15:00,
a regulamin mówi o zakończeniu wydarzenia o 16:00. Jeśli 2:30 to wewnętrzny bufor, ustalcie to wprost. Jeśli nie, mamy
ok. 8 godzin więcej, niż zakłada plan, na film demo i prezentację.

## 2. Jury kategorii „Systemy adaptacyjne”

| Juror | Kim jest (źródła publiczne) | Co to mówi o oczekiwaniach (**wniosek**) |
|---|---|---|
| **Katarzyna Białas**, MSc Eng, WUST | Doktorantka neuroinformatyki na Wydziale Informatyki i Telekomunikacji PWr (Katedra Informatyki Stosowanej, Pracownia Cyberbezpieczeństwa i Neuroinformatyki), opiekunka koła KN Neuron, ok. 10 lat pracy jako inżynier oprogramowania. Publikacje: uproszczone BCI (mało elektrod) do rozpoznawania osób i uwierzytelniania (IEEE Trans. Human-Machine Systems 2022; ECAI 2025), BCI w nauce języków, **analiza widma metodą Welcha** i uczenie maszynowe (Applied Sciences 2026), aktywność wolnofalowa EEG jako biomarker ryzyka otępienia (ICDM Workshops 2025). Była też jurorką poprzedniej edycji | Zna sprzęt z niewielką liczbą kanałów i prosty pipeline widmowy, czyli to, co robimy. Doceni **rygor**: uczciwą walidację, jawne ograniczenia, powtarzalność (notebooki, testy). Zaszkodzi jej przesadzona obietnica i „czarna skrzynka” |
| **Paweł Dzikiewicz**, MSc, WUST | Prezes koła KN Neuron w 2024/2025 i **główny koordynator poprzedniego Heroes of the Brain** (2024: 132 uczestników, 32 zespoły). Koło prowadzi projekty z adaptacją do stanu użytkownika, m.in. *Bore No More* (framework do Unity, klasyfikatory nudy, flow i zdenerwowania, dopasowujący trudność gry) i *NeuroSniper* (koncentracja i relaksacja sterują grą). Innych informacji o nim nie znalazłem | Zna temat „system zmienia się pod stan” z praktyki i widział wiele dem. Wyróżni nas **dojrzałość i cel poza grą** oraz **demo, które działa**. Liczy się czytelność, bo organizator ocenia dużo projektów |
| **Patryk Wekwejt**, Co-founder & COO @ LinkLane (YC W27) | Współzałożyciel i COO LinkLane, startupu z agentami AI do brokerage frachtu (YC, batch Winter 2027, San Francisco, 2 osoby). Harvard College '26. Strona YC podaje „wcześniej naukowiec”. Wyniki wyszukiwania wskazują na badania z neuronauki (zachowanie zwierząt, publikacja z 2023 z afiliacją Instytutu Nenckiego), **niezweryfikowane** | Patrzy jak **founder i naukowiec**: kto za to zapłaci, jak to skalować, czy dane stoją za tezą. **Transport drogowy to jego branża** (LinkLane: „prawie bilion dolarów” rynku przewozów). Przypadek kierowców zawodowych jest dla niego rozpoznawalny, ale i łatwo wyłapie puste hasła |

Pozostałych siedmiu jurorów ze strony (BrainAccess, g.tec, Cortivision, WUST) ocenia inne kategorie. Mogą być na sali.
**Wniosek:** sponsorzy sprzętu chętnie usłyszą, że nasz projekt **otwiera nowy rynek dla BrainAccess** (zastosowania
operatorskie), a nie konkuruje z nim.

## 3. Jak dopasować pitch do kryteriów

| Kryterium | Co pokazać | Czym to mamy poparte |
|---|---|---|
| **Zgodność z tematem (20)** | Pierwszy slajd i pierwsze 15 s filmu: *„System zmienia plan pracy i przerw na podstawie EEG i tętna”*. Pętla: sygnał → stan → **zmiana zachowania** (rekomendacja przerwy, zmiana obsady). Dwa sygnały: EEG i serce | A1–A3 (pipeline, dashboard), notebook 05 (EEG a serce), PVT-B i znaczniki w `session.py` |
| **Innowacyjność (10)** | „EEG kalibruje, zegarek pilnuje” i **limit zmęczenia liczony dla osoby, nie dla zegara**. Wyraźna różnica względem SmartCap (EEG w czapce przez cały dzień, tylko alarm) | `docs/rynek-eeg-wearables.md`, wynik B2: model osobisty 81% kontra wspólny 66–72% |
| **Użyteczność (10)** | Jeden konkretny odbiorca i koszt problemu w pieniądzach, ze źródłem | `docs/rynek-wielkosc-i-kierunek.md` |
| **Jakość implementacji (10)** | Działające demo, tryb odtwarzania jako plan B, 45 testów, powtarzalne notebooki, uczciwe liczby | `docs/trafnosc-na-nagraniach.md`, notebooki 01–05 |
| **Pytania (10)** | Przećwiczone odpowiedzi, patrz niżej | wyniki B1–B3 |

Zasady narracji (**wniosek**):

1. **Mówcie o tym, czego nie umiecie, zanim zapyta jury.** Z tą publicznością to działa na waszą korzyść (Białas: rygor,
   Wekwejt: due diligence). Na slajdzie „zweryfikowane kontra założone” umieśćcie konkretne liczby.
2. **Nie obiecujcie wykrywania mikrosnu.** Mamy wykrywanie zamkniętych oczu (4 z 4 osób) i wskaźnik czujności rosnący z sennością
   w danych publicznych (AUC 0,75). To dwie różne rzeczy i trzeba je rozdzielić.
3. **Jedno zdanie o prawie.** Zmęczenie to stan fizyczny, a nie emocja (AI Act, motyw 18). Surowe dane zostają u pracownika,
   przełożony widzi tylko gotowość. Nie używajcie słów stres, wypalenie, przeciążenie.

## 4. Pytania, których się spodziewać, i uczciwe odpowiedzi

| Pytanie | Odpowiedź oparta na naszych wynikach |
|---|---|
| Czy to wykrywa senność, czy tylko zamknięte oczy? | Na naszych nagraniach potwierdziliśmy zamknięte oczy (5 z 5 nagrań, 4 osoby, mediana opóźnienia 9 s, 1 fałszywy alarm w 48 min; próg dobrany na tych samych nagraniach). Senność sprawdziliśmy na zbiorze publicznym: alfa potyliczna rośnie u 11/11 osób, AUC 0,75 (0,52–0,91). Własnych nagrań sennych dopiero zbieramy |
| Cztery osoby to za mało | Zgoda. To sprawdzenie mechanizmu. Wnioski statystyczne dają dane publiczne (11 i 16 osób) i trzy punkty pomiarowe zespołu |
| Czemu nie kamera? | Kamera widzi skutki (oczy, głowa), EEG i tętno widzą stan organizmu. Nie twierdzimy, że wygramy z kamerą w trafności. Nasza różnica to **osobisty limit** i adaptacja planu pracy |
| Czemu serce, skoro korelacja z EEG jest słaba? | Dlatego, że to **inny sygnał**. To inny sygnał, ale uczciwie: w 10-minutowym teście czujności RMSSD i szybkość reakcji spadają razem (r = 0,18, 22 z 29 osób), głównie dlatego, że obie zmieniają się z czasem zadania; ponad czas zadania RMSSD nie dodaje informacji (notebook 10). Serce traktujemy jako dodatkowy kontekst i miarę pewności, nie jako dowód czujności. EKG w laboratorium to nie zegarek |
| Co z suchymi elektrodami i ruchem? | Odrzucamy 16–21% okien (artefakty). System ma stan „brak wiarygodnego sygnału” i nie zgaduje. Theta czołowa nie nadaje się przy referencji Fp1, więc jej nie używamy |
| Skąd 60 s kalibracji i czy to wystarczy? | Do zamkniętych oczu tak. Do rozróżniania senności sama kalibracja prawie nie pomaga (B2), dopiero model uczony na danych tej osoby (ok. 1 min na klasę daje 81% w laboratorium). Dlatego planujemy sesje osobiste |
| Prywatność i prawo? | Przetwarzanie lokalne, na zewnątrz tylko wskaźnik gotowości, stan fizyczny, nie emocja. Konsultacja prawna (RODO art. 9) po hackathonie |
| Dlaczego próba reakcji, a nie sama alfa? | Sprawdziliśmy: alfa przy otwartych oczach nie przewiduje lapsów w kolejnej minucie (AUC 0,52, 29 osób COG-BCI, notebook 06). Poprzednia reakcja przewiduje lepiej, a próba jest bezpośrednią miarą czujności. EEG mówi nam, co dzieje się teraz (oczy zamknięte, fala alfy), próba sprawdza, czy człowiek reaguje |
| Czemu rezerwa spada, skoro nic nie mierzycie? | Rezerwa łączy założenie kontekstowe (czas zadania, pora doby; parametry oznaczone jako założone) z częścią mierzoną (zdarzenia ostre, wyniki prób). Dziś w demo przeważa założenie, i mówimy to wprost; rozbicie na dashboardzie to zadanie w toku (issue #12). Rezerwy nie przedstawiamy jako pomiaru |
| Czy to działa u każdego? | Nie, i dlatego jest test „marker działa u tej osoby”: skok wyrazistości alfy po zamknięciu oczu (R_z), progi wstępne tak ≥ 2,5, słabo 1,5–2,5, nie < 1,5. W danych publicznych 37% osób „tak”, 26% „słabo”, 37% „nie” (27 osób, elektrody żelowe). Werdykt dotyczy sesji: tydzień później ten sam wynik ma 44–56% osób, więc liczymy go przy każdym założeniu czepka (notebook 07) |
| Co zrobi system, gdy marker u mnie nie działa? | Powie to wprost i oprze się na próbach reakcji i kontekście, zamiast udawać wykrywanie. Dolny próg („nie”) nie wystąpił u nikogo z zespołu, więc na suchych elektrodach jest nieprzetestowany |
| Co jest zwalidowane, a co założone? | Zwalidowane: wykrywanie zamkniętych oczu na naszych nagraniach, alfa rośnie ze zmęczeniem w danych publicznych, model osobisty lepszy od wspólnego, 0 fałszywych alarmów w 15 min ciszy (jedna osoba). Obalone: alfa nie ostrzega przed lapsem, HRV nie mierzy czujności ponad czas zadania. Założone: parametry rezerwy, odstępy prób, osobisty limit jako lepszy od normy (do pilotażu). Slajd 8 w `pitch.md` |

## 5. Use case biznesowy: wersje i jak je opakować

Dwa warianty ze wspólnym rdzeniem technicznym (decyzja zespołu: [`decyzje.md`](decyzje.md)).

**Wariant A: pracownicy zmianowi, kierowcy zawodowi (rekomendacja pod to jury).**

- *Problem:* limity czasu pracy kierowców są stałe dla wszystkich, a zmęczenie nie. W UE obowiązują limity czasu jazdy
  i przerw (rozporządzenie 561/2006), w USA limity godzin służby (FMCSA). **Liczby do sprawdzenia przed slajdem**, tu podaję
  tylko kierunek.
- *Produkt:* „rezerwa czujności” dla konkretnej osoby oraz plan przerw i obsady liczony dla niej. EEG kalibruje wzorzec
  na krótkiej sesji, zegarek pilnuje na co dzień.
- *Dlaczego pasuje do jury:* Wekwejt zna branżę transportową i łańcuch dostaw. **Wniosek:** można mówić o *przydziale ładunków i zmian
  z uwzględnieniem gotowości kierowcy* jako warstwie nad dispatchem. Nie obiecujemy integracji, tylko kierunek.
- *Konkurencja:* SmartCap (czapka, kopalnie, transport), kamery w kabinie. Różnica: osobisty limit, EEG tylko do kalibracji.

**Wariant B: dyżurni IT i SOC** (research w `rynek-wielkosc-i-kierunek.md`). Ból policzalny (9 000 USD za minutę przestoju),
brak konkurencji z EEG, integracje przez API (PagerDuty, Grafana). Szybszy pilotaż, ale dalej od świata BCI,
który zna reszta jury.

**Jak to sprzedać (struktura 90 sekund):**

1. *Hak:* „Normy mierzą czas pracy, nie człowieka. Dwie osoby po tej samej zmianie mają inną rezerwę czujności.”
2. *Dowód problemu:* jedna liczba ze źródłem (koszt zmęczenia albo przestoju).
3. *Rozwiązanie w jednym zdaniu:* „EEG kalibruje, zegarek pilnuje, system zmienia plan przerw.”
4. *Demo:* osoba zamyka oczy, wskaźnik reaguje, dashboard zmienia rekomendację i panel przełożonego.
5. *Dowody i granice:* wykresy z `docs/img/` oraz slajd „zweryfikowane kontra założone”.
6. *Model i pilotaż:* licencja za stanowisko, pilotaż na jednej zmianie z pomiarem przed i po. **Wszystkie liczby rynkowe jako
   założenia z podanym źródłem.**

## Źródła

- Jury i kategorie: [heroesofthebrain.pwr.edu.pl/jury](https://heroesofthebrain.pwr.edu.pl/jury), [strona główna](https://heroesofthebrain.pwr.edu.pl/), [regulamin](https://heroesofthebrain.pwr.edu.pl/regulamin)
- Katarzyna Białas: [strona na wit.pwr.edu.pl](https://wit.pwr.edu.pl/wydzial/struktura-organizacyjna/pracownicy/katarzyna-bialas), [strona osobista](https://www.katarzynabialas.com)
- Poprzednia edycja i skład jury: [Human Brainwave Hackathon (WIT PWr, 2024)](https://wit.pwr.edu.pl/en/news/human-brainwave-hackathon-244.html)
- Koło Neuron, zarządy i projekty: [knneuron.pwr.edu.pl](https://knneuron.pwr.edu.pl/)
- Patryk Wekwejt i LinkLane: [LinkLane w katalogu Y Combinator](https://www.ycombinator.com/companies/linklane). Informacje o badaniach pochodzą z wyników wyszukiwania
  (Google Scholar, ResearchGate), których nie otwierałem bezpośrednio, więc potraktujcie je jako niezweryfikowane.
