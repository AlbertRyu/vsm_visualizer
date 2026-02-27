from __future__ import annotations

from pathlib import Path

import dearpygui.dearpygui as dpg

from .vsm_data_processor import Sample, Measurement


class VisualizerState:
    def __init__(self, start_dir: Path) -> None:
        self.current_dir = start_dir
        self.files: list[Path] = []
        self.selected_file: Path | None = None


def run_app(start_dir: Path) -> None:
    state = VisualizerState(start_dir=start_dir)

    dpg.create_context()
    dpg.create_viewport(title="VSM Data Visualizer", width=1280, height=720)

    with dpg.window(label="PPMS Data Browser", width=1280, height=720):
        with dpg.group(horizontal=True):
            with dpg.child_window(width=380, height=680, border=True):
                dpg.add_text(f"Working directory:\n{state.current_dir}", wrap=360)
                dpg.add_spacer(height=6)
                dpg.add_button(label="Refresh Files", width=160, callback=lambda: refresh_files(state))
                dpg.add_spacer(height=6)
                with dpg.table(
                    tag="file_table",
                    header_row=True,
                    resizable=True,
                    borders_innerH=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_outerV=True,
                    row_background=True,
                    scrollY=True,
                    height=520,
                ):
                    dpg.add_table_column(label="Data File")
                    dpg.add_table_column(label="Size (KB)")
                dpg.add_spacer(height=6)
                dpg.add_text("", tag="status_text", wrap=360)

            with dpg.child_window(width=-1, height=680, border=True):
                dpg.add_text("Temp vs Moment", tag="plot_title")
                dpg.add_spacer(height=6)
                dpg.add_button(label="Render Selected File", width=200, callback=lambda: plot_selected_file(state))
                dpg.add_spacer(height=8)
                dpg.add_text("No file selected.", tag="selected_file_text", wrap=820)
                dpg.add_spacer(height=8)

                with dpg.plot(label="", height=-1, width=-1):

                    dpg.add_plot_legend()

                    dpg.add_plot_axis(dpg.mvXAxis, label="X", tag="x_axis")

                    with dpg.plot_axis(dpg.mvYAxis, label="Moment (emu)", tag="y_axis"):
                        dpg.add_line_series([], [], label="Moment", tag="main_series")

    dpg.setup_dearpygui()
    refresh_files(state)
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


def refresh_files(state: VisualizerState) -> None:
    state.files = sorted(
        [
            p
            for p in state.current_dir.rglob("*")
            if p.is_file() and p.suffix.lower() in {".dat", ".data"}
        ],
        key=lambda p: str(p.relative_to(state.current_dir)).lower(),
    )
    rows = dpg.get_item_children("file_table", 1) or []
    for row in rows:
        dpg.delete_item(row)

    for file_path in state.files:
        size_kb = file_path.stat().st_size / 1024
        relative_label = str(file_path.relative_to(state.current_dir))
        with dpg.table_row(parent="file_table"):
            dpg.add_selectable(
                label=relative_label,
                callback=on_select_file,
                user_data=(state, file_path)
            )
            dpg.add_text(f"{size_kb:.1f}")

    if state.files:
        dpg.set_value("status_text", f"Detected {len(state.files)} data files.")
    else:
        dpg.set_value("status_text", "No .dat/.data files found in current directory.")


def on_select_file(sender, app_data, user_data):
    state, file_path = user_data
    state.selected_file = file_path
    dpg.set_value("selected_file_text", f"Selected: {file_path}")
    dpg.set_value("status_text", f"Selected {file_path}")



def plot_selected_file(state: VisualizerState) -> None:

    test_sample = Sample(name='Test Sample', mass=1)

    if not state.selected_file:
        dpg.set_value("status_text", "Please select a data file first.")
        return
    
    m = Measurement(sample=test_sample, filepath=str(state.selected_file))
    df = m.dataframe
    print(df.keys())

    import math

    T = df["Temperature (K)"]
    M = df["Moment (emu)"]

    T_clean = []
    M_clean = []

    for t, mom in zip(T, M):
        if not (math.isnan(t) or math.isnan(mom)):
            T_clean.append(t)
            M_clean.append(mom)

    dpg.set_value("main_series", [T_clean, M_clean])
    dpg.fit_axis_data("x_axis")
    dpg.fit_axis_data("y_axis")
