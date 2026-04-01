# VSM Visualizer

A lightweight tool for visualizing and comparing PPMS VSM (Vibrating Sample Magnetometer) measurement data.

## Quick Start

Download the latest release from the [Releases](../../releases) page.

### Option 1 — Web App (Recommended)

**[Launch VSM Visualizer](http://ryunosuke.tech/vsm_visualizer/)** — hosted on GitHub Pages, always up to date.

Requires a **Chromium-based browser** (Chrome, Edge, Opera, Brave, etc.). Firefox and Safari are not supported.

1. Click **Open Folder** and select your data folder.
2. Select one or more `.dat` files and click **Render Selected**.

> **Privacy:** All data processing happens entirely in your browser. No files or data are ever uploaded or transmitted anywhere.
>
> **Prefer to run fully offline?** Download `vsm_visualizer.html` from the [Releases](../../releases) page and open it locally — identical functionality, no internet required.
>
> **Not sure where to start?** Download `example_data.zip` from the Releases page, extract it anywhere, and open the app inside one of the subfolders.

---

### Option 2 — Desktop App

A native desktop build is available for Windows and macOS.

| Platform | File |
| --- | --- |
| Windows | `vsm_visualizer_Windows.zip` → `vsm_visualizer.exe` |
| macOS | `vsm_visualizer_macOS.zip` → `vsm_visualizer.app` |

Place the executable inside your data folder and double-click to launch.

> ⚠️ **Antivirus warning:** The Windows executable is compiled from Python and is very likely to be flagged as malware by Windows Defender or other antivirus software. This is a known false positive for Python-compiled binaries. If you encounter this, use the Web App instead.

---

## Features

- Browse `.dat` files recursively from a working directory
- Auto-detect measurement mode: **MT** (Moment vs. Temperature) or **MH** (Moment vs. Magnetic Field)
- Select and overlay multiple curves in a single interactive plot
- Smart legend labels — strips common path prefix so labels stay readable
- Moment normalized by sample mass
- Light / Dark theme toggle
- Handles UTF-8 and ISO-8859-1 encoded PPMS data files

## Supported Data Format

PPMS VSM `.dat` files with a `[Data]` section header. The following columns are parsed:

| Column | Unit |
| --- | --- |
| Temperature | K |
| Magnetic Field | Oe |
| Moment | emu (normalized by mass if provided) |
| M. Std. Err. | emu |

## Run from Source

```bash
pip install -r requirements.txt
python app.py <path/to/data/directory>
```

## Project Structure

```text
vsm_visualizer/
├── src/vsm_visualizer/
│   ├── assets/                # Icon and font
│   ├── ui.py                  # DearPyGui application & plotting logic
│   └── vsm_data_processor.py  # PPMS data parser (Sample / Measurement)
├── web/
│   └── build_web.py           # Builds self-contained vsm_visualizer.html
├── .github/workflows/
│   └── build.yml              # GitHub Actions: auto-build & release
├── example_data/              # Sample PPMS VSM measurements
├── app.py                     # Entry point
└── pyproject.toml
```

## License

See [LICENSE](LICENSE).
