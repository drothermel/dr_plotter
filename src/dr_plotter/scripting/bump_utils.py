from __future__ import annotations

from typing import Any

import pandas as pd
from datadec.model_utils import param_to_numeric


def apply_first_last_filter(
    bump_data: pd.DataFrame, time_col: str = "time", category_col: str = "category"
) -> pd.DataFrame:
    """Extract only first and last time points for each category (compressed bump view).

    This creates a compressed visualization showing only the initial and final
    rankings for each category, connected by straight lines. Useful for
    highlighting ranking changes without trajectory noise.

    Args:
        bump_data: DataFrame with bump plot data structure
        time_col: Name of column containing time/step values
        category_col: Name of column containing category/recipe names

    Returns:
        DataFrame with only first and last time points for each category

    Example:
        >>> filtered_data = apply_first_last_filter(bump_data)
        >>> # Now each category has only 2 points: start and end
    """
    validate_bump_data_structure(bump_data, time_col, category_col)

    filtered_data = []
    for category in bump_data[category_col].unique():
        cat_data = bump_data[bump_data[category_col] == category].copy()

        # Handle both numeric and string time values
        time_values = cat_data[time_col].unique()
        first_value = time_values[0]

        if isinstance(first_value, (str, object)) and hasattr(first_value, "endswith"):
            # String values like "150M", "1B" - use param_to_numeric for sorting
            time_points = sorted(time_values, key=param_to_numeric)
        else:
            # Numeric values like training steps - use regular numeric sorting
            time_points = sorted(time_values)

        if len(time_points) < 2:
            filtered_data.append(cat_data)
        else:
            first_last = cat_data[
                cat_data[time_col].isin([time_points[0], time_points[-1]])
            ]
            filtered_data.append(first_last)

    return (
        pd.concat(filtered_data, ignore_index=True) if filtered_data else pd.DataFrame()
    )


def validate_bump_data_structure(
    bump_data: pd.DataFrame,
    time_col: str = "time",
    category_col: str = "category",
    score_col: str = "score",
) -> None:
    """Validate that DataFrame has required columns and structure for bump plots.

    Args:
        bump_data: DataFrame to validate
        time_col: Expected name of time/step column
        category_col: Expected name of category column
        score_col: Expected name of score column

    Raises:
        AssertionError: If required columns are missing or data is invalid
    """
    assert not bump_data.empty, "Bump data cannot be empty"

    required_cols = {time_col, category_col, score_col}
    missing_cols = required_cols - set(bump_data.columns)
    assert not missing_cols, f"Missing required columns: {missing_cols}"

    assert len(bump_data[category_col].unique()) > 0, "Must have at least one category"
    assert len(bump_data[time_col].unique()) > 0, "Must have at least one time point"

    # Check for numeric score column
    assert pd.api.types.is_numeric_dtype(bump_data[score_col]), (
        f"Score column '{score_col}' must be numeric"
    )


def get_bump_data_summary(
    bump_data: pd.DataFrame, time_col: str = "time", category_col: str = "category"
) -> dict[str, Any]:
    """Get summary statistics about bump plot data structure.

    Args:
        bump_data: DataFrame with bump plot data
        time_col: Name of time/step column
        category_col: Name of category column

    Returns:
        Dictionary with summary information
    """
    validate_bump_data_structure(bump_data, time_col, category_col)

    return {
        "num_categories": len(bump_data[category_col].unique()),
        "num_time_points": len(bump_data[time_col].unique()),
        "total_data_points": len(bump_data),
        "categories": sorted(bump_data[category_col].unique()),
        "time_range": (bump_data[time_col].min(), bump_data[time_col].max()),
        "points_per_category": bump_data.groupby(category_col)[time_col]
        .count()
        .to_dict(),
    }
