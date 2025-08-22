import itertools
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


class StyleEngine:
    def __init__(
        self, theme: Any, enabled_channels: Optional[Dict[str, bool]] = None
    ) -> None:
        self.theme = theme
        self.enabled_channels = enabled_channels or {
            "hue": True,
            "style": True,
            "size": True,
            "marker": True,
            "alpha": True,
        }

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
        hue_by: Optional[str] = None,
        style_by: Optional[str] = None,
        size_by: Optional[str] = None,
        marker_by: Optional[str] = None,
        alpha_by: Optional[str] = None,
        shared_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[Any, Dict[str, Any]]:
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

        column_to_channels = self._map_channels_to_columns(
            hue_by, style_by, size_by, marker_by, alpha_by
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

    def _has_figure_manager_context(
        self, shared_context: Optional[Dict[str, Any]]
    ) -> bool:
        return (
            shared_context is not None
            and hasattr(shared_context, "get")
            and "_figure_manager" in shared_context
        )

    def _map_channels_to_columns(
        self,
        hue_by: Optional[str] = None,
        style_by: Optional[str] = None,
        size_by: Optional[str] = None,
        marker_by: Optional[str] = None,
        alpha_by: Optional[str] = None,
    ) -> Dict[str, List[str]]:
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

    def get_grouping_columns(
        self,
        hue_by: Optional[str] = None,
        style_by: Optional[str] = None,
        size_by: Optional[str] = None,
        marker_by: Optional[str] = None,
        alpha_by: Optional[str] = None,
    ) -> List[str]:
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

        seen = set()
        return [x for x in columns if not (x in seen or seen.add(x))]

    def reset_cycles(self) -> None:
        self._cycles = self._create_cycles()
        self._cycle_positions = {k: 0 for k in self._cycles}
        self._style_cache = {}

    def get_cycle_positions(self) -> Dict[str, int]:
        return self._cycle_positions.copy()
