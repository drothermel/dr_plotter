"""
Atomic plotter for line plots.
"""

from .base import BasePlotter
from ..theme import LINE_THEME


class LinePlotter(BasePlotter):
    """
    An atomic plotter for creating line plots.
    """

    def __init__(self, data, x, y, **kwargs):
        """
        Initialize the LinePlotter.
        """
        super().__init__(data, **kwargs)
        self.x = x
        self.y = y
        self.theme = LINE_THEME

    def render(self, ax):
        """
        Render the line plot on the given axes.
        """
        plot_kwargs = {
            "marker": self._get_style("marker"),
            "linestyle": self._get_style(
                "linestyle", next(self.theme.get("linestyle_cycle"))
            ),
            "linewidth": self._get_style("line_width"),
            "alpha": self._get_style("alpha"),
            "color": self._get_style("color", next(self.theme.get("color_cycle"))),
        }
        plot_kwargs.update(self._filter_plot_kwargs())

        ax.plot(self.data[self.x], self.data[self.y], **plot_kwargs)
        self._apply_styling(ax)
