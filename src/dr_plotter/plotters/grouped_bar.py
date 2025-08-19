"""
Compound plotter for grouped bar plots.
"""

from .base import BasePlotter
from dr_plotter.theme import GROUPED_BAR_THEME
from .plot_data import GroupedBarData


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

    def prepare_data(self):
        """
        Prepare data for grouped bar plotting by pivoting to wide format.
        """
        # Create validated plot data first
        validated_data = GroupedBarData(
            data=self.raw_data,
            x=self.x,
            y=self.y,
            group=self.hue
        )
        
        # Pivot data for grouped bars
        self.plot_data = validated_data.data.pivot(index=self.x, columns=self.hue, values=self.y)
        return self.plot_data

    def render(self, ax):
        """
        Render the grouped bar plot on the given axes.
        """
        self.prepare_data()

        plot_kwargs = {
            "color": [
                next(self.theme.get("color_cycle")) for _ in self.plot_data.columns
            ],
            "alpha": self.theme.get("alpha"),
            "rot": self.theme.get("rotation"),
        }
        plot_kwargs.update(self._filter_plot_kwargs())

        self.plot_data.plot(kind="bar", ax=ax, width=0.8, **plot_kwargs)

        self.kwargs["legend"] = True  # Ensure legend is enabled for grouped bars
        self._apply_styling(ax)
