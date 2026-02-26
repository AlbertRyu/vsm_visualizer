from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from ppms_toolkit.sample import Sample
from ppms_toolkit.measurement import VSMMeasurement
import matplotlib.pyplot as plt


### Hard code sample

test_sample = Sample(name='Test Sample', mass=1)

class ToolkitAdapterError(RuntimeError):
    pass


class PPMSToolkitAdapter:
    """
    Thin adapter for existing ppms_toolkit entrypoints.
    No local reader/processor/plot fallback is implemented.
    """

    def get_figure_for_file(self, file_path: Path) -> Any:

        m = VSMMeasurement(mode='MT',sample=test_sample, filepath=str(file_path))
        fig, ax = plt.subplots()
        ax = m.plot(ax=ax)

        if fig is None:
            raise ToolkitAdapterError(
                "Toolkit plotting function did not return a matplotlib Figure. "
                "Please make your ppms_toolkit plotting entrypoint return Figure."
            )
        return ax.figure
