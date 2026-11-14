"""Summarize checkpoint measurements (KSS, Garmin Venu 2 and PVT-B) across T0/T1/T2.

Usage:
    python experiments/summarize-checkpoints.py
    python experiments/summarize-checkpoints.py --figure docs/img/checkpoints-summary.png
"""

from wachta.summary import main

if __name__ == "__main__":
    raise SystemExit(main())
