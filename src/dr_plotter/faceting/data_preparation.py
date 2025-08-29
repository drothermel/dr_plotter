from typing import Dict, List, Any, Tuple, Set
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
    if row_col is None and col_col is None:
        if target_positions and len(target_positions) == 1:
            return {target_positions[0]: data}
        return {(0, 0): data}

    if row_col and col_col:
        relevant_row_values = set(row_values)
        relevant_col_values = set(col_values)

        mask = data[row_col].isin(relevant_row_values) & data[col_col].isin(
            relevant_col_values
        )
        filtered_data = data[mask]

        if len(filtered_data) == 0:
            return {}
    else:
        filtered_data = data

    if target_positions:
        position_set = set(target_positions)
    else:
        position_set = {
            (r, c) for r in range(len(row_values)) for c in range(len(col_values))
        }

    data_subsets = {}

    if grid_type == "explicit":
        if row_col and col_col and len(position_set) > 4:
            grouped = filtered_data.groupby([row_col, col_col])

            for row_idx, col_idx in position_set:
                if row_idx < len(row_values) and col_idx < len(col_values):
                    row_val = row_values[row_idx]
                    col_val = col_values[col_idx]

                    if (row_val, col_val) in grouped.groups:
                        subset = grouped.get_group((row_val, col_val))
                        data_subsets[(row_idx, col_idx)] = subset
        else:
            data_subsets = _prepare_subsets_individual_filtering(
                filtered_data, row_values, col_values, row_col, col_col, position_set
            )

    elif grid_type == "wrapped_rows":
        assert row_col is not None and row_values, "wrapped_rows requires row dimension"
        assert fill_order is not None, "wrapped_rows requires fill_order"
        for value_idx, value in enumerate(row_values):
            if value_idx < len(fill_order):
                row_idx, col_idx = fill_order[value_idx]
                if target_positions is None or (row_idx, col_idx) in target_positions:
                    filters = {row_col: value}
                    subset_data = create_data_subset(data, filters)
                    data_subsets[(row_idx, col_idx)] = subset_data

    elif grid_type == "wrapped_cols":
        assert col_col is not None and col_values, "wrapped_cols requires col dimension"
        assert fill_order is not None, "wrapped_cols requires fill_order"
        for value_idx, value in enumerate(col_values):
            if value_idx < len(fill_order):
                row_idx, col_idx = fill_order[value_idx]
                if target_positions is None or (row_idx, col_idx) in target_positions:
                    filters = {col_col: value}
                    subset_data = create_data_subset(data, filters)
                    data_subsets[(row_idx, col_idx)] = subset_data

    else:
        assert False, f"Layout type '{grid_type}' not supported"

    return data_subsets


def _prepare_subsets_individual_filtering(
    data: pd.DataFrame,
    row_values: List[str],
    col_values: List[str],
    row_col: str,
    col_col: str,
    position_set: Set[Tuple[int, int]],
) -> Dict[Tuple[int, int], pd.DataFrame]:
    data_subsets = {}

    for row_idx, col_idx in position_set:
        filters = {}
        if row_col and row_idx < len(row_values):
            filters[row_col] = row_values[row_idx]
        if col_col and col_idx < len(col_values):
            filters[col_col] = col_values[col_idx]

        subset = create_data_subset(data, filters)
        if not subset.empty:
            data_subsets[(row_idx, col_idx)] = subset

    return data_subsets


def handle_empty_subplots(
    data_subsets: DataSubsets, empty_subplot_strategy: str
) -> DataSubsets:
    empty_positions = []
    for pos, subset in data_subsets.items():
        if subset.empty:
            empty_positions.append(pos)

    if empty_positions:
        if empty_subplot_strategy == "error":
            assert False, (
                f"Empty subplots found at positions {empty_positions}. "
                f"Set empty_subplot_strategy='warn' or 'silent' to allow empty subplots, "
                f"or filter your data to ensure all subplot combinations have data."
            )
        elif empty_subplot_strategy == "warn":
            print(
                f"Warning: {len(empty_positions)}/{len(empty_positions) + len(data_subsets)} subplot combinations have no data ({100 * len(empty_positions) / (len(empty_positions) + len(data_subsets)):.1f}%). "
                f"Consider filtering data or using different dimensions."
            )
        elif empty_subplot_strategy == "silent":
            pass
        else:
            assert False, (
                f"Invalid empty_subplot_strategy: '{empty_subplot_strategy}'. Use 'warn', 'error', or 'silent'."
            )

    return data_subsets
