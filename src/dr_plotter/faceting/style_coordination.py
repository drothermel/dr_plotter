from typing import Any, Dict, List, Optional, Set
import pandas as pd


class FacetStyleCoordinator:
    def __init__(self, theme: Optional[Dict[str, Any]] = None) -> None:
        self._dimension_values: Dict[str, Set[str]] = {}
        self._style_assignments: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._cycle_positions: Dict[str, int] = {}
        self._max_cached_dimensions = 5
        self._theme = theme or {}

    def register_dimension_values(self, dimension: str, values: List[str]) -> None:
        if (
            len(self._dimension_values) >= self._max_cached_dimensions
            and dimension not in self._dimension_values
        ):
            self._evict_lru_dimension()

        if dimension not in self._dimension_values:
            self._dimension_values[dimension] = set()

        new_values = set(values) - self._dimension_values[dimension]
        if new_values:
            self._dimension_values[dimension].update(new_values)

            if dimension not in self._style_assignments:
                self._style_assignments[dimension] = {}
                self._cycle_positions[dimension] = 0

            self._assign_styles_to_new_values(dimension, sorted(new_values, key=str))

    def _evict_lru_dimension(self) -> None:
        if self._dimension_values:
            oldest_dimension = next(iter(self._dimension_values))
            del self._dimension_values[oldest_dimension]
            if oldest_dimension in self._style_assignments:
                del self._style_assignments[oldest_dimension]
            if oldest_dimension in self._cycle_positions:
                del self._cycle_positions[oldest_dimension]

    def _assign_styles_to_new_values(
        self, dimension: str, ordered_values: List[str]
    ) -> None:
        for value in ordered_values:
            if value not in self._style_assignments[dimension]:
                style_dict = self._get_next_style_from_cycle(dimension)
                self._style_assignments[dimension][value] = style_dict
                self._cycle_positions[dimension] += 1

    def _get_next_style_from_cycle(self, dimension: str) -> Dict[str, Any]:
        position = self._cycle_positions[dimension]

        if "color_cycle" in self._theme and self._theme["color_cycle"]:
            colors = self._theme["color_cycle"]
        else:
            colors = [
                "#1f77b4",
                "#ff7f0e",
                "#2ca02c",
                "#d62728",
                "#9467bd",
                "#8c564b",
                "#e377c2",
                "#7f7f7f",
                "#bcbd22",
                "#17becf",
            ]

        if "marker_cycle" in self._theme and self._theme["marker_cycle"]:
            markers = self._theme["marker_cycle"]
        else:
            markers = ["o", "s", "^", "D", "v", "<", ">", "p", "*", "h"]

        return {
            "color": colors[position % len(colors)],
            "marker": markers[position % len(markers)],
        }

    def get_subplot_styles(
        self,
        row: int,
        col: int,
        dimension: Optional[str],
        subplot_data: pd.DataFrame,
        **plot_kwargs,
    ) -> Dict[str, Any]:
        if dimension is None or dimension not in self._style_assignments:
            return plot_kwargs

        if dimension not in subplot_data.columns:
            return plot_kwargs

        dimension_values = subplot_data[dimension].unique()
        if len(dimension_values) == 1:
            value = dimension_values[0]
            if value in self._style_assignments[dimension]:
                result_kwargs = plot_kwargs.copy()
                result_kwargs.update(self._style_assignments[dimension][value])
                return result_kwargs

        return self._convert_to_plot_params(
            {
                v: self._style_assignments[dimension].get(v, {})
                for v in dimension_values
            },
            dimension_values.tolist(),
            plot_kwargs,
        )

    def _convert_to_plot_params(
        self,
        style_map: Dict[str, Dict[str, Any]],
        values: List[str],
        base_kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        if len(values) == 1:
            value = values[0]
            if value in style_map:
                result_kwargs = base_kwargs.copy()
                result_kwargs.update(style_map[value])
                return result_kwargs
        else:
            result_kwargs = base_kwargs.copy()
            return result_kwargs

        return base_kwargs
