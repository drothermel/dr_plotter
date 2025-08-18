"""
Atomic plotter for scatter plots.
"""

from .base import BasePlotter


class ScatterPlotter(BasePlotter):
    """
    An atomic plotter for creating scatter plots.
    """

    def __init__(self, data, x, y, **kwargs):
        """
        Initialize the ScatterPlotter.

        Args:
            data: A pandas DataFrame.
            x: The column for the x-axis.
            y: The column for the y-axis.
            **kwargs: Styling options for the scatter plot.
        """
        super().__init__(data, **kwargs)
        self.x = x
        self.y = y

    def render(self, ax):
        """
        Render the scatter plot on the given axes.

        Args:
            ax: A matplotlib Axes object.
        """
        ax.scatter(self.data[self.x], self.data[self.y], **self.kwargs)
        self.style.apply_grid(ax)
