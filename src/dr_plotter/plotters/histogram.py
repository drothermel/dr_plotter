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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if self.use_style_applicator:
            self.style_applicator.register_post_processor(
                "histogram", "patches", self._style_histogram_patches
            )

    def _style_histogram_patches(self, patches: Any, styles: Dict[str, Any]) -> None:
        for patch in patches:
            for attr, value in styles.items():
                if hasattr(patch, f"set_{attr}"):
                    setter = getattr(patch, f"set_{attr}")
                    setter(value)

    def _draw(self, ax: Any, data: pd.DataFrame, legend: Legend, **kwargs: Any) -> None:
        n, bins, patches = ax.hist(data[consts.X_COL_NAME], **kwargs)

        if self.use_style_applicator:
            artists = {"patches": patches, "n": n, "bins": bins}
            self.style_applicator.apply_post_processing("histogram", artists)
