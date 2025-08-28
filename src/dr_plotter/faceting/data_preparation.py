from typing import Dict, List, Any
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
) -> DataSubsets:
    data_copy = data.copy()
    data_subsets = {}

    if grid_type == "explicit":
        for row_idx, row_value in enumerate(row_values):
            for col_idx, col_value in enumerate(col_values):
                filters = {}

                if row_col is not None and row_values:
                    filters[row_col] = row_value
                if col_col is not None and col_values:
                    filters[col_col] = col_value

                subset_data = create_data_subset(data_copy, filters)
                data_subsets[(row_idx, col_idx)] = subset_data
    else:
        assert False, f"Layout type '{grid_type}' not supported in this chunk"

    return data_subsets
