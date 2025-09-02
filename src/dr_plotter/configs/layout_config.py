from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        pass
