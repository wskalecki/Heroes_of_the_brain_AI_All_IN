# Workflowy czekające na aktywację

Te dwa pliki to gotowe workflowy GitHub Actions. Leżą tutaj, a nie w `.github/workflows/`, bo token użyty do ich
przygotowania nie ma uprawnienia `workflow` (GitHub odrzuca wtedy push plików z `.github/workflows/`).

**Aktywacja (jedna komenda, z Twoim kontem, które ma to uprawnienie):**

```bash
git mv .github/workflows-pending/ci.yml .github/workflows/ci.yml && git mv .github/workflows-pending/labeler.yml .github/workflows/labeler.yml && git rm -q .github/workflows-pending/README.md && git commit -m "Activate CI and labeler workflows" && git push
```

Albo w przeglądarce: otwórz plik na GitHubie, ołówek, zmień ścieżkę na `.github/workflows/ci.yml`, zapisz (to samo dla `labeler.yml`).

Po aktywacji na gałęzi PR odpali się CI na tym samym PR. Jeśli wszystkie zadania są zielone, można scalać.
