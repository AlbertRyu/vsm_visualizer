from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vsm_visualizer.ui import run_app


if __name__ == "__main__":
    run_app(start_dir=ROOT)
