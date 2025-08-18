"""
Atomic plotter for bar plots.
"""

from .base import BasePlotter


class BarPlotter(BasePlotter):
    """
    An atomic plotter for creating bar plots.
    """

    def __init__(self, data, x, y, **kwargs):
        """
        Initialize the BarPlotter.

        Args:
            data: A pandas DataFrame.
            x: The column for the x-axis (categories).
            y: The column for the y-axis (values).
            **kwargs: Styling options for the bar plot.
        """
        super().__init__(data, **kwargs)
        self.x = x
        self.y = y

    def render(self, ax):
        """
        Render the bar plot on the given axes.

        Args:
            ax: A matplotlib Axes object.
        """
        ax.bar(self.data[self.x], self.data[self.y], **self.kwargs)
        self.style.apply_grid(ax)
