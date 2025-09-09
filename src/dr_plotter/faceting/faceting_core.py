from __future__ import annotations

from typing import TYPE_CHECKING, Any

import matplotlib.axes
import pandas as pd

from dr_plotter.configs import FacetingConfig
from dr_plotter.faceting.dimensional_utils import resolve_dimension_values
from dr_plotter.styling_utils import apply_grid_styling

if TYPE_CHECKING:
    from dr_plotter.figure_manager import FigureManager

GRID_SHAPE_DIMENSIONS = 2


def prepare_faceted_subplots(
    data: pd.DataFrame, config: FacetingConfig, grid_shape: tuple[int, int]
) -> dict[tuple[int, int], pd.DataFrame]:
    assert not data.empty, "Cannot facet empty DataFrame"
    assert config.rows or config.cols or config.rows_and_cols, (
        "Must specify rows, cols, or rows_and_cols for faceting"
    )
    assert isinstance(grid_shape, tuple) and len(grid_shape) == GRID_SHAPE_DIMENSIONS, (
        "grid_shape must be (rows, cols) tuple"
    )

    rows, cols = grid_shape
    if config.target_row is not None and config.target_col is not None:
        assert config.target_row < rows and config.target_col < cols, (
            f"Target position ({config.target_row}, {config.target_col}) "
            f"exceeds grid dimensions {grid_shape}"
        )
        subsets = {(config.target_row, config.target_col): data.copy()}
        return subsets

    if config.rows_and_cols:
        # Handle wrapping layout: single dimension mapped to grid positions
        values = resolve_dimension_values(data, config.rows_and_cols, config)
        rows, cols = grid_shape
        subsets = {}
        for i, val in enumerate(values):
            r = i // cols  # Row position in grid
            c = i % cols  # Column position in grid
            if r < rows:  # Only create subsets within grid bounds
                subset = data[data[config.rows_and_cols] == val].copy()
                if not subset.empty:
                    subsets[(r, c)] = subset
    else:
        # Handle standard row/col layout
        row_values = (
            [None]
            if config.rows is None
            else resolve_dimension_values(data, config.rows, config)
        )
        col_values = (
            [None]
            if config.cols is None
            else resolve_dimension_values(data, config.cols, config)
        )

        subsets = {}
        for r, row_val in enumerate(row_values):
            for c, col_val in enumerate(col_values):
                subset = _create_data_subset(data, config, row_val, col_val)
                if not subset.empty:
                    subsets[(r, c)] = subset
    return subsets


def _extract_dimension_values(
    data: pd.DataFrame, column: str | None, order: list[str] | None
) -> list[Any]:
    if not column:
        return [None]
    values = sorted(data[column].unique())
    if order:
        values = [v for v in order if v in values]
    return values


def _create_data_subset(
    data: pd.DataFrame, config: FacetingConfig, row_val: Any, col_val: Any
) -> pd.DataFrame:
    mask = pd.Series([True] * len(data), index=data.index)
    if row_val is not None and config.rows:
        mask = mask & (data[config.rows] == row_val)
    if col_val is not None and config.cols:
        mask = mask & (data[config.cols] == col_val)
    return data[mask].copy()


def _apply_subplot_customization(
    fm: FigureManager, row: int, col: int, config: FacetingConfig, data: pd.DataFrame
) -> None:
    _apply_axis_labels(fm, row, col, config)
    _apply_exterior_labels(fm, row, col, config, data)
    _apply_axis_limits(fm, row, col, config)
    _apply_dimension_titles(fm, row, col, config, data)
    _apply_grid_styling(fm, row, col)


def _apply_axis_labels(
    fm: FigureManager, row: int, col: int, config: FacetingConfig
) -> None:
    ax = fm.get_axes(row, col)

    if _has_custom_label(config.x_labels, row, col):
        label = config.x_labels[row][col]
        if label is not None:
            ax.set_xlabel(label)

    if _has_custom_label(config.y_labels, row, col):
        label = config.y_labels[row][col]
        if label is not None:
            ax.set_ylabel(label)


def _apply_axis_limits(
    fm: FigureManager, row: int, col: int, config: FacetingConfig
) -> None:
    ax = fm.get_axes(row, col)

    if _has_custom_label(config.xlim, row, col):
        xlim = config.xlim[row][col]
        if xlim is not None:
            ax.set_xlim(xlim)

    if _has_custom_label(config.ylim, row, col):
        ylim = config.ylim[row][col]
        if ylim is not None:
            ax.set_ylim(ylim)


def _has_custom_label(labels: list[list[Any]] | None, row: int, col: int) -> bool:
    return labels is not None and row < len(labels) and col < len(labels[row])


def _apply_exterior_labels(
    fm: FigureManager, row: int, col: int, config: FacetingConfig, data: pd.DataFrame
) -> None:
    if not (config.exterior_x_label or config.exterior_y_label):
        return

    ax = fm.get_axes(row, col)

    # Get grid dimensions - handle rows_and_cols mode
    if config.rows_and_cols:
        # For wrapped layouts, get actual grid dimensions from FigureManager
        n_rows, n_cols = fm.layout_config.rows, fm.layout_config.cols
        dimension_name = config.rows_and_cols
    else:
        # Standard row/col layout
        row_values = (
            resolve_dimension_values(data, config.rows, config) if config.rows else [None]
        )
        col_values = (
            resolve_dimension_values(data, config.cols, config) if config.cols else [None]
        )
        n_rows = len(row_values) if config.rows else 1
        n_cols = len(col_values) if config.cols else 1  # noqa: F841
        dimension_name = config.rows or config.cols

    # Apply exterior x label (bottom row only)
    if config.exterior_x_label and row == n_rows - 1:
        ax.set_xlabel(config.exterior_x_label)

    # Apply exterior y label (leftmost column only)
    if col == 0:
        if config.exterior_y_label:
            # Use explicitly provided label
            ax.set_ylabel(config.exterior_y_label)
        elif config.rows_and_cols and dimension_name:
            # Auto-label with dimension name for rows_and_cols mode
            ax.set_ylabel(dimension_name.capitalize())


def _apply_dimension_titles(
    fm: FigureManager, row: int, col: int, config: FacetingConfig, data: pd.DataFrame
) -> None:
    ax = fm.get_axes(row, col)

    # Handle wrapping layout (rows_and_cols) - add title to every subplot
    if config.rows_and_cols and config.auto_titles:
        values = resolve_dimension_values(data, config.rows_and_cols, config)
        _, grid_cols = fm.layout_config.rows, fm.layout_config.cols

        # Calculate which value this subplot represents
        subplot_index = row * grid_cols + col
        if subplot_index < len(values):
            value = values[subplot_index]
            title = f"{config.rows_and_cols}={value}"
            ax.set_title(title, pad=10)
        return

    # Handle standard row/col layout
    if not (config.row_titles or config.col_titles):
        return

    # Get dimension values using same logic as faceting system
    row_values = (
        resolve_dimension_values(data, config.rows, config) if config.rows else [None]
    )
    col_values = (
        resolve_dimension_values(data, config.cols, config) if config.cols else [None]
    )

    # Row titles (left side, first column only)
    if config.row_titles and col == 0 and row < len(row_values):
        title = _resolve_dimension_title(config.row_titles, row, row_values)
        if title:
            rotation = config.row_title_rotation
            if rotation is None:
                rotation = fm.styler.get_style("row_title_rotation", 90)
            
            offset = config.row_title_offset  
            if offset is None:
                offset = fm.styler.get_style("row_title_offset", -0.15)
                
            fontsize = fm.styler.get_style("title_fontsize", 14)
            _add_row_title(ax, title, offset=offset, rotation=rotation, fontsize=fontsize)

    # Column titles (top, first row only)
    if config.col_titles and row == 0 and col < len(col_values):
        title = _resolve_dimension_title(config.col_titles, col, col_values)
        if title:
            ax.set_title(title, pad=10)


def _resolve_dimension_title(
    title_config: bool | list[str], index: int, dimension_values: list[Any]
) -> str | None:
    if title_config is True:
        return str(dimension_values[index]) if index < len(dimension_values) else None
    elif isinstance(title_config, list):
        return title_config[index] if index < len(title_config) else None
    return None


def _add_row_title(ax: matplotlib.axes.Axes, title: str, offset: float = -0.15, rotation: float = 0, fontsize: float = 14) -> None:
    ax_left = ax.twinx()
    ax_left.yaxis.set_label_position("left")
    ax_left.spines["left"].set_position(("axes", offset))
    ax_left.spines["left"].set_visible(False)
    ax_left.set_yticks([])
    # Adjust vertical alignment based on rotation
    if rotation == 90:
        va = "bottom"  # For vertical text, align to bottom
    elif rotation == 0:
        va = "center"  # For horizontal text, keep centered
    else:
        va = "center"  # Default for other angles
        
    ax_left.set_ylabel(
        title,
        rotation=rotation,
        size=fontsize,
        ha="right",
        va=va,
    )


def _apply_grid_styling(fm: FigureManager, row: int, col: int) -> None:
    ax = fm.get_axes(row, col)
    apply_grid_styling(ax, fm.styler)
