"""
Atomic plotter for scatter plots with multi-series support.
"""

from .base import BasePlotter
from dr_plotter.theme import SCATTER_THEME, BASE_COLORS
from dr_plotter.consts import METRICS, METRICS_STR


class ScatterPlotter(BasePlotter):
    """
    An atomic plotter for creating scatter plots with multi-series support.
    """

    def __init__(
        self, data, x, y, hue=None, size=None, marker=None, alpha=None, **kwargs
    ):
        """
        Initialize the ScatterPlotter.

        Args:
            data: A pandas DataFrame
            x: Column name for x-axis
            y: Column name for y-axis, or list of column names for multiple metrics
            hue: Column name or METRICS for color grouping
            size: Column name or METRICS for marker size grouping
            marker: Column name or METRICS for marker style grouping
            alpha: Column name or METRICS for alpha/transparency grouping
            **kwargs: Additional styling parameters
        """
        super().__init__(data, **kwargs)
        self.x = x
        self.raw_y = y  # Store original y parameter
        self.theme = SCATTER_THEME
        
        # Store parameters for prepare_data
        self.init_hue = hue
        self.init_size = size
        self.init_marker = marker
        self.init_alpha = alpha

    def prepare_data(self):
        """
        Prepare and validate data for scatter plotting.
        """
        # Call parent validation
        super().prepare_data()
        
        # Handle multi-metric case
        if isinstance(self.raw_y, list):
            # Set default hue to METRICS if not specified
            hue = self.init_hue
            if hue is None and self.init_size is None and self.init_marker is None and self.init_alpha is None:
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
        self.size = self._process_grouping_params(self.init_size)
        self.alpha = self._process_grouping_params(self.init_alpha)

        # Handle marker parameter - check if it's a column name or direct matplotlib marker
        if (
            self.init_marker is not None
            and isinstance(self.init_marker, str)
            and self.init_marker not in self.plot_data.columns
            and self.init_marker not in [METRICS, METRICS_STR]
        ):
            # It's a direct matplotlib marker - don't treat as grouping parameter
            self.marker = None
            self.direct_marker = self.init_marker
        else:
            self.marker = self._process_grouping_params(self.init_marker)
            self.direct_marker = None

        # Check if we have any groupings
        self._has_groups = any([self.hue, self.size, self.marker, self.alpha])
        
        return self.plot_data

    def render(self, ax):
        """
        Render the scatter plot on the given axes.
        """
        self.prepare_data()
        
        if not self._has_groups:
            # Simple single scatter plot
            plot_kwargs = {
                "marker": self.direct_marker or self._get_style("marker", "o"),
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
        # Get the group styles
        group_styles = self._get_group_styles(
            self.plot_data,
            self.hue,
            None,
            self.size,
            marker=self.marker,
            alpha=self.alpha,
        )

        # Determine grouping columns
        group_cols = []
        if self.hue:
            group_cols.append(self.hue)
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
