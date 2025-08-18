"""
Atomic plotter for bar plots.
"""

from .base import BasePlotter


class BarPlotter(BasePlotter):
    """
    An atomic plotter for creating bar plots.
    """

    def __init__(self, data, x, y, dr_plotter_kwargs, matplotlib_kwargs):
        """
        Initialize the BarPlotter.

        Args:
            data: A pandas DataFrame.
            x: The column for the x-axis (categories).
            y: The column for the y-axis (values).
            dr_plotter_kwargs: High-level styling options for dr_plotter.
            matplotlib_kwargs: Low-level kwargs to pass to matplotlib.
        """
        super().__init__(data, dr_plotter_kwargs, matplotlib_kwargs)
        self.x = x
        self.y = y

    def render(self, ax):
        """
        Render the bar plot on the given axes.

        Args:
            ax: A matplotlib Axes object.
        """
        if not self.data.empty and self.x is not None and self.y is not None:
            ax.bar(self.data[self.x], self.data[self.y], **self.matplotlib_kwargs)
        
        self.style.apply_grid(ax)
        self._apply_styling(ax)