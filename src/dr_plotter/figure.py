"""
Context manager for creating complex figures.
"""

import matplotlib.pyplot as plt
import pandas as pd
from .utils import create_and_render_plot
from .plotters import (
    ScatterPlotter,
    LinePlotter,
    BarPlotter,
    HistogramPlotter,
    ViolinPlotter,
    HeatmapPlotter,
    BumpPlotter,
    ContourPlotter,
    GroupedBarPlotter,
)

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
        self.fig, self.axes = plt.subplots(rows, cols, constrained_layout=True, **fig_kwargs)

    def get_axes(self, row=None, col=None):
        """
        Get the axes object for a specific subplot for manual manipulation.

        Args:
            row: The row of the subplot.
            col: The column of the subplot.

        Returns:
            A matplotlib Axes object.
        """
        # If self.axes is not an array (e.g., 1x1 subplot), return it directly.
        if not hasattr(self.axes, '__len__'):
            return self.axes
        
        # If self.axes is a 1D array (e.g., 1xN or Nx1 subplots)
        if self.axes.ndim == 1:
            # If col is specified, use it as the index. Otherwise, use row.
            idx = col if col is not None else row
            return self.axes[idx]
        
        # If self.axes is a 2D array
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
        create_and_render_plot(ax, plotter_class, plotter_args, **kwargs)

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
