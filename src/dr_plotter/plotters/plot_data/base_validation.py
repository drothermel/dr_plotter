"""Core validation utilities for plot data."""

import pandas as pd
from typing import List


def validate_columns_exist(data: pd.DataFrame, columns: List[str]) -> None:
    """Check that required columns exist in the DataFrame."""
    missing = [col for col in columns if col not in data.columns]
    if missing:
        available = list(data.columns)
        raise ValueError(
            f"Missing required columns: {missing}. "
            f"Available columns: {available}. "
            f"Check your column names for typos or case sensitivity."
        )


def validate_numeric_columns(data: pd.DataFrame, columns: List[str]) -> None:
    """Check that columns are numeric."""
    for col in columns:
        if col in data.columns:
            if not pd.api.types.is_numeric_dtype(data[col]):
                sample = data[col].head(3).tolist()
                raise ValueError(
                    f"Column '{col}' should be numeric but contains: {sample}. "
                    f"Try converting with pd.to_numeric(data['{col}'], errors='coerce')."
                )


def validate_categorical_columns(data: pd.DataFrame, columns: List[str]) -> None:
    """Check that columns are categorical/string type."""
    for col in columns:
        if col in data.columns:
            dtype = data[col].dtype
            if not (pd.api.types.is_string_dtype(dtype) or 
                   pd.api.types.is_categorical_dtype(dtype) or
                   pd.api.types.is_object_dtype(dtype)):
                sample = data[col].head(3).tolist()
                raise ValueError(
                    f"Column '{col}' should be categorical/string but has dtype {dtype} "
                    f"with values: {sample}. "
                    f"Try converting with data['{col}'].astype(str)."
                )