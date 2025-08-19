"""
Atomic plotter for bar plots.
"""

from .base import BasePlotter
from dr_plotter.theme import BAR_THEME


class BarPlotter(BasePlotter):
    """
    An atomic plotter for creating bar plots.
    """

    def __init__(self, data, x, y, **kwargs):
        """
        Initialize the BarPlotter.
        """
        super().__init__(data, **kwargs)
        self.x = x
        self.y = y
        self.theme = BAR_THEME

    def render(self, ax):
        """
        Render the bar plot on the given axes.
        """
        plot_kwargs = {
            "alpha": self._get_style("alpha"),
            "color": self._get_style("color", next(self.theme.get("color_cycle"))),
        }
        plot_kwargs.update(self._filter_plot_kwargs())

        ax.bar(self.data[self.x], self.data[self.y], **plot_kwargs)
        self._apply_styling(ax)
