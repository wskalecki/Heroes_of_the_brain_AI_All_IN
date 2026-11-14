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

Połączone podsumowanie punktów pomiarowych (`checkpoints.csv` + `pvt.csv`, zmiany względem `T0` i wykres na slajd):

```bash
python experiments/summarize-checkpoints.py --figure docs/img/checkpoints-summary.png
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
