# Jak pracujemy w tym repo

Krótko i praktycznie — tak, żeby przy większej liczbie osób nie zrobił się bałagan.

## Przepływ pracy

1. **Zaktualizuj lokalne repo**: `git pull origin main` (gdy `main` już istnieje).
2. **Załóż gałąź** od `main`:
   - nowa funkcja / pomysł: `feat/<krotki-opis>` (np. `feat/alpha-detector`)
   - poprawka: `fix/<krotki-opis>`
   - notatki / dokumentacja: `docs/<krotki-opis>`
3. **Commituj często, małymi krokami.** Komunikat po angielsku, w trybie rozkazującym,
   mówiący *co* i *po co*: `Add 2s sliding window for band power`.
4. **Wypchnij gałąź i otwórz PR.** W opisie: co się zmienia i jak to sprawdzić.
5. **Review:** przynajmniej jedna osoba z zespołu zerka na PR przed merge.
   Na hackathonie wystarczy szybkie "LGTM" — ale ktoś musi zerknąć.
6. **Merge do `main`** robi autor po akceptacji. Gałąź po merge kasujemy.

## Czego nie robimy

- Nie commitujemy bezpośrednio na `main`.
- Nie robimy `git push --force` na wspólne gałęzie.
- Nie merge'ujemy własnego PR-a bez niczyjego spojrzenia (wyjątek: literówki w docs).
- Nie trzymamy gałęzi tygodniami — im krótsza żywotność gałęzi, tym mniej konfliktów.

## Konflikty i problemy

- Konflikt przy merge? Rozwiązuje autor gałęzi, w razie wątpliwości pyta na czacie zespołu.
- Coś zepsuło `main`? Mówimy od razu, naprawiamy wspólnie — nikt nie "naprawia po cichu".

## Pomysły i notatki

- Osobiste pomysły wrzucaj do swojego folderu `pomysly-<imie>/` — tam masz pełną swobodę
  i nikt nie będzie tego review'ował.
- Gdy pomysł dojrzeje do dyskusji zespołowej, otwórz Issue albo wrzuć go na spotkanie.
