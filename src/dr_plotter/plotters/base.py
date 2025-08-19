"""
Base class for all plotter objects.
"""

import pandas as pd
import itertools
from dr_plotter.theme import BASE_THEME, DR_PLOTTER_STYLE_KEYS
from dr_plotter.consts import METRICS, METRICS_STR


class BasePlotter:
    """
    A base class for all atomic plotters with multi-series support.
    """

    def __init__(self, data, **kwargs):
        """
        Initialize the plotter.

        Args:
            data: A pandas DataFrame.
            **kwargs: All keyword arguments, including styling.
        """
        self.raw_data = data
        self.plot_data = None  # Will be set by prepare_data()
        self.kwargs = kwargs
        self.theme = BASE_THEME  # Default theme
        self.metric_column = None  # Will be set if metrics are melted
        self.melted_data = None  # Will hold melted data if needed

    def _validate_data(self):
        """
        Validate that data meets basic requirements for plotting.

        This base implementation checks:
        - Data is a pandas DataFrame
        - DataFrame is not empty

        Subclasses can override this method to add additional validation.
        """
        assert isinstance(self.raw_data, pd.DataFrame), "Data must be a pandas DataFrame"
        assert not self.raw_data.empty, "DataFrame cannot be empty"

    def prepare_data(self):
        """
        Prepare and validate data for plotting.

        This method validates the input data and performs any necessary
        preprocessing. Subclasses can override this method to add
        plotter-specific data preparation logic.

        Returns:
            The prepared data (by default, returns self.raw_data unchanged)
        """
        self._validate_data()
        # Set default plot_data (subclasses may override)
        self.plot_data = self.raw_data
        return self.plot_data

    def _melt_metrics(
        self, data, id_vars, value_vars, var_name="_metric", value_name="_value"
    ):
        """
        Convert wide format data to long format for multi-metric plotting.

        Args:
            data: DataFrame to melt
            id_vars: Columns to use as ID variables
            value_vars: Columns to melt (the metrics)
            var_name: Name for the metric column
            value_name: Name for the value column
        """
        # Handle case where some value_vars might not exist (wide format)
        existing_value_vars = [col for col in value_vars if col in data.columns]
        missing_value_vars = [col for col in value_vars if col not in data.columns]

        if existing_value_vars:
            # Standard melt for existing columns
            melted = pd.melt(
                data,
                id_vars=id_vars,
                value_vars=existing_value_vars,
                var_name=var_name,
                value_name=value_name,
            )
        else:
            melted = pd.DataFrame()

        # For missing columns, assume they are the value columns themselves (wide format)
        if missing_value_vars:
            wide_data = []
            for metric in missing_value_vars:
                if metric in data.columns:
                    metric_df = data[id_vars + [metric]].copy()
                    metric_df[var_name] = metric
                    metric_df[value_name] = metric_df[metric]
                    wide_data.append(metric_df)

            if wide_data:
                wide_melted = pd.concat(wide_data, ignore_index=True)
                melted = (
                    pd.concat([melted, wide_melted], ignore_index=True)
                    if not melted.empty
                    else wide_melted
                )

        return melted

    def _process_grouping_params(self, param_value):
        """
        Process a grouping parameter, handling METRICS constant.

        Args:
            param_value: The parameter value (could be column name, METRICS, or None)

        Returns:
            Processed column name or None
        """
        if param_value is None:
            return None
        elif param_value is METRICS or param_value == METRICS_STR:
            return self.metric_column
        else:
            return param_value

    def _create_style_cycles(self):
        """Create separate cycles for each visual channel."""
        return {
            "color": itertools.cycle(self.theme.get("color_cycle")),
            "linestyle": itertools.cycle(self.theme.get("linestyle_cycle")),
            "marker": itertools.cycle(self.theme.get("marker_cycle")),
            "size": itertools.cycle([1.0, 1.5, 2.0, 2.5]),  # Size multipliers
            "alpha": itertools.cycle([1.0, 0.7, 0.5, 0.3]),  # Alpha values
        }

    def _get_group_styles(
        self, data, hue=None, style=None, size=None, marker=None, alpha=None
    ):
        """
        Generate styles for each group based on visual encoding parameters.
        Supports redundant encoding where multiple visual channels can vary together.

        Returns:
            Dictionary mapping group values to their visual properties
        """
        cycles = self._create_style_cycles()
        styles = {}

        # Group visual channels by the column they encode
        # This allows multiple visual channels to vary together for the same column
        column_to_channels = {}
        channel_params = [
            ("hue", hue),
            ("style", style),
            ("size", size),
            ("marker", marker),
            ("alpha", alpha),
        ]

        for channel_name, column_name in channel_params:
            if column_name is not None:
                if column_name not in column_to_channels:
                    column_to_channels[column_name] = []
                column_to_channels[column_name].append(channel_name)

        # Create synchronized mappings for each unique column
        value_mappings = {}

        for column_name, channels in column_to_channels.items():
            unique_values = data[column_name].unique()

            # Create synchronized cycles for all channels that encode this column
            synchronized_cycles = {}
            for channel in channels:
                if channel == "hue":
                    synchronized_cycles[channel] = cycles["color"]
                elif channel == "style":
                    synchronized_cycles[channel] = cycles["linestyle"]
                elif channel == "marker":
                    synchronized_cycles[channel] = cycles["marker"]
                elif channel == "size":
                    synchronized_cycles[channel] = cycles["size"]
                elif channel == "alpha":
                    synchronized_cycles[channel] = cycles["alpha"]

            # Advance all cycles together for each unique value
            column_mapping = {}
            for value in unique_values:
                value_styles = {}
                for channel in channels:
                    if channel == "hue":
                        # Check for shared coordination first
                        if hasattr(self, "kwargs") and "_figure_manager" in self.kwargs:
                            shared_styles = self.kwargs["_shared_hue_styles"]
                            if value not in shared_styles:
                                # Get shared cycles from figure manager
                                fm = self.kwargs["_figure_manager"]
                                shared_cycles = fm._get_shared_style_cycles()
                                shared_styles[value] = {
                                    "color": next(shared_cycles["color"])
                                }
                            value_styles["color"] = shared_styles[value]["color"]
                        else:
                            value_styles["color"] = next(synchronized_cycles[channel])
                    elif channel == "style":
                        value_styles["linestyle"] = next(synchronized_cycles[channel])
                    elif channel == "marker":
                        value_styles["marker"] = next(synchronized_cycles[channel])
                    elif channel == "size":
                        value_styles["size_mult"] = next(synchronized_cycles[channel])
                    elif channel == "alpha":
                        value_styles["alpha"] = next(synchronized_cycles[channel])

                column_mapping[value] = value_styles

            value_mappings[column_name] = column_mapping

        # Get unique grouping columns (deduplicated)
        unique_grouping_cols = []
        grouping_params = [
            ("hue", hue),
            ("style", style),
            ("size", size),
            ("marker", marker),
            ("alpha", alpha),
        ]

        for param_name, column_name in grouping_params:
            if column_name is not None and column_name not in unique_grouping_cols:
                unique_grouping_cols.append(column_name)

        # Generate all combinations of unique grouping columns
        if unique_grouping_cols:
            # Get unique values for each unique column
            column_unique_values = [data[col].unique() for col in unique_grouping_cols]

            for combo in itertools.product(*column_unique_values):
                # Create group key from unique columns
                group_key = tuple(zip(unique_grouping_cols, combo))
                group_style = {}

                # Look up synchronized styles for each column in the combination
                for column_name, value in group_key:
                    column_styles = value_mappings[column_name][value]
                    group_style.update(column_styles)

                styles[group_key] = group_style
        else:
            # No grouping, single series
            styles[None] = {
                "color": next(cycles["color"]),
                "linestyle": next(cycles["linestyle"]),
            }

        return styles

    def _get_style(self, key, default_override=None):
        """Gets a style value, prioritizing user kwargs over theme defaults."""
        if key in self.kwargs:
            return self.kwargs.get(key)
        return self.theme.get(key, default_override)

    def _filter_plot_kwargs(self):
        """Removes dr_plotter specific keys from self.kwargs."""
        plot_kwargs = self.kwargs.copy()
        # Extended list of keys to filter
        filter_keys = DR_PLOTTER_STYLE_KEYS + [
            "hue",
            "style",
            "size",
            "marker",
            "alpha",
            "_figure_manager",  # Color coordination
            "_shared_hue_styles",  # Color coordination
        ]
        for key in filter_keys:
            plot_kwargs.pop(key, None)
        return plot_kwargs

    def _apply_styling(self, ax):
        """Apply high-level styling options to the axes object."""
        ax.set_title(
            self._get_style("title"), fontsize=self.theme.get("title_fontsize")
        )

        xlabel = self._get_style(
            "xlabel",
            self.x.replace("_", " ").title() if hasattr(self, "x") and self.x else None,
        )
        ax.set_xlabel(xlabel, fontsize=self.theme.get("label_fontsize"))

        ylabel = self._get_style(
            "ylabel",
            self.y.replace("_", " ").title() if hasattr(self, "y") and self.y else None,
        )
        ax.set_ylabel(ylabel, fontsize=self.theme.get("label_fontsize"))

        if self._get_style("grid", True):
            ax.grid(True, alpha=self.theme.get("grid_alpha"))
        else:
            ax.grid(False)

        if self._get_style("legend") is True or self._get_style("legend") is None:
            # Auto-show legend if we have groupings
            if hasattr(self, "_has_groups") and self._has_groups:
                if not ax.get_legend():
                    ax.legend(fontsize=self.theme.get("legend_fontsize"))
            elif self._get_style("legend") is True:
                if not ax.get_legend():
                    ax.legend(fontsize=self.theme.get("legend_fontsize"))

    def render(self, ax):
        """
        The core method to draw the plot on a matplotlib Axes object.
        """
        raise NotImplementedError(
            "The render method must be implemented by subclasses."
        )
