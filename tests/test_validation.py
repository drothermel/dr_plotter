import pytest
import pandas as pd
from pydantic import ValidationError
from dr_plotter.plotters.plot_data import (
    ScatterPlotData,
    HistogramData,
    HeatmapData,
    BarPlotData,
)


@pytest.fixture
def valid_data():
    return pd.DataFrame(
        {
            "x_num": [1, 2, 3],
            "y_num": [4, 5, 6],
            "category": ["A", "B", "C"],
            "values": [10, 20, 30],
        }
    )


@pytest.fixture
def invalid_data():
    return pd.DataFrame({"x_text": ["a", "b", "c"], "y_num": [4, 5, 6]})


def test_scatter_validation_success(valid_data):
    data = ScatterPlotData(data=valid_data, x="x_num", y="y_num")
    assert data.x == "x_num"
    assert data.y == "y_num"


def test_missing_column_error(valid_data):
    with pytest.raises(ValidationError, match="not found in data"):
        ScatterPlotData(data=valid_data, x="missing", y="y_num")


def test_non_numeric_error(invalid_data):
    with pytest.raises(ValidationError, match="should be numeric"):
        ScatterPlotData(data=invalid_data, x="x_text", y="y_num")


def test_histogram_validation(valid_data):
    data = HistogramData(data=valid_data, x="x_num")
    assert data.x == "x_num"


def test_bar_categorical_validation(valid_data):
    data = BarPlotData(data=valid_data, x="category", y="y_num")
    assert data.x == "category"


def test_heatmap_pivot_validation():
    # Valid: no duplicates
    valid_data = pd.DataFrame(
        {"x_cat": ["A", "B", "C"], "y_cat": ["X", "Y", "Z"], "values": [1, 2, 3]}
    )
    data = HeatmapData(data=valid_data, x="x_cat", y="y_cat", values="values")
    assert data.x == "x_cat"

    # Invalid: duplicate x,y combinations
    dup_data = pd.DataFrame({"x": ["A", "A"], "y": ["B", "B"], "values": [1, 2]})
    with pytest.raises(ValidationError, match="duplicate x,y combinations"):
        HeatmapData(data=dup_data, x="x", y="y", values="values")
