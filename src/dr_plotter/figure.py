"""
Context manager for creating complex figures.
"""

import matplotlib.pyplot as plt
import pandas as pd
import itertools
from .plotters import (
    ScatterPlotter,
    LinePlotter,
    BarPlotter,
    HistogramPlotter,
    ViolinPlotter,
    HeatmapPlotter,
    BumpPlotter,
    ContourPlotter,
)


class FigureManager:
    """
    A context manager for creating complex figures with multiple subplots.
    """

    def __init__(self, rows=1, cols=1, external_ax=None, **fig_kwargs):
        """
        Initialize the FigureManager in managed or external mode.
        
        Args:
            rows: Number of subplot rows (ignored if external_ax provided)
            cols: Number of subplot columns (ignored if external_ax provided)  
            external_ax: Use external axes instead of creating new figure
            **fig_kwargs: Additional arguments for plt.subplots (ignored if external_ax provided)
        """
        if external_ax is not None:
            # External mode: work with provided axes
            self.fig = external_ax.get_figure()
            self.axes = external_ax
            self.external_mode = True
        else:
            # Managed mode: create own figure
            self.fig, self.axes = plt.subplots(
                rows, cols, constrained_layout=True, **fig_kwargs
            )
            self.external_mode = False
            
        # Cross-subplot style coordination
        self._shared_hue_styles = {}  # Maps hue values to consistent colors
        self._shared_style_cycles = None  # Lazy initialization

    def __enter__(self):
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        # No cleanup needed, but context manager protocol requires this
        return False

    def get_axes(self, row=None, col=None):
        """
        Get the axes object for a specific subplot for manual manipulation.
        In external mode, returns the external axes regardless of row/col.
        """
        if self.external_mode:
            return self.axes
            
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

    def _get_shared_style_cycles(self):
        """Initialize shared style cycles once, reuse across subplots."""
        if self._shared_style_cycles is None:
            # Use BASE_THEME to create consistent cycles across subplots
            from .theme import BASE_THEME

            self._shared_style_cycles = {
                "color": itertools.cycle(BASE_THEME.get("color_cycle")),
                "linestyle": itertools.cycle(BASE_THEME.get("linestyle_cycle")),
                "marker": itertools.cycle(BASE_THEME.get("marker_cycle")),
            }
        return self._shared_style_cycles

    def _add_plot(self, plotter_class, plotter_args, row, col, **kwargs):
        """Private helper to add any plot type to a subplot with style coordination."""
        if self.external_mode:
            # In external mode, ignore row/col and use the external axes
            ax = self.axes
        else:
            # In managed mode, use row/col to get the correct subplot
            ax = self.get_axes(row, col)

        # Add shared style state for cross-subplot coordination
        kwargs["_figure_manager"] = self
        kwargs["_shared_hue_styles"] = self._shared_hue_styles

        plotter = plotter_class(*plotter_args, **kwargs)
        plotter.render(ax)

    def scatter(self, row, col, data: pd.DataFrame, x: str, y: str, 
               hue=None, size=None, marker=None, alpha=None, **kwargs):
        """Add a scatter plot to a specified subplot."""
        self._add_plot(ScatterPlotter, (data, x, y, hue, size, marker, alpha), row, col, **kwargs)

    def line(self, row, col, data: pd.DataFrame, x: str, y: str,
            hue=None, style=None, size=None, marker=None, alpha=None, **kwargs):
        """Add a line plot to a specified subplot."""
        self._add_plot(LinePlotter, (data, x, y, hue, style, size, marker, alpha), row, col, **kwargs)

    def bar(self, row, col, data: pd.DataFrame, x: str, y: str, hue=None, **kwargs):
        """Add a bar plot to a specified subplot."""
        self._add_plot(BarPlotter, (data, x, y, hue), row, col, **kwargs)

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

    def heatmap(
        self, row, col, data: pd.DataFrame, x: str, y: str, values: str, **kwargs
    ):
        """
        Add a heatmap to a specified subplot.

        Args:
            row: Row position in subplot grid
            col: Column position in subplot grid
            data: DataFrame containing the data in tidy/long format
            x: Column name for heatmap columns (x-axis)
            y: Column name for heatmap rows (y-axis)
            values: Column name for cell values
            **kwargs: Additional styling parameters
        """
        self._add_plot(HeatmapPlotter, (data, x, y, values), row, col, **kwargs)

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
        self._add_plot(BarPlotter, (data, x, y, hue), row, col, **kwargs)
