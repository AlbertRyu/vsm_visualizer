from pathlib import Path

ROOT = Path(__file__).resolve().parent

from vsm_visualizer.ui import run_app

if __name__ == "__main__":
    run_app(start_dir=ROOT)