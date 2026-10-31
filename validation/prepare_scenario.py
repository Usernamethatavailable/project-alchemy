"""Copy the public synthetic scenario and bind its metadata to a chosen directory."""

import argparse
import json
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    target = args.destination.expanduser().resolve()
    if target.exists():
        parser.error("destination already exists; choose a new directory")
    source = Path(__file__).parent / "fixtures/path-entry"
    shutil.copytree(source, target)
    project = target / "project"
    history = target / "history-store"
    for path in history.rglob("*.jsonl"):
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        for row in rows:
            if row.get("type") == "session_meta":
                token = row["payload"]["cwd"]
                if token == "__PROJECT_ROOT__":
                    row["payload"]["cwd"] = str(project)
                elif token == "__UNRELATED_ROOT__":
                    row["payload"]["cwd"] = str(project.with_name("project-old"))
                else:
                    raise ValueError("unknown fixture path token")
        path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
                        encoding="utf-8")
    print(json.dumps({"project": str(project), "codex_home": str(history)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
