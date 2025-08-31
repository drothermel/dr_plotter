from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class FacetingConfig:
    rows: Optional[str] = None
    cols: Optional[str] = None
    lines: Optional[str] = None

    row_order: Optional[List[str]] = None
    col_order: Optional[List[str]] = None
    lines_order: Optional[List[str]] = None

    target_row: Optional[int] = None
    target_col: Optional[int] = None
    target_rows: Optional[List[int]] = None
    target_cols: Optional[List[int]] = None

    x: Optional[str] = None
    y: Optional[str] = None

    x_labels: Optional[List[List[Optional[str]]]] = None
    y_labels: Optional[List[List[Optional[str]]]] = None
    xlim: Optional[List[List[Optional[Tuple[float, float]]]]] = None
    ylim: Optional[List[List[Optional[Tuple[float, float]]]]] = None

    subplot_titles: Optional[str | List[List[Optional[str]]]] = None
    title_template: Optional[str] = None

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
                f"Current: target_row={self.target_row}, target_rows={self.target_rows}\n"
                f"Use target_row for single row or target_rows for multiple rows."
            )
        if self.target_col is not None and self.target_cols is not None:
            assert False, (
                f"Cannot specify both target_col and target_cols.\n"
                f"Current: target_col={self.target_col}, target_cols={self.target_cols}\n"
                f"Use target_col for single column or target_cols for multiple columns."
            )

        assert self.empty_subplot_strategy in {"warn", "error", "silent"}, (
            f"empty_subplot_strategy must be one of 'warn', 'error', 'silent'. Got '{self.empty_subplot_strategy}'"
        )
