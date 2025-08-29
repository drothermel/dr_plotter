from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class FacetingConfig:
    rows: Optional[str] = None
    cols: Optional[str] = None
    lines: Optional[str] = None

    ncols: Optional[int] = None
    nrows: Optional[int] = None

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

    shared_x: Optional[str | bool] = None
    shared_y: Optional[str | bool] = None

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

        has_explicit_grid = self.rows and self.cols
        has_wrap_layout = self.ncols or self.nrows
        if has_explicit_grid and has_wrap_layout:
            assert False, (
                f"Cannot specify both explicit grid and wrap layout.\n"
                f"Current config: rows='{self.rows}', cols='{self.cols}', ncols={self.ncols}, nrows={self.nrows}\n"
                f"Choose one approach:\n"
                f"  - Explicit grid: rows='{self.rows}', cols='{self.cols}'\n"
                f"  - Wrapped layout: rows='{self.rows}', ncols={self.ncols or self.nrows}\n"
            )

        if self.ncols is not None:
            assert self.rows is not None and self.cols is None, (
                f"ncols requires rows dimension and no cols dimension. Got rows='{self.rows}', cols='{self.cols}', ncols={self.ncols}"
            )
        if self.nrows is not None:
            assert self.cols is not None and self.rows is None, (
                f"nrows requires cols dimension and no rows dimension. Got rows='{self.rows}', cols='{self.cols}', nrows={self.nrows}"
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

        if self.ncols is not None:
            assert isinstance(self.ncols, int) and self.ncols > 0, (
                f"ncols must be a positive integer. Got ncols={self.ncols} (type: {type(self.ncols)})"
            )
        if self.nrows is not None:
            assert isinstance(self.nrows, int) and self.nrows > 0, (
                f"nrows must be a positive integer. Got nrows={self.nrows} (type: {type(self.nrows)})"
            )

        if self.shared_x is not None:
            if isinstance(self.shared_x, str):
                assert self.shared_x in {"all", "row", "col"}, (
                    f"shared_x string must be one of 'all', 'row', 'col'. Got '{self.shared_x}'"
                )
            elif not isinstance(self.shared_x, bool):
                assert False, (
                    f"shared_x must be bool or string ('all', 'row', 'col'). Got {self.shared_x} (type: {type(self.shared_x)})"
                )

        if self.shared_y is not None:
            if isinstance(self.shared_y, str):
                assert self.shared_y in {"all", "row", "col"}, (
                    f"shared_y string must be one of 'all', 'row', 'col'. Got '{self.shared_y}'"
                )
            elif not isinstance(self.shared_y, bool):
                assert False, (
                    f"shared_y must be bool or string ('all', 'row', 'col'). Got {self.shared_y} (type: {type(self.shared_y)})"
                )

        assert self.empty_subplot_strategy in {"warn", "error", "silent"}, (
            f"empty_subplot_strategy must be one of 'warn', 'error', 'silent'. Got '{self.empty_subplot_strategy}'"
        )
