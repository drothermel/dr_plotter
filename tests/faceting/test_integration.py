import pandas as pd

from dr_plotter.faceting_config import FacetingConfig
from dr_plotter.faceting import (
    analyze_data_dimensions,
    compute_grid_dimensions,
    compute_grid_layout_metadata,
    resolve_target_positions,
    prepare_subplot_data_subsets,
    validate_faceting_data_requirements,
)


class TestModuleIntegration:
    def test_end_to_end_explicit_grid(self):
        data = pd.DataFrame(
            {
                "metric": ["acc", "loss", "acc", "loss"],
                "dataset": ["train", "train", "test", "test"],
                "step": [1, 2, 3, 4],
                "value": [0.8, 0.2, 0.7, 0.3],
            }
        )
        config = FacetingConfig(
            rows="metric",
            cols="dataset",
            x="step",
            y="value",
            row_order=["acc", "loss"],
        )

        validate_faceting_data_requirements(data, config)

        dimensions = analyze_data_dimensions(data, config)
        assert dimensions["rows"] == ["acc", "loss"]
        assert dimensions["cols"] == ["test", "train"]

        n_rows, n_cols = compute_grid_dimensions(data, config, dimensions)
        assert n_rows == 2
        assert n_cols == 2

        layout_metadata = compute_grid_layout_metadata(data, config, dimensions)
        assert layout_metadata["grid_type"] == "explicit"

        target_positions = resolve_target_positions(config, n_rows, n_cols)
        assert len(target_positions) == 4

        data_subsets = prepare_subplot_data_subsets(
            data,
            dimensions["rows"],
            dimensions["cols"],
            config.rows,
            config.cols,
            layout_metadata["grid_type"],
        )
        assert len(data_subsets) == 4
        assert all(len(subset) <= 1 for subset in data_subsets.values())

    def test_import_structure(self):
        from dr_plotter.faceting.types import GridLayout

        layout = GridLayout(
            rows=2,
            cols=3,
            row_values=["A", "B"],
            col_values=["X", "Y", "Z"],
            grid_type="explicit",
            metadata={},
        )
        assert layout.rows == 2
        assert layout.cols == 3

    def test_module_boundaries(self):
        data = pd.DataFrame({"row": ["A", "B"], "col": ["X", "Y"], "value": [1, 2]})
        config = FacetingConfig(rows="row", cols="col", x="value", y="value")

        dimensions = analyze_data_dimensions(data, config)

        n_rows, n_cols = compute_grid_dimensions(data, config, dimensions)
        assert n_rows == 2
        assert n_cols == 2

        positions = resolve_target_positions(config, n_rows, n_cols)
        assert len(positions) == 4

        layout_metadata = compute_grid_layout_metadata(data, config, dimensions)
        subsets = prepare_subplot_data_subsets(
            data,
            dimensions["rows"],
            dimensions["cols"],
            config.rows,
            config.cols,
            layout_metadata["grid_type"],
        )

        for pos in positions:
            assert pos in subsets
