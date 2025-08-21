"""
Atomic plotter for scatter plots with multi-series support.
"""

from .base import BasePlotter
from dr_plotter.theme import SCATTER_THEME, BASE_COLORS
from dr_plotter.plotters.style_engine import StyleEngine
from .plot_data import ScatterPlotData


class ScatterPlotter(BasePlotter):
    """
    An atomic plotter for creating scatter plots with multi-series support.
    """

    # Declarative configuration
    plotter_name = "scatter"
    plotter_params = {"x", "y", "hue", "size", "marker", "alpha"}
    param_mapping = {"x": "x", "y": "y"}
    enabled_channels = {"hue": True, "size": True, "marker": True, "alpha": True}
    default_theme = SCATTER_THEME
    data_validator = ScatterPlotData


    def _draw(self, ax, data, legend, **kwargs):
        """
        Draw the scatter plot using matplotlib.

        Args:
            ax: Matplotlib axes
            data: DataFrame with the data to plot
            legend: Legend builder object (unused for scatter plots as they create their own legend entries)
            **kwargs: Plot-specific kwargs including color, marker, s (size), alpha
        """
        ax.scatter(data[self.x], data[self.y], **kwargs)

