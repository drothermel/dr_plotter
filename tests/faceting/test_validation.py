import pandas as pd
import pytest

from dr_plotter.faceting_config import FacetingConfig
from dr_plotter.faceting.validation import (
    validate_required_columns,
    validate_dimension_values,
    get_available_columns_message,
    validate_faceting_data_requirements,
)


class TestValidateRequiredColumns:
    def test_all_columns_present(self):
        data = pd.DataFrame({"a": [1], "b": [2], "c": [3]})
        validate_required_columns(data, ["a", "b"])

    def test_missing_columns(self):
        data = pd.DataFrame({"a": [1], "b": [2]})
        with pytest.raises(AssertionError, match="Missing columns \\['c', 'd'\\]"):
            validate_required_columns(data, ["a", "c", "d"])

    def test_empty_requirements(self):
        data = pd.DataFrame({"a": [1]})
        validate_required_columns(data, [])


class TestValidateDimensionValues:
    def test_column_exists(self):
        data = pd.DataFrame({"col": ["A", "B"]})
        validate_dimension_values(data, "col")

    def test_column_missing(self):
        data = pd.DataFrame({"col": ["A"]})
        with pytest.raises(AssertionError, match="Column 'missing' not found"):
            validate_dimension_values(data, "missing")

    def test_expected_values_present(self):
        data = pd.DataFrame({"col": ["A", "B", "C"]})
        validate_dimension_values(data, "col", ["A", "B"])

    def test_expected_values_missing(self):
        data = pd.DataFrame({"col": ["A", "B"]})
        with pytest.raises(AssertionError, match="Expected values \\['X'\\] not found"):
            validate_dimension_values(data, "col", ["A", "X"])


class TestGetAvailableColumnsMessage:
    def test_message_format(self):
        data = pd.DataFrame({"a": [1], "c": [2], "b": [3]})
        message = get_available_columns_message(data, ["x", "y"])
        assert (
            message == "Missing columns ['x', 'y']. Available columns: ['a', 'b', 'c']"
        )


class TestValidateFacetingDataRequirements:
    def test_valid_dataframe(self):
        data = pd.DataFrame(
            {"rows": ["A"], "cols": ["X"], "lines": ["1"], "x": [1], "y": [2]}
        )
        config = FacetingConfig(rows="rows", cols="cols", lines="lines", x="x", y="y")
        validate_faceting_data_requirements(data, config)

    def test_invalid_data_type(self):
        config = FacetingConfig()
        with pytest.raises(AssertionError, match="data must be DataFrame"):
            validate_faceting_data_requirements("not a dataframe", config)

    def test_missing_required_columns(self):
        data = pd.DataFrame({"a": [1]})
        config = FacetingConfig(rows="missing_col")
        with pytest.raises(AssertionError, match="Missing columns \\['missing_col'\\]"):
            validate_faceting_data_requirements(data, config)

    def test_partial_requirements(self):
        data = pd.DataFrame({"rows": ["A"], "x": [1]})
        config = FacetingConfig(rows="rows", x="x")
        validate_faceting_data_requirements(data, config)
