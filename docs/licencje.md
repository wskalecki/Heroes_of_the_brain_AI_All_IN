# Licencje: zależności i zbiory danych

Przegląd na potrzeby regulaminu (§10: biblioteki open source dozwolone, o ile ich licencje na to pozwalają) i podania źródeł w prezentacji.
Licencje pakietów odczytane z metadanych zainstalowanych wersji; licencje zbiorów z `datasety-eeg-zrodla.md`.

## Zależności kodu (`pyproject.toml`)

| Pakiet | Licencja | Uwagi |
|---|---|---|
| numpy, scipy, mne, uvicorn, pandas, httpx, scikit-learn | BSD-3-Clause (scipy: licencja BSD) | pozwala na użycie komercyjne |
| fastapi, pytest, neurokit2, remotezip, ruff | MIT | pozwala na użycie komercyjne |
| matplotlib | licencja matplotlib (oparta na PSF) | permisywna |
| `brainaccess-board` (opcja `live`) | **niesprawdzona** | pakiet niezainstalowany w tym środowisku; sprawdzić na PyPI i u producenta (BrainAccess) przed złożeniem projektu |
| `fitdecode` (opcja `analysis`) | **niesprawdzona** | j.w.; używany tylko lokalnie do plików `.fit`, nie jest wymagany do uruchomienia |

Samo repozytorium nie ma pliku `LICENSE`. Regulamin zostawia prawa do projektu uczestnikom, więc decyzję (np. MIT albo bez licencji) trzeba podjąć jako zespół i zapisać w `docs/decyzje.md`.

## Zbiory danych użyte w notebookach

| Zbiór | Licencja | Co trzeba zrobić |
|---|---|---|
| EEG During Mental Arithmetic Tasks, PhysioNet (liczenie w pamięci, notebook 02) | Open Data Commons Attribution 1.0 | podać źródło |
| COG-BCI (Zenodo 7413650, notebooki 02, 05–10) | CC BY 4.0 | podać źródło: Hinss i in., Scientific Data 10 (2023) |
| Zbiór Cui, figshare (senność, notebook 04) | CC BY 4.0 | podać źródło |

Zbiory z licencją niekomercyjną (CL-Drive, CC BY-NC) lub niesprawdzoną (FatigueSet, Nokia Bell Labs) opisane w `datasety-eeg-zrodla.md` nie występują w notebookach 02–10.

## Do zrobienia przed złożeniem projektu

1. Sprawdzić licencje `brainaccess-board` i `fitdecode`.
2. Dodać do ostatniego slajdu źródła zbiorów (PhysioNet EEGMAT, COG-BCI, Cui).
3. Zdecydować o licencji repozytorium.
