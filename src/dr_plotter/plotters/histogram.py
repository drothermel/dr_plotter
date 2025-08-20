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
    default_theme = HISTOGRAM_THEME
    enabled_channels = {}  # No grouping support for histograms
    data_validator = HistogramData

    def __init__(self, data, x, **kwargs):
        """
        Initialize the HistogramPlotter.

        Args:
            data: A pandas DataFrame
            x: Column name for the data to histogram
            **kwargs: Additional configuration and styling parameters
        """
        super().__init__(data, **kwargs)
        self.x = x
        # Set y label based on density parameter
        self.y = self._get_style(
            "ylabel", "Density" if self.kwargs.get("density") else "Frequency"
        )

    def _draw(self, ax, data, **kwargs):
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
