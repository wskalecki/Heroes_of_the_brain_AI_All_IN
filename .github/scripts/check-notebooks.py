"""Notebook hygiene checks, run in CI (and locally: python .github/scripts/check-notebooks.py).

For every tracked .ipynb:
* it is valid nbformat JSON,
* no cell output is an error (committed notebooks must have run cleanly),
* every code cell is syntactically valid Python (IPython magics and shell lines are skipped),
* code cells that were executed have outputs saved only when the notebook is an analysis
  notebook (data/analysis); cleared notebooks are fine elsewhere,
* no local absolute paths from a developer machine leak into sources or outputs.
"""

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

LEAK = re.compile(r"/home/user/|/root/|/tmp/claude|C:\\Users\\|/Users/[a-z]")


def notebooks() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "-z", "*.ipynb"], capture_output=True, check=True).stdout
    return [Path(p) for p in out.decode("utf-8").split("\0") if p]


def cell_source(cell: dict) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else source


def output_text(output: dict) -> str:
    if output.get("output_type") == "stream":
        text = output.get("text", "")
        return "".join(text) if isinstance(text, list) else text
    data = output.get("data", {})
    chunks = []
    for key, value in data.items():
        if key.startswith("image/"):
            continue
        chunks.append("".join(value) if isinstance(value, list) else str(value))
    return "\n".join(chunks)


def strip_ipython(code: str) -> str:
    lines = []
    for line in code.splitlines():
        stripped = line.lstrip()
        lines.append("pass" if stripped.startswith(("%", "!")) else line)
    return "\n".join(lines)


def main() -> int:
    errors = []
    for path in notebooks():
        try:
            nb = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: not valid JSON ({exc})")
            continue
        if nb.get("nbformat") != 4:
            errors.append(f"{path}: nbformat {nb.get('nbformat')} (expected 4)")
            continue
        analysis = path.as_posix().startswith("data/analysis/")
        executed = 0
        for index, cell in enumerate(nb.get("cells", [])):
            source = cell_source(cell)
            if LEAK.search(source):
                errors.append(f"{path}: cell {index}: source contains a local absolute path")
            if cell.get("cell_type") != "code":
                continue
            try:
                ast.parse(strip_ipython(source))
            except SyntaxError as exc:
                errors.append(f"{path}: cell {index}: syntax error: {exc.msg} (line {exc.lineno})")
            for output in cell.get("outputs", []):
                if output.get("output_type") == "error":
                    errors.append(f"{path}: cell {index}: saved output is an error ({output.get('ename')})")
                if LEAK.search(output_text(output)):
                    errors.append(f"{path}: cell {index}: output contains a local absolute path")
            if cell.get("execution_count") is not None:
                executed += 1
        if analysis and executed == 0 and any(c.get("cell_type") == "code" for c in nb.get("cells", [])):
            errors.append(f"{path}: analysis notebook has no executed cells (commit it with saved outputs)")
    if errors:
        print("Notebook problems:\n")
        for line in errors:
            print(f"  - {line}")
        print(f"\n{len(errors)} problem(s) in {len(notebooks())} notebook(s).")
        return 1
    print(f"Notebooks: OK ({len(notebooks())} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
