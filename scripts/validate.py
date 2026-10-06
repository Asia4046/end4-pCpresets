#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

ROOT = Path(__file__).resolve().parent.parent
PRESETS = ROOT / "presets"

AUTHOR_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,39}$")
ASSET_EXT = {".png", ".jpg", ".jpeg", ".webp"}
MAX_FILE = 10 * 1024 * 1024
MAX_PRESET = 30 * 1024 * 1024
MAX_FILES = 40
MAX_JSON = 300 * 1024
MAX_DEPTH = 8
MAX_NODES = 4000
MAX_PIXELS = 7680 * 4320

ALLOWED_TOP = {
    "appearance", "background", "bar", "calendar", "crosshair", "dock", "interactions",
    "launcher", "light", "lock", "media", "notifications", "osd", "osk", "overlay",
    "overview", "panelFamily", "profile", "regionSelector", "resources", "settings",
    "sidebar", "tray", "wallpaperSelector", "windows", "hyprland",
}
ALLOWED_HYPRLAND = {"decoration", "gaps", "animations", "general"}
FORBIDDEN_NESTED = {("appearance", "fonts"), ("bar", "weather")}
PRIVATE_KEYS = {"clipboardPins", "clipboardpins", "apiKey", "token", "password", "secret"}

ABS_PATH = re.compile(r"^(/|~|[A-Za-z]:[\\/]|file:)")
CMD_SUBST = re.compile(r"(\$\(|`)")
URL = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")

MAGIC = {
    ".png": [b"\x89PNG\r\n\x1a\n"],
    ".jpg": [b"\xff\xd8\xff"],
    ".jpeg": [b"\xff\xd8\xff"],
    ".webp": [b"RIFF"],
}


class Report:
    def __init__(self):
        self.errors = []

    def error(self, path, message):
        rel = path.relative_to(ROOT) if path.is_absolute() else path
        self.errors.append((str(rel), message))
        print(f"::error file={rel}::{message}")


def strings(node, trail=""):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from strings(value, f"{trail}.{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from strings(value, f"{trail}[{i}]")
    elif isinstance(node, str):
        yield trail, node


def shape(node, depth=1):
    if depth > MAX_DEPTH:
        return None
    count = 1
    children = []
    if isinstance(node, dict):
        children = list(node.values())
    elif isinstance(node, list):
        children = node
    for child in children:
        inner = shape(child, depth + 1)
        if inner is None:
            return None
        count += inner
    return count


def keys(node, trail=""):
    if isinstance(node, dict):
        for key, value in node.items():
            yield f"{trail}.{key}", str(key)
            yield from keys(value, f"{trail}.{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from keys(value, f"{trail}[{i}]")


def check_value_strings(report, path, data):
    pairs = list(strings(data)) + list(keys(data))
    for trail, value in pairs:
        candidates = [value]
        if value.lstrip().startswith("{"):
            try:
                inner = json.loads(value)
                candidates += [v for _, v in strings(inner)]
            except ValueError:
                pass
        for item in candidates:
            if ABS_PATH.match(item):
                report.error(path, f"absolute path in {trail}: {item[:60]!r}. Export the preset again from the shell.")
                return
            if URL.match(item):
                report.error(path, f"URL in {trail}: presets must not load anything from the internet")
                return
            if CMD_SUBST.search(item):
                report.error(path, f"command substitution in {trail}")
                return


def check_config(report, path, data):
    if not isinstance(data, dict):
        report.error(path, "preset must be a JSON object")
        return
    for key in data:
        if key == "_presetMeta":
            continue
        if key not in ALLOWED_TOP:
            report.error(path, f"key '{key}' is not allowed in shared presets")
    hypr = data.get("hyprland")
    if isinstance(hypr, dict):
        for key in hypr:
            if key not in ALLOWED_HYPRLAND:
                report.error(path, f"key 'hyprland.{key}' is not allowed in shared presets")
    for parent, child in FORBIDDEN_NESTED:
        if isinstance(data.get(parent), dict) and child in data[parent]:
            report.error(path, f"key '{parent}.{child}' is not allowed in shared presets")
    for trail, key in keys(data):
        if key in PRIVATE_KEYS:
            report.error(path, f"key '{trail.lstrip('.')}' holds private data and cannot be shared")
    nodes = shape(data)
    if nodes is None:
        report.error(path, f"settings are nested deeper than {MAX_DEPTH} levels")
        return
    if nodes > MAX_NODES:
        report.error(path, f"settings have too many entries ({nodes} > {MAX_NODES})")
        return
    check_value_strings(report, path, data)


def check_asset(report, path):
    ext = path.suffix.lower()
    head = path.read_bytes()[:12]
    if not any(head.startswith(sig) for sig in MAGIC[ext]):
        report.error(path, "file content does not match its image extension")
    elif ext == ".webp" and head[8:12] != b"WEBP":
        report.error(path, "file content does not match its image extension")
    elif Image is not None:
        try:
            with Image.open(path) as image:
                width, height = image.size
                if width * height > MAX_PIXELS:
                    report.error(path, f"image is larger than {MAX_PIXELS // 1000000} megapixels")
                    return
                image.load()
        except Exception:
            report.error(path, "image cannot be decoded")


def check_preset(report, folder):
    name = folder.name
    if not NAME_RE.match(name):
        report.error(folder, "folder name must be 1-40 letters, digits, '-' or '_'")
        return
    files = [p for p in folder.iterdir()]
    if len(files) > MAX_FILES:
        report.error(folder, f"too many files ({len(files)} > {MAX_FILES})")
    total = 0
    names = set()
    for item in files:
        if item.is_symlink() or item.is_dir():
            report.error(item, "symlinks and sub-folders are not allowed")
            continue
        size = item.stat().st_size
        total += size
        names.add(item.name)
        if size > MAX_FILE:
            report.error(item, f"file is larger than {MAX_FILE // 1048576} MB")
        ext = item.suffix.lower()
        if ext == ".json":
            if item.name not in (f"{name}.json", "meta.json"):
                report.error(item, f"only {name}.json and meta.json are allowed")
        elif ext not in ASSET_EXT:
            report.error(item, f"extension '{ext}' is not allowed (png, jpg, jpeg, webp only)")
        else:
            check_asset(report, item)
    if total > MAX_PRESET:
        report.error(folder, f"preset is larger than {MAX_PRESET // 1048576} MB")
    for required in (f"{name}.json", "meta.json"):
        if required not in names:
            report.error(folder, f"missing {required}")

    preset_json = folder / f"{name}.json"
    if preset_json.is_file():
        if preset_json.stat().st_size > MAX_JSON:
            report.error(preset_json, "preset JSON is too large")
        else:
            try:
                check_config(report, preset_json, json.loads(preset_json.read_text(encoding="utf-8")))
            except ValueError as exc:
                report.error(preset_json, f"invalid JSON: {exc}")

    meta_json = folder / "meta.json"
    if meta_json.is_file():
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
        except ValueError as exc:
            report.error(meta_json, f"invalid JSON: {exc}")
            return
        if not isinstance(meta, dict):
            report.error(meta_json, "meta.json must be a JSON object")
            return
        for trail, value in strings(meta):
            if trail == ".author":
                if not AUTHOR_RE.match(value):
                    report.error(meta_json, "author must be a GitHub user name")
                continue
            if value and ("/" in value or "\\" in value):
                report.error(meta_json, f"{trail} must be a file name, not a path")
            elif value and value not in names:
                report.error(meta_json, f"{trail} points to '{value}' which is not in the folder")


def main():
    report = Report()
    if len(sys.argv) > 1:
        folders = [PRESETS / arg for arg in sys.argv[1:]]
    else:
        folders = sorted(p for p in PRESETS.iterdir() if not p.name.startswith("."))
    for item in PRESETS.iterdir():
        if item.is_file() and not item.name.startswith("."):
            report.error(item, "presets/ must only contain preset folders")
    seen = {}
    for item in sorted(PRESETS.iterdir()):
        if item.is_dir():
            other = seen.setdefault(item.name.lower(), item.name)
            if other != item.name:
                report.error(item, f"name clashes with '{other}' when case is ignored")
    for folder in folders:
        if not folder.is_dir():
            report.error(folder, "not a folder")
            continue
        check_preset(report, folder)
    if report.errors:
        print(f"\n{len(report.errors)} problem(s) found")
        return 1
    print(f"OK: {len(folders)} preset(s) valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
