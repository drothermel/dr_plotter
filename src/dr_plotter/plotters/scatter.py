"""
Atomic plotter for scatter plots with multi-series support.
"""

from typing import Any, Dict, List, Set

import pandas as pd

from dr_plotter import consts
from dr_plotter.legend import Legend
from dr_plotter.theme import SCATTER_THEME, Theme
from dr_plotter.types import BasePlotterParamName, SubPlotterParamName, VisualChannel

from .base import BasePlotter


class ScatterPlotter(BasePlotter):
    plotter_name: str = "scatter"
    plotter_params: List[str] = []
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Set[VisualChannel] = {"hue", "size", "marker", "alpha"}
    default_theme: Theme = SCATTER_THEME
    use_style_applicator: bool = True

    def _draw(self, ax: Any, data: pd.DataFrame, legend: Legend, **kwargs: Any) -> None:
        ax.scatter(data[consts.X_COL_NAME], data[consts.Y_COL_NAME], **kwargs)
