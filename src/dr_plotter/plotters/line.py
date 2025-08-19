"""
Atomic plotter for line plots with multi-series support.
"""

from .base import BasePlotter
from dr_plotter.theme import LINE_THEME, BASE_COLORS
from dr_plotter.consts import METRICS


class LinePlotter(BasePlotter):
    """
    An atomic plotter for creating line plots with multi-series support.
    """

    def __init__(
        self,
        data,
        x,
        y,
        hue=None,
        style=None,
        size=None,
        marker=None,
        alpha=None,
        **kwargs,
    ):
        """
        Initialize the LinePlotter.

        Args:
            data: A pandas DataFrame
            x: Column name for x-axis
            y: Column name for y-axis, or list of column names for multiple metrics
            hue: Column name or METRICS for color grouping
            style: Column name or METRICS for linestyle grouping
            size: Column name or METRICS for line width grouping
            marker: Column name or METRICS for marker grouping
            alpha: Column name or METRICS for alpha/transparency grouping
            **kwargs: Additional styling parameters
        """
        super().__init__(data, **kwargs)
        self.x = x
        self.raw_y = y  # Store original y parameter
        self.theme = LINE_THEME
        
        # Store parameters for prepare_data
        self.init_hue = hue
        self.init_style = style
        self.init_size = size
        self.init_marker = marker
        self.init_alpha = alpha

    def prepare_data(self):
        """
        Prepare and validate data for line plotting.
        """
        # Call parent validation
        super().prepare_data()
        
        # Handle multi-metric case
        if isinstance(self.raw_y, list):
            # Set default hue to METRICS if not specified
            hue = self.init_hue
            if (
                hue is None
                and self.init_style is None
                and self.init_size is None
                and self.init_marker is None
                and self.init_alpha is None
            ):
                hue = METRICS

            # Melt the data to long format
            id_vars = [col for col in self.raw_data.columns if col not in self.raw_y and col != self.x]
            if self.x not in id_vars:
                id_vars = [self.x] + id_vars

            self.melted_data = self._melt_metrics(self.raw_data, id_vars, self.raw_y, "_metric", "_value")
            self.metric_column = "_metric"
            self.y = "_value"
            self.plot_data = self.melted_data
        else:
            self.y = self.raw_y
            self.plot_data = self.raw_data
            self.metric_column = None

        # Process grouping parameters
        self.hue = self._process_grouping_params(self.init_hue)
        self.style = self._process_grouping_params(self.init_style)
        self.size = self._process_grouping_params(self.init_size)
        self.marker = self._process_grouping_params(self.init_marker)
        self.alpha = self._process_grouping_params(self.init_alpha)

        # Check if we have any groupings
        self._has_groups = any(
            [self.hue, self.style, self.size, self.marker, self.alpha]
        )
        
        return self.plot_data

    def render(self, ax):
        """
        Render the line plot on the given axes.
        """
        self.prepare_data()
        
        if not self._has_groups:
            # Simple single line plot
            plot_kwargs = {
                "marker": self._get_style("marker"),
                "linestyle": self._get_style("linestyle", "-"),
                "linewidth": self._get_style("line_width"),
                "alpha": self._get_style("alpha"),
                "color": self._get_style("color", next(self.theme.get("color_cycle"))),
            }
            plot_kwargs.update(self._filter_plot_kwargs())

            if "label" in self.kwargs:
                plot_kwargs["label"] = self.kwargs["label"]

            ax.plot(self.plot_data[self.x], self.plot_data[self.y], **plot_kwargs)
        else:
            # Multi-series plot with groupings
            self._render_grouped(ax)

        self._apply_styling(ax)

    def _render_grouped(self, ax):
        """Render grouped line plots based on visual encoding parameters."""
        # Get the group styles
        group_styles = self._get_group_styles(
            self.plot_data, self.hue, self.style, self.size, self.marker, self.alpha
        )

        # Determine grouping columns
        group_cols = []
        if self.hue:
            group_cols.append(self.hue)
        if self.style:
            group_cols.append(self.style)
        if self.size:
            group_cols.append(self.size)
        if self.marker:
            group_cols.append(self.marker)
        if self.alpha:
            group_cols.append(self.alpha)

        # Remove duplicates while preserving order
        seen = set()
        group_cols = [x for x in group_cols if not (x in seen or seen.add(x))]

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
                    "linestyle": styles.get("linestyle", "-"),
                    "linewidth": self._get_style("line_width", 2.0)
                    * styles.get("size_mult", 1.0),
                    "marker": styles.get("marker", self._get_style("marker")),
                    "alpha": styles.get("alpha", self._get_style("alpha", 1.0)),
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

                # Sort by x for proper line plotting
                group_data_sorted = group_data.sort_values(self.x)

                # Plot the line
                ax.plot(
                    group_data_sorted[self.x], group_data_sorted[self.y], **plot_kwargs
                )
