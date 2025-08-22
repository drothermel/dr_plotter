from typing import Any, Dict, List, Set

import pandas as pd

from dr_plotter import consts
from dr_plotter.legend import Legend
from dr_plotter.theme import HISTOGRAM_THEME, Theme
from dr_plotter.types import BasePlotterParamName, SubPlotterParamName, VisualChannel

from .base import BasePlotter


class HistogramPlotter(BasePlotter):
    plotter_name: str = "histogram"
    plotter_params: List[str] = []
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Set[VisualChannel] = set()
    default_theme: Theme = HISTOGRAM_THEME
    use_style_applicator: bool = True

    def _draw(self, ax: Any, data: pd.DataFrame, legend: Legend, **kwargs: Any) -> None:
        ax.hist(data[consts.X_COL_NAME], **kwargs)
