from typing import Dict, List, Tuple, Any
import math
import pandas as pd
from dr_plotter.faceting_config import FacetingConfig


def compute_grid_dimensions(
    data: pd.DataFrame, config: FacetingConfig, dimensions: Dict[str, List[str]]
) -> Tuple[int, int]:
    row_values = dimensions["rows"]
    col_values = dimensions["cols"]

    if config.rows and config.cols:
        return len(row_values), len(col_values)
    elif config.rows and config.ncols:
        n_cols = config.ncols
        n_rows = math.ceil(len(row_values) / n_cols)
        return n_rows, n_cols
    elif config.cols and config.nrows:
        n_rows = config.nrows
        n_cols = math.ceil(len(col_values) / n_rows)
        return n_rows, n_cols
    else:
        assert False, (
            f"Invalid grid configuration. Must specify either (rows + cols), (rows + ncols), or (cols + nrows). Got rows='{config.rows}', cols='{config.cols}', ncols={config.ncols}, nrows={config.nrows}"
        )


def compute_grid_layout_metadata(
    data: pd.DataFrame, config: FacetingConfig, dimensions: Dict[str, List[str]]
) -> Dict[str, Any]:
    row_values = dimensions["rows"]
    col_values = dimensions["cols"]

    if config.rows and config.cols:
        grid_type = "explicit"
        n_rows = len(row_values)
        n_cols = len(col_values)
        fill_order = [(r, c) for r in range(n_rows) for c in range(n_cols)]
    elif config.rows and config.ncols:
        grid_type = "wrapped_rows"
        n_cols = config.ncols
        fill_order = []
        for i, _ in enumerate(row_values):
            row_idx = i // n_cols
            col_idx = i % n_cols
            fill_order.append((row_idx, col_idx))
    elif config.cols and config.nrows:
        grid_type = "wrapped_cols"
        n_rows = config.nrows
        fill_order = []
        for i, _ in enumerate(col_values):
            col_idx = i // n_rows
            row_idx = i % n_rows
            fill_order.append((row_idx, col_idx))
    else:
        assert False, (
            f"Invalid grid configuration. Must specify either (rows + cols), (rows + ncols), or (cols + nrows). Got rows='{config.rows}', cols='{config.cols}', ncols={config.ncols}, nrows={config.nrows}"
        )

    return {
        "row_values": row_values,
        "col_values": col_values,
        "grid_type": grid_type,
        "fill_order": fill_order,
        "dimensions": dimensions,
    }


def resolve_target_positions(
    config: FacetingConfig, grid_rows: int, grid_cols: int
) -> List[Tuple[int, int]]:
    target_row = config.target_row
    target_col = config.target_col
    target_rows = config.target_rows
    target_cols = config.target_cols

    if target_row is not None:
        assert 0 <= target_row < grid_rows, (
            f"target_row={target_row} invalid for {grid_rows}×{grid_cols} grid. Valid range: 0-{grid_rows - 1}"
        )
    if target_col is not None:
        assert 0 <= target_col < grid_cols, (
            f"target_col={target_col} invalid for {grid_rows}×{grid_cols} grid. Valid range: 0-{grid_cols - 1}"
        )
    if target_rows is not None:
        for tr in target_rows:
            assert 0 <= tr < grid_rows, (
                f"target_rows contains {tr} which is invalid for {grid_rows}×{grid_cols} grid. Valid range: 0-{grid_rows - 1}"
            )
    if target_cols is not None:
        for tc in target_cols:
            assert 0 <= tc < grid_cols, (
                f"target_cols contains {tc} which is invalid for {grid_rows}×{grid_cols} grid. Valid range: 0-{grid_cols - 1}"
            )

    if all(x is None for x in [target_row, target_col, target_rows, target_cols]):
        return [(r, c) for r in range(grid_rows) for c in range(grid_cols)]

    effective_rows = (
        target_rows
        if target_rows is not None
        else ([target_row] if target_row is not None else None)
    )
    effective_cols = (
        target_cols
        if target_cols is not None
        else ([target_col] if target_col is not None else None)
    )

    if effective_rows is not None and effective_cols is not None:
        return [(r, c) for r in effective_rows for c in effective_cols]
    elif effective_rows is not None:
        return [(r, c) for r in effective_rows for c in range(grid_cols)]
    elif effective_cols is not None:
        return [(r, c) for r in range(grid_rows) for c in effective_cols]

    return [(r, c) for r in range(grid_rows) for c in range(grid_cols)]
