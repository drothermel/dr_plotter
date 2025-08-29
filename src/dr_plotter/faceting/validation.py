from typing import Any, Dict, List, Optional
import pandas as pd
import difflib
from dr_plotter.faceting_config import FacetingConfig


def validate_required_columns(data: pd.DataFrame, required_columns: List[str]) -> None:
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        available = sorted(data.columns.tolist())
        similar_suggestions = _suggest_similar_columns(missing_columns, available)

        error_msg = f"Missing required columns: {missing_columns}\n"
        error_msg += f"Available columns: {available}\n"
        if similar_suggestions:
            error_msg += f"Did you mean: {similar_suggestions}?"

        assert False, error_msg


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

    if data.empty:
        assert False, (
            "Cannot create faceted plot with empty DataFrame. "
            "Please provide data with at least one row."
        )

    if len(data) < 2:
        print(
            f"Warning: DataFrame has only {len(data)} row(s). "
            f"Faceted plots work best with multiple data points per subplot."
        )

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

    _validate_data_completeness(data, config)


def _suggest_similar_columns(
    missing: List[str], available: List[str]
) -> Dict[str, List[str]]:
    suggestions = {}

    for missing_col in missing:
        matches = difflib.get_close_matches(missing_col, available, n=3, cutoff=0.6)
        if matches:
            suggestions[missing_col] = matches

    return suggestions


def _validate_data_completeness(data: pd.DataFrame, config: FacetingConfig) -> None:
    required_dims = []
    if config.rows:
        required_dims.append(config.rows)
    if config.cols:
        required_dims.append(config.cols)
    if config.lines:
        required_dims.append(config.lines)

    for dim in required_dims:
        if dim in data.columns:
            unique_count = data[dim].nunique()
            total_null = data[dim].isnull().sum()

            if unique_count == 0:
                assert False, (
                    f"Dimension '{dim}' has no non-null values. "
                    f"Cannot create faceted plot without valid dimension values."
                )

            if unique_count == 1:
                single_value = (
                    data[dim].dropna().iloc[0]
                    if len(data[dim].dropna()) > 0
                    else "null"
                )
                print(
                    f"Warning: Dimension '{dim}' has only one unique value: '{single_value}'. "
                    f"This will create a single-row/column grid. Consider using a different dimension."
                )

            if total_null > len(data) * 0.5:
                print(
                    f"Warning: Dimension '{dim}' has {total_null}/{len(data)} null values ({total_null / len(data) * 100:.1f}%). "
                    f"Many subplots may be empty."
                )


def validate_subplot_data_coverage(
    data: pd.DataFrame, config: FacetingConfig
) -> Dict[str, Any]:
    coverage_info = {
        "total_combinations": 1,
        "populated_combinations": 0,
        "empty_combinations": [],
        "sparse_combinations": [],
    }

    if config.rows and config.rows in data.columns:
        row_values = data[config.rows].dropna().unique()
        coverage_info["total_combinations"] *= len(row_values)
        coverage_info["row_values"] = row_values.tolist()

    if config.cols and config.cols in data.columns:
        col_values = data[config.cols].dropna().unique()
        coverage_info["total_combinations"] *= len(col_values)
        coverage_info["col_values"] = col_values.tolist()

    if config.rows and config.cols:
        if config.rows in data.columns and config.cols in data.columns:
            grouped = data.groupby([config.rows, config.cols]).size()
            coverage_info["populated_combinations"] = len(grouped)

            for row_val in coverage_info.get("row_values", []):
                for col_val in coverage_info.get("col_values", []):
                    if (row_val, col_val) not in grouped.index:
                        coverage_info["empty_combinations"].append((row_val, col_val))
                    elif grouped.loc[(row_val, col_val)] < 3:
                        coverage_info["sparse_combinations"].append(
                            (row_val, col_val, grouped.loc[(row_val, col_val)])
                        )

    if coverage_info["empty_combinations"]:
        empty_count = len(coverage_info["empty_combinations"])
        if empty_count > coverage_info["total_combinations"] * 0.3:
            print(
                f"Warning: {empty_count}/{coverage_info['total_combinations']} "
                f"subplot combinations have no data ({empty_count / coverage_info['total_combinations'] * 100:.1f}%). "
                f"Consider filtering data or using different dimensions."
            )

    if coverage_info["sparse_combinations"]:
        sparse_count = len(coverage_info["sparse_combinations"])
        print(
            f"Warning: {sparse_count} subplot(s) have very few data points (< 3). "
            f"Plots may not be meaningful."
        )

    return coverage_info


def validate_common_mistakes(config: FacetingConfig, data: pd.DataFrame) -> None:
    if config.rows and config.rows in data.columns:
        unique_rows = data[config.rows].nunique()
        if unique_rows == 1:
            print(
                f"Warning: rows='{config.rows}' has only 1 unique value. "
                f"Consider using a dimension with multiple values."
            )

    if config.rows and config.cols:
        if config.rows in data.columns and config.cols in data.columns:
            n_rows = data[config.rows].nunique()
            n_cols = data[config.cols].nunique()
            total_subplots = n_rows * n_cols

            if total_subplots > 20:
                print(
                    f"Warning: Large grid ({n_rows}×{n_cols} = {total_subplots} subplots). "
                    f"Consider using wrapped layouts or filtering data."
                )

    if config.lines and config.lines in data.columns:
        avg_points_per_group = len(data) / data[config.lines].nunique()
        if avg_points_per_group < 3:
            print(
                f"Warning: Few data points per {config.lines} group "
                f"(avg {avg_points_per_group:.1f}). Plots may be sparse."
            )


def suggest_error_recovery(error_type: str, context: Dict[str, Any]) -> str:
    suggestions = {
        "missing_columns": [
            "Check column names for typos",
            "Use data.columns to see available columns",
            "Ensure your data has the expected structure",
        ],
        "empty_subsets": [
            "Check if your data has all combinations of row/col values",
            "Consider using target_row/target_col for sparse data",
            "Use empty_subplot_strategy='silent' to suppress warnings",
        ],
        "large_grid": [
            "Use wrapped layouts: rows='metric', ncols=4",
            "Filter data to fewer categories",
            "Consider hierarchical faceting approaches",
        ],
    }

    if error_type in suggestions:
        return "Suggestions:\n" + "\n".join(f"  • {s}" for s in suggestions[error_type])
    return ""


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
