"""
Atomic plotter for line plots with multi-series support.
"""

from .base import BasePlotter
from dr_plotter.theme import LINE_THEME, BASE_COLORS
from dr_plotter.plotters.style_engine import StyleEngine
from .plot_data import LinePlotData


class LinePlotter(BasePlotter):
    """
    An atomic plotter for creating line plots with multi-series support.
    """

    # Declarative configuration
    plotter_name = "line"
    plotter_params = {"x", "y", "hue", "style", "size", "marker", "alpha"}
    param_mapping = {"x": "x", "y": "y"}
    enabled_channels = {"hue": True, "style": True, "size": True, "marker": True, "alpha": True}
    default_theme = LINE_THEME
    data_validator = LinePlotData


    def _draw(self, ax, data, legend, **kwargs):
        """
        Draw the line plot using matplotlib.

        Args:
            ax: Matplotlib axes
            data: DataFrame with the data to plot
            legend: Legend builder object (unused for line plots as they create their own legend entries)
            **kwargs: Plot-specific kwargs including color, linestyle, linewidth, marker, alpha
        """
        # Sort data for proper line plotting
        data_sorted = data.sort_values(self.x)
        ax.plot(data_sorted[self.x], data_sorted[self.y], **kwargs)

