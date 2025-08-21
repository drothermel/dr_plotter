"""
Unified style generation engine for all plotter types.

This module provides a centralized approach to generating visual styles for grouped plots,
replacing the scattered manual color cycling and complex _get_group_styles method.
"""

import itertools


class StyleEngine:
    """
    Unified style generation for all grouped plotting.

    Manages visual style assignment for data groups using configurable visual channels.
    Supports both simple single-channel use (Bar/Violin) and complex multi-channel use (Line/Scatter).
    """

    def __init__(self, theme, enabled_channels=None):
        """
        Initialize the style engine.

        Args:
            theme: Theme object with style configuration
            enabled_channels: Dict of which visual channels to enable
                             Defaults to all channels enabled
        """
        self.theme = theme
        self.enabled_channels = enabled_channels or {
            "hue": True,
            "style": True,
            "size": True,
            "marker": True,
            "alpha": True,
        }

        # Create cycles ONCE and maintain state across calls
        self._cycles = self._create_cycles()

        # Track positions for debugging/reproducibility
        self._cycle_positions = {k: 0 for k in self._cycles}

        # Cache for consistent style assignment across calls
        self._style_cache = {}

    def _create_cycles(self):
        """Create style cycles from theme configuration."""
        return {
            "color": itertools.cycle(self.theme.get("color_cycle")),
            "linestyle": itertools.cycle(self.theme.get("linestyle_cycle")),
            "marker": itertools.cycle(self.theme.get("marker_cycle")),
            "size": itertools.cycle([1.0, 1.5, 2.0, 2.5]),  # Size multipliers
            "alpha": itertools.cycle([1.0, 0.7, 0.5, 0.3]),  # Alpha values
        }

    def generate_styles(
        self,
        data,
        hue_by=None,
        style_by=None,
        size_by=None,
        marker_by=None,
        alpha_by=None,
        shared_context=None,
    ):
        """
        Generate styles for grouped data based on visual encoding parameters.

        Args:
            data: DataFrame to generate styles for
            hue_by: Column name for color grouping
            style_by: Column name for linestyle grouping
            size_by: Column name for size grouping
            marker_by: Column name for marker grouping
            alpha_by: Column name for alpha grouping
            shared_context: Dict with shared styling context (e.g., figure manager)

        Returns:
            Dictionary mapping group keys to their visual properties
        """
        # Filter parameters based on enabled channels
        if not self.enabled_channels.get("hue"):
            hue_by = None
        if not self.enabled_channels.get("style"):
            style_by = None
        if not self.enabled_channels.get("size"):
            size_by = None
        if not self.enabled_channels.get("marker"):
            marker_by = None
        if not self.enabled_channels.get("alpha"):
            alpha_by = None

        styles = {}

        # Group visual channels by the column they encode
        column_to_channels = self._map_channels_to_columns(
            hue_by, style_by, size_by, marker_by, alpha_by
        )

        if not column_to_channels:
            # No grouping, single series
            styles[None] = {
                "color": next(self._cycles["color"]),
                "linestyle": next(self._cycles["linestyle"]),
            }
            return styles

        # Create value mappings for each column
        value_mappings = self._create_value_mappings(
            data, column_to_channels, shared_context
        )

        # Build final group style combinations
        return self._build_group_combinations(data, column_to_channels, value_mappings)

    def _map_channels_to_columns(
        self, hue_by=None, style_by=None, size_by=None, marker_by=None, alpha_by=None
    ):
        """Map visual channels to the data columns they encode."""
        column_to_channels = {}
        channel_params = [
            ("hue", hue_by),
            ("style", style_by),
            ("size", size_by),
            ("marker", marker_by),
            ("alpha", alpha_by),
        ]

        for channel_name, column_name in channel_params:
            if column_name is not None:
                if column_name not in column_to_channels:
                    column_to_channels[column_name] = []
                column_to_channels[column_name].append(channel_name)

        return column_to_channels

    def _create_value_mappings(self, data, column_to_channels, shared_context=None):
        """Create style mappings for unique values in each column."""
        value_mappings = {}

        for column_name, channels in column_to_channels.items():
            unique_values = data[column_name].unique()

            # Generate styles for each unique value using cache for consistency
            column_mapping = {}
            for value in unique_values:
                # Create cache key for this column-value pair
                cache_key = (column_name, value)

                if cache_key in self._style_cache:
                    # Use cached styles for consistency
                    value_styles = self._style_cache[cache_key]
                else:
                    # Generate new styles and cache them
                    value_styles = {}
                    for channel in channels:
                        if channel == "hue":
                            # Check for shared coordination first
                            if (
                                shared_context
                                and hasattr(shared_context, "get")
                                and "_figure_manager" in shared_context
                            ):
                                shared_styles = shared_context["_shared_hue_styles"]
                                if value not in shared_styles:
                                    # Get shared cycles from figure manager
                                    fm = shared_context["_figure_manager"]
                                    shared_cycles = fm._get_shared_style_cycles()
                                    shared_styles[value] = {
                                        "color": next(shared_cycles["color"])
                                    }
                                value_styles["color"] = shared_styles[value]["color"]
                            else:
                                value_styles["color"] = next(self._cycles["color"])
                        elif channel == "style":
                            value_styles["linestyle"] = next(self._cycles["linestyle"])
                        elif channel == "marker":
                            value_styles["marker"] = next(self._cycles["marker"])
                        elif channel == "size":
                            value_styles["size_mult"] = next(self._cycles["size"])
                        elif channel == "alpha":
                            value_styles["alpha"] = next(self._cycles["alpha"])

                    # Cache the generated styles
                    self._style_cache[cache_key] = value_styles

                column_mapping[value] = value_styles

            value_mappings[column_name] = column_mapping

        return value_mappings

    def _build_group_combinations(self, data, column_to_channels, value_mappings):
        """Build final style dictionary for all group combinations."""
        styles = {}

        # Get unique grouping columns (deduplicated)
        unique_grouping_cols = list(column_to_channels.keys())

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

        return styles

    def get_grouping_columns(
        self, hue_by=None, style_by=None, size_by=None, marker_by=None, alpha_by=None
    ):
        """
        Get list of columns used for grouping based on enabled channels.

        Returns:
            List of column names that will be used for groupby operations
        """
        columns = []

        if hue_by is not None and self.enabled_channels.get("hue"):
            columns.append(hue_by)
        if style_by is not None and self.enabled_channels.get("style"):
            columns.append(style_by)
        if size_by is not None and self.enabled_channels.get("size"):
            columns.append(size_by)
        if marker_by is not None and self.enabled_channels.get("marker"):
            columns.append(marker_by)
        if alpha_by is not None and self.enabled_channels.get("alpha"):
            columns.append(alpha_by)

        # Remove duplicates while preserving order
        seen = set()
        return [x for x in columns if not (x in seen or seen.add(x))]

    def reset_cycles(self):
        """Reset all style cycles to their starting positions."""
        self._cycles = self._create_cycles()
        self._cycle_positions = {k: 0 for k in self._cycles}
        self._style_cache = {}  # Clear cache when resetting

    def get_cycle_positions(self):
        """Get current positions of all cycles (for debugging/reproducibility)."""
        return self._cycle_positions.copy()
