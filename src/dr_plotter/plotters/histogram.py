from typing import Any, Dict, List, Optional, Set

import pandas as pd
from matplotlib.patches import Patch

from dr_plotter import consts
from dr_plotter.theme import HISTOGRAM_THEME, Theme
from dr_plotter.types import (
    BasePlotterParamName,
    SubPlotterParamName,
    VisualChannel,
    Phase,
    ComponentSchema,
)

from .base import BasePlotter


class HistogramPlotter(BasePlotter):
    plotter_name: str = "histogram"
    plotter_params: List[str] = []
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Set[VisualChannel] = set()
    default_theme: Theme = HISTOGRAM_THEME

    component_schema: Dict[Phase, ComponentSchema] = {
        "plot": {
            "main": {
                "color",
                "alpha",
                "edgecolor",
                "linewidth",
                "bins",
                "label",
                "histtype",
                "cumulative",
                "density",
                "weights",
                "bottom",
                "rwidth",
            }
        },
        "axes": {
            "title": {"text", "fontsize", "color"},
            "xlabel": {"text", "fontsize", "color"},
            "ylabel": {"text", "fontsize", "color"},
            "grid": {"visible", "alpha", "color", "linestyle"},
            "patches": {"facecolor", "edgecolor", "linewidth", "alpha"},
        },
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.style_applicator.register_post_processor(
            "histogram", "patches", self._style_histogram_patches
        )

    def _style_histogram_patches(self, patches: Any, styles: Dict[str, Any]) -> None:
        for patch in patches:
            for attr, value in styles.items():
                if hasattr(patch, f"set_{attr}"):
                    setter = getattr(patch, f"set_{attr}")
                    setter(value)

    def _draw(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        label = kwargs.pop("label", None)
        n, bins, patches = ax.hist(data[consts.X_COL_NAME], **kwargs)

        artists = {"patches": patches, "n": n, "bins": bins}
        self.style_applicator.apply_post_processing("histogram", artists)

        self._apply_post_processing({"patches": patches}, label)

    def _apply_post_processing(
        self, parts: Dict[str, Any], label: Optional[str] = None
    ) -> None:
        if not self._should_create_legend():
            return

        if self.figure_manager and label and "patches" in parts:
            if parts["patches"]:
                first_patch = parts["patches"][0]
                proxy = Patch(
                    facecolor=first_patch.get_facecolor(),
                    edgecolor=first_patch.get_edgecolor(),
                    alpha=first_patch.get_alpha(),
                )

                entry = self.style_applicator.create_legend_entry(
                    proxy, label, self.current_axis
                )
                if entry:
                    self.figure_manager.register_legend_entry(entry)
