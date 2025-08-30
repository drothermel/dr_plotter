from typing import Dict, Any, Optional, List
import matplotlib.pyplot as plt


class FacetStyleCoordinator:
    def __init__(self, theme: Optional[Dict[str, Any]] = None) -> None:
        self._style_assignments: Dict[str, Dict[Any, Dict[str, Any]]] = {}
        self._color_cycle = self._get_color_cycle(theme)
        self._marker_cycle = self._get_marker_cycle(theme)
        self._next_color_index = 0
        
    def _get_color_cycle(self, theme: Optional[Dict[str, Any]]) -> List[str]:
        if theme and "color_cycle" in theme:
            return theme["color_cycle"]
        return [
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
            "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
        ]
    
    def _get_marker_cycle(self, theme: Optional[Dict[str, Any]]) -> List[str]:
        if theme and "marker_cycle" in theme:
            return theme["marker_cycle"]
        return ["o", "s", "^", "D", "v", "<", ">", "p", "*", "h"]
    
    def register_dimension_values(self, dimension: str, values: List[Any]) -> None:
        if dimension not in self._style_assignments:
            self._style_assignments[dimension] = {}
        
        for value in values:
            if value not in self._style_assignments[dimension]:
                self._assign_style_to_value(dimension, value)
    
    def _assign_style_to_value(self, dimension: str, value: Any) -> None:
        color_idx = self._next_color_index % len(self._color_cycle)
        marker_idx = self._next_color_index % len(self._marker_cycle)
        
        self._style_assignments[dimension][value] = {
            "color": self._color_cycle[color_idx],
            "marker": self._marker_cycle[marker_idx]
        }
        self._next_color_index += 1
    
    def get_consistent_style(self, dimension: str, value: Any) -> Dict[str, Any]:
        if dimension not in self._style_assignments:
            self._style_assignments[dimension] = {}
        
        if value not in self._style_assignments[dimension]:
            self._assign_style_to_value(dimension, value)
        
        return self._style_assignments[dimension][value].copy()
    
    def get_subplot_styles(
        self,
        row: int,
        col: int,
        dimension: Optional[str],
        subplot_data: 'pandas.DataFrame',
        **plot_kwargs
    ) -> Dict[str, Any]:
        if dimension is None or dimension not in subplot_data.columns:
            return plot_kwargs
        
        dimension_values = subplot_data[dimension].unique()
        
        if len(dimension_values) == 1:
            value = dimension_values[0]
            style = self.get_consistent_style(dimension, value)
            result_kwargs = plot_kwargs.copy()
            result_kwargs.update(style)
            return result_kwargs
        
        return plot_kwargs