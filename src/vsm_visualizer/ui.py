from __future__ import annotations

from pathlib import Path

import dearpygui.dearpygui as dpg

from .vsm_data_processor import Sample, Measurement
from dearpygui_ext import themes



class VisualizerState:
    def __init__(self, start_dir: Path) -> None:
        self.current_dir = start_dir
        self.files: list[Path] = []
        self.selected_files: set[Path] = set()
        self.file_modes: dict[Path, str] = {}
        self.dataframes: dict[Path, dict] = {}
        self.theme_state = "light"



def run_app(start_dir: Path) -> None:
    state = VisualizerState(start_dir=start_dir)

    dpg.create_context()
    dpg.create_viewport(title="VSM Data Visualizer", width=1280, height=720)

    dark_theme = themes.create_theme_imgui_dark()
    light_theme = themes.create_theme_imgui_light()

    dpg.bind_theme(light_theme)


    with dpg.window(label="PPMS Data Browser", width=1280, height=720):
        with dpg.group(horizontal=True):
            with dpg.child_window(width=480, height=680, border=True):
                dpg.add_text(f"Working directory:\n{state.current_dir}", wrap=360)
                dpg.add_spacer(height=6)
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Refresh Files", width=160, callback=lambda: refresh_files(state))
                    dpg.add_button(label="Toggle Theme", width=140, callback=lambda: toggle_theme(state))
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
                    policy=dpg.mvTable_SizingStretchProp,
                    scrollY=True,
                    height=520,
                ):
                    dpg.add_table_column(label="Data File")
                    dpg.add_table_column(label="Size(MB)")
                    dpg.add_table_column(label="Mode")

                dpg.add_spacer(height=6)
                dpg.add_text("", tag="status_text", wrap=360)

            with dpg.child_window(width=-1, height=680, border=True):
                dpg.add_text("VSM Plot", tag="plot_title")
                dpg.add_spacer(height=6)
                dpg.add_button(label="Render Selected File", width=200, callback=lambda: plot_selected_file(state))
                dpg.add_spacer(height=8)

                with dpg.plot(label="Simple Plot", tag="main_plot", height=-1, width=-1):

                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label="X", tag="x_axis")
                    dpg.add_plot_axis(dpg.mvYAxis, label="Moment (emu)", tag="y_axis")

    dpg.setup_dearpygui()
    refresh_files(state)
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

def toggle_theme(state):

    dark_theme = themes.create_theme_imgui_dark()
    light_theme = themes.create_theme_imgui_light()

    if state.theme_state == "dark":
        dpg.bind_theme(light_theme)
        state.theme_state = 'light'
        
    else:
        dpg.bind_theme(dark_theme)
        state.theme_state = 'dark'


def detect_mode(df):

    T = df["Temperature (K)"]
    H = df["Magnetic Field (Oe)"]

    T_span = max(T) - min(T)
    H_span = max(H) - min(H)

    if H_span > T_span:
        return "MH"
    else:
        return "MT"


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

    
    test_sample = Sample(name='Test Sample', mass=1)

    for file_path in state.files:
        size_mb = file_path.stat().st_size / 1024 / 1024
        relative_label = str(file_path.relative_to(state.current_dir))

        m = Measurement(sample=test_sample, filepath=str(file_path))
        df = m.dataframe
        state.dataframes[file_path] = df
        defaul_mode = detect_mode(df)

        with dpg.table_row(parent="file_table"):
            dpg.add_selectable(
                label=relative_label,
                tag=str(file_path),
                default_value=False,
                callback=on_select_file,
                user_data=(state, file_path)
            )
            dpg.add_text(f"{size_mb:.1f}")
            # ⭐ 每一行一个独立 radio group
            with dpg.group(horizontal=True):
                mode_tag = f"mode_{file_path}"
                dpg.add_radio_button(
                    items=["MT", "MH"],
                    default_value=defaul_mode,
                    tag=mode_tag,
                    horizontal=True,
                    callback=on_mode_select,
                    user_data=(state, file_path)
                )
        state.file_modes[file_path] = defaul_mode

    if state.files:
        dpg.set_value("status_text", f"Detected {len(state.files)} data files.")
    else:
        dpg.set_value("status_text", "No .dat/.data files found in current directory.")


def smart_labels(paths):
    # ⭐ 只有一个文件 → 直接显示文件名
    if len(paths) == 1:
        return [paths[0].stem]

    parts = [p.parts for p in paths]

    # 找共同前缀长度
    prefix_len = 0

    for i in range(min(len(p) for p in parts)):

        column = {p[i] for p in parts}

        if len(column) == 1:
            prefix_len += 1
        else:
            break

    # 删除共同前缀
    labels = [
        "/".join(p[prefix_len:]).replace(".DAT","")
        for p in parts
    ]

    return labels
    
def on_mode_select(sender, app_data, user_data):
    state, file_path = user_data
    state.file_modes[file_path] = app_data


def on_select_file(sender, app_data, user_data):
    state, file_path = user_data

    if app_data:   # 被选中
        state.selected_files.add(file_path)
    else:          # 被取消
        state.selected_files.discard(file_path)

    dpg.set_value("status_text", f"Selected {file_path}")

def plot_selected_file(state: VisualizerState) -> None:

    if not state.selected_files:
        dpg.set_value("status_text", "Please select a data file first.")
        return
    
    # Check if user choosed multiple mode
    modes = {
        state.file_modes.get(file_path, "MT")
        for file_path in state.selected_files
    }

    if len(modes) > 1:
        dpg.set_value(
            "status_text",
            "Error: Selected files contain mixed modes (MT & MH). Please select files with the same mode."
        )
        return

    ## Re-generate the plot
    children = dpg.get_item_children("main_plot", 1)
    if children:
        for child in children:
            dpg.delete_item(child)
    dpg.add_plot_legend(parent="main_plot")
    dpg.add_plot_axis(dpg.mvXAxis, label="X", parent="main_plot", tag="x_axis")
    dpg.add_plot_axis(dpg.mvYAxis, label="Moment (emu)", parent="main_plot", tag="y_axis")
    
    import math
    selected = list(state.selected_files)
    labels = smart_labels(selected)
    for file_path, label in zip(selected, labels):

        df = state.dataframes[file_path]

        T = df["Temperature (K)"]
        M = df["Moment (emu)"]
        H = df['Magnetic Field (Oe)']


        T_clean = []
        M_clean = []
        H_clean = []

        for t, mom, h in zip(T, M, H):
            if not (math.isnan(t) or math.isnan(mom) or math.isnan(h)):
                T_clean.append(t)
                M_clean.append(mom)
                H_clean.append(h)

        # 🟢 添加一条新曲线
        if state.file_modes[file_path] == 'MT':
            x_value = T_clean
        else:
            x_value = H_clean

        dpg.add_line_series(
            x_value,
            M_clean,
            label=label,
            parent="y_axis"
        )

    dpg.fit_axis_data("x_axis")
    dpg.fit_axis_data("y_axis")

 

