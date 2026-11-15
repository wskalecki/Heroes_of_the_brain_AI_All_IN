# Kryteria oceny oraz pytania i odpowiedzi

Kryteria pochodzą z regulaminu hackathonu (§8). Odpowiedzi opierają się na wynikach z `docs/` i notebooków w `data/analysis/`.

## 1. Kryteria oceny (regulamin, §8)

| Etap | Co jest oceniane | Punkty |
|---|---|---|
| 1. Ocena wstępna | nadesłana prezentacja i film demo | maks. 50 |
| 2. Finał | prezentacja na scenie i pytania | maks. 20 |

Etap 1: zgodność z tematem (1–20), innowacyjność (1–10), użyteczność (1–10), jakość implementacji (1–10).
Etap 2: odpowiedzi na pytania (1–10) i jakość prezentacji (1–10).

Temat kategorii „Systemy adaptacyjne”: oprogramowanie, które zmienia swoje zachowanie w oparciu o EEG i inne sygnały biologiczne.
Jak Wachta to realizuje: [`pitch.md`](pitch.md), slajd 5.

## 2. Pytania i uczciwe odpowiedzi

| Pytanie | Odpowiedź oparta na naszych wynikach |
|---|---|
| Czy to wykrywa senność, czy tylko zamknięte oczy? | Na naszych nagraniach potwierdziliśmy zamknięte oczy (5 z 5 nagrań, 4 osoby, mediana opóźnienia 9 s, 1 fałszywy alarm w 48 min; próg dobrany na tych samych nagraniach). Senność sprawdziliśmy na zbiorze publicznym: alfa potyliczna rośnie u 11/11 osób, AUC 0,75 (0,52–0,91). Własnych nagrań sennych dopiero zbieramy |
| Cztery osoby to za mało | Zgoda. To sprawdzenie mechanizmu. Wnioski statystyczne dają dane publiczne (11 i 16 osób) i trzy punkty pomiarowe zespołu |
| Czemu nie kamera? | Kamera widzi skutki (oczy, głowa), EEG i tętno widzą stan organizmu. Nie twierdzimy, że wygramy z kamerą w trafności. Nasza różnica to **osobisty limit** i adaptacja planu pracy |
| Czemu serce, skoro korelacja z EEG jest słaba? | Dlatego, że to **inny sygnał**. To inny sygnał, ale uczciwie: w 10-minutowym teście czujności RMSSD i szybkość reakcji spadają razem (r = 0,18, 22 z 29 osób), głównie dlatego, że obie zmieniają się z czasem zadania; ponad czas zadania RMSSD nie dodaje informacji (notebook 10). Serce traktujemy jako dodatkowy kontekst i miarę pewności, nie jako dowód czujności. EKG w laboratorium to nie zegarek |
| Co z suchymi elektrodami i ruchem? | Odrzucamy od 0,7% do 15% okien zależnie od osoby i warunków (artefakty; 0,7% w cichej sesji T1). System ma stan „brak wiarygodnego sygnału” i nie zgaduje. Theta czołowa nie nadaje się przy referencji Fp1, więc jej nie używamy |
| Skąd 60 s kalibracji i czy to wystarczy? | Do zamkniętych oczu tak. Do rozróżniania senności sama kalibracja prawie nie pomaga (B2), dopiero model uczony na danych tej osoby (ok. 1 min na klasę daje 81% w laboratorium). Dlatego planujemy sesje osobiste |
| Prywatność i prawo? | Przetwarzanie lokalne, na zewnątrz tylko wskaźnik gotowości, stan fizyczny, nie emocja. Konsultacja prawna (RODO art. 9) po hackathonie |
| Dlaczego próba reakcji, a nie sama alfa? | Sprawdziliśmy: alfa przy otwartych oczach nie przewiduje lapsów w kolejnej minucie (AUC 0,52 na 20 osobach z co najmniej 3 lapsami, z 29 w COG-BCI; notebook 06). Poprzednia reakcja przewiduje lepiej, a próba jest bezpośrednią miarą czujności. EEG mówi nam, co dzieje się teraz (oczy zamknięte, fala alfy), próba sprawdza, czy człowiek reaguje |
| Czemu rezerwa spada, skoro nic nie mierzycie? | Rezerwa łączy założenie kontekstowe (czas zadania, pora doby; parametry oznaczone jako założone) z częścią mierzoną (zdarzenia ostre, wyniki prób). Dziś w demo przeważa założenie, i mówimy to wprost; rozbicie na dashboardzie to zadanie w toku (issue #12). Rezerwy nie przedstawiamy jako pomiaru |
| Czy to działa u każdego? | Nie, i dlatego jest test „marker działa u tej osoby”: skok wyrazistości alfy po zamknięciu oczu (R_z), progi wstępne tak ≥ 2,5, słabo 1,5–2,5, nie < 1,5. W danych publicznych 37% osób „tak”, 26% „słabo”, 37% „nie” (27 osób, elektrody żelowe). Werdykt dotyczy sesji: tydzień później ten sam wynik ma 44–56% osób, więc liczymy go przy każdym założeniu czepka (notebook 07) |
| Co zrobi system, gdy marker u mnie nie działa? | Powie to wprost i oprze się na próbach reakcji i kontekście, zamiast udawać wykrywanie. Dolny próg („nie”) nie wystąpił u nikogo z zespołu, więc na suchych elektrodach jest nieprzetestowany |
| Co jest zwalidowane, a co założone? | Zwalidowane: wykrywanie zamkniętych oczu na naszych nagraniach, alfa rośnie ze zmęczeniem w danych publicznych, model osobisty lepszy od wspólnego, 0 fałszywych alarmów w 15 min ciszy (jedna osoba). Obalone: alfa nie ostrzega przed lapsem, HRV nie mierzy czujności ponad czas zadania. Założone: parametry rezerwy, odstępy prób, osobisty limit jako lepszy od normy (do pilotażu). Slajd 8 w `pitch.md` |

## Źródła

- Regulamin i kategorie: [heroesofthebrain.pwr.edu.pl](https://heroesofthebrain.pwr.edu.pl/)
