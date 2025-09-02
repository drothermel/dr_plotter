from typing import Any, Dict, List, Optional, Set

import pandas as pd
from matplotlib.patches import Patch

from dr_plotter import consts
from dr_plotter.configs import GroupingConfig
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
    supports_grouped: bool = False

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

    def __init__(
        self,
        data: pd.DataFrame,
        grouping_cfg: GroupingConfig,
        theme: Optional[Theme] = None,
        figure_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(data, grouping_cfg, theme, figure_manager, **kwargs)
        self.styler.register_post_processor(
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
        self.styler.apply_post_processing("histogram", artists)

        self._apply_post_processing({"patches": patches}, label)

    def _apply_post_processing(
        self, parts: Dict[str, Any], label: Optional[str] = None
    ) -> None:
        if "patches" in parts and parts["patches"]:
            first_patch = parts["patches"][0]
            proxy = Patch(
                facecolor=first_patch.get_facecolor(),
                edgecolor=first_patch.get_edgecolor(),
                alpha=first_patch.get_alpha(),
            )
            self._register_legend_entry_if_valid(proxy, label)
