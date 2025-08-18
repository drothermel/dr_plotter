"""
Atomic plotter for scatter plots.
"""

from .base import BasePlotter
from ..theme import SCATTER_THEME


class ScatterPlotter(BasePlotter):
    """
    An atomic plotter for creating scatter plots.
    """

    def __init__(self, data, x, y, **kwargs):
        """
        Initialize the ScatterPlotter.
        """
        super().__init__(data, **kwargs)
        self.x = x
        self.y = y
        self.theme = SCATTER_THEME

    def render(self, ax):
        """
        Render the scatter plot on the given axes.
        """
        plot_kwargs = {
            "marker": self._get_style("marker"),
            "s": self._get_style("marker_size"),
            "alpha": self._get_style("alpha"),
            "color": self._get_style("color", next(self.theme.get("color_cycle"))),
        }
        plot_kwargs.update(self._filter_plot_kwargs())

        ax.scatter(self.data[self.x], self.data[self.y], **plot_kwargs)
        self._apply_styling(ax)
