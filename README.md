# Heroes of the Brain — AI All In

Repozytorium drużyny na hackathon **Heroes of the Brain 2026** (kategoria: Adaptive Systems).

> **Status projektu: budujemy.** Kierunek: zmęczenie i czujność pracowników zmianowych mierzone na człowieku,
> a nie na zegarze (EEG kalibruje, zegarek pilnuje). Plan: [`docs/plan-projektu.md`](docs/plan-projektu.md),
> zadania: [`docs/zadania.md`](docs/zadania.md), decyzje: [`docs/decyzje.md`](docs/decyzje.md).

## Sprzęt

- BrainAccess MINI, 8 suchych elektrod
- Montaż ze starter packa: **F3, F4, C3, C4, P3, P4, O1, O2**
- Próbkowanie 250 Hz, dane w formacie MNE

## Struktura repozytorium

| Ścieżka | Co tu jest |
|---|---|
| `pomysly-adi/` | Pomysły i notatki Adiego (inspiracja, nic potwierdzonego) |
| `docs/` | Dokumentacja: decyzje, plan projektu, pomysły, zbiory danych, research rynku i konkurencji |
| `data/recordings/` | Nagrania testowe z BrainAccess MINI (za zgodą uczestników) |
| `data/analysis/` | Notebooki z analizą nagrań i porównaniem z danymi publicznymi |
| `src/wachta/` | Kod: pipeline sygnału, kalibracja na osobę, wskaźnik czujności i rezerwa |
| `tests/` | Testy (`pytest`) |
| `experiments/` | Skrypty analityczne, m.in. trafność pipeline'u na nagraniach |
| `AGENTS.md` | Zasady pracy w repo — obowiązują ludzi i agentów AI |
| `CONTRIBUTING.md` | Jak dokładać zmiany: gałęzie, commity, PR-y |

Instalacja, testy i uruchomienie: [`docs/uruchomienie.md`](docs/uruchomienie.md).

## Zasady w skrócie

1. Przeczytaj [`AGENTS.md`](AGENTS.md) zanim zaczniesz pracę.
2. Nie commitujemy na `main` — pracujemy na gałęziach i robimy PR-y (szczegóły w [`CONTRIBUTING.md`](CONTRIBUTING.md)).
3. **Nie commitujemy surowych nagrań EEG z prawdziwych osób** (wyjątek: nagrania zespołu w `data/recordings/` za zgodą nagranych osób, patrz `docs/decyzje.md`) **ani żadnych sekretów** (klucze API, tokeny).
4. Nazwy plików i folderów: małe litery, bez polskich znaków i spacji (`pomysly-adi`, nie `Pomysły Adi`).

## Zespół

Dopiszcie się tutaj:

- Adrian (Adi)
- …
