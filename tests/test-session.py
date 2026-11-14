import csv
from datetime import datetime, timezone
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from wachta.session import (
    CHECKPOINT_FIELDS,
    annotations_path_for,
    append_checkpoint_row,
    build_parser,
    build_steps,
    find_candidate_recordings,
    main,
    parse_kss,
    parse_optional_number,
    run_countdown,
    run_session,
    write_annotations,
)


class FakeClock:
    def __init__(self, start: float = 0.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def sleep(self, dt: float) -> None:
        self.now += max(dt, 0.0)


class SessionTests(unittest.TestCase):
    def test_annotations_match_exact_checkpoint_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fif_path = Path(tmp) / "subj-1_ses-S001_task-filip-t0_run-001-raw.fif"
            ann_path = annotations_path_for(fif_path)
            self.assertEqual(
                ann_path.name,
                "subj-1_ses-S001_task-filip-t0_run-001-raw_annotations.csv",
            )

            write_annotations(ann_path)
            self.assertEqual(
                ann_path.read_text(encoding="utf-8"),
                "onset,duration,description\n"
                "0.000,60.000,eyes_open\n"
                "60.000,60.000,eyes_closed\n"
                "120.000,60.000,math\n",
            )

    def test_annotations_path_for_plain_fif_filename(self) -> None:
        path = annotations_path_for(Path("data/recordings/wojtek-t1.fif"))
        self.assertEqual(path, Path("data/recordings/wojtek-t1-raw_annotations.csv"))

    def test_checkpoints_csv_creation_and_append_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cp_path = Path(tmp) / "checkpoints.csv"
            append_checkpoint_row(
                cp_path,
                {
                    "person": "filip",
                    "checkpoint": "T0",
                    "started_at": "2026-11-14T14:35:00+01:00",
                    "kss": "3",
                    "recording_file": "filip-t0-raw.fif",
                    "notes": "pierwszy pomiar",
                },
            )
            append_checkpoint_row(
                cp_path,
                {
                    "person": "wojtek",
                    "checkpoint": "T0",
                    "started_at": "2026-11-14T14:42:00+01:00",
                    "kss": "4",
                    "body_battery": "68",
                    "stress": "32",
                    "heart_rate": "66",
                    "hrv_ms": "47.5",
                    "recording_file": "wojtek-t0-raw.fif",
                    "notes": "",
                },
            )

            with cp_path.open("r", newline="", encoding="utf-8") as handle:
                rows = list(csv.reader(handle))

            self.assertEqual(tuple(rows[0]), CHECKPOINT_FIELDS)
            self.assertEqual(len(rows), 3)
            self.assertEqual(
                rows[1],
                [
                    "filip",
                    "T0",
                    "2026-11-14T14:35:00+01:00",
                    "3",
                    "",
                    "",
                    "",
                    "",
                    "filip-t0-raw.fif",
                    "pierwszy pomiar",
                ],
            )
            self.assertEqual(
                rows[2],
                [
                    "wojtek",
                    "T0",
                    "2026-11-14T14:42:00+01:00",
                    "4",
                    "68",
                    "32",
                    "66",
                    "47.5",
                    "wojtek-t0-raw.fif",
                    "",
                ],
            )

    def test_append_checkpoint_rejects_mismatched_header(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cp_path = Path(tmp) / "checkpoints.csv"
            cp_path.write_text("person,kss\nadi,3\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                append_checkpoint_row(cp_path, {"person": "adi", "checkpoint": "T0", "kss": "3"})

    def test_validation_helpers(self) -> None:
        self.assertEqual(parse_kss("1"), 1)
        self.assertEqual(parse_kss(" 9 "), 9)
        for bad in ("0", "10", "abc", ""):
            with self.assertRaises(ValueError):
                parse_kss(bad)

        self.assertEqual(parse_optional_number("", "hrv_ms"), "")
        self.assertEqual(parse_optional_number("42,5", "hrv_ms", min_value=1), "42.5")
        self.assertEqual(parse_optional_number("65.0", "hrv_ms", min_value=1), "65")
        with self.assertRaises(ValueError):
            parse_optional_number("120", "body_battery", min_value=0, max_value=100, integer=True)

    def test_countdown_advances_through_all_three_steps_and_rings_bell(self) -> None:
        clock = FakeClock(100.0)
        buf = io.StringIO()
        steps = build_steps(3.0)
        run_countdown(steps, out=buf, bell=True, clock=clock, sleep=clock.sleep)

        text = buf.getvalue()
        self.assertIn("EYES_OPEN", text)
        self.assertIn("EYES_CLOSED", text)
        self.assertIn("MATH", text)
        self.assertEqual(text.count("\a"), 4)
        self.assertGreaterEqual(clock.now, 109.0)

    def test_interactive_session_for_wojtek_with_auto_discovered_recording(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rec_dir = Path(tmp)
            older = rec_dir / "subj-1_ses-S001_task-adi-t0_run-001-raw.fif"
            older.write_bytes(b"old")
            target = rec_dir / "subj-1_ses-S001_task-wojtek-t1_run-001-raw.fif"
            target.write_bytes(b"new")

            clock = FakeClock(10.0)
            out = io.StringIO()
            answers = iter(
                [
                    "",       # Enter to start recording countdown
                    "invalid",
                    "6",      # valid KSS after retry
                    "55",     # body_battery
                    "38",     # stress
                    "72",     # heart_rate
                    "41.2",   # hrv_ms
                    "",       # accept auto-discovered recording
                    "po polowie hackathonu",
                ]
            )
            args = build_parser().parse_args(
                [
                    "--person",
                    "wojtek",
                    "--checkpoint",
                    "t1",
                    "--recordings-dir",
                    str(rec_dir),
                    "--step-seconds",
                    "2",
                    "--no-bell",
                ]
            )
            fixed_now = datetime(2026, 11, 14, 18, 0, 0, tzinfo=timezone.utc)
            result = run_session(
                args,
                input_fn=lambda _prompt: next(answers),
                out=out,
                clock=clock,
                sleep=clock.sleep,
                now_fn=lambda: fixed_now,
            )

            self.assertEqual(result["annotations_path"], annotations_path_for(target))
            self.assertTrue(annotations_path_for(target).exists())
            row = result["row"]
            self.assertEqual(row["person"], "wojtek")
            self.assertEqual(row["checkpoint"], "T1")
            self.assertEqual(row["kss"], "6")
            self.assertEqual(row["body_battery"], "55")
            self.assertEqual(row["stress"], "38")
            self.assertEqual(row["heart_rate"], "72")
            self.assertEqual(row["hrv_ms"], "41.2")
            self.assertEqual(row["recording_file"], target.name)
            self.assertEqual(row["notes"], "po polowie hackathonu")

    def test_find_candidate_recordings_prioritizes_matching_person_and_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rec_dir = Path(tmp)
            a = rec_dir / "subj-1_task-adi-t0-raw.fif"
            b = rec_dir / "nested" / "subj-1_task-rudy-t2-raw.fif"
            b.parent.mkdir(parents=True)
            a.write_bytes(b"a")
            b.write_bytes(b"b")
            candidates = find_candidate_recordings(rec_dir, "rudy", "T2")
            self.assertEqual(candidates[0], b)

    def test_cli_module_execution_non_interactive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rec_dir = Path(tmp)
            fif = rec_dir / "subj-1_task-rudy-t0-raw.fif"
            fif.write_bytes(b"dummy")
            repo_root = Path(__file__).resolve().parents[1]
            env = dict(os.environ)
            env["PYTHONPATH"] = str(repo_root / "src")

            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "wachta.session",
                    "--person",
                    "Rudy",
                    "--checkpoint",
                    "t0",
                    "--kss",
                    "4",
                    "--recordings-dir",
                    str(rec_dir),
                    "--recording",
                    str(fif),
                    "--started-at",
                    "2026-11-14T15:10:00+01:00",
                    "--notes",
                    "cli test",
                    "--no-countdown",
                ],
                cwd=repo_root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            self.assertTrue((rec_dir / "checkpoints.csv").exists())
            self.assertTrue((rec_dir / "subj-1_task-rudy-t0-raw_annotations.csv").exists())

            exit_code = main(["--person", "adi", "--checkpoint", "t0", "--kss", "99", "--no-countdown"])
            self.assertEqual(exit_code, 2)


if __name__ == "__main__":
    unittest.main()
