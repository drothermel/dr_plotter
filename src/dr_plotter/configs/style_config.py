from __future__ import annotations

from dataclasses import field
from typing import Any, dataclass

from dr_plotter.theme import Theme
from dr_plotter.types import ColorPalette


@dataclass
class StyleConfig:
    colors: ColorPalette | None = None
    plot_styles: dict[str, Any] | None = field(default_factory=dict)
    fonts: dict[str, Any] | None = field(default_factory=dict)
    figure_styles: dict[str, Any] | None = field(default_factory=dict)
    theme: str | Theme | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        pass
