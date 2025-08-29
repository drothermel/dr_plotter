from typing import Any, Dict, List, Optional, Set
import pandas as pd


class FacetStyleCoordinator:
    def __init__(self) -> None:
        self._dimension_values: Dict[str, Set[str]] = {}
        self._style_assignments: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._cycle_positions: Dict[str, int] = {}

    def register_dimension_values(self, dimension: str, values: List[str]) -> None:
        if dimension not in self._dimension_values:
            self._dimension_values[dimension] = set()
        self._dimension_values[dimension].update(values)

        ordered_values = sorted(self._dimension_values[dimension], key=str)
        if dimension not in self._style_assignments:
            self._style_assignments[dimension] = {}
            self._cycle_positions[dimension] = 0

        self._assign_styles_to_new_values(dimension, ordered_values)

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

        return {
            "color": colors[position % len(colors)],
            "marker": ["o", "s", "^", "D", "v", "<", ">", "p", "*", "h"][position % 10],
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

        dimension_values = subplot_data[dimension].unique().tolist()

        subplot_style_map = {}
        for value in dimension_values:
            if value in self._style_assignments[dimension]:
                subplot_style_map[value] = self._style_assignments[dimension][value]

        plot_styles = self._convert_to_plot_params(
            subplot_style_map, dimension_values, plot_kwargs
        )
        return plot_styles

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
