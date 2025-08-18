"""
Atomic plotter for scatter plots with multi-series support.
"""

from .base import BasePlotter
from ..theme import SCATTER_THEME, BASE_COLORS
from ..consts import METRICS, METRICS_STR


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
        self.theme = SCATTER_THEME

        # Handle multi-metric case
        if isinstance(y, list):
            # Set default hue to METRICS if not specified
            if hue is None and size is None and marker is None and alpha is None:
                hue = METRICS

            # Melt the data to long format
            id_vars = [col for col in data.columns if col not in y and col != x]
            if x not in id_vars:
                id_vars = [x] + id_vars

            self.melted_data = self._melt_metrics(data, id_vars, y, "_metric", "_value")
            self.metric_column = "_metric"
            self.y = "_value"
            self.plot_data = self.melted_data
        else:
            self.y = y
            self.plot_data = data
            self.metric_column = None

        # Process grouping parameters
        self.hue = self._process_grouping_params(hue)
        self.size = self._process_grouping_params(size)
        self.alpha = self._process_grouping_params(alpha)

        # Handle marker parameter - check if it's a column name or direct matplotlib marker
        if (
            marker is not None
            and isinstance(marker, str)
            and marker not in self.plot_data.columns
            and marker not in [METRICS, METRICS_STR]
        ):
            # It's a direct matplotlib marker - don't treat as grouping parameter
            self.marker = None
            self.direct_marker = marker
        else:
            self.marker = self._process_grouping_params(marker)
            self.direct_marker = None

        # Check if we have any groupings
        self._has_groups = any([self.hue, self.size, self.marker, self.alpha])

    def render(self, ax):
        """
        Render the scatter plot on the given axes.
        """
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
