<div align="center">

# end4-pCpresets

**Community presets for the end4-pC Quickshell config.**
Share your desktop with one button. Try someone else's with another.

[![Validate presets](https://github.com/pctrade/end4-pCpresets/actions/workflows/validate.yml/badge.svg)](https://github.com/pctrade/end4-pCpresets/actions/workflows/validate.yml)

[Share a preset](#share-your-preset) · [Use a preset](#use-a-preset) · [Rules](#rules-the-check-enforces) · [Remove or report](#remove-or-report-a-preset)

</div>

---

## How it works

The shell reads this repository directly. A preset merged here shows up in the **Presets** gallery of everyone using the shell.

Presets are plain files. Nothing is collected from anyone: the shell only downloads public files from GitHub, and nothing runs when you browse.

## Use a preset

Open **Dashboard → Presets**, pick a preset from the gallery and choose what to do:

| Button | What it does |
|---|---|
| **Download** | Copies the preset to the shell's cache so you can see its bar, colors and widgets and apply it. |
| **Install** | Keeps the preset for good. Its images are copied to your folders and it is saved in **My presets**. |

Where **Install** puts the images:

| Image | Folder |
|---|---|
| Wallpapers (main, centered, collage, lock screen) | `~/Pictures/Wallpapers/` |
| Avatar | `~/Pictures/avatar/` |
| Everything else (banner, custom image, sticker) | `~/Pictures/preset-assets/` |

An image you already have is never copied twice, and nothing of yours is overwritten. If a file has the same name but different content, the copy gets a short suffix such as `photo-a1b2c3d4.jpg`.

> [!NOTE]
> Presets installed from the gallery belong to their author. They cannot be exported or uploaded again.

## Share your preset

> [!IMPORTANT]
> Everything you upload is **public**: the preset, its images (wallpaper, avatar, banner) and the preview. Only upload images you own or are free to share, and make sure the preview does not show personal data. By sending a preset you confirm you have the right to share its images. Maintainers may remove any preset at any time.

1. Open **Dashboard → Presets** and open one of your presets.
2. Press **Upload**. A file picker asks for a **preview image**. Pick a screenshot of your desktop.
3. The shell prepares a clean folder and opens three things: the folder, this repository's upload page and a notification.
4. Drag the folder into the GitHub page, press **Propose changes** and then **Create pull request**. GitHub makes the fork for you, no git needed.
5. A check validates the pull request. When a maintainer merges it, the preset appears in everyone's gallery.

To update a preset you already shared, repeat the steps with the same name. The pull request replaces its files.

### What a preset does not include

The export keeps only visual settings. These never leave your computer:

- Fonts, language, time, battery, audio and sounds
- API keys, accounts and anything from services (AI, weather, updates)
- Commands and scripts, including the apps you set as terminal or launcher
- Keyboard and input settings
- Your personal paths: they are turned into plain file names

### A good preview

- 16:9, a full screenshot of the desktop with the bar visible.
- No notifications, usernames, e-mails or private windows.
- Do not edit the preset JSON by hand. Export it again instead.

<details>
<summary><b>Without the Upload button</b></summary>

<br>

Export the preset as a ZIP, unzip it into `presets/<name>/`, add your `preview.png` and list it in `meta.json`:

```json
{
  "preview": "preview.png",
  "screenshots": [],
  "wallpapers": ["wallpaper.jpg"]
}
```

Then open the pull request the same way.

If you use git, run the same check as the pull request before you push:

```
python3 scripts/validate.py
```

</details>

## Rules the check enforces

| Rule | Detail |
|---|---|
| Folder | One folder per preset inside `presets/`, named with letters, digits, `-` or `_` (up to 40 characters) |
| Files | Only `<name>.json`, `meta.json` and `png`, `jpg`, `jpeg` or `webp` images. No videos, scripts, archives or sub-folders |
| Size | Up to 10 MB per file and 30 MB per preset. The Upload button shrinks bigger images automatically (4K at most) |
| Settings | Only visual settings. Keys that run commands (`apps`, `custom`, `hacks`, `policies`, `conflictKiller`) and most of `hyprland` are rejected. Decoration, gaps, animations and general are allowed |
| Values | No absolute paths (`/home/you/...`), no URLs (`https://...`) and no command substitution |
| `meta.json` | May only name files that exist in the folder |

## Remove or report a preset

- **Remove your own preset:** open a pull request that deletes your folder from `presets/`, or open an issue with its name.
- **Report a preset:** open an issue with the preset name and the reason (offensive content, images you do not own, personal data). Reports about personal data are handled first.

## Maintainers

- Review the **Files changed** tab. The check blocks pull requests from others that touch anything outside `presets/`, but a green check does not replace looking at the previews.
- `main` is protected by a ruleset: a pull request is required and the `Validate presets` check must pass.
- Never merge a pull request that changes `.github/` or `scripts/` unless you wrote it.
