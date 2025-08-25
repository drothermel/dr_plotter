from typing import Any, Dict, List, Optional, Set

import matplotlib.patheffects as path_effects
import pandas as pd

from dr_plotter.grouping_config import GroupingConfig
from dr_plotter.theme import BUMP_PLOT_THEME, Theme
from dr_plotter.types import VisualChannel, Phase, ComponentSchema

from .base import BasePlotter, BasePlotterParamName, SubPlotterParamName


class BumpPlotter(BasePlotter):
    plotter_name: str = "bump"
    plotter_params: List[str] = ["time_col", "category_col", "value_col"]
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Set[VisualChannel] = {"hue", "style"}
    default_theme: Theme = BUMP_PLOT_THEME

    component_schema: Dict[Phase, ComponentSchema] = {
        "plot": {
            "main": {
                "color",
                "linestyle",
                "linewidth",
                "marker",
                "markersize",
                "alpha",
                "label",
            }
        },
        "axes": {
            "title": {"text", "fontsize", "color"},
            "xlabel": {"text", "fontsize", "color"},
            "ylabel": {"text", "fontsize", "color"},
            "grid": {"visible", "alpha", "color", "linestyle"},
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

    def _initialize_subplot_specific_params(self) -> None:
        self.time_col = self.kwargs.get("time_col")
        self.value_col = self.kwargs.get("value_col")
        self.category_col = self.kwargs.get("category_col")
        # Ensure that the coloring is based on the category column
        self.grouping_params.hue = self.category_col

    def _plot_specific_data_prep(self) -> pd.DataFrame:
        self.plot_data["rank"] = self.plot_data.groupby(self.time_col)[
            self.value_col
        ].rank(method="first", ascending=False)
        self.value_col = "rank"
        return self.plot_data

    def _draw(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        group_cols = list(self.grouping_params.active.values())
        if group_cols:
            grouped = self.plot_data.groupby(group_cols)

            for name, group_data in grouped:
                if isinstance(name, tuple):
                    group_values = dict(zip(group_cols, name))
                else:
                    group_values = {group_cols[0]: name}

                styles = self.style_engine.get_styles_for_group(
                    group_values, self.grouping_params
                )

                # Build plot kwargs for this group
                plot_kwargs = self._build_group_plot_kwargs(styles, name, group_cols)

                self._draw_simple(ax, group_data, **plot_kwargs)
        ax.set_ylabel(self._get_style("ylabel", "Rank"))

    def _draw_simple(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        # Sort data by time for proper line drawing
        category_data = data.sort_values(by=self.time_col)

        label = kwargs.pop("label", None)
        lines = ax.plot(
            category_data[self.time_col], category_data[self.value_col], **kwargs
        )

        self._apply_post_processing(lines, label)

        # Add category label at the end of the line
        if not category_data.empty:
            last_point = category_data.iloc[-1]
            category_name = kwargs.get("label", "Unknown")
            # Extract just the category name from "category=Cat_A" format if present
            if "=" in category_name:
                category_name = category_name.split("=")[1]
            text = ax.text(
                last_point[self.time_col],
                last_point[self.value_col],
                f" {category_name}",
                va="center",
                color=self._get_style("text_color", "black"),
                fontweight=self._get_style("fontweight", "bold"),
            )
            text.set_path_effects(
                [
                    path_effects.Stroke(linewidth=2, foreground="white"),
                    path_effects.Normal(),
                ]
            )

        # Configure bump plot specific axes (only set once)
        if not hasattr(ax, "_bump_configured"):
            ax.invert_yaxis()
            max_rank = int(self.plot_data["rank"].max())
            ax.set_yticks(range(1, max_rank + 1))
            ax.margins(x=0.15)
            ax._bump_configured = True

    def _apply_post_processing(self, lines: Any, label: Optional[str] = None) -> None:
        if lines:
            line = lines[0] if isinstance(lines, list) else lines
            self._register_legend_entry_if_valid(line, label)

        self._apply_styling(self.current_axis)
