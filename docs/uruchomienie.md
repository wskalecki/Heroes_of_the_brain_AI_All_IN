# Uruchomienie

Kod jest w `src/wachta/`. Potrzebny jest Python 3.10 lub nowszy.

## Instalacja

W katalogu repo, najlepiej w wirtualnym środowisku:

```bash
python -m venv .venv
```

```bash
source .venv/bin/activate
```

```bash
pip install -e ".[dev,analysis]"
```

Na laptopie ze sprzętem BrainAccess dodatkowo:

```bash
pip install -e ".[live]"
```

## Testy

```bash
pytest
```

Testy na nagraniach zespołu uruchamiają się tylko wtedy, gdy pliki z `data/recordings/` są na dysku.

## Trafność na nagraniach

```bash
python experiments/validate-on-recordings.py
```

Wynik i jego ograniczenia: [`trafnosc-na-nagraniach.md`](trafnosc-na-nagraniach.md).

## Punkt pomiarowy i test PVT

Narzędzie punktu pomiarowego (protokół 3 × 60 s, KSS i opcjonalnie Garmin Venu 2, zapis adnotacji oraz `data/recordings/checkpoints.csv`):

```bash
python -m wachta.session --person wojtek --checkpoint T1
```

Test czasu reakcji PVT-B (3 min) w przeglądarce z zapisem wyników do `data/recordings/pvt.csv`:

```bash
python -m wachta.pvt --person wojtek --checkpoint T1
```

Jeśli test był otwarty bez działającego serwera i zapisał surowy plik JSON, można go dograć przez `python -m wachta.pvt --import <plik.json>`.

## Dashboard

Serwer liczy wskaźnik dla każdego źródła i wysyła wyniki do przeglądarki. Strona: http://127.0.0.1:8000.
Działa bez internetu (bez zewnętrznych bibliotek w przeglądarce).

Odtworzenie nagrania Filipa od 500 s, cztery razy szybciej, z dwiema osobami w panelu przełożonego:

```bash
python -m wachta.server --file filip --start 500 --speed 4 --team rudy:0 adi:60
```

Blok `eyes_closed` Filipa (600–660 s) pojawia się po ok. 25 s: stan zmienia się na „Przerwa teraz”,
a panel przełożonego wskazuje osobę z największą rezerwą.

Na żywo z BrainAccess Board (Board uruchomiony, czepek połączony, `pip install -e ".[live]"`):

```bash
python -m wachta.server --source board --name Wojtek --team rudy:0 adi:60
```

Kalibracja trwa ok. 60 s spokojnego patrzenia przed siebie. Przyciski na stronie: przerwa, próba reakcji, ponowna kalibracja,
nowa zmiana. „Nowa zmiana” zaczyna zmianę od nowa dla całego zespołu naraz (rezerwa 100%, zegar od `--clock`), ale zachowuje
kalibrację, więc można skalibrować osobę przed demo. Przebieg demo: [`scenariusz-demo.md`](scenariusz-demo.md).

Co widać na stronie poza stanem i rezerwą:

- **Oczy:** otwarte albo zamknięte, z liczbą mrugnięć na minutę (z F3/F4). Spadek czujności jest opisany jako
  „oczy zamknięte” albo „senność przy otwartych oczach”.
- **Próba reakcji:** po wykrytym spadku czujności (gdy oczy znów się otworzą) oraz kontrolnie co 20 minut pojawia się
  żółte kółko z dźwiękiem. Trzeba nacisnąć spację albo kliknąć. Reakcja wolniejsza niż osobista norma (na starcie 355 ms)
  albo jej brak w ciągu 3 s liczy się jako spadek czujności. Przycisk „Sprawdź reakcję” wywołuje próbę ręcznie (do demo).

Przydatne opcje:

- `--time-scale 60` (domyślnie): 1 minuta na ekranie to 1 godzina zmiany, żeby rezerwa zmieniała się w czasie demo. `--time-scale 1` to czas rzeczywisty.
- `--wake 07:00 --clock 02:30`: godzina przebudzenia i godzina na starcie zmiany (domyślnie teraz). Włącza kontekst:
  rezerwa spada szybciej w nocy (najmocniej ok. 4:30) i po długim czuwaniu. Parametry to założenia, opisane w `config.py`.
- `--file` przyjmuje nazwę nagrania zespołu (`adi`, `filip`, `rudy`, `wojtek`) albo ścieżkę do pliku `.fif`.
- `--team NAZWA:START` dodaje odtwarzane nagrania do panelu przełożonego. `NAZWA:START-KONIEC` (np. `rudy:380-520`) zapętla nagranie na wybranym odcinku, żeby osoba z panelu nie trafiła na blok zamkniętych oczu ani na zaszumiony początek pliku.
- `GET /api/state` zwraca ostatni wynik każdego pracownika (do szybkiego sprawdzenia bez przeglądarki).

Tryb na żywo czyta nowe próbki z bazy danych sesji Board (`brainaccess-board`, metoda `get_data_since`) co 0,25 s.
Sprawdzony na sprzęcie 14.11.2026: kalibracja i zmiana stanu po zamknięciu oczu działają.
Przy pracy w czasie rzeczywistym dodaj `--time-scale 1`. Jeśli port 8000 jest zajęty, użyj np. `--port 8001`.

## Nocny punkt pomiarowy

Protokół i analiza: [`protokol-nocny.md`](protokol-nocny.md). W skrócie:

```bash
python -m wachta.session --person wojtek --checkpoint N1 --monotony-min 10
```

```bash
python experiments/analyze-night-checkpoint.py --fit wojtek-n1=plik.fit --figure docs/img/noc-vs-dzien.png
```

## Pipeline w kodzie

```python
from wachta.pipeline import Pipeline

pipeline = Pipeline()
for result in pipeline.push(chunk):   # chunk: tablica (8, n) w woltach, kanały F3 F4 C3 C4 P3 P4 O1 O2
    print(result["t"], result["state"], result["reserve"])
```

Każdy wynik odpowiada jednemu oknu (co sekundę). Najważniejsze pola: `state`, `reserve`, `fast`, `slow`, `quality`.
Parametry i ich uzasadnienie są w `src/wachta/config.py`.
