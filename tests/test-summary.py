import csv
import io
from pathlib import Path
import tempfile
import unittest

from wachta.pvt import PVT_FIELDS, append_result, build_row
from wachta.session import append_checkpoint_row
from wachta.summary import (
    MERGED_FIELDS,
    format_markdown_table,
    load_and_merge,
    main,
    save_summary_figure,
    write_merged_csv,
)


class SummaryTests(unittest.TestCase):
    def _write_sample_files(self, tmp_dir: Path) -> tuple[Path, Path]:
        cp_path = tmp_dir / "checkpoints.csv"
        pvt_path = tmp_dir / "pvt.csv"

        append_checkpoint_row(
            cp_path,
            {
                "person": "wojtek",
                "checkpoint": "T0",
                "started_at": "2026-11-14T10:00:00+01:00",
                "kss": "3",
                "body_battery": "82",
                "stress": "24",
                "heart_rate": "62",
                "hrv_ms": "58.5",
                "recording_file": "",
                "notes": "start",
            },
        )
        append_checkpoint_row(
            cp_path,
            {
                "person": "wojtek",
                "checkpoint": "T1",
                "started_at": "2026-11-14T14:00:00+01:00",
                "kss": "6",
                "body_battery": "49",
                "stress": "41",
                "heart_rate": "68",
                "hrv_ms": "42.0",
                "recording_file": "",
                "notes": "po 4h",
            },
        )
        append_checkpoint_row(
            cp_path,
            {
                "person": "adi",
                "checkpoint": "T0",
                "started_at": "2026-11-14T10:05:00+01:00",
                "kss": "4",
                "body_battery": "",
                "stress": "",
                "heart_rate": "",
                "hrv_ms": "",
                "recording_file": "",
                "notes": "",
            },
        )

        append_result(
            pvt_path,
            build_row(
                {
                    "person": "wojtek",
                    "checkpoint": "T0",
                    "started_at": "2026-11-14T10:04:00+01:00",
                    "duration_s": 180,
                    "rts_ms": [240, 250, 260],
                    "anticipations": 0,
                }
            ),
        )
        append_result(
            pvt_path,
            build_row(
                {
                    "person": "wojtek",
                    "checkpoint": "T1",
                    "started_at": "2026-11-14T14:04:00+01:00",
                    "duration_s": 180,
                    "rts_ms": [290, 310, 380, 410],
                    "anticipations": 1,
                }
            ),
        )
        append_result(
            pvt_path,
            build_row(
                {
                    "person": "filip",
                    "checkpoint": "T1",
                    "started_at": "2026-11-14T14:10:00+01:00",
                    "duration_s": 180,
                    "rts_ms": [255, 265, 275],
                    "anticipations": 0,
                }
            ),
        )
        return cp_path, pvt_path

    def test_load_and_merge_combines_checkpoints_and_pvt_and_computes_deltas(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cp_path, pvt_path = self._write_sample_files(Path(tmp))
            rows = load_and_merge(cp_path, pvt_path)
            keys = [(r["person"], r["checkpoint"]) for r in rows]
            self.assertEqual(
                keys,
                [("adi", "T0"), ("filip", "T1"), ("wojtek", "T0"), ("wojtek", "T1")],
            )

            w_t0 = next(r for r in rows if (r["person"], r["checkpoint"]) == ("wojtek", "T0"))
            w_t1 = next(r for r in rows if (r["person"], r["checkpoint"]) == ("wojtek", "T1"))
            self.assertEqual(w_t0["kss"], 3)
            self.assertEqual(w_t0["median_rt_ms"], 250.0)
            self.assertEqual(w_t0["delta_kss"], 0)
            self.assertEqual(w_t0["delta_median_rt_ms"], 0.0)

            self.assertEqual(w_t1["kss"], 6)
            self.assertEqual(w_t1["delta_kss"], 3)
            self.assertEqual(w_t1["median_rt_ms"], 345.0)
            self.assertEqual(w_t1["delta_median_rt_ms"], 95.0)
            self.assertEqual(w_t1["lapses"], 2)
            self.assertEqual(w_t1["delta_body_battery"], -33)
            self.assertAlmostEqual(w_t1["delta_hrv_ms"], -16.5)

            f_t1 = next(r for r in rows if (r["person"], r["checkpoint"]) == ("filip", "T1"))
            self.assertIsNone(f_t1["kss"])
            self.assertIsNone(f_t1["delta_median_rt_ms"])
            self.assertEqual(f_t1["median_rt_ms"], 265.0)

    def test_latest_duplicate_row_wins_and_checkpoint_ordering_is_canonical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cp_path = Path(tmp) / "checkpoints.csv"
            for cp, kss in [("T2", "7"), ("T0", "2"), ("T0", "3"), ("T1", "5")]:
                append_checkpoint_row(
                    cp_path,
                    {
                        "person": "wojtek",
                        "checkpoint": cp,
                        "started_at": "2026-11-14T10:00:00+01:00",
                        "kss": kss,
                    },
                )
            rows = load_and_merge(cp_path, Path(tmp) / "missing-pvt.csv")
            self.assertEqual([r["checkpoint"] for r in rows], ["T0", "T1", "T2"])
            self.assertEqual(rows[0]["kss"], 3)
            self.assertEqual(rows[2]["delta_kss"], 4)

    def test_format_markdown_table_uses_polish_commas_and_em_dashes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cp_path, pvt_path = self._write_sample_files(Path(tmp))
            rows = load_and_merge(cp_path, pvt_path)
            table = format_markdown_table(rows)
            self.assertIn("| Osoba | Punkt | KSS (1–9) |", table)
            self.assertIn("| wojtek | T1 | 6 (+3) |", table)
            self.assertIn("345,0 (+95,0)", table)
            self.assertIn("42,0 (-16,5)", table)
            self.assertIn("| filip | T1 | — |", table)

    def test_write_merged_csv_and_save_summary_figure_under_300kb(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            cp_path, pvt_path = self._write_sample_files(tmp_dir)
            rows = load_and_merge(cp_path, pvt_path)

            out_csv = tmp_dir / "merged.csv"
            write_merged_csv(out_csv, rows)
            with out_csv.open(newline="", encoding="utf-8") as handle:
                parsed = list(csv.reader(handle))
            self.assertEqual(tuple(parsed[0]), MERGED_FIELDS)
            self.assertEqual(len(parsed), 5)

            fig_path = tmp_dir / "summary.png"
            save_summary_figure(rows, fig_path)
            self.assertTrue(fig_path.exists())
            data = fig_path.read_bytes()
            self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertLess(len(data), 300 * 1024)

    def test_cli_main_prints_table_and_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            cp_path, pvt_path = self._write_sample_files(tmp_dir)
            out_csv = tmp_dir / "out.csv"
            fig_path = tmp_dir / "out.png"
            buf = io.StringIO()
            rc = main(
                [
                    "--checkpoints",
                    str(cp_path),
                    "--pvt",
                    str(pvt_path),
                    "--out-csv",
                    str(out_csv),
                    "--figure",
                    str(fig_path),
                ],
                out=buf,
            )
            self.assertEqual(rc, 0)
            self.assertIn("| wojtek | T1 |", buf.getvalue())
            self.assertTrue(out_csv.exists())
            self.assertTrue(fig_path.exists())


if __name__ == "__main__":
    unittest.main()
