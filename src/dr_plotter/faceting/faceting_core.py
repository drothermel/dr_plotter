from typing import Dict, Tuple, Optional, List, Any
import pandas as pd


def prepare_faceted_subplots(
    data: pd.DataFrame,
    config: 'FacetingConfig',
    grid_shape: Tuple[int, int]
) -> Dict[Tuple[int, int], pd.DataFrame]:
    rows, cols = grid_shape
    
    row_values = sorted(data[config.rows].unique()) if config.rows else [None]
    col_values = sorted(data[config.cols].unique()) if config.cols else [None]
    
    if config.row_order:
        row_values = [v for v in config.row_order if v in row_values]
    if config.col_order:
        col_values = [v for v in config.col_order if v in col_values]
    
    subsets = {}
    
    for r, row_val in enumerate(row_values):
        for c, col_val in enumerate(col_values):
            if _should_include_position(r, c, config):
                subset = _create_data_subset(data, config, row_val, col_val)
                if not subset.empty:
                    subsets[(r, c)] = subset
    
    return subsets


def _should_include_position(row: int, col: int, config: 'FacetingConfig') -> bool:
    if config.target_row is not None and row != config.target_row:
        return False
    if config.target_col is not None and col != config.target_col:
        return False
    if config.target_rows is not None and row not in config.target_rows:
        return False
    if config.target_cols is not None and col not in config.target_cols:
        return False
    return True


def _create_data_subset(
    data: pd.DataFrame,
    config: 'FacetingConfig', 
    row_val: Any,
    col_val: Any
) -> pd.DataFrame:
    mask = pd.Series([True] * len(data), index=data.index)
    
    if row_val is not None and config.rows:
        mask = mask & (data[config.rows] == row_val)
    if col_val is not None and config.cols:
        mask = mask & (data[config.cols] == col_val)
    
    return data[mask].copy()


def plot_faceted_data(
    fm: 'FigureManager',
    data_subsets: Dict[Tuple[int, int], pd.DataFrame],
    plot_type: str,
    config: 'FacetingConfig',
    style_coordinator: 'FacetStyleCoordinator',
    **kwargs
) -> None:
    valid_plot_types = ["line", "scatter", "bar", "fill_between", "heatmap"]
    assert plot_type in valid_plot_types, (
        f"Unsupported plot type: '{plot_type}'. "
        f"Supported types: {valid_plot_types}"
    )
    
    for (row, col), subplot_data in data_subsets.items():
        if config.lines and config.lines in subplot_data.columns:
            _plot_with_lines(
                fm, row, col, subplot_data, plot_type, config, style_coordinator, **kwargs
            )
        else:
            _plot_single_series(
                fm, row, col, subplot_data, plot_type, config, **kwargs
            )
        
        _apply_subplot_customization(fm, row, col, config)


def _plot_with_lines(
    fm: 'FigureManager',
    row: int,
    col: int,
    subplot_data: pd.DataFrame,
    plot_type: str,
    config: 'FacetingConfig',
    style_coordinator: 'FacetStyleCoordinator',
    **kwargs
) -> None:
    ax = fm.get_axes(row, col)
    
    lines_values = sorted(subplot_data[config.lines].unique())
    if config.lines_order:
        lines_values = [v for v in config.lines_order if v in lines_values]
    
    for line_value in lines_values:
        line_data = subplot_data[subplot_data[config.lines] == line_value]
        if line_data.empty:
            continue
            
        plot_kwargs = style_coordinator.get_consistent_style(config.lines, line_value)
        plot_kwargs.update(kwargs)
        
        _execute_plot_call(ax, plot_type, line_data, config, **plot_kwargs)


def _plot_single_series(
    fm: 'FigureManager',
    row: int,
    col: int,
    subplot_data: pd.DataFrame,
    plot_type: str,
    config: 'FacetingConfig',
    **kwargs
) -> None:
    ax = fm.get_axes(row, col)
    _execute_plot_call(ax, plot_type, subplot_data, config, **kwargs)


def _execute_plot_call(
    ax: 'matplotlib.axes.Axes',
    plot_type: str,
    data: pd.DataFrame,
    config: 'FacetingConfig',
    **kwargs
) -> None:
    if plot_type == "line":
        ax.plot(data[config.x], data[config.y], **kwargs)
    elif plot_type == "scatter":
        ax.scatter(data[config.x], data[config.y], **kwargs)
    elif plot_type == "bar":
        ax.bar(data[config.x], data[config.y], **kwargs)
    elif plot_type == "fill_between":
        ax.fill_between(data[config.x], data[config.y], **kwargs)
    elif plot_type == "heatmap":
        values = data.pivot_table(index=config.y, columns=config.x, values='value')
        im = ax.imshow(values, **kwargs)
        ax.set_xticks(range(len(values.columns)))
        ax.set_yticks(range(len(values.index)))
        ax.set_xticklabels(values.columns)
        ax.set_yticklabels(values.index)


def _apply_subplot_customization(
    fm: 'FigureManager',
    row: int,
    col: int, 
    config: 'FacetingConfig'
) -> None:
    ax = fm.get_axes(row, col)
    
    if config.x_labels and row < len(config.x_labels) and col < len(config.x_labels[row]):
        label = config.x_labels[row][col]
        if label is not None:
            ax.set_xlabel(label)
    
    if config.y_labels and row < len(config.y_labels) and col < len(config.y_labels[row]):
        label = config.y_labels[row][col]
        if label is not None:
            ax.set_ylabel(label)
    
    if config.xlim and row < len(config.xlim) and col < len(config.xlim[row]):
        xlim = config.xlim[row][col]
        if xlim is not None:
            ax.set_xlim(xlim)
    
    if config.ylim and row < len(config.ylim) and col < len(config.ylim[row]):
        ylim = config.ylim[row][col]
        if ylim is not None:
            ax.set_ylim(ylim)


def get_grid_dimensions(data: pd.DataFrame, config: 'FacetingConfig') -> Tuple[int, int]:
    n_rows = len(data[config.rows].unique()) if config.rows else 1
    n_cols = len(data[config.cols].unique()) if config.cols else 1
    return n_rows, n_cols


def handle_empty_subplots(
    data_subsets: Dict[Tuple[int, int], pd.DataFrame], 
    strategy: str
) -> Dict[Tuple[int, int], pd.DataFrame]:
    if strategy == "error":
        empty_positions = [(r, c) for (r, c), df in data_subsets.items() if df.empty]
        if empty_positions:
            assert False, f"Empty subplots found at positions {empty_positions}"
    elif strategy == "warn":
        empty_count = sum(1 for df in data_subsets.values() if df.empty)
        if empty_count > 0:
            total = len(data_subsets)
            print(f"Warning: {empty_count}/{total} subplots are empty")
    
    return data_subsets