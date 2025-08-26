"""
Atomic plotter for line plots with multi-series support.
"""

from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd

from dr_plotter import consts
from dr_plotter.legend import Legend
from dr_plotter.theme import LINE_THEME, Theme

from .base import BasePlotter, BasePlotterParamName, SubPlotterParamName


class LinePlotter(BasePlotter):
    plotter_name: str = "line"
    plotter_params: List[str] = []
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Dict[str, bool] = {
        "hue": True,
        "style": True,
        "size": True,
        "marker": True,
        "alpha": True,
    }
    default_theme: Theme = LINE_THEME

    def _draw(self, ax: plt.Axes, data: pd.DataFrame, legend: Legend, **kwargs):
        data_sorted = data.sort_values(consts.X_COL_NAME)
        ax.plot(
            data_sorted[consts.X_COL_NAME], data_sorted[consts.Y_COL_NAME], **kwargs
        )
