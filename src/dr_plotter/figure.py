"""
Context manager for creating complex figures.
"""

import matplotlib.pyplot as plt
import pandas as pd
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
    """

    def __init__(self, rows=1, cols=1, **fig_kwargs):
        """
        Initialize the FigureManager.
        """
        self.fig, self.axes = plt.subplots(
            rows, cols, constrained_layout=True, **fig_kwargs
        )

    def get_axes(self, row=None, col=None):
        """
        Get the axes object for a specific subplot for manual manipulation.
        """
        if not hasattr(self.axes, "__len__"):
            return self.axes
        if self.axes.ndim == 1:
            idx = col if col is not None else row
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
        plotter = plotter_class(*plotter_args, **kwargs)
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

    def violin(
        self,
        row,
        col,
        data: pd.DataFrame,
        x: str = None,
        y: str = None,
        hue: str = None,
        **kwargs,
    ):
        """Add a violin plot to a specified subplot."""
        self._add_plot(ViolinPlotter, (data, x, y, hue), row, col, **kwargs)

    def heatmap(self, row, col, data: pd.DataFrame, **kwargs):
        """Add a heatmap to a specified subplot."""
        self._add_plot(HeatmapPlotter, (data,), row, col, **kwargs)

    def bump_plot(
        self,
        row,
        col,
        data: pd.DataFrame,
        time_col: str,
        category_col: str,
        value_col: str,
        **kwargs,
    ):
        """Add a bump plot to a specified subplot."""
        self._add_plot(
            BumpPlotter, (data, time_col, category_col, value_col), row, col, **kwargs
        )

    def gmm_level_set(self, row, col, data: pd.DataFrame, x: str, y: str, **kwargs):
        """Add a GMM level set plot to a specified subplot."""
        self._add_plot(ContourPlotter, (data, x, y), row, col, **kwargs)

    def grouped_bar(
        self, row, col, data: pd.DataFrame, x: str, y: str, hue: str, **kwargs
    ):
        """Add a grouped bar plot to a specified subplot."""
        self._add_plot(GroupedBarPlotter, (data, x, y, hue), row, col, **kwargs)
