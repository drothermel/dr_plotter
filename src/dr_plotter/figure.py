"""
Context manager for creating complex figures.
"""

import matplotlib.pyplot as plt
import pandas as pd
from .utils import partition_kwargs
from .plotters.scatter import ScatterPlotter
from .plotters.line import LinePlotter
from .plotters.bar import BarPlotter
from .plotters.histogram import HistogramPlotter
from .plotters.violin import ViolinPlotter
from .plotters.heatmap import HeatmapPlotter
from .plotters.bump import BumpPlotter
from .plotters.contour import ContourPlotter
from .plotters.grouped_bar import GroupedBarPlotter

class FigureManager:
    """
    A context manager for creating complex figures with multiple subplots.
    Provides a high-level API similar to the main dr_plotter.api.
    """

    def __init__(self, rows=1, cols=1, **fig_kwargs):
        """
        Initialize the FigureManager.

        Args:
            rows: The number of rows of subplots.
            cols: The number of columns of subplots.
            **fig_kwargs: Keyword arguments to be passed to plt.subplots().
        """
        self.fig, self.axes = plt.subplots(rows, cols, **fig_kwargs)

    def get_axes(self, row=None, col=None):
        """
        Get the axes object for a specific subplot for manual manipulation.

        Args:
            row: The row of the subplot.
            col: The column of the subplot.

        Returns:
            A matplotlib Axes object.
        """
        if not hasattr(self.axes, '__len__'):
            return self.axes
        if self.axes.ndim == 1:
            idx = col if row is None else row
            return self.axes[idx]
        if row is not None and col is not None:
            return self.axes[row, col]
        elif row is not None:
            return self.axes[row, :]
        elif col is not None:
            return self.axes[:, col]
        return self.axes

    def _add_plot(self, plotter_class, plotter_args, row, col, **kwargs):
        """Private helper to add any plot type to a subplot."""
        ax = self.get_axes(row, col)
        dr_plotter_kwargs, matplotlib_kwargs = partition_kwargs(kwargs)
        plotter = plotter_class(*plotter_args, dr_plotter_kwargs, matplotlib_kwargs)
        plotter.render(ax)

    def scatter(self, row, col, data: pd.DataFrame, x: str, y: str, **kwargs):
        """Add a scatter plot to a specified subplot."""
        self._add_plot(ScatterPlotter, (data, x, y), row, col, **kwargs)

    def line(self, row, col, data: pd.DataFrame, x: str, y: str, **kwargs):
        """Add a line plot to a specified subplot."""
        self._add_plot(LinePlotter, (data, x, y), row, col, **kwargs)

    def bar(self, row, col, data: pd.DataFrame, x: str, y: str, **kwargs):
        """Add a bar plot to a specified subplot."""
        self._add_plot(BarPlotter, (data, x, y), row, col, **kwargs)

    def hist(self, row, col, data: pd.DataFrame, x: str, **kwargs):
        """Add a histogram to a specified subplot."""
        self._add_plot(HistogramPlotter, (data, x), row, col, **kwargs)

    def violin(self, row, col, data: pd.DataFrame, x: str = None, y: str = None, hue: str = None, **kwargs):
        """Add a violin plot to a specified subplot."""
        self._add_plot(ViolinPlotter, (data, x, y, hue), row, col, **kwargs)

    def heatmap(self, row, col, data: pd.DataFrame, **kwargs):
        """Add a heatmap to a specified subplot."""
        self._add_plot(HeatmapPlotter, (data,), row, col, **kwargs)

    def bump_plot(self, row, col, data: pd.DataFrame, time_col: str, category_col: str, value_col: str, **kwargs):
        """Add a bump plot to a specified subplot."""
        self._add_plot(BumpPlotter, (data, time_col, category_col, value_col), row, col, **kwargs)

    def gmm_level_set(self, row, col, data: pd.DataFrame, x: str, y: str, **kwargs):
        """Add a GMM level set plot to a specified subplot."""
        self._add_plot(ContourPlotter, (data, x, y), row, col, **kwargs)

    def grouped_bar(self, row, col, data: pd.DataFrame, x: str, y: str, hue: str, **kwargs):
        """Add a grouped bar plot to a specified subplot."""
        self._add_plot(GroupedBarPlotter, (data, x, y, hue), row, col, **kwargs)