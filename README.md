# VSM Visualizer

A lightweight desktop application for visualizing and comparing PPMS VSM (Vibrating Sample Magnetometer) measurement data.

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
│   ├── __init__.py
│   ├── ui.py                  # DearPyGui application & plotting logic
│   └── vsm_data_processor.py  # PPMS data parser (Sample / Measurement)
├── example_data/
│   ├── axis-1/                # MH and MT data (axis 1)
│   ├── axis-2/                # MH and MT data (axis 2)
│   └── b-axis/                # MH and MT data (B-axis), incl. ZFC/FC curves
├── requirements.txt
└── LICENSE
```

## Example Data

The `example_data/` directory contains real PPMS VSM measurements along different crystallographic axes, including:

- ZFC / FC M-T curves at various applied fields (1000 Oe, 18 000 Oe, 22 000 Oe)
- M-H hysteresis loops at temperatures from 2 K to 30 K
- High-field M-T sweeps at 8 T, 10 T, and 12 T (B-axis)

## License

See [LICENSE](LICENSE).
