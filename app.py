from pathlib import Path
import sys
import os

print('something')
def get_exe_dir():
    if "__compiled__" in globals():
        return Path(sys.argv[0]).resolve().parent
    return Path(__file__).resolve().parent

ROOT = get_exe_dir()
print(ROOT)


from vsm_visualizer.ui import run_app

if __name__ == "__main__":
    print(ROOT)

    run_app(start_dir=ROOT)
    