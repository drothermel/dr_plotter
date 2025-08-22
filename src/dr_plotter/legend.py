from typing import List

from matplotlib.patches import Patch
from matplotlib.lines import Line2D


class Legend:
    def __init__(self) -> None:
        self.handles: List = []

    def add_patch(self, label: str, **kwargs) -> None:
        self.handles.append(Patch(label=label, **kwargs))

    def add_line(self, label: str, **kwargs) -> None:
        if "xdata" not in kwargs:
            kwargs["xdata"] = []
        if "ydata" not in kwargs:
            kwargs["ydata"] = []
        self.handles.append(Line2D(label=label, **kwargs))

    def get_handles(self) -> List:
        return self.handles

    def has_entries(self) -> bool:
        return len(self.handles) > 0
