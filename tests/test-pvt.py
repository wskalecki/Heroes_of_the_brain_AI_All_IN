import csv
import io
import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

from wachta.pvt import (
    CONFIG_PLACEHOLDER,
    PVT_FIELDS,
    PvtConfig,
    PvtServer,
    append_result,
    build_row,
    import_result,
    main,
    render_page,
    score_pvt,
)


class ScoringTests(unittest.TestCase):
    def test_lapses_false_starts_and_performance_score(self) -> None:
        # 50 ms is a false start, 355 and 600 are lapses (>= 355 ms), 30000 is a timeout lapse.
        metrics = score_pvt([250, 300, 50, 355, 600, 30000, 280], anticipations=2)
        self.assertEqual(metrics["n_stimuli"], 7)
        self.assertEqual(metrics["false_starts"], 3)
        self.assertEqual(metrics["lapses"], 3)
        # 1 - (3 lapses + 3 false starts) / (7 stimuli + 2 anticipations)
        self.assertAlmostEqual(metrics["performance_score"], round(1 - 6 / 9, 3))
        self.assertEqual(metrics["median_rt_ms"], 327.5)
        valid = [250, 300, 355, 600, 30000, 280]
        self.assertAlmostEqual(metrics["mean_speed"], round(sum(1000 / r for r in valid) / 6, 3))
        self.assertAlmostEqual(metrics["slowest10_speed"], round(1000 / 30000, 3))

    def test_alert_run_has_no_lapses(self) -> None:
        metrics = score_pvt([210, 230, 250, 240, 220])
        self.assertEqual(metrics["lapses"], 0)
        self.assertEqual(metrics["false_starts"], 0)
        self.assertEqual(metrics["performance_score"], 1.0)
        self.assertEqual(metrics["mean_rt_ms"], 230.0)

    def test_empty_run_does_not_crash(self) -> None:
        metrics = score_pvt([], anticipations=0)
        self.assertEqual(metrics["n_stimuli"], 0)
        self.assertIsNone(metrics["mean_rt_ms"])
        self.assertIsNone(metrics["performance_score"])

    def test_threshold_follows_config(self) -> None:
        self.assertEqual(score_pvt([400, 450], cfg=PvtConfig(lapse_ms=500))["lapses"], 0)


class RowTests(unittest.TestCase):
    def payload(self, **overrides):
        data = {
            "person": "Wojtek",
            "checkpoint": "t1",
            "started_at": "2026-11-14T17:00:00.000Z",
            "duration_s": 180,
            "rts_ms": [250.4, 310, 80],
            "anticipations": 1,
        }
        data.update(overrides)
        return data

    def test_build_row_normalizes_and_scores(self) -> None:
        row = build_row(self.payload())
        self.assertEqual(row["person"], "wojtek")
        self.assertEqual(row["checkpoint"], "T1")
        self.assertEqual(row["false_starts"], 2)
        self.assertEqual(row["rts_ms"], "250.4;310;80")
        self.assertRegex(row["started_at"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$")

    def test_build_row_rejects_bad_input(self) -> None:
        bad_payloads = [
            self.payload(person=""),
            self.payload(person=123),
            self.payload(rts_ms="250"),
            self.payload(rts_ms=[250, -1]),
            self.payload(rts_ms=[250, 40000]),
            self.payload(rts_ms=[float("nan")]),
            self.payload(rts_ms=[True]),
            self.payload(anticipations=-1),
            self.payload(anticipations=1.5),
            self.payload(anticipations=float("inf")),
            self.payload(started_at="yesterday"),
            self.payload(duration_s=0),
        ]
        for payload in bad_payloads:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                build_row(payload)

    def test_append_result_writes_header_once_and_checks_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pvt.csv"
            append_result(path, build_row(self.payload()))
            append_result(path, build_row(self.payload(person="adi", checkpoint="T0")))
            with path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.reader(handle))
            self.assertEqual(tuple(rows[0]), PVT_FIELDS)
            self.assertEqual([r[0] for r in rows[1:]], ["wojtek", "adi"])

            other = Path(tmp) / "other.csv"
            other.write_text("person,kss\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                append_result(other, build_row(self.payload()))

    def test_import_result_from_downloaded_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp) / "pvt-rudy-T2.json"
            raw.write_text(json.dumps(self.payload(person="rudy", checkpoint="T2")), encoding="utf-8")
            out = Path(tmp) / "pvt.csv"
            self.assertEqual(main(["--import", str(raw), "--results-file", str(out)]), 0)
            self.assertIn("rudy,T2", out.read_text(encoding="utf-8"))
            self.assertEqual(import_result(raw, out)["person"], "rudy")


class PageAndServerTests(unittest.TestCase):
    def test_page_embeds_escaped_config(self) -> None:
        page = render_page(PvtConfig(duration_s=60.0), person="</script>x", checkpoint="T0")
        self.assertNotIn(CONFIG_PLACEHOLDER, page)
        self.assertIn('"duration_s": 60.0', page)
        self.assertNotIn("</script>x", page)

    def test_server_serves_page_and_saves_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            results = Path(tmp) / "pvt.csv"
            server = PvtServer(("127.0.0.1", 0), results, person="filip", checkpoint="T0", once=True, out=io.StringIO())
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_address[1]}"
            try:
                with urllib.request.urlopen(base + "/") as response:
                    page = response.read().decode("utf-8")
                self.assertIn("window.PVT_CONFIG", page)
                self.assertIn('"person": "filip"', page)

                bad = urllib.request.Request(base + "/api/result", data=b'{"person": ""}', method="POST",
                                             headers={"Content-Type": "application/json"})
                with self.assertRaises(urllib.error.HTTPError) as ctx:
                    urllib.request.urlopen(bad)
                self.assertEqual(ctx.exception.code, 400)

                body = json.dumps({"person": "filip", "checkpoint": "T0", "rts_ms": [240, 260, 400],
                                   "anticipations": 0, "duration_s": 180}).encode("utf-8")
                good = urllib.request.Request(base + "/api/result", data=body, method="POST",
                                              headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(good) as response:
                    data = json.loads(response.read().decode("utf-8"))
                self.assertTrue(data["ok"])
                self.assertEqual(data["result"]["lapses"], 1)
            finally:
                thread.join(timeout=5)
                server.server_close()
            self.assertFalse(thread.is_alive(), "server should stop after the first saved result with once=True")
            self.assertEqual(len(results.read_text(encoding="utf-8").splitlines()), 2)


if __name__ == "__main__":
    unittest.main()
