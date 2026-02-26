from __future__ import annotations

from pathlib import Path

import dearpygui.dearpygui as dpg
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg

from .ppms_adapter import PPMSToolkitAdapter, ToolkitAdapterError


class VisualizerState:
    def __init__(self, start_dir: Path) -> None:
        self.current_dir = start_dir
        self.adapter = PPMSToolkitAdapter()
        self.files: list[Path] = []
        self.selected_file: Path | None = None
        self.texture_tag = "plot_texture"
        self.image_tag = "plot_image"
        self.texture_size: tuple[int, int] | None = None


def run_app(start_dir: Path) -> None:
    state = VisualizerState(start_dir=start_dir)

    dpg.create_context()
    dpg.create_viewport(title="VSM Data Visualizer", width=1280, height=720)
    with dpg.texture_registry(tag="texture_registry", show=False):
        pass

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
                dpg.add_text("Matplotlib Preview", tag="plot_title")
                dpg.add_spacer(height=6)
                dpg.add_button(label="Render Selected File", width=200, callback=lambda: render_selected_file(state))
                dpg.add_spacer(height=8)
                dpg.add_text("No file selected.", tag="selected_file_text", wrap=820)
                dpg.add_spacer(height=8)
                with dpg.group(tag="plot_container"):
                    dpg.add_text("No plot yet.", tag="plot_placeholder")

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



def render_selected_file(state: VisualizerState) -> None:
    if not state.selected_file:
        dpg.set_value("status_text", "Please select a data file first.")
        return

    try:
        fig = state.adapter.get_figure_for_file(state.selected_file)
        rgba, width, height = figure_to_rgba(fig)
        upsert_plot_texture(state, rgba, width, height)
        dpg.set_value("status_text", f"Rendered {state.selected_file.name}")
    except ToolkitAdapterError as exc:
        dpg.set_value("status_text", f"Toolkit error: {exc}")
    except Exception as exc:  # pragma: no cover
        dpg.set_value("status_text", f"Unexpected error: {exc}")


def figure_to_rgba(fig: object) -> tuple[list[float], int, int]:
    canvas = FigureCanvasAgg(fig)  # type: ignore[arg-type]
    canvas.draw()
    buffer = np.asarray(canvas.buffer_rgba(), dtype=np.uint8)
    height, width = buffer.shape[0], buffer.shape[1]
    normalized = (buffer.astype(np.float32) / 255.0).ravel().tolist()
    return normalized, width, height


def upsert_plot_texture(state: VisualizerState, rgba: list[float], width: int, height: int) -> None:
    if dpg.does_item_exist("plot_placeholder"):
        dpg.delete_item("plot_placeholder")

    if dpg.does_item_exist(state.texture_tag):
        if state.texture_size == (width, height):
            dpg.set_value(state.texture_tag, rgba)
        else:
            if dpg.does_item_exist(state.image_tag):
                dpg.delete_item(state.image_tag)
            dpg.delete_item(state.texture_tag)
            dpg.add_dynamic_texture(
                width=width,
                height=height,
                default_value=rgba,
                tag=state.texture_tag,
                parent="texture_registry",
            )
            dpg.add_image(state.texture_tag, tag=state.image_tag, parent="plot_container")
    else:
        dpg.add_dynamic_texture(
            width=width,
            height=height,
            default_value=rgba,
            tag=state.texture_tag,
            parent="texture_registry",
        )
        dpg.add_image(state.texture_tag, tag=state.image_tag, parent="plot_container")

    state.texture_size = (width, height)
