from __future__ import annotations
from typing import Any, TYPE_CHECKING

import matplotlib.axes
import pandas as pd

from dr_plotter.configs import FacetingConfig

if TYPE_CHECKING:
    from dr_plotter.figure_manager import FigureManager
    from dr_plotter.faceting.style_coordination import FacetStyleCoordinator

SUPPORTED_PLOT_TYPES = ["line", "scatter", "bar", "fill_between", "heatmap"]
GRID_SHAPE_DIMENSIONS = 2


def prepare_faceted_subplots(
    data: pd.DataFrame, config: FacetingConfig, grid_shape: tuple[int, int]
) -> dict[tuple[int, int], pd.DataFrame]:
    assert not data.empty, "Cannot facet empty DataFrame"
    assert config.rows or config.cols, "Must specify rows or cols for faceting"
    assert isinstance(grid_shape, tuple) and len(grid_shape) == GRID_SHAPE_DIMENSIONS, (
        "grid_shape must be (rows, cols) tuple"
    )

    rows, cols = grid_shape

    row_values = _extract_dimension_values(data, config.rows, config.row_order)
    col_values = _extract_dimension_values(data, config.cols, config.col_order)

    subsets = {}

    for r, row_val in enumerate(row_values):
        for c, col_val in enumerate(col_values):
            if _should_include_position(r, c, config):
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


def _should_include_position(row: int, col: int, config: FacetingConfig) -> bool:
    if config.target_row is not None and row != config.target_row:
        return False
    if config.target_col is not None and col != config.target_col:
        return False
    if config.target_rows is not None and row not in config.target_rows:
        return False
    return not (config.target_cols is not None and col not in config.target_cols)


def _create_data_subset(
    data: pd.DataFrame, config: FacetingConfig, row_val: Any, col_val: Any
) -> pd.DataFrame:
    mask = pd.Series([True] * len(data), index=data.index)

    if row_val is not None and config.rows:
        mask = mask & (data[config.rows] == row_val)
    if col_val is not None and config.cols:
        mask = mask & (data[config.cols] == col_val)

    return data[mask].copy()


def plot_faceted_data(
    fm: FigureManager,
    data_subsets: dict[tuple[int, int], pd.DataFrame],
    plot_type: str,
    config: FacetingConfig,
    style_coordinator: FacetStyleCoordinator,
    **kwargs: Any,
) -> None:
    assert data_subsets, "Cannot plot with empty data_subsets"
    assert plot_type in SUPPORTED_PLOT_TYPES, f"Unsupported plot type: {plot_type}"
    assert config.x and config.y, "Must specify x and y columns for plotting"

    for (row, col), subplot_data in data_subsets.items():
        _plot_subplot_at_position(
            fm, row, col, subplot_data, plot_type, config, style_coordinator, **kwargs
        )


def _plot_subplot_at_position(
    fm: FigureManager,
    row: int,
    col: int,
    subplot_data: pd.DataFrame,
    plot_type: str,
    config: FacetingConfig,
    style_coordinator: FacetStyleCoordinator,
    **kwargs: Any,
) -> None:
    if config.lines and config.lines in subplot_data.columns:
        _plot_with_style_coordination(
            fm, row, col, subplot_data, plot_type, config, style_coordinator, **kwargs
        )
    else:
        _plot_single_series_at_position(
            fm, row, col, subplot_data, plot_type, config, **kwargs
        )

    _apply_subplot_customization(fm, row, col, config)


def _plot_with_style_coordination(
    fm: FigureManager,
    row: int,
    col: int,
    subplot_data: pd.DataFrame,
    plot_type: str,
    config: FacetingConfig,
    style_coordinator: FacetStyleCoordinator,
    **kwargs: Any,
) -> None:
    ax = fm.get_axes(row, col)

    lines_values = _extract_dimension_values(
        subplot_data, config.lines, config.lines_order
    )

    for line_value in lines_values:
        if line_value is None:
            continue

        line_data = subplot_data[subplot_data[config.lines] == line_value]
        assert not line_data.empty, f"Line data for {line_value} is empty"

        plot_kwargs = style_coordinator.get_consistent_style(config.lines, line_value)
        plot_kwargs.update(kwargs)

        _execute_plot_call(ax, plot_type, line_data, config, **plot_kwargs)


def _plot_single_series_at_position(
    fm: FigureManager,
    row: int,
    col: int,
    subplot_data: pd.DataFrame,
    plot_type: str,
    config: FacetingConfig,
    **kwargs: Any,
) -> None:
    ax = fm.get_axes(row, col)
    _execute_plot_call(ax, plot_type, subplot_data, config, **kwargs)


def _execute_plot_call(
    ax: matplotlib.axes.Axes,
    plot_type: str,
    data: pd.DataFrame,
    config: FacetingConfig,
    **kwargs: Any,
) -> None:
    plot_handlers = {
        "line": _plot_line_data,
        "scatter": _plot_scatter_data,
        "bar": _plot_bar_data,
        "fill_between": _plot_fill_between_data,
        "heatmap": _plot_heatmap_data,
    }
    plot_handlers[plot_type](ax, data, config, **kwargs)


def _plot_line_data(
    ax: matplotlib.axes.Axes, data: pd.DataFrame, config: FacetingConfig, **kwargs: Any
) -> None:
    ax.plot(data[config.x], data[config.y], **kwargs)


def _plot_scatter_data(
    ax: matplotlib.axes.Axes, data: pd.DataFrame, config: FacetingConfig, **kwargs: Any
) -> None:
    ax.scatter(data[config.x], data[config.y], **kwargs)


def _plot_bar_data(
    ax: matplotlib.axes.Axes, data: pd.DataFrame, config: FacetingConfig, **kwargs: Any
) -> None:
    filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ["marker"]}
    ax.bar(data[config.x], data[config.y], **filtered_kwargs)


def _plot_fill_between_data(
    ax: matplotlib.axes.Axes, data: pd.DataFrame, config: FacetingConfig, **kwargs: Any
) -> None:
    ax.fill_between(data[config.x], data[config.y], **kwargs)


def _plot_heatmap_data(
    ax: matplotlib.axes.Axes, data: pd.DataFrame, config: FacetingConfig, **kwargs: Any
) -> None:
    values = data.pivot_table(index=config.y, columns=config.x, values="value")
    ax.imshow(values, **kwargs)
    ax.set_xticks(range(len(values.columns)))
    ax.set_yticks(range(len(values.index)))
    ax.set_xticklabels(values.columns)
    ax.set_yticklabels(values.index)


def _apply_subplot_customization(
    fm: FigureManager, row: int, col: int, config: FacetingConfig
) -> None:
    _apply_axis_labels(fm, row, col, config)
    _apply_axis_limits(fm, row, col, config)


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


def get_grid_dimensions(data: pd.DataFrame, config: FacetingConfig) -> tuple[int, int]:
    assert not data.empty, "Cannot compute dimensions from empty DataFrame"

    n_rows = len(data[config.rows].unique()) if config.rows else 1
    n_cols = len(data[config.cols].unique()) if config.cols else 1
    return n_rows, n_cols


def handle_empty_subplots(
    data_subsets: dict[tuple[int, int], pd.DataFrame], strategy: str
) -> dict[tuple[int, int], pd.DataFrame]:
    assert strategy in ["error", "warn", "silent"], f"Invalid strategy: {strategy}"

    if strategy == "error":
        empty_positions = [(r, c) for (r, c), df in data_subsets.items() if df.empty]
        assert not empty_positions, (
            f"Empty subplots found at positions {empty_positions}"
        )
    elif strategy == "warn":
        empty_count = sum(1 for df in data_subsets.values() if df.empty)
        if empty_count > 0:
            total = len(data_subsets)
            print(f"Warning: {empty_count}/{total} subplots are empty")

    return data_subsets
