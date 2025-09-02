from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dr_plotter.configs.figure_config import FigureConfig
from dr_plotter.configs.legend_config import LegendConfig
from dr_plotter.legend_manager import resolve_legend_config
from dr_plotter.plot_presets import PLOT_CONFIGS
from dr_plotter.theme import BAR_THEME, BASE_THEME, LINE_THEME, SCATTER_THEME, Theme
from dr_plotter.types import ColorPalette


@dataclass
class LayoutConfig:
    rows: int = 1
    cols: int = 1
    figsize: tuple[float, float] = (12.0, 8.0)
    tight_layout_pad: float = 0.5
    figure_kwargs: dict[str, Any] = field(default_factory=dict)
    subplot_kwargs: dict[str, Any] = field(default_factory=dict)
    x_labels: list[list[str | None]] | None = None
    y_labels: list[list[str | None]] | None = None


@dataclass
class StyleConfig:
    colors: ColorPalette | None = None
    plot_styles: dict[str, Any] | None = field(default_factory=dict)
    fonts: dict[str, Any] | None = field(default_factory=dict)
    figure_styles: dict[str, Any] | None = field(default_factory=dict)
    theme: str | Theme | None = None


@dataclass
class PlotConfig:
    layout: tuple[int, int] | dict[str, Any] | LayoutConfig | None = None
    style: str | dict[str, Any] | StyleConfig | None = None
    legend: str | dict[str, Any] | LegendConfig | None = None

    @classmethod
    def from_preset(cls, preset_name: str) -> PlotConfig:
        assert preset_name in PLOT_CONFIGS, (
            f"Unknown preset: {preset_name}. Available: {list(PLOT_CONFIGS.keys())}"
        )

        preset_config = PLOT_CONFIGS[preset_name]
        return cls(**preset_config)

    def _resolve_layout_config(self) -> LayoutConfig:
        if self.layout is None:
            return LayoutConfig()
        elif isinstance(self.layout, LayoutConfig):
            return self.layout
        elif isinstance(self.layout, tuple):
            assert len(self.layout) in {2, 3}
            kwarg_index = 2
            has_kwargs = len(self.layout) == kwarg_index + 1
            if has_kwargs:
                return LayoutConfig(
                    rows=self.layout[0], cols=self.layout[1], **self.layout[2]
                )
            return LayoutConfig(rows=self.layout[0], cols=self.layout[1])
        elif isinstance(self.layout, dict):
            return LayoutConfig(**self.layout)

        return LayoutConfig()

    def _resolve_style_config(self) -> StyleConfig:
        if self.style is None:
            return StyleConfig()
        elif isinstance(self.style, StyleConfig):
            return self.style
        elif isinstance(self.style, str):
            return StyleConfig(theme=self.style)
        elif isinstance(self.style, dict):
            return StyleConfig(**self.style)

        return StyleConfig()

    def _to_legacy_configs(self) -> tuple[FigureConfig, LegendConfig, Theme | None]:
        layout_config = self._resolve_layout_config()
        style_config = self._resolve_style_config()

        figure_config = self._create_figure_config_from_layout(layout_config)
        legend_config = self._resolve_legend_config()
        theme = self._resolve_theme_from_style(style_config)

        return figure_config, legend_config, theme

    def _create_figure_config_from_layout(
        self, layout_config: LayoutConfig
    ) -> FigureConfig:
        return FigureConfig(
            rows=layout_config.rows,
            cols=layout_config.cols,
            figsize=layout_config.figsize,
            tight_layout_pad=layout_config.tight_layout_pad,
            figure_kwargs=layout_config.figure_kwargs,
            subplot_kwargs=layout_config.subplot_kwargs,
            x_labels=layout_config.x_labels,
            y_labels=layout_config.y_labels,
        )

    def _resolve_legend_config(self) -> LegendConfig:
        if self.legend is None:
            return LegendConfig()

        if isinstance(self.legend, LegendConfig):
            return self.legend

        if isinstance(self.legend, str):
            return resolve_legend_config(self.legend)

        assert isinstance(self.legend, dict), (
            f"Legend must be string, dict, or LegendConfig, got {type(self.legend)}"
        )
        return self._convert_legend_dict_to_config(self.legend)

    def _convert_legend_dict_to_config(
        self, legend_dict: dict[str, Any]
    ) -> LegendConfig:
        legend_kwargs = {}
        for key, value in legend_dict.items():
            if key == "style":
                legend_kwargs["strategy"] = value
            else:
                legend_kwargs[key] = value
        return LegendConfig(**legend_kwargs)

    def _resolve_theme_from_style(self, style_config: StyleConfig) -> Theme | None:
        if style_config.theme is None:
            return None

        if isinstance(style_config.theme, Theme):
            return style_config.theme

        theme_map = {
            "base": BASE_THEME,
            "line": LINE_THEME,
            "scatter": SCATTER_THEME,
            "bar": BAR_THEME,
        }
        assert style_config.theme in theme_map, (
            f"Unknown theme: {style_config.theme}. Available: {list(theme_map.keys())}"
        )
        return theme_map[style_config.theme]
