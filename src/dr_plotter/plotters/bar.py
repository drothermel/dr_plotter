from typing import Any, Dict, List, Optional, Set

import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from dr_plotter import consts
from dr_plotter.legend import Legend
from dr_plotter.theme import BAR_THEME, Theme
from dr_plotter.types import BasePlotterParamName, SubPlotterParamName, VisualChannel

from .base import BasePlotter

type Phase = str
type ComponentSchema = Dict[str, Set[str]]


class BarPlotter(BasePlotter):
    plotter_name: str = "bar"
    plotter_params: List[str] = []
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Set[VisualChannel] = {"hue"}
    default_theme: Theme = BAR_THEME
    use_style_applicator: bool = True
    use_legend_manager: bool = True

    component_schema: Dict[Phase, ComponentSchema] = {
        "plot": {
            "main": {
                "color",
                "alpha",
                "edgecolor",
                "linewidth",
                "width",
                "bottom",
                "align",
                "label",
            }
        },
        "post": {"patches": {"facecolor", "edgecolor", "alpha", "linewidth"}},
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if self.use_style_applicator:
            self.style_applicator.register_post_processor(
                "bar", "patches", self._style_bar_patches
            )

    def _style_bar_patches(self, patches: Any, styles: Dict[str, Any]) -> None:
        for patch in patches:
            for attr, value in styles.items():
                if hasattr(patch, f"set_{attr}"):
                    setter = getattr(patch, f"set_{attr}")
                    setter(value)

    def _draw(self, ax: Any, data: pd.DataFrame, legend: Legend, **kwargs: Any) -> None:
        if not self._has_groups:
            self._draw_simple(ax, data, legend, **kwargs)

    def _draw_simple(
        self, ax: Any, data: pd.DataFrame, legend: Legend, **kwargs: Any
    ) -> None:
        label = kwargs.pop("label", None)
        patches = ax.bar(data[consts.X_COL_NAME], data[consts.Y_COL_NAME], **kwargs)

        if self.use_style_applicator:
            artists = {"patches": patches}
            self.style_applicator.apply_post_processing("bar", artists)

        self._apply_post_processing(patches, legend, label)

    def _apply_post_processing(
        self, patches: Any, legend: Legend, label: Optional[str] = None
    ) -> None:
        if self.use_legend_manager and self.figure_manager and label and patches:
            first_patch = patches[0]
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
        elif label and patches:
            first_patch = patches[0]
            legend.add_patch(
                label=label,
                facecolor=first_patch.get_facecolor(),
                edgecolor=first_patch.get_edgecolor(),
                alpha=first_patch.get_alpha(),
            )

    def _draw_grouped(
        self,
        ax: Any,
        data: pd.DataFrame,
        group_position: Dict[str, Any],
        legend: Legend,
        **kwargs: Any,
    ) -> None:
        # Use shared x_categories from all groups if available
        x_categories = group_position.get("x_categories")
        if x_categories is None:
            x_categories = data[consts.X_COL_NAME].unique()

        # Map data to positions based on shared categories
        x_positions = []
        y_values = []
        for i, cat in enumerate(x_categories):
            cat_data = data[data[consts.X_COL_NAME] == cat]
            if not cat_data.empty:
                x_positions.append(i + group_position["offset"])
                y_values.append(cat_data[consts.Y_COL_NAME].values[0])

        # Draw bars at offset positions
        if x_positions:
            ax.bar(x_positions, y_values, width=group_position["width"], **kwargs)

        # Set x-axis labels (only on first group to avoid duplication)
        if group_position["index"] == 0:
            ax.set_xticks(np.arange(len(x_categories)))
            ax.set_xticklabels(x_categories)
