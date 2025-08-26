"""
Atomic plotter for line plots with multi-series support.
"""

from typing import Dict, List, Set

import matplotlib.pyplot as plt
import pandas as pd

from dr_plotter import consts
from dr_plotter.legend import Legend
from dr_plotter.theme import LINE_THEME, Theme
from dr_plotter.types import VisualChannel

from .base import BasePlotter, BasePlotterParamName, SubPlotterParamName


class LinePlotter(BasePlotter):
    plotter_name: str = "line"
    plotter_params: List[str] = []
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Set[VisualChannel] = {"hue", "style", "size", "marker", "alpha"}
    default_theme: Theme = LINE_THEME

    def _draw(self, ax: plt.Axes, data: pd.DataFrame, legend: Legend, **kwargs):
        data_sorted = data.sort_values(consts.X_COL_NAME)
        ax.plot(
            data_sorted[consts.X_COL_NAME], data_sorted[consts.Y_COL_NAME], **kwargs
        )
