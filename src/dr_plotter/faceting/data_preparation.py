from typing import Dict, List, Any, Tuple
import pandas as pd
from .types import DataSubsets


def create_data_subset(data: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    if not filters:
        return data.copy()

    mask = pd.Series([True] * len(data), index=data.index)

    for column, value in filters.items():
        if column in data.columns:
            mask = mask & (data[column] == value)

    return data[mask].copy()


def prepare_subplot_data_subsets(
    data: pd.DataFrame,
    row_values: List[str],
    col_values: List[str],
    row_col: str,
    col_col: str,
    grid_type: str,
    fill_order: List[tuple] = None,
    target_positions: List[Tuple[int, int]] = None,
) -> DataSubsets:
    data_copy = data.copy()
    data_subsets = {}

    if grid_type == "explicit":
        for row_idx, row_value in enumerate(row_values):
            for col_idx, col_value in enumerate(col_values):
                if target_positions is None or (row_idx, col_idx) in target_positions:
                    filters = {}

                    if row_col is not None and row_values:
                        filters[row_col] = row_value
                    if col_col is not None and col_values:
                        filters[col_col] = col_value

                    subset_data = create_data_subset(data_copy, filters)
                    data_subsets[(row_idx, col_idx)] = subset_data

    elif grid_type == "wrapped_rows":
        assert row_col is not None and row_values, "wrapped_rows requires row dimension"
        assert fill_order is not None, "wrapped_rows requires fill_order"
        for value_idx, value in enumerate(row_values):
            if value_idx < len(fill_order):
                row_idx, col_idx = fill_order[value_idx]
                if target_positions is None or (row_idx, col_idx) in target_positions:
                    filters = {row_col: value}
                    subset_data = create_data_subset(data_copy, filters)
                    data_subsets[(row_idx, col_idx)] = subset_data

    elif grid_type == "wrapped_cols":
        assert col_col is not None and col_values, "wrapped_cols requires col dimension"
        assert fill_order is not None, "wrapped_cols requires fill_order"
        for value_idx, value in enumerate(col_values):
            if value_idx < len(fill_order):
                row_idx, col_idx = fill_order[value_idx]
                if target_positions is None or (row_idx, col_idx) in target_positions:
                    filters = {col_col: value}
                    subset_data = create_data_subset(data_copy, filters)
                    data_subsets[(row_idx, col_idx)] = subset_data

    else:
        assert False, f"Layout type '{grid_type}' not supported"

    return data_subsets
