"""
Context manager for creating complex figures.
"""

import matplotlib.pyplot as plt
import pandas as pd
import itertools
import warnings
from .plotters import BasePlotter
# Import all plotters to ensure they're registered


class FigureManager:
    """
    A context manager for creating complex figures with multiple subplots.
    """

    def __init__(self, rows=1, cols=1, external_ax=None, layout_rect=None, layout_pad=None, **fig_kwargs):
        """
        Initialize the FigureManager in managed or external mode.

        Args:
            rows: Number of subplot rows (ignored if external_ax provided)
            cols: Number of subplot columns (ignored if external_ax provided)
            external_ax: Use external axes instead of creating new figure
            layout_rect: Optional custom rect parameter for tight_layout [left, bottom, right, top]
            layout_pad: Optional padding value for tight_layout (default: 0.5)
            **fig_kwargs: Additional arguments for plt.subplots (ignored if external_ax provided)
        """
        self._layout_rect = layout_rect  # Store for use in __exit__
        self._layout_pad = layout_pad if layout_pad is not None else 0.5  # Default to proven value
        
        if external_ax is not None:
            # External mode: work with provided axes
            self.fig = external_ax.get_figure()
            self.axes = external_ax
            self.external_mode = True
        else:
            # Managed mode: create own figure
            # Use tight_layout approach consistently with make_axes_locatable
            self.fig, self.axes = plt.subplots(
                rows, cols, constrained_layout=False, **fig_kwargs
            )
            self.external_mode = False

        # Cross-subplot style coordination
        self._shared_hue_styles = {}  # Maps hue values to consistent colors
        self._shared_style_cycles = None  # Lazy initialization

    def __enter__(self):
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager and finalize layout."""
        # Apply intelligent tight_layout with suptitle detection and user overrides
        try:
            if self._layout_rect is not None:
                # User-specified rect for edge cases
                self.fig.tight_layout(rect=self._layout_rect, pad=self._layout_pad)
            elif self.fig._suptitle is not None:
                # Standard 5% top margin for suptitle - proven community value
                self.fig.tight_layout(rect=[0, 0, 1, 0.95], pad=self._layout_pad)
            elif self._has_subplot_titles():
                # Reserve space for subplot titles in single-subplot figures
                self.fig.tight_layout(rect=[0, 0, 1, 0.95], pad=self._layout_pad)
            else:
                # Standard layout with good padding
                self.fig.tight_layout(pad=self._layout_pad)
        except ValueError as e:
            # Common tight_layout issues: overlapping elements, insufficient space
            warnings.warn(f"tight_layout failed: {e}. Layout may not be optimal.", UserWarning)
        except RuntimeError as e:
            # Runtime issues with layout computation
            warnings.warn(f"tight_layout runtime error: {e}. Layout may not be optimal.", UserWarning)
        return False

    def _has_subplot_titles(self):
        """Check if any subplot has a title that needs space."""
        # Handle both single axes and array of axes
        if hasattr(self.axes, 'flat'):
            # Multiple subplots - check all axes
            axes_to_check = self.axes.flat
        elif hasattr(self.axes, '__iter__') and not isinstance(self.axes, str):
            # Array of axes
            axes_to_check = self.axes
        else:
            # Single subplot
            axes_to_check = [self.axes]
        
        for ax in axes_to_check:
            if ax.get_title():  # Returns empty string if no title
                return True
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

    def scatter(
        self,
        row,
        col,
        data: pd.DataFrame,
        x: str,
        y: str,
        hue_by=None,
        size_by=None,
        marker_by=None,
        alpha_by=None,
        **kwargs,
    ):
        """Add a scatter plot to a specified subplot."""
        plotter_class = BasePlotter.get_plotter("scatter")
        self._add_plot(
            plotter_class,
            (data, x, y, hue_by, size_by, marker_by, alpha_by),
            row,
            col,
            **kwargs,
        )

    def line(
        self,
        row,
        col,
        data: pd.DataFrame,
        x: str,
        y: str,
        hue_by=None,
        style_by=None,
        size_by=None,
        marker_by=None,
        alpha_by=None,
        **kwargs,
    ):
        """Add a line plot to a specified subplot."""
        plotter_class = BasePlotter.get_plotter("line")
        self._add_plot(
            plotter_class,
            (data, x, y, hue_by, style_by, size_by, marker_by, alpha_by),
            row,
            col,
            **kwargs,
        )

    def bar(self, row, col, data: pd.DataFrame, x: str, y: str, hue_by=None, **kwargs):
        """Add a bar plot to a specified subplot."""
        plotter_class = BasePlotter.get_plotter("bar")
        self._add_plot(plotter_class, (data, x, y, hue_by), row, col, **kwargs)

    def hist(self, row, col, data: pd.DataFrame, x: str, **kwargs):
        """Add a histogram to a specified subplot."""
        plotter_class = BasePlotter.get_plotter("histogram")
        self._add_plot(plotter_class, (data, x), row, col, **kwargs)

    def violin(
        self,
        row,
        col,
        data: pd.DataFrame,
        x: str = None,
        y: str = None,
        hue_by: str = None,
        **kwargs,
    ):
        """Add a violin plot to a specified subplot."""
        plotter_class = BasePlotter.get_plotter("violin")
        self._add_plot(plotter_class, (data, x, y, hue_by), row, col, **kwargs)

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
        plotter_class = BasePlotter.get_plotter("heatmap")
        self._add_plot(plotter_class, (data, x, y, values), row, col, **kwargs)

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
        plotter_class = BasePlotter.get_plotter("bump")
        self._add_plot(
            plotter_class, (data, time_col, category_col, value_col), row, col, **kwargs
        )

    def gmm_level_set(self, row, col, data: pd.DataFrame, x: str, y: str, **kwargs):
        """Add a GMM level set plot to a specified subplot."""
        plotter_class = BasePlotter.get_plotter("contour")
        self._add_plot(plotter_class, (data, x, y), row, col, **kwargs)

    def grouped_bar(
        self, row, col, data: pd.DataFrame, x: str, y: str, hue_by: str, **kwargs
    ):
        """Add a grouped bar plot to a specified subplot."""
        plotter_class = BasePlotter.get_plotter("bar")
        self._add_plot(plotter_class, (data, x, y, hue_by), row, col, **kwargs)

    def plot(self, plot_type, row, col, *args, **kwargs):
        """
        Generic plot method that uses the registry to create any plot type.

        Args:
            plot_type: String name of the plot type (e.g., "scatter", "line")
            row: Row position in subplot grid
            col: Column position in subplot grid
            *args: Positional arguments to pass to the plotter constructor
            **kwargs: Keyword arguments to pass to the plotter constructor

        Example:
            fm.plot("scatter", 0, 0, data, "x_col", "y_col", hue="category")
            fm.plot("custom", 1, 0, data, custom_param=value)
        """
        plotter_class = BasePlotter.get_plotter(plot_type)
        self._add_plot(plotter_class, args, row, col, **kwargs)
