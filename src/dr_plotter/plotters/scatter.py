from typing import Any, Dict, List, Optional, Set

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from dr_plotter import consts
from dr_plotter.legend import Legend
from dr_plotter.theme import SCATTER_THEME, Theme
from dr_plotter.types import BasePlotterParamName, SubPlotterParamName, VisualChannel

from .base import BasePlotter

type Phase = str
type ComponentSchema = Dict[str, Set[str]]


class ScatterPlotter(BasePlotter):
    plotter_name: str = "scatter"
    plotter_params: List[str] = []
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Set[VisualChannel] = {"hue", "size", "marker", "alpha"}
    default_theme: Theme = SCATTER_THEME
    use_style_applicator: bool = True
    use_legend_manager: bool = True

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
        "post": {
            "collection": {
                "sizes",
                "facecolors",
                "edgecolors",
                "linewidths",
                "alpha",
            }
        },
    }

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
        label = kwargs.pop("label", None)

        # Handle continuous size channel
        if "size" in self.grouping_params.active_channels:
            size_col = self.grouping_params.size
            if size_col and size_col in data.columns:
                # Calculate sizes for each point based on continuous mapping
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

        if self.use_style_applicator:
            artists = {"collection": collection}
            self.style_applicator.apply_post_processing("scatter", artists)

        self._apply_post_processing(collection, legend, label)

    def _apply_post_processing(
        self, collection: Any, legend: Legend, label: Optional[str] = None
    ) -> None:
        if self.use_legend_manager and self.figure_manager and label and collection:
            proxy = self._create_proxy_artist_from_collection(collection)
            if proxy:
                # Create legend entries for each active channel
                for channel in self.grouping_params.active_channels_ordered:
                    entry = self.style_applicator.create_legend_entry(
                        proxy, label, self.current_axis, explicit_channel=channel
                    )
                    if entry:
                        self.figure_manager.register_legend_entry(entry)
        elif label and collection:
            proxy = self._create_proxy_artist_from_collection(collection)
            if proxy:
                legend.handles.append(proxy)

    def _create_proxy_artist_from_collection(self, collection: Any) -> Optional[Any]:
        facecolors = collection.get_facecolors()
        edgecolors = collection.get_edgecolors()
        sizes = collection.get_sizes()

        face_color = "blue"
        if len(facecolors) > 0:
            face_color = facecolors[0]

        edge_color = "none"
        if len(edgecolors) > 0:
            edge_color = edgecolors[0]

        marker_size = 8
        if len(sizes) > 0:
            marker_size = np.sqrt(sizes[0] / np.pi) * 2

        marker_style = (
            collection.get_paths()[0] if len(collection.get_paths()) > 0 else "o"
        )

        proxy = Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor=face_color,
            markeredgecolor=edge_color,
            markersize=marker_size,
            linestyle="",
            label=collection.get_label() if hasattr(collection, "get_label") else "",
        )

        return proxy
