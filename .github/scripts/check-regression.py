"""Regression gate: the streaming pipeline must keep detecting the team's eyes-closed blocks.

Runs experiments/validate-on-recordings.py on data/recordings and parses its summary line:

    Razem: wykryto 4 z 4 bloków, 1 fałszywy alarm w 32 min poza blokiem ...

Fails when fewer blocks are detected than annotated, or when false alarms exceed the budget.
The baseline (4 of 4 blocks, 1 false alarm) is documented in docs/trafnosc-na-nagraniach.md. If a
deliberate change moves it, update that document and MAX_FALSE_ALARMS in the same pull request.

Usage (from the repo root, package installed or PYTHONPATH=src):
    python .github/scripts/check-regression.py
"""

import os
import re
import subprocess
import sys

MAX_FALSE_ALARMS = 3   # baseline is 1; some slack for numerical differences between library versions


def main() -> int:
    env = dict(os.environ, PYTHONPATH="src" + os.pathsep + os.environ.get("PYTHONPATH", ""))
    run = subprocess.run(
        [sys.executable, "experiments/validate-on-recordings.py"], capture_output=True, text=True, env=env
    )
    print(run.stdout)
    if run.returncode != 0:
        print(run.stderr, file=sys.stderr)
        print("validate-on-recordings.py crashed")
        return 1
    match = re.search(r"Razem: wykryto (\d+) z (\d+) bloków, (\d+) fałszyw", run.stdout)
    if not match:
        print("Could not find the summary line ('Razem: wykryto ...') in the script output.")
        return 1
    detected, total, false_alarms = (int(g) for g in match.groups())
    problems = []
    if total == 0:
        problems.append("no annotated recordings found in data/recordings")
    if detected < total:
        problems.append(f"only {detected} of {total} eyes-closed blocks detected (expected all)")
    if false_alarms > MAX_FALSE_ALARMS:
        problems.append(f"{false_alarms} false alarms outside the block (budget {MAX_FALSE_ALARMS})")
    if problems:
        print("Pipeline regression:\n  - " + "\n  - ".join(problems))
        return 1
    print(f"Pipeline regression gate: OK ({detected}/{total} blocks, {false_alarms} false alarm(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
