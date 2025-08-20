"""
Atomic plotter for bar plots with optional grouping support.
"""

import numpy as np

from dr_plotter.theme import BAR_THEME
from dr_plotter.plotters.style_engine import StyleEngine

from .base import BasePlotter
from .plot_data import BarPlotData


class BarPlotter(BasePlotter):
    """
    An atomic plotter for creating bar plots with optional grouping support.
    """

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
        super().__init__(data, **kwargs)
        self.x = x
        self.y_param = y  # Store original y parameter
        self.hue_by = hue_by
        self.theme = BAR_THEME

        # Create style engine with only hue channel enabled (bars only use color)
        self.style_engine = StyleEngine(self.theme, enabled_channels={"hue": True})

    def prepare_data(self):
        """
        Prepare and validate data for bar plotting.
        """
        # Gets multi-metric support for free
        self.plot_data, self.y, self.metric_column = self._prepare_multi_metric_data(
            self.y_param, self.x, auto_hue_groupings={"hue": self.hue_by}
        )

        # Update hue_by if auto-set to METRICS
        if self.metric_column and self.hue_by is None:
            self.hue_by = self.metric_column

        # Create validated plot data for single metrics
        if self.metric_column is None:
            validated_data = BarPlotData(data=self.plot_data, x=self.x, y=self.y)
            self.plot_data = validated_data.data

        # Process grouping parameters
        self.hue_by = self._process_grouping_params(self.hue_by)

        # Check if we have groupings
        self._has_groups = self.hue_by is not None

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

            ax.bar(self.plot_data[self.x], self.plot_data[self.y], **plot_kwargs)
        else:
            # Grouped bar plot
            self._render_grouped(ax)

        self._apply_styling(ax)

    def _render_grouped(self, ax):
        """Render grouped bars using unified style system."""
        # Setup
        x_categories = self.plot_data[self.x].unique()
        x_pos = np.arange(len(x_categories))

        # Generate styles using unified engine (same pattern as Line/Scatter!)
        group_styles = self.style_engine.generate_styles(
            self.plot_data, hue_by=self.hue_by
        )

        # Get grouping columns (will be [self.hue_by])
        group_cols = self.style_engine.get_grouping_columns(hue_by=self.hue_by)

        # Use standard groupby pattern (same as Line/Scatter!)
        if group_cols:
            grouped = self.plot_data.groupby(group_cols)
            n_groups = len(list(grouped))
            width = 0.8 / n_groups if n_groups > 0 else 0.8

            for i, (name, group_data) in enumerate(grouped):
                # Standard style lookup (same as Line/Scatter!)
                group_key = tuple([(group_cols[0], name)])
                styles = group_styles.get(group_key, {})

                # Extract color from unified styles
                color = styles.get("color", "blue")

                # Bar-specific geometry calculations
                offset = width * (i - n_groups / 2 + 0.5)
                y_values = []
                for x_cat in x_categories:
                    cat_data = group_data[group_data[self.x] == x_cat]
                    if not cat_data.empty:
                        y_values.append(cat_data[self.y].iloc[0])
                    else:
                        y_values.append(0)  # Default to 0 if no data

                # Plot bars with unified style
                plot_kwargs = {
                    "alpha": self._get_style("alpha"),
                    "color": color,
                    "label": str(name),
                }
                plot_kwargs.update(self._filter_plot_kwargs())

                ax.bar(x_pos + offset, y_values, width, **plot_kwargs)

        # Set x-axis labels
        ax.set_xticks(x_pos)
        ax.set_xticklabels(x_categories)

        # Ensure legend is shown for grouped bars
        if self._get_style("legend") is not False:
            ax.legend()
