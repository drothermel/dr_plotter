from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FacetingConfig:
    rows: str | None = None
    cols: str | None = None
    lines: str | None = None

    row_order: list[str] | None = None
    col_order: list[str] | None = None
    lines_order: list[str] | None = None

    target_row: int | None = None
    target_col: int | None = None
    target_rows: list[int] | None = None
    target_cols: list[int] | None = None

    x: str | None = None
    y: str | None = None

    x_labels: list[list[str | None]] | None = None
    y_labels: list[list[str | None]] | None = None
    xlim: list[list[tuple[float, float] | None]] | None = None
    ylim: list[list[tuple[float, float] | None]] | None = None

    subplot_titles: str | list[list[str | None]] | None = None
    title_template: str | None = None

    empty_subplot_strategy: str = "warn"

    color_wrap: bool = False

    def validate(self) -> None:
        if not (self.rows or self.cols):
            assert False, (
                "Must specify at least one faceting dimension.\n"
                "Examples:\n"
                "  - rows='metric' (facet by metric across rows)\n"
                "  - cols='dataset' (facet by dataset across columns)\n"
                "  - rows='metric', cols='dataset' (2D grid)"
            )

        if self.target_row is not None and self.target_rows is not None:
            assert False, (
                f"Cannot specify both target_row and target_rows.\n"
                f"Current: "
                f"target_row={self.target_row}, target_rows={self.target_rows}\n"
                f"Use target_row for single row or target_rows for multiple rows."
            )
        if self.target_col is not None and self.target_cols is not None:
            assert False, (
                f"Cannot specify both target_col and target_cols.\n"
                f"Current: "
                f"target_col={self.target_col}, target_cols={self.target_cols}\n"
                f"Use target_col for single column or target_cols for multiple columns."
            )

        assert self.empty_subplot_strategy in {"warn", "error", "silent"}, (
            f"empty_subplot_strategy must be one of 'warn', "
            f"'error', 'silent'. Got '{self.empty_subplot_strategy}'"
        )
