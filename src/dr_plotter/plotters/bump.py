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
    supports_grouped: bool = False

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

    def _plot_specific_data_prep(self) -> None:
        self.plot_data["rank"] = self.plot_data.groupby(self.time_col)[
            self.value_col
        ].rank(method="first", ascending=False)
        self.value_col = "rank"

        categories = self.plot_data[self.category_col].unique()
        self.trajectory_data = []

        for i, category in enumerate(categories):
            cat_data = self.plot_data[self.plot_data[self.category_col] == category]
            cat_data = cat_data.sort_values(by=self.time_col).copy()

            style = self._get_category_style(category, i, len(categories))
            cat_data["_bump_color"] = style["color"]
            cat_data["_bump_linestyle"] = style.get("linestyle", "-")
            cat_data["_bump_label"] = str(category)

            self.trajectory_data.append(cat_data)

    def _get_category_style(
        self, category: Any, index: int, total_categories: int
    ) -> Dict[str, Any]:
        base_colors = self.theme.get(
            "base_colors", ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
        )
        color = base_colors[index % len(base_colors)]
        return {"color": color, "linestyle": "-"}

    def _draw(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        for traj_data in self.trajectory_data:
            if not traj_data.empty:
                lines = ax.plot(
                    traj_data[self.time_col],
                    traj_data[self.value_col],
                    color=traj_data["_bump_color"].iloc[0],
                    linestyle=traj_data["_bump_linestyle"].iloc[0],
                    **self._filtered_plot_kwargs,
                )

                last_point = traj_data.iloc[-1]
                category_name = traj_data["_bump_label"].iloc[0]
                text = ax.text(
                    last_point[self.time_col],
                    last_point[self.value_col],
                    f" {category_name}",
                    va="center",
                    color=self.style_applicator.get_style_with_fallback(
                        "text_color", "black"
                    ),
                    fontweight=self.style_applicator.get_style_with_fallback(
                        "fontweight", "bold"
                    ),
                )
                text.set_path_effects(
                    [
                        path_effects.Stroke(linewidth=2, foreground="white"),
                        path_effects.Normal(),
                    ]
                )

                self._register_legend_entry_if_valid(lines[0], category_name)

        if not hasattr(ax, "_bump_configured"):
            ax.invert_yaxis()
            max_rank = int(self.plot_data["rank"].max())
            ax.set_yticks(range(1, max_rank + 1))
            ax.margins(x=0.15)
            ax.set_ylabel(
                self.style_applicator.get_style_with_fallback("ylabel", "Rank")
            )
            ax._bump_configured = True
