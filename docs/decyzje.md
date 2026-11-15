# Decyzje zespołu

Decyzje o kierunku projektu, stacku i podziale pracy. Najnowsze na górze.
Każdy wpis: data, co ustaliliśmy, dlaczego, kto zgłosił i jaki ma status.

## 2026-11-14 — Kierunek: zmęczenie mierzone na człowieku, nie na zegarze

**Status:** zgłoszone przez Wojtka w imieniu zespołu. Pozostali potwierdzają przy przeglądzie PR.

**Decyzja.** Budujemy oprogramowanie, które z sygnałów człowieka ocenia zmęczenie i mówi, kiedy konkretna osoba
powinna przerwać pracę. Przykładowi odbiorcy: kierowca zawodowy, pielęgniarka, lekarz. Najpierw z EEG,
docelowo z tanich urządzeń noszonych (zegarek), żeby dało się to wdrożyć bez drogiej aparatury.

**Dlaczego.**
- Normy BHP opierają się dziś na czasie pracy, a nie na stanie osoby. Chcemy, żeby limit był liczony dla konkretnego
  człowieka: jedna osoba powinna skończyć po 6 godzinach, inna może bezpiecznie pracować dłużej.
- Wykrywanie senności z alfy potylicznej działa na naszym sprzęcie u wszystkich czterech osób (`data/analysis/`).
- Zmęczenie i senność to stan fizyczny, którego wykrywanie w celach bezpieczeństwa jest zgodne z AI Act
  ([`rynek-wielkosc-i-kierunek.md`](rynek-wielkosc-i-kierunek.md) §3).

**Co to zmienia.**
- Cel produktu to **zmęczenie i spadek czujności**. Nie obiecujemy wykrywania przeciążenia poznawczego:
  reguła nie zadziałała na naszych nagraniach, a prawnie to szara strefa.
- Nazwa robocza zostaje: Wachta.
- Wcześniejszy wariant (dyżurni IT, „AI oddaje ster”) korzysta z tej samej techniki i zostaje jako alternatywny scenariusz pitchu.
- Plan pracy: [`plan-projektu.md`](plan-projektu.md).

**Punkty otwarte.**
1. **Segment wejścia.** Research rynku rekomendował IT ops, a kierunek powyżej to pracownicy zmianowi (transport, ochrona zdrowia).
   Trzeba wybrać jeden na pitch i pokazać różnicę względem SmartCap.
2. **Nazwa** produktu na slajdach.
3. **Kolejne nagrania.** Propozycja: tylko `.fif` z adnotacjami, bez kopii CSV, w `data/recordings/`, zawsze za zgodą nagrywanej osoby.
4. **Spójność zasad.** `README.md` i `AGENTS.md` mówią, że surowych nagrań EEG nie commitujemy, a nagrania zespołu są w repo za zgodą.
   Zasadę trzeba ujednolicić.
5. **Role** Filipa i Rudego z planu to propozycja.

## 2026-11-14 — Nagrania testowe zespołu w repo

**Status:** przyjęte. Zgodę czterech nagranych osób potwierdził Wojtek.

**Decyzja.** Cztery nagrania testowe z BrainAccess MINI (Adi, Filip, Rudy, Wojtek) są w `data/recordings/`
razem z adnotacjami protokołu. W `.gitignore` jest wyjątek dla plików `.fif` w tym folderze.

**Dlaczego.** Bez własnych nagrań nie da się sprawdzić pipeline'u na naszym sprzęcie, a dane publiczne
pochodzą z elektrod żelowych i innych montaży.

## 2026-11-15 — Licencja repozytorium: MIT

**Status:** przyjęte przez Adriana; do potwierdzenia przez resztę zespołu (decyzje o stosie zapadają wspólnie).

**Decyzja.** Kod i dokumentacja repozytorium są na licencji MIT (plik `LICENSE`, właściciel praw: „AI All In”).
Licencja **nie obejmuje** nagrań EEG w `data/recordings/`: to dane biometryczne członków zespołu, udostępnione w repo
wyłącznie na potrzeby projektu, za zgodą nagranych osób (patrz wyżej). Nie wolno ich dalej rozpowszechniać na podstawie MIT.

**Dlaczego.** MIT jest permisywna, zgodna z licencjami naszych zależności (BSD, MIT, PSF) i z regulaminem hackathonu
(prawa do projektu zostają przy uczestnikach), a nie blokuje komercjalizacji.

**Punkty otwarte.**
1. Czy repo ma być publiczne po hackathonie. Jeśli tak, trzeba ponownie potwierdzić zgodę nagranych osób albo usunąć nagrania z historii.
2. `brainaccess-board` (opcja `live`) jest własnościowy (PyPI: Proprietary). Nie dołączamy go do repo; trzeba potwierdzić u BrainAccess,
   że użycie w konkursie jest dozwolone (to SDK do sprzętu od organizatora).

