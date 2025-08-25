from typing import Any, Dict, List, Optional, Set

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from dr_plotter import consts
from dr_plotter.grouping_config import GroupingConfig
from dr_plotter.theme import SCATTER_THEME, Theme
from dr_plotter.types import (
    BasePlotterParamName,
    SubPlotterParamName,
    VisualChannel,
    Phase,
    ComponentSchema,
)

from .base import BasePlotter


class ScatterPlotter(BasePlotter):
    plotter_name: str = "scatter"
    plotter_params: List[str] = []
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Set[VisualChannel] = {"hue", "size", "marker", "alpha"}
    default_theme: Theme = SCATTER_THEME

    component_schema: Dict[Phase, ComponentSchema] = {
        "plot": {
            "main": {
                "s",
                "alpha",
                "color",
                "marker",
                "edgecolors",
                "linewidths",
                "c",
                "cmap",
                "vmin",
                "vmax",
            }
        },
        "axes": {
            "title": {"text", "fontsize", "color"},
            "xlabel": {"text", "fontsize", "color"},
            "ylabel": {"text", "fontsize", "color"},
            "grid": {"visible", "alpha", "color", "linestyle"},
            "collection": {
                "sizes",
                "facecolors",
                "edgecolors",
                "linewidths",
                "alpha",
            },
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

    def _draw(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        label = kwargs.pop("label", None)

        if "size" in self.grouping_params.active_channels:
            size_col = self.grouping_params.size
            if size_col and size_col in data.columns:
                sizes = []
                for value in data[size_col]:
                    style = self.style_engine._get_continuous_style(
                        "size", size_col, value
                    )
                    size_mult = style.get("size_mult", 1.0)
                    base_size = kwargs.get("s", 50)
                    sizes.append(
                        base_size * size_mult
                        if isinstance(base_size, (int, float))
                        else 50 * size_mult
                    )
                kwargs["s"] = sizes

        collection = ax.scatter(
            data[consts.X_COL_NAME], data[consts.Y_COL_NAME], **kwargs
        )

        artists = {"collection": collection}
        self.style_applicator.apply_post_processing("scatter", artists)

        self._apply_post_processing(collection, label)

    def _apply_post_processing(
        self, collection: Any, label: Optional[str] = None
    ) -> None:
        if not self._should_create_legend():
            return

        if self.figure_manager and label and collection:
            for channel in self.grouping_params.active_channels_ordered:
                proxy = self._create_channel_specific_proxy(collection, channel)
                if proxy:
                    entry = self.style_applicator.create_legend_entry(
                        proxy, label, self.current_axis, explicit_channel=channel
                    )
                    if entry:
                        self.figure_manager.register_legend_entry(entry)

    def _create_channel_specific_proxy(
        self, collection: Any, channel: str
    ) -> Optional[Any]:
        facecolors = collection.get_facecolors()
        edgecolors = collection.get_edgecolors()
        sizes = collection.get_sizes()

        if len(facecolors) > 0:
            face_color = facecolors[0]
        else:
            face_color = self.figure_manager.legend_manager.get_error_color(
                "face", self.theme
            )

        if len(edgecolors) > 0:
            edge_color = edgecolors[0]
        else:
            edge_color = self.figure_manager.legend_manager.get_error_color(
                "edge", self.theme
            )

        marker_size = self._get_style("marker_size", 8)
        if len(sizes) > 0:
            marker_size = np.sqrt(sizes[0] / np.pi) * 2

        marker_style = "o"
        if self.style_applicator.group_values:
            styles = self.style_engine.get_styles_for_group(
                self.style_applicator.group_values, self.grouping_params
            )
            marker_style = styles.get("marker", "o")

        proxy = Line2D(
            [0],
            [0],
            marker=marker_style,
            color="none",
            markerfacecolor=face_color,
            markeredgecolor=edge_color,
            markersize=marker_size,
            linestyle="",
        )

        return proxy
