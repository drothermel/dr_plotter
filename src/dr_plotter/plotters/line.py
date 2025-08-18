"""
Atomic plotter for line plots.
"""

from .base import BasePlotter


class LinePlotter(BasePlotter):
    """
    An atomic plotter for creating line plots.
    """

    def __init__(self, data, x, y, **kwargs):
        """
        Initialize the LinePlotter.

        Args:
            data: A pandas DataFrame.
            x: The column for the x-axis.
            y: The column for the y-axis.
            **kwargs: Styling options for the line plot.
        """
        super().__init__(data, **kwargs)
        self.x = x
        self.y = y

    def render(self, ax):
        """
        Render the line plot on the given axes.

        Args:
            ax: A matplotlib Axes object.
        """
        ax.plot(self.data[self.x], self.data[self.y], **self.kwargs)
        self.style.apply_grid(ax)
