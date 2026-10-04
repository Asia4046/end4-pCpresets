# end4-pCpresets

Community presets for the end4-pC Quickshell config. The shell reads this repository directly, so a preset merged here shows up in the Presets gallery for everyone.

Presets are plain files. Nothing is collected from anyone: the shell only downloads public files from this repository.

## Share your preset

Everything you upload is **public**: the preset, its images (wallpaper, avatar, banner) and the preview. Only upload images you own or are free to share, and make sure the preview does not show personal data.

1. In the shell open Dashboard → Presets and open one of your presets.
2. Press **Upload**. A file picker asks for a **preview image**, a screenshot of your desktop. Pick it.
3. The shell prepares a clean folder (personal paths, keys and anything that runs commands are removed) and opens three things: the folder, this repository's upload page and a notification.
4. Drag the folder into the GitHub page and press **Propose changes**, then **Create pull request**. GitHub makes the fork for you, no git needed.
5. A check validates the pull request. When a maintainer merges it, the preset appears in everyone's gallery.

To update a preset you already shared, do the same steps with the same name. The pull request will replace its files.

### Without the Upload button

Export the preset as a ZIP, unzip it into `presets/<name>/`, add your `preview.png` and list it in `meta.json`:

```json
{
  "preview": "preview.png",
  "screenshots": [],
  "wallpapers": ["wallpaper.jpg"]
}
```

Then open the pull request the same way.

## How the shell uses this repository

The shell lists the folders inside `presets/` and shows `preview.png` as the cover. Nothing is installed or run when browsing. When someone presses **Download**, the shell copies the preset's files to their cache and applies only visual settings. No data is sent to anyone: the shell only reads public files from GitHub.

## Rules the check enforces

- One folder per preset inside `presets/`, named with letters, digits, `-` or `_` (up to 40 characters).
- Only `<name>.json`, `meta.json` and `png`, `jpg`, `jpeg` or `webp` images. No videos, scripts, archives or sub-folders.
- Up to 10 MB per file and 30 MB per preset.
- Only visual settings. Keys that run commands (`apps`, `custom`, `hacks`, `policies`, `conflictKiller`) and the rest of `hyprland` except decoration, gaps, animations and general are rejected.
- No absolute paths (`/home/you/...`) and no command substitution in any value.
- `meta.json` may only name files that exist in the folder.

## Maintainers

- Review the **Files changed** tab. The check blocks PRs from others that touch anything outside `presets/`, but a green check does not replace looking at the previews.
- Turn on branch protection for `main` (Settings → Branches): require a pull request and a passing `Validate presets` check.
- Never merge a PR that changes `.github/` or `scripts/` unless you wrote it.
