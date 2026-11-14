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

## Pipeline w kodzie

```python
from wachta.pipeline import Pipeline

pipeline = Pipeline()
for result in pipeline.push(chunk):   # chunk: tablica (8, n) w woltach, kanały F3 F4 C3 C4 P3 P4 O1 O2
    print(result["t"], result["state"], result["reserve"])
```

Każdy wynik odpowiada jednemu oknu (co sekundę). Najważniejsze pola: `state`, `reserve`, `fast`, `slow`, `quality`.
Parametry i ich uzasadnienie są w `src/wachta/config.py`.
