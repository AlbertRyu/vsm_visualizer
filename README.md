# vsm_visualizer
A small form-factor VSM Visualizer for a short look and comparison of the PPMS VSM Data.

## Basic starter app

This repository now includes a basic DearPyGui app that:

- Uses a left-right split layout
- Left panel: table listing `.dat/.data` files in current directory
- Right panel: matplotlib preview image rendered from your `ppms_toolkit`
- Does not implement reader/processing/plotting logic locally

### Run

```bash
python -m pip install -r requirements.txt
python app.py
```

### Notes on `ppms_toolkit` integration

`src/vsm_visualizer/ppms_adapter.py` is the integration point. It currently tries these APIs:

- `ppms_toolkit.plot_file(path)`
- `ppms_toolkit.plot_dat(path)`
- `ppms_toolkit.plot_datafile(path)`
- `ppms_toolkit.create_figure(path)`
- `ppms_toolkit.build_figure(path)`

Your toolkit plotting entrypoint should return a matplotlib `Figure`.
If your toolkit uses a different entrypoint name, update `FIGURE_ENTRYPOINT_CANDIDATES` in `PPMSToolkitAdapter`.
