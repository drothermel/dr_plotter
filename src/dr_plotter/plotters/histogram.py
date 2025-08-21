"""
Atomic plotter for histograms.
"""

from .base import BasePlotter
from dr_plotter.theme import HISTOGRAM_THEME
from .plot_data import HistogramData


class HistogramPlotter(BasePlotter):
    """
    An atomic plotter for creating histograms using declarative configuration.
    """

    # Declarative configuration
    plotter_name = "histogram"
    plotter_params = {"x"}
    param_mapping = {"x": "x"}
    enabled_channels = {}  # No grouping support for histograms
    default_theme = HISTOGRAM_THEME
    data_validator = HistogramData


    def _draw(self, ax, data, legend, **kwargs):
        """
        Draw the histogram using matplotlib.

        Args:
            ax: Matplotlib axes
            data: DataFrame with the data to plot
            **kwargs: Plot-specific kwargs including color, alpha, edgecolor
        """
        # Add edgecolor if not in kwargs
        if "edgecolor" not in kwargs:
            kwargs["edgecolor"] = self._get_style("edgecolor")

        ax.hist(data[self.x], **kwargs)
