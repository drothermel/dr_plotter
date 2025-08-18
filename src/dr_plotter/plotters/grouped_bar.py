"""
Compound plotter for grouped bar plots.
"""

from .base import BasePlotter
from ..theme import GROUPED_BAR_THEME


class GroupedBarPlotter(BasePlotter):
    """
    A compound plotter for creating grouped bar plots.
    """

    def __init__(self, data, x, y, hue, **kwargs):
        """
        Initialize the GroupedBarPlotter.
        """
        super().__init__(data, **kwargs)
        self.x = x
        self.y = y
        self.hue = hue
        self.theme = GROUPED_BAR_THEME

    def render(self, ax):
        """
        Render the grouped bar plot on the given axes.
        """
        pivoted_data = self.data.pivot(index=self.x, columns=self.hue, values=self.y)

        plot_kwargs = {
            "color": [
                next(self.theme.get("color_cycle")) for _ in pivoted_data.columns
            ],
            "alpha": self.theme.get("alpha"),
            "rot": self.theme.get("rotation"),
        }
        plot_kwargs.update(self._filter_plot_kwargs())

        pivoted_data.plot(kind="bar", ax=ax, width=0.8, **plot_kwargs)

        self.kwargs["legend"] = True  # Ensure legend is enabled for grouped bars
        self._apply_styling(ax)
