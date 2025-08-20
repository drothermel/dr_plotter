"""
Atomic plotter for bar plots with optional grouping support.
"""

import numpy as np

from dr_plotter.theme import BAR_THEME

from .base import BasePlotter
from .plot_data import BarPlotData


class BarPlotter(BasePlotter):
    """
    An atomic plotter for creating bar plots with optional grouping support using declarative configuration.
    """

    # Declarative configuration
    default_theme = BAR_THEME
    enabled_channels = {"hue": True}  # Bars support hue grouping
    data_validator = BarPlotData

    def __init__(self, data, x, y, hue_by=None, **kwargs):
        """
        Initialize the BarPlotter.

        Args:
            data: A pandas DataFrame
            x: Column name for x-axis (categories)
            y: Column name for y-axis (values), or list of column names for multiple metrics
            hue: Optional column name for grouping bars within each category
            **kwargs: Additional styling parameters
        """
        super().__init__(data, hue_by=hue_by, **kwargs)
        self.x = x
        self.y_param = y  # Store original y parameter

    def _draw(self, ax, data, **kwargs):
        """
        Draw the bar plot using matplotlib.

        Args:
            ax: Matplotlib axes
            data: DataFrame with the data to plot
            **kwargs: Plot-specific kwargs including color, alpha, label
        """
        # For single (non-grouped) plots, draw simple bars
        if not self._has_groups:
            ax.bar(data[self.x], data[self.y], **kwargs)
        else:
            # For grouped plots, we need special bar positioning logic
            self._draw_grouped_bars(ax, data, **kwargs)

    def _draw_grouped_bars(self, ax, data, **kwargs):
        """Draw grouped bars with proper positioning."""
        # Setup
        x_categories = self.plot_data[self.x].unique()
        x_pos = np.arange(len(x_categories))

        # Get all groups to calculate width
        group_cols = self.style_engine.get_grouping_columns(hue_by=self.hue_by)
        if group_cols:
            all_groups = list(self.plot_data.groupby(group_cols))
            n_groups = len(all_groups)
            width = 0.8 / n_groups if n_groups > 0 else 0.8

            # Find which group this data belongs to
            group_data_values = (
                data[group_cols].iloc[0]
                if len(group_cols) == 1
                else tuple(data[group_cols[i]].iloc[0] for i in range(len(group_cols)))
            )
            group_index = 0
            for i, (name, _) in enumerate(all_groups):
                if (
                    isinstance(name, tuple) and name == group_data_values
                ) or name == group_data_values:
                    group_index = i
                    break

            # Calculate offset for this group
            offset = width * (group_index - n_groups / 2 + 0.5)

            # Prepare y values for each x category
            y_values = []
            for x_cat in x_categories:
                cat_data = data[data[self.x] == x_cat]
                if not cat_data.empty:
                    y_values.append(cat_data[self.y].iloc[0])
                else:
                    y_values.append(0)  # Default to 0 if no data

            # Draw bars for this group
            ax.bar(x_pos + offset, y_values, width, **kwargs)

            # Set x-axis labels (only once)
            if not ax.get_xticklabels() or ax.get_xticklabels()[0].get_text() == "0":
                ax.set_xticks(x_pos)
                ax.set_xticklabels(x_categories)
