from typing import Dict, List, Optional, Tuple
import pandas as pd
from dr_plotter.faceting_config import FacetingConfig


def extract_dimension_values(
    data: pd.DataFrame,
    column: str,
    order: Optional[List[str]] = None,
    dimension_name: str = "dimension",
) -> List[str]:
    assert column in data.columns, (
        f"{dimension_name.capitalize()} dimension column '{column}' not found in data. Available columns: {sorted(data.columns.tolist())}"
    )

    values = data[column].unique().tolist()

    if order is not None:
        missing_values = [v for v in order if v not in values]
        assert not missing_values, (
            f"{dimension_name.capitalize()} order values {missing_values} not found in data['{column}']. Available values: {sorted(values)}"
        )
        return order
    else:
        return sorted(values, key=str)


def analyze_data_dimensions(
    data: pd.DataFrame, config: FacetingConfig
) -> Dict[str, List[str]]:
    result = {"rows": [], "cols": [], "lines": []}

    if config.rows is not None:
        result["rows"] = extract_dimension_values(
            data, config.rows, config.row_order, "row"
        )

    if config.cols is not None:
        result["cols"] = extract_dimension_values(
            data, config.cols, config.col_order, "column"
        )

    if config.lines is not None:
        result["lines"] = extract_dimension_values(
            data, config.lines, config.lines_order, "lines"
        )

    return result


def detect_missing_combinations(
    data: pd.DataFrame,
    row_values: List[str],
    col_values: List[str],
    row_col: str,
    col_col: str,
) -> List[Tuple[str, str]]:
    if not row_values or not col_values or not row_col or not col_col:
        return []

    actual_combinations = set()
    for _, row in data.iterrows():
        row_val = row[row_col]
        col_val = row[col_col]
        actual_combinations.add((row_val, col_val))

    expected_combinations = {(r, c) for r in row_values for c in col_values}
    missing = expected_combinations - actual_combinations

    return sorted(list(missing))
