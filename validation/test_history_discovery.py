"""Behavior checks for the read-only local-history entry point."""

import importlib.util
import json
from contextlib import closing
import os
from pathlib import Path
import subprocess
import sqlite3
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "project-salvage/scripts/find_project_history.py"
SPEC = importlib.util.spec_from_file_location("history_discovery", SCRIPT)
HISTORY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HISTORY)


class HistoryDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "项目"
        self.project.mkdir()
        self.home = self.root / "codex"

    def record(self, name, cwd, archived=False, timestamp="2026-10-01T00:00:00Z"):
        folder = self.home / ("archived_sessions" if archived else "sessions")
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / (name + ".jsonl")
        header = {"type": "session_meta", "payload": {
            "id": name, "cwd": str(cwd), "timestamp": timestamp}}
        path.write_text(json.dumps(header, ensure_ascii=False) + '\n' +
                        '{"type":"message","text":"DO_NOT_ECHO_MESSAGE_BODY"}\n',
                        encoding="utf-8")
        return path

    def run_script(self, *extra, project=None):
        return subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(SCRIPT), str(project or self.project),
             "--codex-home", str(self.home), *extra],
            capture_output=True, encoding="utf-8", check=False,
        )

    def manifest(self, *extra):
        run = self.run_script(*extra)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertNotIn("DO_NOT_ECHO_MESSAGE_BODY", run.stdout)
        return json.loads(run.stdout)

    def index(self, rows, name="state_5.sqlite"):
        self.home.mkdir(parents=True, exist_ok=True)
        path = self.home / name
        with closing(sqlite3.connect(path)) as connection, connection:
            connection.execute("CREATE TABLE threads (id TEXT, cwd TEXT, rollout_path TEXT, "
                               "created_at INTEGER, first_user_message TEXT)")
            connection.executemany("INSERT INTO threads VALUES (?, ?, ?, ?, ?)", [
                (*row, "DO_NOT_ECHO_MESSAGE_BODY") for row in rows])
        return path

    def compressed_record(self, name):
        folder = self.home / "sessions"
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / (name + ".jsonl.zst")
        path.write_bytes(b"DO_NOT_ECHO_MESSAGE_BODY")
        return path

    def test_extended_windows_and_unc_paths_match_without_name_prefixes(self):
        cases = [
            (r"\\?\D:\Projects\App\src", "d:/projects/app", True),
            (r"\\?\D:\Projects\App-old", "d:/projects/app", False),
            (r"\\?\UNC\Server\Share\App\src", r"\\server\share\app", True),
            (r"\\?\UNC\Server\Share\App-old", r"\\server\share\app", False),
            ("//?/UNC/Server/Share/App", "file://server/share/app", True),
        ]
        for cwd, root, expected in cases:
            with self.subTest(cwd=cwd):
                self.assertEqual(HISTORY.belongs_to(cwd, root), expected)

    def test_index_finds_compressed_records_and_excludes_same_name_prefix(self):
        compressed = self.compressed_record("indexed")
        unrelated = self.compressed_record("unrelated")
        cwd = ("\\\\?\\" + str(self.project)) if os.name == "nt" else str(self.project)
        database = self.index([
            ("indexed", cwd, str(compressed), 1790812800),
            ("unrelated", str(self.project) + "-old", str(unrelated), 1790812800),
        ])
        before = database.read_bytes()
        data = self.manifest()
        self.assertEqual(data["matched_count"], 1)
        self.assertEqual(data["matches"][0]["source"], str(compressed))
        self.assertEqual(data["matches"][0]["thread_id"], "indexed")
        self.assertEqual(data["index_databases"], [str(database)])
        self.assertEqual(data["scanned_index_rows"], 2)
        self.assertEqual(data["scanned_files"], 0)
        self.assertEqual(database.read_bytes(), before)

    def test_index_and_headers_deduplicate_by_thread_id_or_record_path(self):
        header = self.record("shared", self.project)
        compressed = self.compressed_record("duplicate")
        rows = [("shared", str(self.project), str(compressed), 1790812800),
                ("alias", str(self.project), str(header), 1790812800)]
        self.index(rows)
        self.index(rows, "state_6.sqlite")
        data = self.manifest()
        self.assertEqual(data["matched_count"], 1)
        self.assertEqual(data["matches"][0]["source"], str(header))
        self.assertEqual(data.get("scanned_index_rows"), 4)

    def test_stale_index_does_not_replace_a_valid_header_match(self):
        header = self.record("shared", self.project)
        self.index([("shared", str(self.project), str(self.home / "missing.jsonl.zst"), 0)])
        data = self.manifest()
        self.assertEqual(data["matched_count"], 1)
        self.assertEqual(data["matches"][0]["source"], str(header))
        self.assertTrue(data.get("index_errors"))
        self.assertEqual(data["index_errors"][0]["error"], "missing_record")

    def test_unknown_schema_and_corrupt_index_are_reported(self):
        self.home.mkdir()
        unknown = self.home / "state_1.sqlite"
        with closing(sqlite3.connect(unknown)) as connection, connection:
            connection.execute("CREATE TABLE threads (id TEXT, cwd TEXT)")
        (self.home / "state_2.sqlite").write_bytes(b"not a database")
        (self.home / "unrelated.sqlite").write_bytes(b"not a database")
        data = self.manifest()
        self.assertEqual(data["matched_count"], 0)
        self.assertEqual(len(data.get("index_databases", [])), 2)
        self.assertEqual({error["error"] for error in data["index_errors"]},
                         {"unrecognized_schema", "DatabaseError"})

    def test_unknown_record_format_is_reported_without_reading_contents(self):
        unknown = self.home / "unknown.data"
        self.home.mkdir()
        unknown.write_text("DO_NOT_ECHO_MESSAGE_BODY", encoding="utf-8")
        self.index([("unknown", str(self.project), str(unknown), 0)])
        data = self.manifest()
        self.assertEqual(data["matched_count"], 0)
        self.assertTrue(data.get("index_errors"))
        self.assertEqual(data["index_errors"][0]["error"], "unrecognized_record_format")

    def test_index_reads_committed_wal_metadata_without_changing_database(self):
        compressed = self.compressed_record("wal")
        database = self.index([])
        connection = sqlite3.connect(database)
        self.addCleanup(connection.close)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("INSERT INTO threads VALUES (?, ?, ?, ?, ?)",
                           ("wal", str(self.project), str(compressed), 1790812800,
                            "DO_NOT_ECHO_MESSAGE_BODY"))
        connection.commit()
        wal = Path(str(database) + "-wal")
        before = (database.read_bytes(), wal.read_bytes())
        data = self.manifest()
        self.assertEqual(data["matched_count"], 1)
        self.assertEqual(data["matches"][0]["thread_id"], "wal")
        self.assertEqual((database.read_bytes(), wal.read_bytes()), before)

    def test_index_results_keep_output_limit_and_header_scan_budget(self):
        self.record("a", self.project, timestamp="2026-10-01T00:00:00Z")
        self.record("b", self.project, timestamp="2026-10-02T00:00:00Z")
        compressed = self.compressed_record("newest")
        self.index([("newest", str(self.project), str(compressed), 1790985600)])
        data = self.manifest("--limit", "1", "--max-files", "1")
        self.assertEqual(data["matched_count"], 2)
        self.assertEqual(data["matches"][0]["thread_id"], "newest")
        self.assertTrue(data["results_truncated"])
        self.assertTrue(data["scan_truncated"])
        self.assertEqual(data["scanned_files"], 1)
        self.assertEqual(data["scanned_index_rows"], 1)

    def test_matches_root_subdirectory_and_archive_but_not_name_prefix(self):
        self.record("root", self.project)
        self.record("child", self.project / "src", archived=True)
        self.record("other", self.project.with_name(self.project.name + "-old"))
        data = self.manifest()
        self.assertEqual({r["thread_id"] for r in data["matches"]}, {"root", "child"})
        self.assertEqual(data["scanned_files"], 3)
        self.assertEqual(data["matched_count"], 2)

    def test_accepts_file_uri_and_native_windows_case_rules(self):
        self.record("uri", self.project.as_uri())
        if os.name == "nt":
            self.record("case", str(self.project).upper().replace("\\", "/"))
        data = self.manifest()
        expected = {"uri", "case"} if os.name == "nt" else {"uri"}
        self.assertEqual({r["thread_id"] for r in data["matches"]}, expected)

    def test_related_worktree_requires_explicit_existing_root(self):
        related = self.root / "worktree"
        related.mkdir()
        self.record("worktree", related)
        self.assertEqual(self.manifest()["matched_count"], 0)
        data = self.manifest("--related-root", str(related))
        self.assertEqual(data["matches"][0]["thread_id"], "worktree")
        self.assertEqual(data["matches"][0]["association"], "related-root")

    def test_confirmed_old_directory_can_match_after_project_was_moved(self):
        old = self.root / "old-project-location"
        self.record("before-move", old)
        self.assertFalse(old.exists())
        data = self.manifest("--related-root", str(old))
        self.assertEqual(data["matches"][0]["thread_id"], "before-move")
        self.assertFalse(old.exists())

    def test_limits_output_and_reports_unrecognized_records(self):
        self.record("older", self.project, timestamp="2026-10-01T00:00:00Z")
        self.record("newer", self.project, timestamp="2026-10-02T00:00:00Z")
        folder = self.home / "sessions"
        (folder / "bad.jsonl").write_text("not JSON\n", encoding="utf-8")
        data = self.manifest("--limit", "1")
        self.assertEqual(data["matched_count"], 2)
        self.assertEqual(data["matches"][0]["thread_id"], "newer")
        self.assertTrue(data["results_truncated"])
        self.assertEqual(data["unrecognized_files"], 1)

    def test_missing_history_and_invalid_paths_are_explicit(self):
        data = self.manifest()
        self.assertEqual(data["history_directories"], [])
        self.assertEqual(data["matched_count"], 0)
        run = self.run_script(project=self.root / "missing")
        self.assertNotEqual(run.returncode, 0)
        self.assertNotIn("Traceback", run.stderr)
        self.assertFalse((self.root / "missing").exists())
        self.assertNotEqual(self.run_script("--limit", "0").returncode, 0)

    def test_scan_budget_and_oversized_headers_report_incomplete_coverage(self):
        self.record("a", self.project)
        self.record("b", self.project)
        data = self.manifest("--max-files", "1")
        self.assertTrue(data["scan_truncated"])
        self.assertEqual(data["scanned_files"], 1)
        (self.home / "sessions/large.jsonl").write_text("x" * (512 * 1024 + 1), encoding="utf-8")
        data = self.manifest()
        self.assertEqual(data["unrecognized_files"], 1)


if __name__ == "__main__":
    unittest.main()
