from typing import Any, Dict, List, Optional, Set

import matplotlib.pyplot as plt
import pandas as pd

from dr_plotter import consts
from dr_plotter.grouping_config import GroupingConfig
from dr_plotter.theme import LINE_THEME, Theme
from dr_plotter.types import VisualChannel, Phase, ComponentSchema

from .base import BasePlotter, BasePlotterParamName, SubPlotterParamName


class LinePlotter(BasePlotter):
    plotter_name: str = "line"
    plotter_params: List[str] = []
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Set[VisualChannel] = {"hue", "style", "size", "marker", "alpha"}
    default_theme: Theme = LINE_THEME

    component_schema: Dict[Phase, ComponentSchema] = {
        "plot": {
            "main": {
                "color",
                "linestyle",
                "linewidth",
                "marker",
                "markersize",
                "alpha",
                "label",
            }
        },
        "axes": {
            "title": {"text", "fontsize", "color"},
            "xlabel": {"text", "fontsize", "color"},
            "ylabel": {"text", "fontsize", "color"},
            "grid": {"visible", "alpha", "color", "linestyle"},
        },
    }

    def __init__(
        self,
        data: pd.DataFrame,
        grouping_cfg: GroupingConfig,
        theme: Optional[Theme] = None,
        figure_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(data, grouping_cfg, theme, figure_manager, **kwargs)

    def _draw(self, ax: plt.Axes, data: pd.DataFrame, **kwargs: Any) -> None:
        label = kwargs.pop("label", None)
        data_sorted = data.sort_values(consts.X_COL_NAME)
        lines = ax.plot(
            data_sorted[consts.X_COL_NAME], data_sorted[consts.Y_COL_NAME], **kwargs
        )

        self._apply_post_processing(lines, label)

    def _apply_post_processing(self, lines: Any, label: Optional[str] = None) -> None:
        if not self._should_create_legend():
            self._apply_styling(self.current_axis)
            return

        if self.figure_manager and label and lines:
            line = lines[0] if isinstance(lines, list) else lines
            for channel in self.grouping_params.active_channels_ordered:
                entry = self.styler.create_legend_entry(
                    line, label, self.current_axis, explicit_channel=channel
                )
                if entry:
                    self.figure_manager.register_legend_entry(entry)

        self._apply_styling(self.current_axis)
