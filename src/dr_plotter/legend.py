from typing import Any, List, Optional

from matplotlib.patches import Patch
from matplotlib.lines import Line2D


class Legend:
    def __init__(self, figure_manager: Optional[Any] = None) -> None:
        self.handles: List = []
        self.fm = figure_manager

    def add_patch(self, label: str, **kwargs) -> None:
        patch = Patch(label=label, **kwargs)
        self.handles.append(patch)

        if self.fm and hasattr(self.fm, "legend_manager"):
            from dr_plotter.legend_manager import LegendEntry

            entry = LegendEntry(
                artist=patch,
                label=label,
                visual_channel=None,
                channel_value=None,
                group_key={},
                plotter_type="unknown",
                artist_type="patch",
            )
            self.fm.register_legend_entry(entry)

    def add_line(self, label: str, **kwargs) -> None:
        if "xdata" not in kwargs:
            kwargs["xdata"] = []
        if "ydata" not in kwargs:
            kwargs["ydata"] = []
        line = Line2D(label=label, **kwargs)
        self.handles.append(line)

        if self.fm and hasattr(self.fm, "legend_manager"):
            from dr_plotter.legend_manager import LegendEntry

            entry = LegendEntry(
                artist=line,
                label=label,
                visual_channel=None,
                channel_value=None,
                group_key={},
                plotter_type="unknown",
                artist_type="line",
            )
            self.fm.register_legend_entry(entry)

    def get_handles(self) -> List:
        return self.handles

    def has_entries(self) -> bool:
        return len(self.handles) > 0
