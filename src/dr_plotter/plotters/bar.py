"""
Atomic plotter for bar plots with optional grouping support.
"""

import numpy as np

from dr_plotter.theme import BAR_THEME

from .base import BasePlotter
from .plot_data import BarPlotData


class BarPlotter(BasePlotter):
    """
    An atomic plotter for creating bar plots with optional grouping support.
    """

    def __init__(self, data, x, y, hue=None, **kwargs):
        """
        Initialize the BarPlotter.

        Args:
            data: A pandas DataFrame
            x: Column name for x-axis (categories)
            y: Column name for y-axis (values), or list of column names for multiple metrics
            hue: Optional column name for grouping bars within each category
            **kwargs: Additional styling parameters
        """
        super().__init__(data, **kwargs)
        self.x = x
        self.y_param = y  # Store original y parameter
        self.hue = hue
        self.theme = BAR_THEME

    def prepare_data(self):
        """
        Prepare and validate data for bar plotting.
        """
        # Gets multi-metric support for free
        self.plot_data, self.y, self.metric_column = self._prepare_multi_metric_data(
            self.y_param, self.x, 
            auto_hue_groupings={'hue': self.hue}
        )
        
        # Update hue if auto-set to METRICS
        if self.metric_column and self.hue is None:
            self.hue = self.metric_column
        
        # Create validated plot data for single metrics
        if self.metric_column is None:
            validated_data = BarPlotData(
                data=self.plot_data,
                x=self.x,
                y=self.y
            )
            self.plot_data = validated_data.data
        
        # Process grouping parameters
        self.hue = self._process_grouping_params(self.hue)
        
        # Validate hue column if provided
        if self.hue is not None:
            from .plot_data.base_validation import validate_columns_exist, validate_categorical_columns
            validate_columns_exist(self.plot_data, [self.hue])
            validate_categorical_columns(self.plot_data, [self.hue])
            self._has_groups = True
        else:
            self._has_groups = False

        return self.plot_data

    def render(self, ax):
        """
        Render the bar plot on the given axes.
        """
        self.prepare_data()

        if not self._has_groups:
            # Simple single bar plot
            plot_kwargs = {
                "alpha": self._get_style("alpha"),
                "color": self._get_style("color", next(self.theme.get("color_cycle"))),
            }
            plot_kwargs.update(self._filter_plot_kwargs())

            ax.bar(
                self.plot_data[self.x], self.plot_data[self.y], **plot_kwargs
            )
        else:
            # Grouped bar plot
            self._render_grouped(ax)

        self._apply_styling(ax)

    def _render_grouped(self, ax):
        """Render grouped bar plots using direct matplotlib positioning."""
        # Get unique categories and groups
        x_categories = self.plot_data[self.x].unique()
        hue_values = self.plot_data[self.hue].unique()

        # Calculate positioning
        x_pos = np.arange(len(x_categories))
        width = 0.8 / len(hue_values)  # Total width divided by number of groups

        # Get colors from theme
        colors = [next(self.theme.get("color_cycle")) for _ in range(len(hue_values))]

        # Plot each hue group
        for i, hue_val in enumerate(hue_values):
            # Filter data for this hue value
            hue_data = self.plot_data[self.plot_data[self.hue] == hue_val]

            # Get y values in the same order as x_categories
            y_values = []
            for x_cat in x_categories:
                cat_data = hue_data[hue_data[self.x] == x_cat]
                if not cat_data.empty:
                    y_values.append(cat_data[self.y].iloc[0])
                else:
                    y_values.append(0)  # Default to 0 if no data

            # Calculate offset for this group
            offset = width * (i - len(hue_values) / 2 + 0.5)

            # Plot bars for this hue group
            plot_kwargs = {
                "alpha": self._get_style("alpha"),
                "color": colors[i],
                "label": str(hue_val),
            }
            plot_kwargs.update(self._filter_plot_kwargs())

            ax.bar(x_pos + offset, y_values, width, **plot_kwargs)

        # Set x-axis labels
        ax.set_xticks(x_pos)
        ax.set_xticklabels(x_categories)

        # Ensure legend is shown for grouped bars
        if self._get_style("legend") is not False:
            ax.legend()
