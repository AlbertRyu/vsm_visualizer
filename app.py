from pathlib import Path


import sys
import os


def get_exe_dir():
    if "__compiled__" in globals():
        return Path(sys.argv[0]).resolve().parent
    return Path(__file__).resolve().parent


ROOT = get_exe_dir()

from vsm_visualizer.ui import run_app

if __name__ == "__main__":
    run_app(start_dir=ROOT)