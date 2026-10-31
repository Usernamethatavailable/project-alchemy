"""Find project-associated Codex records without reading message bodies.

Supports session_meta headers and threads metadata in existing state_*.sqlite.
Only reads files and writes a compact JSON manifest to stdout. Python 3.9+.
"""

import argparse
from contextlib import closing
from datetime import datetime, timezone
import json
import ntpath
import os
from pathlib import Path
import posixpath
import sqlite3
import sys
from urllib.parse import unquote, urlsplit


HEADER_LIMIT = 512 * 1024


def path_key(value):
    """Normalize native paths and file URIs without collapsing name prefixes."""
    if value.startswith("file:"):
        uri = urlsplit(value)
        value = unquote(uri.path)
        if uri.netloc and uri.netloc != "localhost":
            value = "//" + uri.netloc + value
        elif len(value) > 2 and value[0] == "/" and value[2] == ":":
            value = value[1:]
    # Extended Windows paths name the same directory as their ordinary form.
    windows = value.replace("/", "\\")
    if windows.lower().startswith("\\\\?\\unc\\"):
        value = "\\\\" + windows[8:]
    elif windows.startswith("\\\\?\\"):
        value = windows[4:]
    if ntpath.splitdrive(value)[0]:
        return ntpath.normcase(ntpath.normpath(value)).replace("\\", "/")
    return posixpath.normpath(value)


def belongs_to(cwd, root):
    key, base = path_key(cwd), path_key(str(root))
    return key == base or key.startswith(base.rstrip("/") + "/")


def indexed_records(codex_home, roots):
    """Read only locating metadata, including rollouts stored as .jsonl.zst."""
    databases = sorted(codex_home.glob("state_*.sqlite"))
    matches, errors, scanned = [], [], 0
    for database in databases:
        try:
            with closing(sqlite3.connect(database.resolve().as_uri() + "?mode=ro",
                                         uri=True, timeout=1)) as connection:
                connection.execute("PRAGMA query_only=ON")
                columns = {row[1] for row in connection.execute("PRAGMA table_info(threads)")}
                if not {"id", "cwd", "rollout_path"}.issubset(columns):
                    errors.append({"path": str(database), "error": "unrecognized_schema"})
                    continue
                timestamp_column = "created_at" if "created_at" in columns else "NULL"
                rows = connection.execute(
                    "SELECT id, cwd, rollout_path, " + timestamp_column + " FROM threads")
                for thread_id, cwd, rollout, timestamp in rows:
                    scanned += 1
                    if not isinstance(cwd, str):
                        errors.append({"path": str(database), "error": "unrecognized_index_row"})
                        continue
                    association = next((label for root, label in roots if belongs_to(cwd, root)), None)
                    if not association:
                        continue
                    detail = {"path": str(database), "thread_id": thread_id}
                    if not isinstance(rollout, str) or not rollout:
                        errors.append({**detail, "error": "unrecognized_index_row"})
                        continue
                    path = Path(rollout)
                    if not path.is_absolute():
                        path = codex_home / path
                    detail["source"] = str(path)
                    if not rollout.lower().endswith((".jsonl", ".jsonl.zst")):
                        errors.append({**detail, "error": "unrecognized_record_format"})
                        continue
                    try:
                        # Open only to check access; never read or decompress the record.
                        with path.open("rb"):
                            pass
                    except FileNotFoundError:
                        errors.append({**detail, "error": "missing_record"})
                        continue
                    except OSError as error:
                        errors.append({**detail, "error": type(error).__name__})
                        continue
                    if isinstance(timestamp, (int, float)):
                        try:
                            timestamp = datetime.fromtimestamp(timestamp, timezone.utc).isoformat()
                        except (ValueError, OverflowError, OSError):
                            errors.append({**detail, "error": "unrecognized_timestamp"})
                            timestamp = None
                    matches.append({"source": str(path), "thread_id": thread_id, "cwd": cwd,
                                    "timestamp": timestamp, "association": association})
        except (OSError, sqlite3.Error) as error:
            errors.append({"path": str(database), "error": type(error).__name__})
    return matches, databases, scanned, errors


def discover(project, codex_home, related_roots, limit, max_files):
    roots = [(project, "project")] + [(p, "related-root") for p in related_roots]
    directories = [codex_home / name for name in ("sessions", "archived_sessions")
                   if (codex_home / name).is_dir()]
    paths, scan_errors = [], []
    for directory in directories:
        # os.walk skips linked directories; report inaccessible subtrees explicitly.
        def onerror(error):
            scan_errors.append({"path": str(error.filename), "error": type(error).__name__})

        for folder, _, filenames in os.walk(directory, onerror=onerror, followlinks=False):
            for filename in filenames:
                path = Path(folder) / filename
                if filename.endswith(".jsonl") and not path.is_symlink():
                    paths.append(path)
    paths.sort(key=lambda p: (p.name, str(p)), reverse=True)
    matches, unreadable, unrecognized = [], 0, 0
    for path in paths[:max_files]:
        try:
            with path.open("rb") as handle:
                header = handle.readline(HEADER_LIMIT + 1)
            if len(header) > HEADER_LIMIT:
                unrecognized += 1
                continue
            record = json.loads(header.decode("utf-8-sig"))
            payload = record.get("payload") if isinstance(record, dict) else None
            if (record.get("type") != "session_meta" or not isinstance(payload, dict)
                    or not isinstance(payload.get("cwd"), str)):
                unrecognized += 1
                continue
            association = next((label for root, label in roots
                                if belongs_to(payload["cwd"], root)), None)
            if association:
                matches.append({
                    "source": str(path),
                    "thread_id": payload.get("id") or payload.get("session_id"),
                    "cwd": payload["cwd"],
                    "timestamp": payload.get("timestamp"),
                    "association": association,
                })
        except OSError:
            unreadable += 1
        except (ValueError, UnicodeError, AttributeError):
            unrecognized += 1
    indexed, databases, index_rows, index_errors = indexed_records(codex_home, roots)
    unique, thread_ids, sources = [], set(), set()
    # Valid headers win over a stale or duplicate index entry.
    for match in matches + indexed:
        thread_id, source = match["thread_id"], path_key(match["source"])
        identity = str(thread_id) if thread_id else None
        duplicate = (identity is not None and identity in thread_ids) or source in sources
        if identity is not None:
            thread_ids.add(identity)
        sources.add(source)
        if not duplicate:
            unique.append(match)
    matches = sorted(unique, key=lambda r: (str(r["timestamp"] or ""), r["source"]), reverse=True)
    return {
        "project": str(project),
        "codex_home": str(codex_home),
        "history_directories": [str(p) for p in directories],
        "candidate_files": len(paths),
        "scanned_files": min(len(paths), max_files),
        "scan_truncated": len(paths) > max_files,
        "unreadable_files": unreadable,
        "unrecognized_files": unrecognized,
        "scan_errors": scan_errors,
        "index_databases": [str(p) for p in databases],
        "scanned_index_rows": index_rows,
        "index_errors": index_errors,
        "matched_count": len(matches),
        "results_truncated": len(matches) > limit,
        "matches": matches[:limit],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--codex-home", type=Path,
                        default=Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex"))
    parser.add_argument("--related-root", type=Path, action="append", default=[],
                        help="A verified related absolute path; may be an old location (repeatable).")
    parser.add_argument("--limit", type=int, default=20, help="Maximum returned records.")
    parser.add_argument("--max-files", type=int, default=10000,
                        help="Maximum JSONL headers to inspect; does not limit directory listing.")
    args = parser.parse_args()
    if args.limit < 1 or args.max_files < 1:
        parser.error("--limit and --max-files must be positive")
    if not args.project.expanduser().is_dir():
        parser.error("directory does not exist or is inaccessible: " + str(args.project))
    for path in args.related_root:
        if not path.expanduser().is_absolute():
            parser.error("--related-root must be an absolute path: " + str(path))
    result = discover(args.project.expanduser().resolve(), args.codex_home.expanduser().resolve(),
                      [p.expanduser().resolve() for p in args.related_root],
                      args.limit, args.max_files)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
