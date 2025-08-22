import itertools
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from dr_plotter import consts
from dr_plotter.grouping import GroupingConfig
from dr_plotter.theme import Theme
from dr_plotter.types import VisualChannel


class StyleEngine:
    def __init__(
        self, theme: Theme, enabled_channels: Optional[Dict[VisualChannel, bool]] = None
    ) -> None:
        self.theme = theme
        self.enabled_channels = enabled_channels or consts.DEFAULT_ENABLED_CHANNELS

        self._cycles = self._create_cycles()
        self._cycle_positions: Dict[str, int] = {k: 0 for k in self._cycles}
        self._style_cache: Dict[Tuple[str, Any], Dict[str, Any]] = {}

    def _create_cycles(self) -> Dict[str, Any]:
        return {
            "color": itertools.cycle(self.theme.get("color_cycle")),
            "linestyle": itertools.cycle(self.theme.get("linestyle_cycle")),
            "marker": itertools.cycle(self.theme.get("marker_cycle")),
            "size": itertools.cycle([1.0, 1.5, 2.0, 2.5]),  # Size multipliers
            "alpha": itertools.cycle([1.0, 0.7, 0.5, 0.3]),  # Alpha values
        }

    def generate_styles(
        self,
        data: pd.DataFrame,
        grouping_config: GroupingConfig,
        shared_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[Any, Dict[str, Any]]:
        styles = {}

        column_to_channels = self._build_column_to_channels_from_grouping(
            grouping_config
        )

        if not column_to_channels:
            styles[None] = {
                "color": next(self._cycles["color"]),
                "linestyle": next(self._cycles["linestyle"]),
            }
            return styles

        value_mappings = self._create_value_mappings(
            data, column_to_channels, shared_context
        )
        return self._build_group_combinations(data, column_to_channels, value_mappings)

    def _build_column_to_channels_from_grouping(
        self, grouping_config: GroupingConfig
    ) -> Dict[str, List[str]]:
        column_to_channels = {}

        for channel, column_name in grouping_config.active.items():
            if self.enabled_channels.get(channel, False) and column_name is not None:
                if column_name not in column_to_channels:
                    column_to_channels[column_name] = []
                column_to_channels[column_name].append(channel)

        return column_to_channels

    def _has_figure_manager_context(
        self, shared_context: Optional[Dict[str, Any]]
    ) -> bool:
        return (
            shared_context is not None
            and hasattr(shared_context, "get")
            and "_figure_manager" in shared_context
        )

    def _create_value_mappings(
        self,
        data: pd.DataFrame,
        column_to_channels: Dict[str, List[str]],
        shared_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Dict[Any, Dict[str, Any]]]:
        value_mappings = {}

        for column_name, channels in column_to_channels.items():
            unique_values = data[column_name].unique()

            column_mapping = {}
            for value in unique_values:
                cache_key = (column_name, value)

                if cache_key in self._style_cache:
                    value_styles = self._style_cache[cache_key]
                else:
                    value_styles = {}
                    for channel in channels:
                        if channel == "hue":
                            if self._has_figure_manager_context(shared_context):
                                shared_styles = shared_context["_shared_hue_styles"]
                                if value not in shared_styles:
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

                    self._style_cache[cache_key] = value_styles

                column_mapping[value] = value_styles

            value_mappings[column_name] = column_mapping

        return value_mappings

    def _build_group_combinations(
        self,
        data: pd.DataFrame,
        column_to_channels: Dict[str, List[str]],
        value_mappings: Dict[str, Dict[Any, Dict[str, Any]]],
    ) -> Dict[Tuple[Tuple[str, Any], ...], Dict[str, Any]]:
        styles = {}

        unique_grouping_cols = list(column_to_channels.keys())

        if unique_grouping_cols:
            column_unique_values = [data[col].unique() for col in unique_grouping_cols]

            for combo in itertools.product(*column_unique_values):
                group_key = tuple(zip(unique_grouping_cols, combo))
                group_style = {}

                for column_name, value in group_key:
                    column_styles = value_mappings[column_name][value]
                    group_style.update(column_styles)

                styles[group_key] = group_style

        return styles

    def reset_cycles(self) -> None:
        self._cycles = self._create_cycles()
        self._cycle_positions = {k: 0 for k in self._cycles}
        self._style_cache = {}

    def get_cycle_positions(self) -> Dict[str, int]:
        return self._cycle_positions.copy()
