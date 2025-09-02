from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from dr_plotter.configs import PositioningConfig


@dataclass
class FigureDimensions:
    width: float
    height: float
    rows: int
    cols: int
    has_title: bool = False
    has_subplot_titles: bool = False


@dataclass
class LegendMetadata:
    num_legends: int
    num_handles_per_legend: int
    has_titles: bool = False
    strategy: str = "figure_below"


@dataclass
class PositioningResult:
    legend_positions: Dict[int, Tuple[float, float]]
    layout_rect: Optional[Tuple[float, float, float, float]] = None
    tight_layout_pad: float = 0.5
    margin_adjustments: Optional[Dict[str, float]] = None


class PositioningCalculator:
    def __init__(self, config: Optional[PositioningConfig] = None) -> None:
        self.config = config or PositioningConfig()

    def calculate_positions(
        self,
        figure_dimensions: FigureDimensions,
        legend_metadata: LegendMetadata,
        manual_overrides: Optional[Dict[str, Any]] = None,
        layout_hint: Optional[str] = None,
    ) -> PositioningResult:
        return self._resolve_positioning_hierarchy(
            figure_dimensions, legend_metadata, manual_overrides or {}, layout_hint
        )

    def _resolve_positioning_hierarchy(
        self,
        figure_dimensions: FigureDimensions,
        legend_metadata: LegendMetadata,
        manual_overrides: Dict[str, Any],
        layout_hint: Optional[str] = None,
    ) -> PositioningResult:
        if "bbox_to_anchor" in manual_overrides:
            return self._handle_manual_positioning(manual_overrides, figure_dimensions)

        if legend_metadata.strategy in ["grouped_by_channel", "figure_below"]:
            return self._calculate_figure_legend_positions(
                figure_dimensions, legend_metadata, manual_overrides, layout_hint
            )

        return self._calculate_default_positioning(
            figure_dimensions, legend_metadata, layout_hint
        )

    def _handle_manual_positioning(
        self, manual_overrides: Dict[str, Any], figure_dimensions: FigureDimensions
    ) -> PositioningResult:
        bbox = manual_overrides["bbox_to_anchor"]
        return PositioningResult(
            legend_positions={0: bbox},
            layout_rect=self._calculate_layout_rect(figure_dimensions),
            tight_layout_pad=self.config.tight_layout_pad,
        )

    def _calculate_figure_legend_positions(
        self,
        figure_dimensions: FigureDimensions,
        legend_metadata: LegendMetadata,
        manual_overrides: Dict[str, Any],
        layout_hint: Optional[str] = None,
    ) -> PositioningResult:
        num_legends = legend_metadata.num_legends

        positions = {}
        for legend_index in range(num_legends):
            x, y = self._calculate_systematic_position(
                num_legends, legend_index, figure_dimensions.width
            )
            positions[legend_index] = (x, y)

        if layout_hint:
            hint_modifiers = self.process_layout_hint(
                layout_hint, figure_dimensions, legend_metadata
            )
            positions = self._apply_hint_modifiers(positions, hint_modifiers)

        layout_rect = self._calculate_layout_rect_with_legends(figure_dimensions)

        return PositioningResult(
            legend_positions=positions,
            layout_rect=layout_rect,
            tight_layout_pad=self.config.tight_layout_pad,
            margin_adjustments={
                "bottom": self.config.default_margin_bottom,
                "top": self.config.default_margin_top,
            },
        )

    def _calculate_systematic_position(
        self, num_legends: int, legend_index: int, figure_width: float
    ) -> Tuple[float, float]:
        y_position = self.config.legend_y_offset_factor

        if num_legends == 1:
            return (self.config.legend_alignment_center, y_position)

        if num_legends == 2:
            return (self.config.two_legend_positions[legend_index], y_position)

        spacing, start_x = self._calculate_multi_legend_layout(
            num_legends, figure_width
        )
        x_position = start_x + (legend_index * spacing)

        return (x_position, y_position)

    def _calculate_multi_legend_layout(
        self, num_legends: int, figure_width: float
    ) -> Tuple[float, float]:
        if figure_width >= self.config.wide_figure_threshold:
            max_spacing = self.config.wide_spacing_max
            span_factor = self.config.wide_span_factor
        elif figure_width >= self.config.medium_figure_threshold:
            max_spacing = self.config.medium_spacing_max
            span_factor = self.config.medium_span_factor
        else:
            return (
                self.config.legend_spacing_base,
                self.config.multi_legend_start_factor,
            )

        optimal_spacing = min(max_spacing, span_factor / (num_legends - 1))
        start_x = (
            self.config.legend_alignment_center
            - (num_legends - 1) * optimal_spacing / 2
        )

        return (optimal_spacing, start_x)

    def calculate_layout_rect(
        self, figure_dimensions: FigureDimensions
    ) -> Optional[Tuple[float, float, float, float]]:
        return self._calculate_layout_rect(figure_dimensions)

    def _calculate_layout_rect(
        self, figure_dimensions: FigureDimensions
    ) -> Optional[Tuple[float, float, float, float]]:
        if figure_dimensions.has_title or figure_dimensions.has_subplot_titles:
            return (0.0, 0.0, 1.0, self.config.title_space_factor)
        return None

    def _calculate_layout_rect_with_legends(
        self, figure_dimensions: FigureDimensions
    ) -> Tuple[float, float, float, float]:
        return (
            self.config.default_margin_left,
            self.config.default_margin_bottom,
            self.config.default_margin_right,
            self.config.default_margin_top,
        )

    def _calculate_default_positioning(
        self,
        figure_dimensions: FigureDimensions,
        legend_metadata: LegendMetadata,
        layout_hint: Optional[str] = None,
    ) -> PositioningResult:
        positions = {
            0: (
                self.config.legend_alignment_center,
                self.config.legend_y_offset_factor,
            )
        }

        if layout_hint:
            hint_modifiers = self.process_layout_hint(
                layout_hint, figure_dimensions, legend_metadata
            )
            positions = self._apply_hint_modifiers(positions, hint_modifiers)

        return PositioningResult(
            legend_positions=positions,
            layout_rect=self._calculate_layout_rect(figure_dimensions),
            tight_layout_pad=self.config.tight_layout_pad,
        )

    def process_layout_hint(
        self,
        hint: str,
        figure_dimensions: FigureDimensions,
        legend_metadata: LegendMetadata,
    ) -> Dict[str, Any]:
        hint_modifiers = {
            "below": self._calculate_below_hint_modifiers,
            "side": self._calculate_side_hint_modifiers,
            "compact": self._calculate_compact_hint_modifiers,
            "spacious": self._calculate_spacious_hint_modifiers,
        }

        assert hint in hint_modifiers, (
            f"Invalid layout_hint '{hint}'. Valid options: {list(hint_modifiers.keys())}"
        )

        modifier_func = hint_modifiers[hint]
        return modifier_func(figure_dimensions, legend_metadata)

    def _apply_hint_modifiers(
        self, positions: Dict[int, Tuple[float, float]], modifiers: Dict[str, Any]
    ) -> Dict[int, Tuple[float, float]]:
        modified_positions = {}
        for legend_index, (x, y) in positions.items():
            new_x = x + modifiers.get("x_offset", 0)
            new_y = y + modifiers.get("y_offset", 0)

            if "x_position" in modifiers:
                new_x = modifiers["x_position"]
            if "y_position" in modifiers:
                new_y = modifiers["y_position"]

            modified_positions[legend_index] = (new_x, new_y)
        return modified_positions

    def _calculate_below_hint_modifiers(
        self, figure_dimensions: FigureDimensions, legend_metadata: LegendMetadata
    ) -> Dict[str, Any]:
        return {
            "y_position": 0.05,
            "x_position": 0.5,
        }

    def _calculate_side_hint_modifiers(
        self, figure_dimensions: FigureDimensions, legend_metadata: LegendMetadata
    ) -> Dict[str, Any]:
        side_x_position = 1.02
        if figure_dimensions.width < 8:
            side_x_position = 1.05
        elif figure_dimensions.width > 16:
            side_x_position = 1.01

        return {
            "x_position": side_x_position,
            "y_position": 0.5,
        }

    def _calculate_compact_hint_modifiers(
        self, figure_dimensions: FigureDimensions, legend_metadata: LegendMetadata
    ) -> Dict[str, Any]:
        return {
            "y_offset": -0.02,
            "x_offset": 0.0,
        }

    def _calculate_spacious_hint_modifiers(
        self, figure_dimensions: FigureDimensions, legend_metadata: LegendMetadata
    ) -> Dict[str, Any]:
        return {
            "y_offset": 0.03,
            "x_offset": 0.0,
        }
