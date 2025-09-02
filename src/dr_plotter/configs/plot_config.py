from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dr_plotter.configs.layout_config import LayoutConfig
from dr_plotter.configs.legend_config import LegendConfig
from dr_plotter.configs.style_config import StyleConfig
from dr_plotter.legend_manager import resolve_legend_config
from dr_plotter.plot_presets import PLOT_CONFIGS


@dataclass
class PlotConfig:
    layout: tuple[int, int] | dict[str, Any] | LayoutConfig | None = None
    style: str | dict[str, Any] | StyleConfig | None = None
    legend: str | dict[str, Any] | LegendConfig | None = None

    def __post_init__(self) -> None:
        self.validate()
        self.layout = self._resolve_layout_config()
        self.style = self._resolve_style_config()
        self.legend = self._resolve_legend_config()

    def validate(self) -> None:
        pass

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
