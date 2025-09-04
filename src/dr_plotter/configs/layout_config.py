from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any


@dataclass
class LayoutConfig:
    rows: int = 1
    cols: int = 1
    figsize: tuple[float, float] = (12.0, 8.0)
    tight_layout: bool = True
    constrained_layout: bool = False

    tight_layout_pad: float = 0.5
    tight_layout_rect: tuple[float, float, float, float] | None = None
    figure_kwargs: dict[str, Any] = field(default_factory=dict)
    subplot_kwargs: dict[str, Any] = field(default_factory=dict)
    x_labels: list[list[str | None]] | None = None
    y_labels: list[list[str | None]] | None = None
    figure_title: str | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        assert not (self.constrained_layout and self.tight_layout), (
            "Only one of constrained_layout or tight_layout can be True"
        )

        self._validate_no_config_overlap()

    def _validate_no_config_overlap(self) -> None:
        config_field_names = {f.name for f in fields(self)}

        figure_overlaps = set(self.figure_kwargs.keys()) & config_field_names
        subplot_overlaps = set(self.subplot_kwargs.keys()) & config_field_names

        assert not figure_overlaps, (
            f"figure_kwargs contains config field names: {sorted(figure_overlaps)}. "
            f"Use explicit config fields instead of kwargs for proper configuration."
        )

        assert not subplot_overlaps, (
            f"subplot_kwargs contains config field names: {sorted(subplot_overlaps)}. "
            f"Use explicit config fields instead of kwargs for proper configuration."
        )

    @property
    def combined_kwargs(self) -> dict[str, Any]:
        return {**self.figure_kwargs, **self.subplot_kwargs}

    @classmethod
    def from_input(
        cls, value: tuple[int, int] | dict[str, Any] | LayoutConfig | None
    ) -> LayoutConfig:
        if value is None:
            return cls()
        elif isinstance(value, cls):
            return value
        elif isinstance(value, tuple):
            assert len(value) in {2, 3}, (
                f"Tuple must have 2 or 3 elements, got {len(value)}"
            )
            if len(value) == 2:
                return cls(rows=value[0], cols=value[1])
            else:
                return cls(rows=value[0], cols=value[1], **value[2])
        elif isinstance(value, dict):
            return cls(**value)
        else:
            raise TypeError(f"Cannot create LayoutConfig from {type(value).__name__}")
