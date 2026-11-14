"""Tests for the CI hygiene scripts in .github/scripts (naming, secrets, links, notebooks)."""

import importlib.util
import re
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / ".github" / "scripts"


def load(name: str):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RepoChecks(unittest.TestCase):
    def setUp(self):
        self.mod = load("check-repo")

    def test_good_names(self):
        for path in ("docs/pitch.md", "src/wachta/index.py", "README.md", "data/analysis/01-recordings-quality.ipynb",
                     "tests/test-index.py", ".github/ISSUE_TEMPLATE/zadanie.md"):
            self.assertIsNone(self.mod.check_name(path), path)

    def test_bad_names(self):
        for path in ("docs/Plan Projektu.md", "docs/plan-projektu-żółć.md", "docs/MyNotes.md", "pomysly-adi/final_v2.md"):
            self.assertIsNotNone(self.mod.check_name(path), path)

    def test_recordings_are_exempt(self):
        self.assertIsNone(self.mod.check_name("data/recordings/subj-1_ses-S001_task-adi_test_run-001_raw.fif"))

    def test_secret_patterns(self):
        patterns = self.mod.SECRET_PATTERNS
        samples = {
            "private key": "-----BEGIN RSA PRIVATE KEY-----",
            "AWS access key": "AKIAABCDEFGHIJKLMNOP",
            "GitHub token": "ghp_" + "a" * 36,
            "generic secret assignment": 'api_key = "abcdefghijklmnopqrstuvwxyz123456"',
        }
        for name, text in samples.items():
            self.assertTrue(patterns[name].search(text), name)
        for harmless in ("password policy is described in docs", "token = 5", 'name = "wachta"'):
            self.assertFalse(any(p.search(harmless) for p in patterns.values()), harmless)


class LinkChecks(unittest.TestCase):
    def setUp(self):
        self.mod = load("check-links")

    def test_link_regex_finds_relative_targets(self):
        line = "See [plan](plan-projektu.md), ![fig](img/x.png) and [web](https://example.com)."
        targets = [(m.group(1) or m.group(2)) for m in self.mod.LINK.finditer(line)]
        self.assertEqual(targets, ["plan-projektu.md", "img/x.png", "https://example.com"])

    def test_inline_code_is_ignored(self):
        cleaned = self.mod.INLINE_CODE.sub("", "use `[x](not-a-file.md)` here")
        self.assertFalse(self.mod.LINK.search(cleaned))


class NotebookChecks(unittest.TestCase):
    def setUp(self):
        self.mod = load("check-notebooks")

    def test_leak_regex(self):
        for text in ("/home/user/project/x", "/tmp/claude-0/work", "C:\\Users\\jan\\x", "/Users/jan/x", "/root/.cache"):
            self.assertTrue(self.mod.LEAK.search(text), text)
        self.assertFalse(self.mod.LEAK.search("data/recordings and ../recordings"))

    def test_ipython_lines_are_neutralised(self):
        code = "%pip install -q mne\n!ls\nx = 1\n"
        compile(self.mod.strip_ipython(code), "cell", "exec")

    def test_output_text_skips_images(self):
        output = {"output_type": "display_data", "data": {"image/png": "AAAA", "text/plain": ["hello"]}}
        self.assertEqual(self.mod.output_text(output), "hello")


class RegressionGate(unittest.TestCase):
    def test_summary_regex(self):
        mod = load("check-regression")
        text = "Razem: wykryto 4 z 4 bloków, 1 fałszywy alarm w 32 min poza blokiem (po kalibracji)."
        self.assertTrue(re.search(r"Razem: wykryto (\d+) z (\d+) bloków, (\d+) fałszyw", text))
        self.assertGreaterEqual(mod.MAX_FALSE_ALARMS, 1)


if __name__ == "__main__":
    unittest.main()
