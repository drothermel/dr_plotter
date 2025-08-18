"""
Atomic plotter for histograms.
"""

from .base import BasePlotter


class HistogramPlotter(BasePlotter):
    """
    An atomic plotter for creating histograms.
    """

    def __init__(self, data, x, dr_plotter_kwargs, matplotlib_kwargs):
        """
        Initialize the HistogramPlotter.

        Args:
            data: A pandas DataFrame.
            x: The column for the data to be binned.
            dr_plotter_kwargs: High-level styling options for dr_plotter.
            matplotlib_kwargs: Low-level kwargs to pass to matplotlib.
        """
        super().__init__(data, dr_plotter_kwargs, matplotlib_kwargs)
        self.x = x
        self.y = None # Histograms don't have a y column

    def render(self, ax):
        """
        Render the histogram on the given axes.

        Args:
            ax: A matplotlib Axes object.
        """
        ax.hist(self.data[self.x], **self.matplotlib_kwargs)
        self.style.apply_grid(ax)

        # Apply styling with smart default for ylabel
        if 'ylabel' not in self.dr_plotter_kwargs:
            if self.matplotlib_kwargs.get('density'):
                self.dr_plotter_kwargs['ylabel'] = 'Density'
            else:
                self.dr_plotter_kwargs['ylabel'] = 'Frequency'
        self._apply_styling(ax)