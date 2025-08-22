"""
Atomic plotter for bar plots with optional grouping support.
"""

from typing import Dict, List

import numpy as np

from dr_plotter import consts
from dr_plotter.theme import BAR_THEME, Theme
from dr_plotter.types import VisualChannel

from .base import BasePlotter, BasePlotterParamName, SubPlotterParamName
from .plot_data import BarPlotData, PlotData


class BarPlotter(BasePlotter):
    plotter_name: str = "bar"
    plotter_params: List[str] = []
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Dict[VisualChannel, bool] = {
        "hue": True,
    }
    default_theme: Theme = BAR_THEME
    data_validator: PlotData = BarPlotData

    def _draw(self, ax, data, legend, **kwargs):
        if self._has_groups:
            self._render_with_grouped_method(ax, legend)
        else:
            self._draw_simple(ax, data, legend, **kwargs)
        self._style_zero_line(ax)

    def _draw_simple(self, ax, data, legend, **kwargs):
        ax.bar(data[consts.X_COL_NAME], data[consts.Y_COL_NAME], **kwargs)

    def _draw_grouped(self, ax, data, group_position, legend, **kwargs):
        # Use shared x_categories from all groups if available
        x_categories = group_position.get("x_categories")
        if x_categories is None:
            x_categories = data[consts.X_COL_NAME].unique()

        # Map data to positions based on shared categories
        x_positions = []
        y_values = []
        for i, cat in enumerate(x_categories):
            cat_data = data[data[consts.X_COL_NAME] == cat]
            if not cat_data.empty:
                x_positions.append(i + group_position["offset"])
                y_values.append(cat_data[consts.Y_COL_NAME].values[0])

        # Draw bars at offset positions
        if x_positions:
            ax.bar(x_positions, y_values, width=group_position["width"], **kwargs)

        # Set x-axis labels (only on first group to avoid duplication)
        if group_position["index"] == 0:
            ax.set_xticks(np.arange(len(x_categories)))
            ax.set_xticklabels(x_categories)
