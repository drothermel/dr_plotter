from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FacetingConfig:
    x: str | None = None
    y: str | None = None

    rows_by: str | None = None
    cols_by: str | None = None
    wrap_by: str | None = None
    max_cols: int | None = None
    max_rows: int | None = None

    hue_by: str | None = None
    alpha_by: str | None = None
    size_by: str | None = None
    marker_by: str | None = None
    style_by: str | None = None

    fixed_dimensions: dict[str, str] | None = None
    ordered_dimensions: dict[str, list[str]] | None = None
    exclude_dimensions: dict[str, list[str]] | None = None

    subplot_width: float | None = None
    subplot_height: float | None = None
    auto_titles: bool = True

    x_labels: list[list[str | None]] | None = None
    y_labels: list[list[str | None]] | None = None
    xlim: list[list[tuple[float, float] | None]] | None = None
    ylim: list[list[tuple[float, float] | None]] | None = None

    subplot_titles: str | list[list[str | None]] | None = None
    title_template: str | None = None

    color_wrap: bool = False

    row_titles: bool | list[str] | None = None
    col_titles: bool | list[str] | None = None
    row_title_rotation: float | None = (
        None  # Rotation angle for row titles (None=use theme default)
    )
    row_title_offset: float | None = (
        None  # Distance from plot area (None=use theme default)
    )

    exterior_x_label: str | None = None
    exterior_y_label: str | None = None

    target_row: int | None = None
    target_col: int | None = None

    target_positions: dict[tuple[int, int], tuple[int, int]] | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        assert self.x is not None, "x parameter is required for faceting"
        assert self.y is not None, "y parameter is required for faceting"
