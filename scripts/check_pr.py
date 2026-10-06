#!/usr/bin/env python3
import json
import os
import subprocess
import sys

BASE = os.environ.get("BASE_REF", "main")
AUTHOR = os.environ.get("PR_AUTHOR", "").lower()
REPO = os.environ.get("REPO", "")
REPO_OWNER = REPO.split("/")[0].lower()


def out(args):
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout


def fail(message):
    print(f"::error::{message}")
    sys.exit(1)


def first_author(folder):
    try:
        raw = out(["gh", "api", "--paginate", f"repos/{REPO}/commits?sha={BASE}&path=presets/{folder}&per_page=100",
                   "--jq", ".[].author.login"])
    except subprocess.CalledProcessError:
        fail(f"could not look up who owns '{folder}'")
    logins = [line for line in raw.split() if line and line != "null"]
    if not logins:
        fail(f"could not look up who owns '{folder}'")
    return logins[-1].lower()


def main():
    if not AUTHOR:
        fail("missing PR_AUTHOR")
    if AUTHOR == REPO_OWNER:
        return
    changed = [p for p in out(["git", "diff", "--name-only", "--no-renames", f"origin/{BASE}...HEAD"]).splitlines() if p]
    outside = [p for p in changed if not p.startswith("presets/") or p.count("/") < 2]
    if outside:
        fail("this PR changes files outside presets/<name>/: " + ", ".join(outside))
    folders = sorted({p.split("/")[1] for p in changed})
    if len(folders) > 1:
        fail("one preset per pull request: " + ", ".join(folders))
    existing = [p.split("/")[1] for p in out(["git", "ls-tree", "--name-only", f"origin/{BASE}", "presets/"]).splitlines()]
    for folder in folders:
        clash = [e for e in existing if e.lower() == folder.lower() and e != folder]
        if clash:
            fail(f"'{folder}' clashes with the existing preset '{clash[0]}'")
        if folder in existing and first_author(folder) != AUTHOR:
            fail(f"'{folder}' belongs to someone else and can only be changed by its author")


main()
