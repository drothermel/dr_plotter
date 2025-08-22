import itertools
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from dr_plotter.grouping import GroupingConfig
from dr_plotter.theme import Theme
from dr_plotter.types import VisualChannel


class StyleEngine:
    def __init__(self, theme: Theme, figure_manager: Optional[Any] = None) -> None:
        self.theme = theme
        self.figure_manager = figure_manager
        self._cycles = self._create_cycles()
        self._cycle_positions: Dict[str, int] = {k: 0 for k in self._cycles}
        self._style_cache: Dict[Tuple[str, Any], Dict[str, Any]] = {}

    @property
    def _ungrouped_default_styles(self) -> Dict[None, Dict[str, Any]]:
        return {
            None: {
                "color": next(self._cycles["color"]),
                "linestyle": next(self._cycles["linestyle"]),
            }
        }

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
        grp_cfg: GroupingConfig,
    ) -> Dict[Any, Dict[str, Any]]:
        if not grp_cfg.any_active:
            return self._ungrouped_default_styles
        col_to_viz = self._invert_groupings_to_column_mapping(grp_cfg.active)
        value_mappings = self._create_value_mappings(data, col_to_viz)
        return self._build_group_combinations(data, col_to_viz, value_mappings)

    def _invert_groupings_to_column_mapping(
        self, active_groupings: Dict[VisualChannel, str]
    ) -> Dict[str, List[str]]:
        inverted = {}
        for channel, column_name in active_groupings.items():
            if column_name not in inverted:
                inverted[column_name] = []
            inverted[column_name].append(channel)
        return inverted

    def _create_value_mappings(
        self,
        data: pd.DataFrame,
        column_to_channels: Dict[str, List[str]],
    ) -> Dict[str, Dict[Any, Dict[str, Any]]]:
        value_mappings = {}

        for column_name, channels in column_to_channels.items():
            unique_values = data[column_name].unique()
            column_mapping = self._create_column_value_mapping(
                column_name, unique_values, channels
            )
            value_mappings[column_name] = column_mapping

        return value_mappings

    def _create_column_value_mapping(
        self,
        column_name: str,
        unique_values: Any,
        channels: List[str],
    ) -> Dict[Any, Dict[str, Any]]:
        column_mapping = {}

        for value in unique_values:
            value_styles = self._get_or_create_value_styles(
                column_name, value, channels
            )
            column_mapping[value] = value_styles

        return column_mapping

    def _get_or_create_value_styles(
        self,
        column_name: str,
        value: Any,
        channels: List[str],
    ) -> Dict[str, Any]:
        cache_key = (column_name, value)

        if cache_key in self._style_cache:
            return self._style_cache[cache_key]

        value_styles = self._generate_value_styles(channels, value)
        self._style_cache[cache_key] = value_styles
        return value_styles

    def _generate_value_styles(
        self,
        channels: List[str],
        value: Any,
    ) -> Dict[str, Any]:
        value_styles = {}

        for channel in channels:
            style_attribute = self._get_style_for_channel(channel, value)
            value_styles.update(style_attribute)

        return value_styles

    def _get_style_for_channel(
        self,
        channel: str,
        value: Any,
    ) -> Dict[str, Any]:
        if channel == "hue":
            return {"color": self._get_hue_color(value)}
        elif channel == "style":
            return {"linestyle": next(self._cycles["linestyle"])}
        elif channel == "marker":
            return {"marker": next(self._cycles["marker"])}
        elif channel == "size":
            return {"size_mult": next(self._cycles["size"])}
        elif channel == "alpha":
            return {"alpha": next(self._cycles["alpha"])}
        return {}

    def _get_hue_color(self, value: Any) -> str:
        if self.figure_manager is None:
            return next(self._cycles["color"])

        shared_styles = self.figure_manager._shared_hue_styles
        if value in shared_styles:
            return shared_styles[value]["color"]

        shared_cycles = self.figure_manager._get_shared_style_cycles()
        color = next(shared_cycles["color"])
        shared_styles[value] = {"color": color}
        return color

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
