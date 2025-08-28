import pandas as pd
import pytest

from dr_plotter.faceting_config import FacetingConfig
from dr_plotter.faceting.grid_computation import (
    compute_grid_dimensions,
    compute_grid_layout_metadata,
    resolve_target_positions,
)


class TestComputeGridDimensions:
    def test_explicit_grid(self):
        data = pd.DataFrame(
            {"metric": ["A", "B", "A", "B"], "recipe": ["X", "Y", "Z", "X"]}
        )
        config = FacetingConfig(rows="metric", cols="recipe")
        dimensions = {"rows": ["A", "B"], "cols": ["X", "Y", "Z"], "lines": []}

        n_rows, n_cols = compute_grid_dimensions(data, config, dimensions)
        assert n_rows == 2
        assert n_cols == 3

    def test_wrapped_rows(self):
        data = pd.DataFrame(
            {
                "metric": ["A", "B", "C", "D", "E"],
            }
        )
        config = FacetingConfig(rows="metric", ncols=3)
        dimensions = {"rows": ["A", "B", "C", "D", "E"], "cols": [], "lines": []}

        n_rows, n_cols = compute_grid_dimensions(data, config, dimensions)
        assert n_rows == 2
        assert n_cols == 3

    def test_wrapped_cols(self):
        data = pd.DataFrame(
            {
                "recipe": ["X", "Y", "Z", "W"],
            }
        )
        config = FacetingConfig(cols="recipe", nrows=2)
        dimensions = {"rows": [], "cols": ["X", "Y", "Z", "W"], "lines": []}

        n_rows, n_cols = compute_grid_dimensions(data, config, dimensions)
        assert n_rows == 2
        assert n_cols == 2

    def test_invalid_config(self):
        data = pd.DataFrame({"x": [1, 2, 3]})
        config = FacetingConfig()
        dimensions = {"rows": [], "cols": [], "lines": []}

        with pytest.raises(AssertionError, match="Invalid grid configuration"):
            compute_grid_dimensions(data, config, dimensions)


class TestComputeGridLayoutMetadata:
    def test_explicit_layout_metadata(self):
        data = pd.DataFrame({"metric": ["A", "B"], "recipe": ["X", "Y"]})
        config = FacetingConfig(rows="metric", cols="recipe")
        dimensions = {"rows": ["A", "B"], "cols": ["X", "Y"], "lines": []}

        metadata = compute_grid_layout_metadata(data, config, dimensions)

        assert metadata["grid_type"] == "explicit"
        assert metadata["row_values"] == ["A", "B"]
        assert metadata["col_values"] == ["X", "Y"]
        assert metadata["fill_order"] == [(0, 0), (0, 1), (1, 0), (1, 1)]

    def test_wrapped_rows_layout_metadata(self):
        data = pd.DataFrame(
            {
                "metric": ["A", "B", "C", "D"],
            }
        )
        config = FacetingConfig(rows="metric", ncols=3)
        dimensions = {"rows": ["A", "B", "C", "D"], "cols": [], "lines": []}

        metadata = compute_grid_layout_metadata(data, config, dimensions)

        assert metadata["grid_type"] == "wrapped_rows"
        assert metadata["fill_order"] == [(0, 0), (0, 1), (0, 2), (1, 0)]


class TestResolveTargetPositions:
    def test_no_targeting(self):
        config = FacetingConfig()
        positions = resolve_target_positions(config, 2, 3)
        expected = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
        assert positions == expected

    def test_target_row(self):
        config = FacetingConfig(target_row=1)
        positions = resolve_target_positions(config, 2, 3)
        expected = [(1, 0), (1, 1), (1, 2)]
        assert positions == expected

    def test_target_col(self):
        config = FacetingConfig(target_col=1)
        positions = resolve_target_positions(config, 2, 3)
        expected = [(0, 1), (1, 1)]
        assert positions == expected

    def test_target_row_and_col(self):
        config = FacetingConfig(target_row=0, target_col=2)
        positions = resolve_target_positions(config, 2, 3)
        expected = [(0, 2)]
        assert positions == expected

    def test_target_rows(self):
        config = FacetingConfig(target_rows=[0, 2])
        positions = resolve_target_positions(config, 3, 2)
        expected = [(0, 0), (0, 1), (2, 0), (2, 1)]
        assert positions == expected

    def test_invalid_target_row(self):
        config = FacetingConfig(target_row=3)
        with pytest.raises(AssertionError, match="target_row=3 invalid for 2×2 grid"):
            resolve_target_positions(config, 2, 2)

    def test_invalid_target_col(self):
        config = FacetingConfig(target_col=3)
        with pytest.raises(AssertionError, match="target_col=3 invalid for 2×2 grid"):
            resolve_target_positions(config, 2, 2)
