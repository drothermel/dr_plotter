import pytest
import pandas as pd
from dr_plotter.utils.validation import validate_columns_exist, validate_numeric_columns


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'numeric': [1, 2, 3],
        'text': ['a', 'b', 'c'],
        'float': [1.5, 2.5, 3.5]
    })


def test_validate_columns_exist_success(sample_df):
    validate_columns_exist(sample_df, 'numeric')
    validate_columns_exist(sample_df, ['numeric', 'text'])
    validate_columns_exist(sample_df, None)


def test_validate_columns_exist_failure(sample_df):
    with pytest.raises(AssertionError, match="Column 'missing' not found"):
        validate_columns_exist(sample_df, 'missing')


def test_validate_numeric_columns_success(sample_df):
    validate_numeric_columns(sample_df, 'numeric')
    validate_numeric_columns(sample_df, ['numeric', 'float'])
    validate_numeric_columns(sample_df, None)


def test_validate_numeric_columns_failure(sample_df):
    with pytest.raises(AssertionError, match="must contain numeric data"):
        validate_numeric_columns(sample_df, 'text')