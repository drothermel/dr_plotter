from typing import Any, List, Optional
import pandas as pd
from dr_plotter.faceting_config import FacetingConfig


def validate_required_columns(data: pd.DataFrame, required_columns: List[str]) -> None:
    missing_columns = [col for col in required_columns if col not in data.columns]
    assert not missing_columns, (
        f"Missing columns {missing_columns}. Available columns: {sorted(data.columns.tolist())}"
    )


def validate_dimension_values(
    data: pd.DataFrame, column: str, expected_values: Optional[List[str]] = None
) -> None:
    assert column in data.columns, (
        f"Column '{column}' not found in data. Available columns: {sorted(data.columns.tolist())}"
    )

    if expected_values is not None:
        actual_values = data[column].unique().tolist()
        missing_values = [v for v in expected_values if v not in actual_values]
        assert not missing_values, (
            f"Expected values {missing_values} not found in data['{column}']. Available values: {sorted(actual_values)}"
        )


def get_available_columns_message(
    data: pd.DataFrame, missing_columns: List[str]
) -> str:
    available = sorted(data.columns.tolist())
    return f"Missing columns {missing_columns}. Available columns: {available}"


def validate_faceting_data_requirements(
    data: pd.DataFrame, config: FacetingConfig
) -> None:
    assert isinstance(data, pd.DataFrame), f"data must be DataFrame, got {type(data)}"

    required_columns = []
    if config.rows is not None:
        required_columns.append(config.rows)
    if config.cols is not None:
        required_columns.append(config.cols)
    if config.lines is not None:
        required_columns.append(config.lines)
    if config.x is not None:
        required_columns.append(config.x)
    if config.y is not None:
        required_columns.append(config.y)

    validate_required_columns(data, required_columns)


def validate_nested_list_dimensions(
    nested_list: List[List[Any]],
    expected_rows: int,
    expected_cols: int,
    param_name: str,
) -> None:
    if nested_list is None:
        return

    assert len(nested_list) == expected_rows, (
        f"{param_name} must have {expected_rows} rows, got {len(nested_list)}"
    )

    for i, row in enumerate(nested_list):
        assert len(row) == expected_cols, (
            f"{param_name}[{i}] must have {expected_cols} columns, got {len(row)}"
        )
