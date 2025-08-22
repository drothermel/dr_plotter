"""
Atomic plotter for histograms.
"""

from typing import Dict, List

from dr_plotter import consts
from dr_plotter.theme import HISTOGRAM_THEME, Theme
from dr_plotter.types import BasePlotterParamName, SubPlotterParamName, VisualChannel

from .base import BasePlotter
from .plot_data import HistogramData, PlotData


class HistogramPlotter(BasePlotter):
    plotter_name: str = "histogram"
    plotter_params: List[str] = []
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Dict[VisualChannel, bool] = {}
    default_theme: Theme = HISTOGRAM_THEME
    data_validator: PlotData = HistogramData

    def _draw(self, ax, data, legend, **kwargs):
        ax.hist(data[consts.X_COL_NAME], **kwargs)
        ax.set_ylabel(self.theme.axes_styles.get("ylabel"))
