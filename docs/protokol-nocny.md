# Protokół nocnego punktu pomiarowego (zadanie C4)

Cel: pierwsze **własne** dane o senności przy otwartych oczach. Dziś mamy tylko zamknięte oczy na czterech nagraniach
i dane publiczne. Ten sam protokół w dzień (punkty `T*`) i w nocy (punkty `N*`) pozwala porównać u tej samej osoby
ocenę senności, test reakcji i wskaźnik EEG.

Czas na osobę: ok. 20 min. Najlepiej po północy, po dniu hackathonu. Kolejność: najpierw film demo i próby (C3), potem pomiar.

## Sprzęt

- Czepek BrainAccess i laptop z BrainAccess Board.
- Garmin Venu 2 z paskiem Garmin HRM sparowanym z zegarkiem (Ustawienia → Czujniki i akcesoria). Pasek zwilżony.
- Repo zaktualizowane, pakiet zainstalowany: `pip install -e ".[analysis]"`.

## Kroki

| Krok | Czas | Co robić |
|---|---|---|
| 1 | 1 min | Załóż pasek i czepek. W Board sprawdź, że sygnał płynie |
| 2 | — | Na zegarku uruchom aktywność (np. „Joga” albo „Inne”), żeby tętno z paska zapisywało się do pliku |
| 3 | 3 min | Uruchom narzędzie punktu pomiarowego (komenda niżej). Gdy poprosi, włącz nagrywanie w Board z nazwą zadania `<imie>-n1` i naciśnij Enter w tej samej chwili. Kroki: oczy otwarte, oczy zamknięte, liczenie, po 60 s |
| 4 | 10 min | **Monotonia** (narzędzie prowadzi dalej): siedź spokojnie, oczy otwarte, patrz w jeden punkt, bez telefonu i rozmowy. Wolno mrugać. Nie walcz z zamykaniem oczu, ale też go nie wywołuj |
| 5 | 1 min | Zatrzymaj nagrywanie w Board. Narzędzie pyta o KSS (1–9), wpisz szczerze. U Wojtka też odczyty z zegarka |
| 6 | 3 min | Test reakcji PVT-B w przeglądarce (komenda niżej) |
| 7 | — | Zatrzymaj aktywność na zegarku i zsynchronizuj z Garmin Connect |

Komendy (zamiast `wojtek` i `N1` wpisz swoje imię i punkt; drugi nocny punkt to `N2`, dzienny `T0`/`T1`):

```bash
python -m wachta.session --person wojtek --checkpoint N1 --monotony-min 10
```

```bash
python -m wachta.pvt --person wojtek --checkpoint N1
```

Narzędzie zapisze adnotacje obok nagrania (z blokiem `monotony`) i wiersz w `data/recordings/checkpoints.csv`,
a test reakcji wiersz w `data/recordings/pvt.csv`.

**Plik z zegarka:** w Garmin Connect w przeglądarce otwórz aktywność, menu (koło zębate) → „Eksportuj oryginał”.
W pobranym archiwum jest plik `.fit`. **Nie wrzucaj go do repo** (jest w `.gitignore`), trzymaj lokalnie.

## Analiza

```bash
python experiments/analyze-night-checkpoint.py --fit wojtek-n1=~/Downloads/12345678_ACTIVITY.fit --figure docs/img/noc-vs-dzien.png
```

Skrypt bierze każde nagranie z blokiem `monotony` i liczy:

- wskaźnik czujności (wyrazistość alfy, z-score względem własnej kalibracji z bloku „oczy otwarte”) w pierwszych
  i ostatnich 2 minutach monotonii oraz jego zmianę;
- odsetek okien nad progiem próby reakcji, spadki czujności i ich rodzaj (oczy otwarte / zamknięte), mrugnięcia na minutę;
- KSS i wynik testu reakcji (lapsy, mediana czasu reakcji);
- z pliku FIT tętno w spoczynku i w monotonii, a jeśli plik zawiera odstępy uderzenie-uderzenie, także RMSSD;
- kontrolę jakości: czy blok „oczy zamknięte” został wykryty.

Plik FIT jest opcjonalny. Jeśli nie zawiera odstępów R–R (zależy od ustawień zegarka), skrypt poda tylko tętno.
Odczyt prawdziwego pliku z Venu 2 nie był jeszcze sprawdzony: przy pierwszym uruchomieniu zwróćcie uwagę na komunikaty.

## Co z tego wolno powiedzieć

- Jeśli w nocy rośnie KSS, lapsy w teście reakcji **i** alfa w monotonii przy mrugających oczach: „u naszych osób wskaźnik EEG
  rośnie razem z sennością i wolniejszymi reakcjami, przy otwartych oczach”. Z liczbą osób, bez statystyki.
- Jeśli alfa nie rośnie mimo wyższego KSS: to też wynik. Mówimy, że na tak krótkiej próbie sygnał był za słaby, i że dlatego
  produkt opiera się na osobistym profilu i teście reakcji, a nie na samym EEG.
- Tętno i RMSSD z paska pokazujemy jako osobny sygnał. Nie twierdzimy, że zastępują EEG (`podstawy-naukowe.md` §6).
- Kilka osób to studium przypadku, nie walidacja.
