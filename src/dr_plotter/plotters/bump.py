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
    plotter_name = "bump"
    plotter_params = {"time_col", "category_col", "value_col", "hue", "style"}
    param_mapping = {"time_col": "x", "category_col": "group", "value_col": "y"}
    enabled_channels = {"hue": True, "style": True}
    default_theme = BUMP_PLOT_THEME
    data_validator = BumpPlotData


    def __init__(self, data, **kwargs):
        """Initialize with category_col mapped to hue_by for grouping."""
        # Map category_col to hue_by for proper grouping
        if 'category_col' in kwargs and 'hue_by' not in kwargs:
            kwargs['hue_by'] = kwargs.get('category_col')
        super().__init__(data, **kwargs)
    
    def _prepare_specific_data(self):
        """Calculate ranks for each category at each time point."""
        # Add rank calculation
        plot_data = self.plot_data.copy()
        plot_data["rank"] = plot_data.groupby(self.x)[self.y].rank(
            method="first", ascending=False
        )
        # Update y to point to rank column for plotting
        self.y = "rank"
        return plot_data

    def _draw(self, ax, data, legend, **kwargs):
        """
        Draw the bump plot using matplotlib.

        Args:
            ax: Matplotlib axes
            data: DataFrame with the data to plot (specific to one category)
            **kwargs: Plot-specific kwargs including color, marker, linewidth, label
        """
        # Sort data by time for proper line drawing
        category_data = data.sort_values(by=self.x)

        # Set defaults for bump-specific styling
        plot_kwargs = {
            "marker": self._get_style("marker"),
            "linewidth": self._get_style("line_width"),
        }
        plot_kwargs.update(kwargs)

        # Draw the line for this category
        ax.plot(category_data[self.x], category_data[self.y], **plot_kwargs)

        # Add category label at the end of the line
        if not category_data.empty:
            last_point = category_data.iloc[-1]
            category_name = kwargs.get("label", "Unknown")
            # Extract just the category name from "category=Cat_A" format if present
            if "=" in category_name:
                category_name = category_name.split("=")[1]
            text = ax.text(
                last_point[self.x],
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
            max_rank = int(self.plot_data["rank"].max())
            ax.set_yticks(range(1, max_rank + 1))
            ax.margins(x=0.15)
            ax._bump_configured = True
