from pathlib import Path


import sys
import os

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)

ROOT = get_base_path()

from vsm_visualizer.ui import run_app

if __name__ == "__main__":
    run_app(start_dir=ROOT)