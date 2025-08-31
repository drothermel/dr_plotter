from typing import Any, Dict, List, Optional, Set

import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from dr_plotter import consts
from dr_plotter.configs.grouping_config import GroupingConfig
from dr_plotter.theme import BAR_THEME, Theme
from dr_plotter.types import (
    BasePlotterParamName,
    SubPlotterParamName,
    VisualChannel,
    Phase,
    ComponentSchema,
)

from .base import BasePlotter


class BarPlotter(BasePlotter):
    plotter_name: str = "bar"
    plotter_params: List[str] = []
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Set[VisualChannel] = {"hue"}
    default_theme: Theme = BAR_THEME

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
        "axes": {
            "title": {"text", "fontsize", "color"},
            "xlabel": {"text", "fontsize", "color"},
            "ylabel": {"text", "fontsize", "color"},
            "grid": {"visible", "alpha", "color", "linestyle"},
            "patches": {"facecolor", "edgecolor", "alpha", "linewidth"},
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
        self.styler.register_post_processor("bar", "patches", self._style_bar_patches)

    def _style_bar_patches(self, patches: Any, styles: Dict[str, Any]) -> None:
        for patch in patches:
            for attr, value in styles.items():
                if hasattr(patch, f"set_{attr}"):
                    setter = getattr(patch, f"set_{attr}")
                    setter(value)

    def _draw(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        if not self._has_groups:
            self._draw_simple(ax, data, **kwargs)

    def _draw_simple(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        label = kwargs.pop("label", None)
        patches = ax.bar(data[consts.X_COL_NAME], data[consts.Y_COL_NAME], **kwargs)

        artists = {"patches": patches}
        self.styler.apply_post_processing("bar", artists)

        self._apply_post_processing(patches, label)

    def _apply_post_processing(self, patches: Any, label: Optional[str] = None) -> None:
        if patches:
            first_patch = patches[0]
            proxy = Patch(
                facecolor=first_patch.get_facecolor(),
                edgecolor=first_patch.get_edgecolor(),
                alpha=first_patch.get_alpha(),
            )
            self._register_legend_entry_if_valid(proxy, label)

    def _draw_grouped(
        self,
        ax: Any,
        data: pd.DataFrame,
        group_position: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        label = kwargs.pop("label", None)

        x_categories = group_position.get("x_categories")
        if x_categories is None:
            x_categories = data[consts.X_COL_NAME].unique()

        x_positions = []
        y_values = []
        for i, cat in enumerate(x_categories):
            cat_data = data[data[consts.X_COL_NAME] == cat]
            if not cat_data.empty:
                x_positions.append(i + group_position["offset"])
                y_values.append(cat_data[consts.Y_COL_NAME].values[0])

        patches = None
        if x_positions:
            patches = ax.bar(
                x_positions, y_values, width=group_position["width"], **kwargs
            )

        if group_position["index"] == 0:
            ax.set_xticks(np.arange(len(x_categories)))
            ax.set_xticklabels(x_categories)

        self._apply_post_processing(patches, label)
