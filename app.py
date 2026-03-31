from pathlib import Path
import sys

from vsm_visualizer.ui import run_app


def get_exe_dir():
    if "__compiled__" in globals():
        # sys.argv[0] is inside app.app/Contents/MacOS/ — go up 3 levels to the folder containing the .app
        exe = Path(sys.argv[0]).resolve()
        if exe.parts[-3:-1] == ("Contents", "MacOS"):
            return exe.parent.parent.parent.parent
        return exe.parent
    return Path(__file__).resolve().parent

if __name__ == "__main__":
    if len(sys.argv) > 1:
        start_dir = Path(sys.argv[1]).resolve()
    else:
        start_dir = get_exe_dir()
    run_app(start_dir=start_dir)
