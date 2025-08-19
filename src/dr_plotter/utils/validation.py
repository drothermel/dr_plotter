"""
Data validation utility functions for dr_plotter.

These functions provide reusable validation logic that can be used
by plotter classes to validate their input data.
"""

import pandas as pd
from typing import Union, List


def validate_columns_exist(data: pd.DataFrame, columns: Union[str, List[str]]) -> None:
    """
    Validate that specified columns exist in the DataFrame.
    
    Args:
        data: The DataFrame to validate
        columns: Column name(s) to check for existence. Can be:
            - A single column name (str)
            - A list of column names
            - None (validation passes)
    
    Raises:
        AssertionError: If any specified column is not found in the DataFrame
    
    Examples:
        >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        >>> validate_columns_exist(df, 'a')  # Passes
        >>> validate_columns_exist(df, ['a', 'b'])  # Passes  
        >>> validate_columns_exist(df, 'c')  # Raises AssertionError
        >>> validate_columns_exist(df, None)  # Passes (no validation)
    """
    if columns is None:
        return
    
    # Convert single column to list for uniform processing
    if isinstance(columns, str):
        columns = [columns]
    
    # Check each column exists
    for col in columns:
        assert col in data.columns, f"Column '{col}' not found in data. Available columns: {list(data.columns)}"


def validate_numeric_columns(data: pd.DataFrame, columns: Union[str, List[str]]) -> None:
    """
    Validate that specified columns contain numeric data.
    
    Args:
        data: The DataFrame to validate
        columns: Column name(s) to check for numeric data. Can be:
            - A single column name (str)
            - A list of column names
            - None (validation passes)
    
    Raises:
        AssertionError: If any specified column is not numeric
    
    Examples:
        >>> df = pd.DataFrame({'numeric': [1, 2, 3], 'text': ['a', 'b', 'c']})
        >>> validate_numeric_columns(df, 'numeric')  # Passes
        >>> validate_numeric_columns(df, 'text')  # Raises AssertionError
        >>> validate_numeric_columns(df, None)  # Passes (no validation)
    """
    if columns is None:
        return
        
    # Convert single column to list for uniform processing
    if isinstance(columns, str):
        columns = [columns]
    
    # Check each column is numeric
    for col in columns:
        assert col in data.columns, f"Column '{col}' not found in data"
        assert pd.api.types.is_numeric_dtype(data[col]), f"Column '{col}' must contain numeric data, got {data[col].dtype}"