"""Check that relative links in Markdown files point to files that exist.

Run in CI (and locally: python .github/scripts/check-links.py). External links (http, mailto)
and in-page anchors are not checked. Links inside fenced code blocks and inline code are skipped.
"""

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

LINK = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)|!\[[^\]]*\]\(([^)\s]+)\)")
FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`]*`")


def markdown_files() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "-z", "*.md"], capture_output=True, check=True).stdout
    return [Path(p) for p in out.decode("utf-8").split("\0") if p]


def main() -> int:
    errors = []
    for md in markdown_files():
        in_fence = False
        for number, line in enumerate(md.read_text(encoding="utf-8").splitlines(), start=1):
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for match in LINK.finditer(INLINE_CODE.sub("", line)):
                target = (match.group(1) or match.group(2)).strip("<>")
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path = unquote(target.split("#", 1)[0])
                if not path:
                    continue
                resolved = (md.parent / path).resolve() if not path.startswith("/") else Path(path.lstrip("/")).resolve()
                if not resolved.exists():
                    errors.append(f"{md}:{number}: broken link -> {target}")
    if errors:
        print("Broken relative links:\n")
        for line in errors:
            print(f"  - {line}")
        print(f"\n{len(errors)} broken link(s).")
        return 1
    print(f"Markdown links: OK ({len(markdown_files())} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
