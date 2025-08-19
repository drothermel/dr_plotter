"""
Atomic plotter for bar plots.
"""

from .base import BasePlotter
from dr_plotter.theme import BAR_THEME
from .plot_data import BarPlotData


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

    def prepare_data(self):
        """
        Prepare and validate data for bar plotting.
        """
        # Create validated plot data
        self.plot_data = BarPlotData(
            data=self.raw_data,
            x=self.x,
            y=self.y
        )
        return self.plot_data

    def render(self, ax):
        """
        Render the bar plot on the given axes.
        """
        self.prepare_data()
        
        plot_kwargs = {
            "alpha": self._get_style("alpha"),
            "color": self._get_style("color", next(self.theme.get("color_cycle"))),
        }
        plot_kwargs.update(self._filter_plot_kwargs())

        ax.bar(self.plot_data.data[self.x], self.plot_data.data[self.y], **plot_kwargs)
        self._apply_styling(ax)
