# AGENTS.md — zasady pracy w tym repozytorium

Ten plik czytają zarówno ludzie, jak i agenci AI (Claude Code, Copilot itp.).
Jeśli pracujesz w tym repo — te zasady Cię obowiązują.

## Kontekst projektu

- Hackathon **Heroes of the Brain 2026**, kategoria Adaptive Systems.
- Sprzęt: BrainAccess MINI, 8 suchych elektrod (F3, F4, C3, C4, P3, P4, O1, O2), 250 Hz, dane w MNE.
- **Kierunek jest ustalony:** zmęczenie i czujność mierzone na człowieku, nie na zegarze.
  Decyzja: `docs/decyzje.md`, plan: `docs/plan-projektu.md`, podział zadań: `docs/zadania.md`.
- Buduj według planu i zadań, nie według luźnych pomysłów.

## Język

- Dokumentacja, notatki i komunikacja w repo: **po polsku**.
- Kod, nazwy zmiennych, funkcji, plików i commity: **po angielsku** (łatwiej o spójność i narzędzia).

## Struktura i porządek

- Nazwy plików i folderów: małe litery, myślniki zamiast spacji, bez polskich znaków
  (`docs/plan-projektu.md`, `signal-processing.py`).
- Nowe pomysły i notatki osobiste: każdy ma swój folder `pomysly-<imie>/`.
- Kod projektu (gdy powstanie): `src/`, eksperymenty i prototypy: `experiments/`,
  dokumentacja: `docs/`. Nie twórz tych folderów "na zapas" — dopiero gdy jest co do nich włożyć.
- Jeden plik = jedna odpowiedzialność. Nie trzymamy w repo plików "roboczych kopii"
  typu `final_v2_poprawione.md`.

## Git

- Nie commituj bezpośrednio na `main`. Pracuj na gałęzi i otwórz PR (szczegóły: `CONTRIBUTING.md`).
- Commity małe i opisowe, w trybie rozkazującym po angielsku: `Add alpha band power calculation`.
- Nie commituj: plików generowanych, cache'ów, `venv/`, notebooków z wielkimi outputami
  (wyczyść outputy przed commitem), dużych plików binarnych.

## Dane i bezpieczeństwo — zasady twarde

1. **Surowe nagrania EEG prawdziwych osób nie trafiają do repo.** To dane biometryczne.
   **Wyjątek:** nagrania członków zespołu w `data/recordings/` (tylko `.fif` z adnotacjami), za wyraźną zgodą nagranej osoby, zgodnie z `docs/decyzje.md`.
   Do testów używamy danych syntetycznych albo krótkich, anonimowych próbek za zgodą zespołu.
2. **Żadnych sekretów w repo**: kluczy API, tokenów, haseł, adresów prywatnych.
   Konfiguracja przez zmienne środowiskowe i plik `.env` (który jest w `.gitignore`).
3. Dane uczestników demo (imiona, nagrania) — tylko za ich wyraźną zgodą.

## Zasady dla agentów AI

- Zanim coś zmienisz, przeczytaj `README.md` i ten plik.
- Zanim zaczniesz pracę, przeczytaj `docs/plan-projektu.md` i `docs/zadania.md`. Bierz zadania tylko ze strumienia
  osoby, z którą pracujesz, trzymaj się plików tego strumienia i zmieniaj status zadania w tym samym PR co pracę.
- Nie refaktoruj i nie "porządkuj" cudzych plików bez wyraźnej prośby.
- Nie usuwaj niczyich notatek ani pomysłów — nawet jeśli wyglądają na nieaktualne.
- Nie twórz PR-ów, nie pushuj na `main` i nie zmieniaj ustawień repo bez wyraźnego polecenia.
- Duże zmiany (nowa struktura folderów, nowe zależności) — najpierw zaproponuj, potem rób.
- Trzymaj się języka: dokumentacja po polsku, kod i commity po angielsku.

## Decyzje zespołowe

Decyzje o kierunku projektu (wybór pomysłu, stack technologiczny, podział pracy)
zapadają wspólnie i są zapisywane w `docs/decyzje.md`.
Punkty otwarte są wypisane przy każdej decyzji. Czego tam nie ma, to nie jest ustalone.
