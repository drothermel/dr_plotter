"""
Atomic plotter for scatter plots with multi-series support.
"""

from typing import Dict, List

from dr_plotter import consts
from dr_plotter.theme import SCATTER_THEME, Theme
from dr_plotter.types import BasePlotterParamName, SubPlotterParamName, VisualChannel

from .base import BasePlotter
from .plot_data import PlotData, ScatterPlotData


class ScatterPlotter(BasePlotter):
    """
    An atomic plotter for creating scatter plots with multi-series support.
    """

    # Declarative configuration
    plotter_name: str = "scatter"
    plotter_params: List[str] = []
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Dict[VisualChannel, bool] = {
        "hue": True,
        "size": True,
        "marker": True,
        "alpha": True,
    }
    default_theme: Theme = SCATTER_THEME
    data_validator: PlotData = ScatterPlotData

    def _draw(self, ax, data, legend, **kwargs):
        ax.scatter(data[consts.X_COL_NAME], data[consts.Y_COL_NAME], **kwargs)
