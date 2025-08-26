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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if self.use_style_applicator:
            self.style_applicator.register_post_processor(
                "scatter", "collection", self._style_scatter_collection
            )

    def _style_scatter_collection(
        self, collection: Any, styles: Dict[str, Any]
    ) -> None:
        for attr, value in styles.items():
            if attr == "sizes" and hasattr(collection, "set_sizes"):
                collection.set_sizes([value])
            elif attr == "facecolors" and hasattr(collection, "set_facecolors"):
                collection.set_facecolors(value)
            elif attr == "edgecolors" and hasattr(collection, "set_edgecolors"):
                collection.set_edgecolors(value)
            elif attr == "linewidths" and hasattr(collection, "set_linewidths"):
                collection.set_linewidths(value)
            elif attr == "alpha" and hasattr(collection, "set_alpha"):
                collection.set_alpha(value)
            elif hasattr(collection, f"set_{attr}"):
                setter = getattr(collection, f"set_{attr}")
                setter(value)

    def _draw(self, ax: Any, data: pd.DataFrame, legend: Legend, **kwargs: Any) -> None:
        collection = ax.scatter(
            data[consts.X_COL_NAME], data[consts.Y_COL_NAME], **kwargs
        )

        if self.use_style_applicator:
            artists = {"collection": collection}
            self.style_applicator.apply_post_processing("scatter", artists)
