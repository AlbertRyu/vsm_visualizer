# VSM Visualizer

A lightweight desktop application for visualizing and comparing PPMS VSM (Vibrating Sample Magnetometer) measurement data.

## Quick Start

No installation required. Download the latest release for your platform from the [Releases](../../releases) page.

| Platform | File |
| --- | --- |
| Windows | `VSM_Visualizer.exe` |
| macOS | `VSM_Visualizer.app` |

1. Copy the executable into your data folder (the one containing `.dat` / `.data` files).
2. Double-click to launch — the app opens with that folder as the working directory.
3. Select files and click **Render Selected File** to plot.

---

## Features

- Browse `.dat` / `.data` files recursively from a working directory
- Auto-detect measurement mode: **MT** (Moment vs. Temperature) or **MH** (Moment vs. Magnetic Field)
- Select and overlay multiple curves in a single interactive plot
- Smart legend labels — strips common path prefix so labels stay readable
- Moment normalized by sample mass
- Light / Dark theme toggle
- Handles UTF-8 and ISO-8859-1 encoded PPMS data files

## Supported Data Format

PPMS VSM `.DAT` files with a `[Data]` section header. The following columns are parsed:

| Column | Unit |
| --- | --- |
| Temperature | K |
| Magnetic Field | Oe |
| Moment | emu (normalized by mass if provided) |
| M. Std. Err. | emu |

## Installation

```bash
python -m pip install -r requirements.txt
```

**Dependencies:**

| Package | Version |
| --- | --- |
| dearpygui | ≥ 1.11.1 |
| dearpygui-ext | latest |
| matplotlib | ≥ 3.8.0 |
| numpy | ≥ 1.24.0 |

## Usage

```bash
python -m vsm_visualizer <path/to/data/directory>
```

Or point it at the bundled example data:

```bash
python -m vsm_visualizer example_data/b-axis
```

### Workflow

1. On launch, the left panel lists all `.dat` / `.data` files found recursively under the working directory.
2. Each file shows its size and an auto-detected **MT / MH** radio button — switch it if the auto-detection is wrong.
3. Select one or more files (same mode only) using the checkboxes.
4. Click **Render Selected File** to plot. Axes and legend update automatically.
5. Use **Refresh Files** to reload after adding new files, and **Toggle Theme** to switch between light and dark mode.

## Project Structure

```text
vsm_visualizer/
├── src/vsm_visualizer/
│   ├── assets/                # Icon and font bundled into the app
│   ├── __init__.py
│   ├── ui.py                  # DearPyGui application & plotting logic
│   └── vsm_data_processor.py  # PPMS data parser (Sample / Measurement)
├── .github/workflows/
│   └── build.yml              # GitHub Actions: auto-build & release
├── example_data/              # Sample PPMS VSM measurements
├── app.py                     # Entry point
├── pyproject.toml
└── LICENSE
```

## License

See [LICENSE](LICENSE).
