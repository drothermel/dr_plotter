"""
Atomic plotter for histograms.
"""

from .base import BasePlotter
from dr_plotter.theme import HISTOGRAM_THEME


class HistogramPlotter(BasePlotter):
    """
    An atomic plotter for creating histograms.
    """

    def __init__(self, data, x, **kwargs):
        """
        Initialize the HistogramPlotter.
        """
        super().__init__(data, **kwargs)
        self.x = x
        self.y = self._get_style(
            "ylabel", "Density" if self.kwargs.get("density") else "Frequency"
        )
        self.theme = HISTOGRAM_THEME

    def render(self, ax):
        """
        Render the histogram on the given axes.
        """
        plot_kwargs = {
            "alpha": self._get_style("alpha"),
            "color": self._get_style("color", next(self.theme.get("color_cycle"))),
            "edgecolor": self._get_style("edgecolor"),
        }
        plot_kwargs.update(self._filter_plot_kwargs())

        ax.hist(self.data[self.x], **plot_kwargs)
        self._apply_styling(ax)
