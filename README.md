# end4-pCpresets

Community presets for the end4-pC Quickshell config. The shell reads this repository directly, so a preset merged here shows up in the Presets gallery for everyone.

Presets are plain files. Nothing is collected from anyone: the shell only downloads public files from this repository.

## Share your preset

1. In the shell open Dashboard → Presets, pick your preset and press **Export**. This creates a `.zip` in `~/.config/illogical-impulse/presets/`. The export already removes personal paths, API keys, commands and any setting that is not visual.
2. Unzip it into a folder named after the preset. The result must look like this:

   ```
   presets/MyPreset/
     MyPreset.json
     meta.json
     wallpaper.jpg
     ...other images
   ```

3. Add a `preview.png` (a screenshot of your desktop) and, optionally, `preview-lock.png`, then list them in `meta.json`:

   ```json
   {
     "preview": "preview.png",
     "screenshots": ["preview-lock.png"],
     "wallpapers": ["wallpaper.jpg"]
   }
   ```

4. Open a pull request. On GitHub you can do everything from the browser: **Add file → Upload files**, drop the folder inside `presets/`, and GitHub creates the fork and the PR for you.

A check runs on every pull request. If it fails, the log tells you which file and why.

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
