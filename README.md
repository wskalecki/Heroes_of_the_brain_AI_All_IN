# Wachta — zmęczenie i czujność mierzone na człowieku, nie na zegarze

Projekt drużyny **AI All In** na hackathon **Heroes of the Brain 2026**, kategoria **Systemy adaptacyjne**.

Przepisy dają wszystkim ten sam limit czasu pracy, a zmęczenie każdego dopada inaczej. Wachta to oprogramowanie,
które na podstawie EEG z suchych elektrod (BrainAccess MINI) i krótkich prób reakcji **zmienia swoje zachowanie i plan pracy**:
upraszcza widok, prosi o reakcję, proponuje przerwę i wskazuje zmiennika z największą rezerwą czujności.
**Wszystko działa lokalnie:** surowe EEG nie opuszcza komputera pracownika, przełożony widzi tylko gotowość i rezerwę.

## Zgłoszenie

| Co | Gdzie |
|---|---|
| Prezentacja (10 slajdów, PDF) | [`submission/wachta-prezentacja-10-slajdow.pdf`](submission/wachta-prezentacja-10-slajdow.pdf) |
| Film demo (ok. 2 min) | [`submission/wachta-demo-2min.mp4`](submission/wachta-demo-2min.mp4) |
| Treść slajdów ze źródłami | [`docs/pitch.md`](docs/pitch.md) |
| Co zweryfikowane, a co założone | [`docs/pitch.md`](docs/pitch.md), slajd 8 |

## Jak to działa

1. **Kalibracja osobista (60 s):** baza alfy dla tej osoby.
2. **Sygnały w pętli:** wyrazistość alfy z tyłu głowy (O1, O2), mrugnięcia i stan oczu (F3, F4), reakcja na krótką próbę dźwiękową
   względem osobistej normy, kontekst (czas od przebudzenia, pora doby).
3. **Stan:** „Możesz pracować”, „Zaplanuj przerwę”, „Przerwa teraz”, „Brak wiarygodnego sygnału”, plus rezerwa czujności (model z jawnymi założeniami).
4. **Zmiana zachowania:** widok upraszcza się w stanie „Przerwa teraz”, system sam prosi o reakcję po zamknięciu oczu i co 20 min,
   panel przełożonego wskazuje zmiennika.

## Co pokazaliśmy (szczegóły i ograniczenia w `docs/`)

- Zamknięte oczy wykryte w **5 z 5** nagrań zespołu (4 osoby), mediana opóźnienia 9 s, **1 fałszywy alarm w 48 min**
  ([`docs/trafnosc-na-nagraniach.md`](docs/trafnosc-na-nagraniach.md)); **0 fałszywych alarmów** w 15 min monotonii.
- Dane publiczne: alfa rośnie ze zmęczeniem u **11 z 11** osób (średnie AUC 0,75), model uczony na danych danej osoby: AUC 0,76 → 0,90.
- Wyniki negatywne, które zmieniły projekt: alfa przy otwartych oczach **nie zapowiada** spadku reakcji (AUC 0,52), a zmienność rytmu serca
  nie mierzy czujności ponad czas zadania. Dlatego czujność sprawdzamy próbą reakcji, a nie zgadujemy z sygnału.
- Notebooki z analizami: [`data/analysis/`](data/analysis/).

## Przykładowe zastosowania

Wszędzie tam, gdzie praca w nocy i zmęczenie spotykają się z decyzjami o wysokiej stawce:

- **kopalnie, budowa, operatorzy ciężkich maszyn** (kask już jest, wkładka EEG nie zmienia stroju pracy);
- **lotnictwo, kontrola ruchu, energetyka i dyspozytornie** (branże z obowiązkiem zarządzania zmęczeniem);
- **szpitale:** lekarze i pielęgniarki na dyżurach nocnych;
- **IT:** nocne dyżury DevOps i SRE (on-call przy awariach);
- **finanse:** nocne operacje (monitoring transakcji, rozliczenia);
- **transport drogowy** (tu konkurujemy z obowiązkową kamerą, więc wchodzimy z okresową kalibracją i modelem kontekstu).

Zastosowania poza kopalniami, lotnictwem i transportem to kierunki do sprawdzenia w pilotażu, bez własnych danych.

## Dalszy rozwój

- **Wearables:** opaska, wkładka do kasku, słuchawki z elektrodami w uchu; suche elektrody grafenowe (dziś etap badań).
- **Drugi sygnał w pętli:** tętno i ruch z zegarka jako miara pewności oceny ([issue #17](https://github.com/wskalecki/Heroes_of_the_brain_AI_All_IN/issues/17)).
- **Integracje:** systemy grafików i dyżurów (rotacja on-call w IT, grafik oddziału), żeby propozycja zmiennika trafiała tam, gdzie planuje się obsadę.
- **Pilotaż:** jedna zmiana, porównanie sztywnej normy, samego modelu kontekstu i osobistego profilu.
- **Zasada bez zmian:** przetwarzanie lokalne, na zewnątrz wychodzi tylko gotowość.

## Uruchomienie

Python 3.10+. Szczegóły: [`docs/uruchomienie.md`](docs/uruchomienie.md).

```bash
pip install -e ".[dev,analysis]"
```

```bash
pytest
```

Demo bez sprzętu (odtworzenie nagrania z `data/recordings/`, dashboard pod adresem z komunikatu serwera):

```bash
python -m wachta.server --file filip --start 480 --port 8002 --time-scale 30 --wake 07:00 --clock 02:30 --team rudy:380-520 adi:370-500
```

Na żywo z BrainAccess MINI: `pip install -e ".[live]"` i komendy z [`docs/scenariusz-demo.md`](docs/scenariusz-demo.md).

## Struktura repozytorium

| Ścieżka | Co tu jest |
|---|---|
| `src/wachta/` | Kod: przetwarzanie sygnału, kalibracja na osobę, stany i rezerwa, próby reakcji, serwer i dashboard |
| `tests/` | Testy (`pytest`) |
| `experiments/` | Skrypty: trafność na nagraniach, analiza nocnych punktów pomiarowych |
| `data/recordings/` | Nagrania testowe zespołu z BrainAccess MINI (za zgodą nagranych osób) |
| `data/analysis/` | Notebooki z analizami nagrań i danych publicznych |
| `docs/` | Dokumentacja: decyzje, plan, pitch, wyniki, literatura, rynek, licencje ([indeks](docs/README.md)) |
| `submission/` | Pliki zgłoszenia: prezentacja, film, skrypty do ich odtworzenia |
| `AGENTS.md`, `CONTRIBUTING.md` | Zasady pracy w repo dla ludzi i agentów AI |

## Licencja

Kod i dokumentacja: MIT ([`LICENSE`](LICENSE)). Nagrania EEG w `data/recordings/` nie są objęte tą licencją
(dane biometryczne, udostępnione za zgodą nagranych osób). Zależności i zbiory danych: [`docs/licencje.md`](docs/licencje.md).

## Zespół

- **Wojtek:** sygnał i aplikacja
- **Adrian (Adi):** dane i dowody
- **Filip:** pomiary i protokoły
- **Rudy:** pitch, rynek i demo
