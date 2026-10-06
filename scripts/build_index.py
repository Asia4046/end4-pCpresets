#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRESETS = ROOT / "presets"
REPO = os.environ.get("REPO", "pctrade/end4-pCpresets")


def run(args):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True).stdout.strip()


def meta_author(folder):
    path = folder / "meta.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8")).get("author", "")
    except (OSError, ValueError, AttributeError):
        return ""
    return value if isinstance(value, str) else ""


def history_author(folder):
    sha = run(["git", "log", "--diff-filter=A", "-n", "1", "--format=%H", "--", f"presets/{folder.name}/{folder.name}.json"])
    if not sha:
        return ""
    login = run(["gh", "api", f"repos/{REPO}/commits/{sha}", "--jq", ".author.login"])
    return "" if login in ("", "null") else login


def updated_at(folder):
    return run(["git", "log", "-n", "1", "--format=%cI", "--", f"presets/{folder.name}"])


def main():
    entries = {}
    for folder in sorted(p for p in PRESETS.iterdir() if p.is_dir() and not p.name.startswith(".")):
        author = meta_author(folder) or history_author(folder)
        entries[folder.name] = {"author": author, "updated": updated_at(folder)}
    index = {
        "version": 1,
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "presets": entries,
    }
    json.dump(index, sys.stdout, indent=2)
    sys.stdout.write("\n")


main()
