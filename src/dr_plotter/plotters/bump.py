"""
Compound plotter for bump plots.
"""

import matplotlib.patheffects as path_effects
from .base import BasePlotter
from dr_plotter.theme import BUMP_PLOT_THEME
from .plot_data import BumpPlotData


class BumpPlotter(BasePlotter):
    """
    A compound plotter for creating bump plots using declarative configuration.
    """

    # Declarative configuration
    default_theme = BUMP_PLOT_THEME
    enabled_channels = {"hue": True}  # Bump plots support hue grouping for categories
    data_validator = BumpPlotData

    def __init__(self, data, time_col, category_col, value_col, **kwargs):
        """
        Initialize the BumpPlotter.
        """
        super().__init__(data, hue_by=category_col, **kwargs)
        self.time_col = time_col
        self.category_col = category_col
        self.value_col = value_col
        self.x = time_col
        self.y = "rank"

    def _prepare_specific_data(self):
        """Calculate ranks for each category at each time point."""
        # Add rank calculation
        plot_data = self.plot_data.copy()
        plot_data["rank"] = plot_data.groupby(self.time_col)[self.value_col].rank(
            method="first", ascending=False
        )
        return plot_data

    def _draw(self, ax, data, **kwargs):
        """
        Draw the bump plot using matplotlib.

        Args:
            ax: Matplotlib axes
            data: DataFrame with the data to plot (specific to one category)
            **kwargs: Plot-specific kwargs including color, marker, linewidth, label
        """
        # Sort data by time for proper line drawing
        category_data = data.sort_values(by=self.time_col)

        # Set defaults for bump-specific styling
        plot_kwargs = {
            "marker": self._get_style("marker"),
            "linewidth": self._get_style("line_width"),
        }
        plot_kwargs.update(kwargs)

        # Draw the line for this category
        ax.plot(category_data[self.time_col], category_data[self.y], **plot_kwargs)

        # Add category label at the end of the line
        if not category_data.empty:
            last_point = category_data.iloc[-1]
            category_name = kwargs.get("label", "Unknown")
            text = ax.text(
                last_point[self.time_col],
                last_point[self.y],
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
            max_rank = int(self.plot_data[self.y].max())
            ax.set_yticks(range(1, max_rank + 1))
            ax.margins(x=0.15)
            ax._bump_configured = True
