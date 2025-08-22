"""
Compound plotter for bump plots.
"""

from typing import Dict, List

import matplotlib.patheffects as path_effects

from dr_plotter.plotters.plot_data import PlotData
from dr_plotter.theme import BUMP_PLOT_THEME, Theme
from dr_plotter.types import VisualChannel

from .base import BasePlotter, BasePlotterParamName, SubPlotterParamName
from .plot_data import BumpPlotData


class BumpPlotter(BasePlotter):
    plotter_name: str = "bump"
    plotter_params: List[str] = ["time_col", "category_col", "value_col"]
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Dict[VisualChannel, bool] = {"hue": True, "style": True}
    default_theme: Theme = BUMP_PLOT_THEME
    data_validator: PlotData = BumpPlotData

    def _initialize_subplot_specific_params(self) -> None:
        self.time_col = self.kwargs.get("time_col")
        self.value_col = self.kwargs.get("value_col")
        self.category_col = self.kwargs.get("category_col")
        # Ensure that the coloring is based on the category column
        self.grouping_params.hue = self.category_col

    def _plot_specific_data_prep(self) -> None:
        """Calculate ranks for each category at each time point."""
        # Add rank calculation
        self.plot_data["rank"] = self.plot_data.groupby(self.time_col)[
            self.value_col
        ].rank(method="first", ascending=False)
        # Update y to point to rank column for plotting
        self.value_col = "rank"

    def _draw(self, ax, data, legend, **kwargs):
        group_styles, group_cols = self._get_group_styles_cols()
        if group_cols:
            grouped = self.plot_data.groupby(group_cols)

            for name, group_data in grouped:
                # Create group key for style lookup
                if isinstance(name, tuple):
                    group_key = tuple(zip(group_cols, name))
                else:
                    group_key = tuple([(group_cols[0], name)])

                # Get styles for this group
                styles = group_styles.get(group_key, {})

                # Build plot kwargs for this group
                plot_kwargs = self._build_group_plot_kwargs(styles, name, group_cols)

                # Call the concrete plotter's draw method
                self._draw_simple(ax, group_data, legend, **plot_kwargs)
        ax.set_ylabel(self._get_style("ylabel", "Rank"))

    def _draw_simple(self, ax, data, legend, **kwargs):
        # Sort data by time for proper line drawing
        category_data = data.sort_values(by=self.time_col)

        # Draw the line for this category
        ax.plot(category_data[self.time_col], category_data[self.value_col], **kwargs)

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
                color=kwargs.get("color", "black"),
                fontweight="bold",
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
