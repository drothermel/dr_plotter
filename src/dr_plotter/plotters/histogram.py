"""
Atomic plotter for histograms.
"""

from .base import BasePlotter


class HistogramPlotter(BasePlotter):
    """
    An atomic plotter for creating histograms.
    """

    def __init__(self, data, x, **kwargs):
        """
        Initialize the HistogramPlotter.

        Args:
            data: A pandas DataFrame.
            x: The column for the data to be binned.
            **kwargs: Styling options for the histogram.
        """
        super().__init__(data, **kwargs)
        self.x = x

    def render(self, ax):
        """
        Render the histogram on the given axes.

        Args:
            ax: A matplotlib Axes object.
        """
        ax.hist(self.data[self.x], **self.kwargs)
        self.style.apply_grid(ax)
