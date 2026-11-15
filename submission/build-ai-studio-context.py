#!/usr/bin/env python3
"""Rebuild submission/wachta-repo-dla-ai-studio.txt: README, key docs and source code in one text file
(for drag and drop into Google AI Studio or NotebookLM). Run from anywhere: python submission/build-ai-studio-context.py"""

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "submission" / "wachta-repo-dla-ai-studio.txt"
DOCS = [
    "README.md", "docs/pitch.md", "docs/scenariusz-demo.md", "docs/jury-i-kryteria.md", "docs/decyzje.md",
    "docs/plan-projektu.md", "docs/trafnosc-na-nagraniach.md", "docs/sesja-monotonii-wojtek.md",
    "docs/analiza-i-adaptacja.md", "docs/podstawy-naukowe.md", "docs/rynek-eeg-wearables.md",
    "docs/rynek-wielkosc-i-kierunek.md", "docs/licencje.md", "docs/uruchomienie.md",
]


def main() -> None:
    files = DOCS + sorted(
        p.relative_to(REPO).as_posix()
        for p in (REPO / "src" / "wachta").rglob("*")
        if p.is_file() and p.suffix in {".py", ".html", ".js", ".css"} and "__pycache__" not in p.parts
    )
    parts = ["# Pełny kontekst repozytorium Wachta (Heroes of the Brain 2026 — Adaptive Systems)\n\n"]
    for rel in files:
        text = (REPO / rel).read_text(encoding="utf-8").rstrip("\n")
        parts.append(f"\n---\n## FILE: `{rel}`\n```\n{text}\n```\n")
    OUT.write_text("".join(parts), encoding="utf-8")
    print(f"{OUT.relative_to(REPO)}: {len(files)} files, {OUT.stat().st_size / 1024:.0f} kB")


if __name__ == "__main__":
    main()
