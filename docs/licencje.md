# Licencje: zależności i zbiory danych

Przegląd na potrzeby regulaminu (§10: biblioteki open source dozwolone, o ile ich licencje na to pozwalają) i podania źródeł w prezentacji.
Licencje pakietów odczytane z metadanych zainstalowanych wersji; licencje zbiorów z `datasety-eeg-zrodla.md`.

## Zależności kodu (`pyproject.toml`)

| Pakiet | Licencja | Uwagi |
|---|---|---|
| numpy, scipy, mne, uvicorn, pandas, httpx, scikit-learn | BSD-3-Clause (scipy: licencja BSD) | pozwala na użycie komercyjne |
| fastapi, pytest, neurokit2, remotezip, ruff | MIT | pozwala na użycie komercyjne |
| matplotlib | licencja matplotlib (oparta na PSF) | permisywna |
| `brainaccess-board` (opcja `live`) | **własnościowa** (PyPI: „Proprietary”, wersja 1.0.3) | SDK do sprzętu; nie jest dołączone do repo i nie podlega naszej licencji MIT. Do potwierdzenia u BrainAccess, że użycie w konkursie jest dozwolone |
| `fitdecode` (opcja `analysis`) | MIT (PyPI, wersja 0.11.0) | używany tylko lokalnie do plików `.fit`, nie jest wymagany do uruchomienia |

Repozytorium jest na licencji **MIT** (plik `LICENSE`, decyzja w `docs/decyzje.md`). Licencja obejmuje kod i dokumentację, **nie** nagrania EEG w `data/recordings/`.

## Zbiory danych użyte w notebookach

| Zbiór | Licencja | Co trzeba zrobić |
|---|---|---|
| EEG During Mental Arithmetic Tasks, PhysioNet (liczenie w pamięci, notebook 02) | Open Data Commons Attribution 1.0 | podać źródło |
| COG-BCI (Zenodo 7413650, notebooki 02, 05–10) | CC BY 4.0 | podać źródło: Hinss i in., Scientific Data 10 (2023) |
| Zbiór Cui, figshare (senność, notebook 04) | CC BY 4.0 | podać źródło |

Zbiory z licencją niekomercyjną (CL-Drive, CC BY-NC) lub niesprawdzoną (FatigueSet, Nokia Bell Labs) opisane w `datasety-eeg-zrodla.md` nie występują w notebookach 02–10.

## Do zrobienia przed złożeniem projektu

1. Potwierdzić u BrainAccess, że użycie `brainaccess-board` w konkursie jest dozwolone.
2. Dodać do ostatniego slajdu źródła zbiorów (PhysioNet EEGMAT, COG-BCI, Cui).
3. Zdecydować, czy repo będzie publiczne po hackathonie (nagrania zespołu, patrz `decyzje.md`).
