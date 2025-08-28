import pandas as pd
import pytest

from dr_plotter.faceting_config import FacetingConfig
from dr_plotter.faceting.data_analysis import (
    extract_dimension_values,
    analyze_data_dimensions,
    detect_missing_combinations,
)


class TestExtractDimensionValues:
    def test_basic_extraction(self):
        data = pd.DataFrame({"col": ["B", "A", "C", "A"]})
        values = extract_dimension_values(data, "col")
        assert values == ["A", "B", "C"]

    def test_with_order(self):
        data = pd.DataFrame({"col": ["B", "A", "C"]})
        values = extract_dimension_values(data, "col", order=["C", "A", "B"])
        assert values == ["C", "A", "B"]

    def test_missing_column(self):
        data = pd.DataFrame({"col": [1, 2, 3]})
        with pytest.raises(
            AssertionError, match="Dimension dimension column 'missing' not found"
        ):
            extract_dimension_values(data, "missing")

    def test_invalid_order_values(self):
        data = pd.DataFrame({"col": ["A", "B"]})
        with pytest.raises(
            AssertionError, match="Dimension order values \\['X'\\] not found"
        ):
            extract_dimension_values(data, "col", order=["A", "X"])


class TestAnalyzeDataDimensions:
    def test_all_dimensions(self):
        data = pd.DataFrame(
            {
                "metric": ["A", "B", "A"],
                "recipe": ["X", "Y", "Z"],
                "model": ["1", "2", "1"],
            }
        )
        config = FacetingConfig(
            rows="metric", cols="recipe", lines="model", row_order=["B", "A"]
        )

        result = analyze_data_dimensions(data, config)

        assert result["rows"] == ["B", "A"]
        assert result["cols"] == ["X", "Y", "Z"]
        assert result["lines"] == ["1", "2"]

    def test_partial_dimensions(self):
        data = pd.DataFrame({"metric": ["A", "B"], "value": [1, 2]})
        config = FacetingConfig(rows="metric")

        result = analyze_data_dimensions(data, config)

        assert result["rows"] == ["A", "B"]
        assert result["cols"] == []
        assert result["lines"] == []

    def test_empty_config(self):
        data = pd.DataFrame({"x": [1, 2]})
        config = FacetingConfig()

        result = analyze_data_dimensions(data, config)

        assert result["rows"] == []
        assert result["cols"] == []
        assert result["lines"] == []


class TestDetectMissingCombinations:
    def test_complete_combinations(self):
        data = pd.DataFrame({"row": ["A", "A", "B", "B"], "col": ["X", "Y", "X", "Y"]})
        missing = detect_missing_combinations(
            data, ["A", "B"], ["X", "Y"], "row", "col"
        )
        assert missing == []

    def test_missing_combinations(self):
        data = pd.DataFrame({"row": ["A", "A", "B"], "col": ["X", "Y", "X"]})
        missing = detect_missing_combinations(
            data, ["A", "B"], ["X", "Y"], "row", "col"
        )
        assert missing == [("B", "Y")]

    def test_empty_inputs(self):
        data = pd.DataFrame({"x": [1]})
        missing = detect_missing_combinations(data, [], [], "", "")
        assert missing == []
