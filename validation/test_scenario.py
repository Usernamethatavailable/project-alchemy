"""Check that public fixtures can be prepared outside this checkout safely."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ScenarioTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def prepare(self, destination):
        return subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(ROOT / "validation/prepare_scenario.py"),
             str(destination)], cwd=self.folder, capture_output=True, encoding="utf-8",
        )

    def test_prepare_in_new_directory_and_find_only_matching_history(self):
        destination = self.folder / "换个目录" / "scenario"
        run = self.prepare(destination)
        self.assertEqual(run.returncode, 0, run.stderr)
        locations = json.loads(run.stdout)
        lookup = subprocess.run(
            [sys.executable, "-B", "-X", "utf8",
             str(ROOT / "project-salvage/scripts/find_project_history.py"),
             locations["project"], "--codex-home", locations["codex_home"]],
            cwd=self.folder, capture_output=True, encoding="utf-8",
        )
        self.assertEqual(lookup.returncode, 0, lookup.stderr)
        matches = json.loads(lookup.stdout)["matches"]
        self.assertEqual([row["thread_id"] for row in matches], ["fixture-target"])
        self.assertEqual(Path(matches[0]["source"]).parent.name, "archived_sessions")
        source = ROOT / "validation/fixtures/path-entry/history-store/archived_sessions/target.jsonl"
        self.assertIn("__PROJECT_ROOT__", source.read_text(encoding="utf-8"))

    def test_existing_directory_is_never_overwritten(self):
        destination = self.folder / "existing"
        destination.mkdir()
        marker = destination / "keep.txt"
        marker.write_text("unchanged", encoding="utf-8")
        run = self.prepare(destination)
        self.assertNotEqual(run.returncode, 0)
        self.assertEqual(marker.read_text(encoding="utf-8"), "unchanged")
        self.assertEqual(list(destination.iterdir()), [marker])


if __name__ == "__main__":
    unittest.main()
