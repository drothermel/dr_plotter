"""
Atomic plotter for scatter plots with multi-series support.
"""

from .base import BasePlotter
from dr_plotter.theme import SCATTER_THEME, BASE_COLORS
from dr_plotter.plotters.style_engine import StyleEngine
from .plot_data import ScatterPlotData


class ScatterPlotter(BasePlotter):
    """
    An atomic plotter for creating scatter plots with multi-series support.
    """

    def __init__(
        self,
        data,
        x,
        y,
        hue_by=None,
        size_by=None,
        marker_by=None,
        alpha_by=None,
        **kwargs,
    ):
        """
        Initialize the ScatterPlotter.

        Args:
            data: A pandas DataFrame
            x: Column name for x-axis
            y: Column name for y-axis, or list of column names for multiple metrics
            hue_by: Column name or METRICS for color grouping
            size_by: Column name or METRICS for marker size grouping
            marker_by: Column name or METRICS for marker style grouping
            alpha_by: Column name or METRICS for alpha/transparency grouping
            **kwargs: Additional styling parameters (including direct matplotlib params)
        """
        super().__init__(data, **kwargs)
        self.x = x
        self.y_param = y  # Store original y parameter
        self.hue_by = hue_by
        self.size_by = size_by
        self.marker_by = marker_by
        self.alpha_by = alpha_by
        self.theme = SCATTER_THEME

        # Create style engine with all channels enabled for complex scatter plots
        self.style_engine = StyleEngine(self.theme)

    def prepare_data(self):
        """
        Prepare and validate data for scatter plotting.
        """
        # Single unified call replaces 30+ lines of duplicated logic
        self.plot_data, self.y, self.metric_column = self._prepare_multi_metric_data(
            self.y_param,
            self.x,
            auto_hue_groupings={
                "hue": self.hue_by,
                "size": self.size_by,
                "marker": self.marker_by,
                "alpha": self.alpha_by,
            },
        )

        # Update hue_by if auto-set to METRICS
        if self.metric_column and self.hue_by is None:
            self.hue_by = self.metric_column

        # Create validated plot data
        validated_data = ScatterPlotData(data=self.plot_data, x=self.x, y=self.y)
        # Keep using DataFrame for consistency with other plotters
        self.plot_data = validated_data.data

        # Process grouping parameters (now with _by suffix)
        self.hue_by = self._process_grouping_params(self.hue_by)
        self.size_by = self._process_grouping_params(self.size_by)
        self.alpha_by = self._process_grouping_params(self.alpha_by)
        self.marker_by = self._process_grouping_params(self.marker_by)

        # Check if we have any groupings
        self._has_groups = any(
            [self.hue_by, self.size_by, self.marker_by, self.alpha_by]
        )

        return self.plot_data

    def render(self, ax):
        """
        Render the scatter plot on the given axes.
        """
        self.prepare_data()

        if not self._has_groups:
            # Simple single scatter plot
            plot_kwargs = {
                "marker": self._get_style("marker", "o"),
                "s": self._get_style("marker_size"),
                "alpha": self._get_style("alpha"),
                "color": self._get_style("color", next(self.theme.get("color_cycle"))),
            }
            plot_kwargs.update(self._filter_plot_kwargs())

            if "label" in self.kwargs:
                plot_kwargs["label"] = self.kwargs["label"]

            ax.scatter(self.plot_data[self.x], self.plot_data[self.y], **plot_kwargs)
        else:
            # Multi-series scatter with groupings
            self._render_grouped(ax)

        self._apply_styling(ax)

    def _render_grouped(self, ax):
        """Render grouped scatter plots based on visual encoding parameters."""
        # Get the group styles using style engine
        group_styles = self.style_engine.generate_styles(
            self.plot_data,
            hue_by=self.hue_by,
            size_by=self.size_by,
            marker_by=self.marker_by,
            alpha_by=self.alpha_by,
            shared_context=self.kwargs,
        )

        # Get grouping columns from style engine
        group_cols = self.style_engine.get_grouping_columns(
            hue_by=self.hue_by,
            size_by=self.size_by,
            marker_by=self.marker_by,
            alpha_by=self.alpha_by,
        )

        # Group the data and plot each group
        if group_cols:
            grouped = self.plot_data.groupby(group_cols)

            for name, group_data in grouped:
                # Create group key for style lookup
                if isinstance(name, tuple):
                    group_key = tuple(zip(group_cols, name))
                else:
                    group_key = tuple([(group_cols[0], name)])

                # Get styles for this group
                styles = group_styles.get(group_key, {})

                # Build plot kwargs - use consistent defaults for non-grouped properties
                if "color" not in styles:
                    # Use first color from theme's BASE_COLORS for consistency when color is not grouped
                    default_color = BASE_COLORS[0]
                else:
                    default_color = styles["color"]

                plot_kwargs = {
                    "color": default_color,
                    "marker": styles.get("marker", self._get_style("marker", "o")),
                    "s": self._get_style("marker_size", 50)
                    * styles.get("size_mult", 1.0),
                    "alpha": styles.get("alpha", self._get_style("alpha", 0.7)),
                }

                # Add any user-specified kwargs that aren't group-controlled
                user_kwargs = self._filter_plot_kwargs()
                for k, v in user_kwargs.items():
                    if k not in plot_kwargs:
                        plot_kwargs[k] = v

                # Create label
                if isinstance(name, tuple):
                    label_parts = []
                    for col, val in zip(group_cols, name):
                        if self.metric_column and col == self.metric_column:
                            label_parts.append(str(val))
                        else:
                            label_parts.append(f"{col}={val}")
                    plot_kwargs["label"] = ", ".join(label_parts)
                else:
                    if self.metric_column and group_cols[0] == self.metric_column:
                        plot_kwargs["label"] = str(name)
                    else:
                        plot_kwargs["label"] = f"{group_cols[0]}={name}"

                # Plot the scatter
                ax.scatter(group_data[self.x], group_data[self.y], **plot_kwargs)
