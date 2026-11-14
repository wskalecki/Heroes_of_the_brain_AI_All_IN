"""Repository hygiene checks, run in CI (and locally: python .github/scripts/check-repo.py).

Rules come from AGENTS.md:
* file and folder names: lowercase, hyphens instead of spaces, no Polish characters,
* no secrets, no raw EEG recordings outside data/recordings, no large binaries.

Only tracked files are checked. Exit code 1 when any rule is broken.
"""

import re
import subprocess
import sys
from pathlib import Path

# Files that keep a conventional upper-case name.
UPPERCASE_OK = {"README.md", "AGENTS.md", "CONTRIBUTING.md", "LICENSE", "CODEOWNERS"}
# Folders where names come from the acquisition software or from GitHub conventions, not from us.
NAME_EXEMPT = ("data/recordings/", ".github/")   # .github follows GitHub conventions (ISSUE_TEMPLATE, pull_request_template.md)
MAX_BYTES = 5 * 1024 * 1024
MAX_BYTES_NOTEBOOK = 3 * 1024 * 1024
RAW_EEG_SUFFIXES = {".edf", ".bdf", ".vhdr", ".vmrk", ".eeg", ".set", ".fdt", ".xdf", ".gdf"}
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    "Slack token": re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"),
    "OpenAI/Anthropic-style key": re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_-]{32,}\b"),
    "generic secret assignment": re.compile(
        r"""(?i)\b(?:api[_-]?key|secret|passwd|password|token)\b\s*[:=]\s*['"][A-Za-z0-9/+_\-]{20,}['"]"""
    ),
}
TEXT_SUFFIXES = {".py", ".md", ".txt", ".toml", ".yml", ".yaml", ".json", ".js", ".html", ".css", ".ipynb", ".cfg", ".ini", ".sh"}


def tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z"], capture_output=True, check=True).stdout
    return [p for p in out.decode("utf-8").split("\0") if p]


def check_name(path: str) -> str | None:
    if path.startswith(NAME_EXEMPT):
        return None
    for part in Path(path).parts:
        if part.startswith("."):
            continue
        if " " in part:
            return "contains a space"
        if not part.isascii():
            return "contains non-ASCII characters (no Polish letters in names)"
        if part != part.lower() and part not in UPPERCASE_OK:
            return f"'{part}' is not lowercase"
        if "_" in part and not part.endswith(".py") and not part.startswith("__"):
            return f"'{part}' uses underscores; use hyphens"
    return None


def main() -> int:
    errors: list[str] = []
    for path in tracked_files():
        file = Path(path)
        if not file.is_file():
            continue
        problem = check_name(path)
        if problem:
            errors.append(f"naming: {path}: {problem}")

        size = file.stat().st_size
        if not path.startswith("data/recordings/"):
            limit = MAX_BYTES_NOTEBOOK if file.suffix == ".ipynb" else MAX_BYTES
            if size > limit:
                errors.append(f"size: {path}: {size / 1e6:.1f} MB exceeds {limit / 1e6:.0f} MB (notebooks: clear outputs or shrink figures)")
            if file.suffix.lower() in RAW_EEG_SUFFIXES:
                errors.append(f"raw EEG: {path}: raw recordings belong only in data/recordings (consent required, see AGENTS.md)")

        if file.name == ".env" or (file.name.startswith(".env.") and file.name != ".env.example"):
            errors.append(f"secrets: {path}: environment files must not be committed")

        if file.suffix.lower() in TEXT_SUFFIXES and size < 4_000_000 and not path.startswith("data/recordings/"):
            text = file.read_text(encoding="utf-8", errors="ignore")
            for name, pattern in SECRET_PATTERNS.items():
                match = pattern.search(text)
                if match:
                    errors.append(f"secrets: {path}: looks like a {name} ({match.group(0)[:12]}...)")

    if errors:
        print("Repository hygiene problems:\n")
        for line in errors:
            print(f"  - {line}")
        print(f"\n{len(errors)} problem(s). Rules: AGENTS.md (names, data, secrets).")
        return 1
    print("Repository hygiene: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
