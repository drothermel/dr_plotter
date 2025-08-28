import pandas as pd
import pytest

from dr_plotter.faceting.data_preparation import (
    create_data_subset,
    prepare_subplot_data_subsets,
)


class TestCreateDataSubset:
    def test_no_filters(self):
        data = pd.DataFrame({"x": [1, 2, 3], "y": ["A", "B", "C"]})
        subset = create_data_subset(data, {})
        pd.testing.assert_frame_equal(subset, data)

    def test_single_filter(self):
        data = pd.DataFrame({"x": [1, 2, 3], "y": ["A", "B", "A"]})
        subset = create_data_subset(data, {"y": "A"})
        expected = pd.DataFrame({"x": [1, 3], "y": ["A", "A"]}, index=[0, 2])
        pd.testing.assert_frame_equal(subset, expected)

    def test_multiple_filters(self):
        data = pd.DataFrame(
            {"x": [1, 2, 3, 4], "y": ["A", "B", "A", "B"], "z": ["X", "X", "Y", "Y"]}
        )
        subset = create_data_subset(data, {"y": "A", "z": "Y"})
        expected = pd.DataFrame({"x": [3], "y": ["A"], "z": ["Y"]}, index=[2])
        pd.testing.assert_frame_equal(subset, expected)

    def test_nonexistent_column(self):
        data = pd.DataFrame({"x": [1, 2]})
        subset = create_data_subset(data, {"missing": "value"})
        pd.testing.assert_frame_equal(subset, data)


class TestPrepareSubplotDataSubsets:
    def test_explicit_grid(self):
        data = pd.DataFrame(
            {
                "metric": ["A", "A", "B", "B"],
                "recipe": ["X", "Y", "X", "Y"],
                "value": [1, 2, 3, 4],
            }
        )

        subsets = prepare_subplot_data_subsets(
            data, ["A", "B"], ["X", "Y"], "metric", "recipe", "explicit"
        )

        assert len(subsets) == 4

        assert len(subsets[(0, 0)]) == 1
        assert subsets[(0, 0)].iloc[0]["value"] == 1

        assert len(subsets[(0, 1)]) == 1
        assert subsets[(0, 1)].iloc[0]["value"] == 2

        assert len(subsets[(1, 0)]) == 1
        assert subsets[(1, 0)].iloc[0]["value"] == 3

    def test_empty_subset(self):
        data = pd.DataFrame(
            {"metric": ["A", "A"], "recipe": ["X", "X"], "value": [1, 2]}
        )

        subsets = prepare_subplot_data_subsets(
            data, ["A", "B"], ["X", "Y"], "metric", "recipe", "explicit"
        )

        assert len(subsets[(0, 0)]) == 2
        assert len(subsets[(0, 1)]) == 0
        assert len(subsets[(1, 0)]) == 0
        assert len(subsets[(1, 1)]) == 0

    def test_none_columns(self):
        data = pd.DataFrame({"value": [1, 2, 3]})

        subsets = prepare_subplot_data_subsets(data, [], [], None, None, "explicit")

        assert len(subsets) == 0

    def test_unsupported_grid_type(self):
        data = pd.DataFrame({"x": [1]})

        with pytest.raises(AssertionError, match="Layout type 'wrapped' not supported"):
            prepare_subplot_data_subsets(data, [], [], None, None, "wrapped")
