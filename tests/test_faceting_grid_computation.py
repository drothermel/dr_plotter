import pytest
import pandas as pd

from dr_plotter.faceting_config import FacetingConfig
from dr_plotter.figure import FigureManager
from dr_plotter.figure_config import FigureConfig


class TestDataDimensionAnalysis:
    def test_dimension_extraction_and_ordering(self) -> None:
        data = pd.DataFrame(
            {
                "metric": ["accuracy", "loss", "accuracy", "loss"],
                "model": ["gpt", "gpt", "bert", "bert"],
                "dataset": ["train", "val", "train", "val"],
                "value": [0.9, 0.1, 0.85, 0.15],
            }
        )

        fm = FigureManager()
        config = FacetingConfig(rows="metric", cols="model", lines="dataset")

        dimensions = fm._analyze_data_dimensions(data, config)

        assert set(dimensions["rows"]) == {"accuracy", "loss"}
        assert set(dimensions["cols"]) == {"bert", "gpt"}
        assert set(dimensions["lines"]) == {"train", "val"}

    def test_custom_ordering_applied(self) -> None:
        data = pd.DataFrame(
            {
                "metric": ["loss", "accuracy", "f1"],
                "model": ["bert", "gpt", "llama"],
                "value": [0.1, 0.9, 0.8],
            }
        )

        fm = FigureManager()
        config = FacetingConfig(
            rows="metric",
            cols="model",
            row_order=["accuracy", "f1", "loss"],
            col_order=["llama", "gpt", "bert"],
        )

        dimensions = fm._analyze_data_dimensions(data, config)

        assert dimensions["rows"] == ["accuracy", "f1", "loss"]
        assert dimensions["cols"] == ["llama", "gpt", "bert"]

    def test_missing_column_error(self) -> None:
        data = pd.DataFrame({"value": [1, 2, 3]})
        fm = FigureManager()
        config = FacetingConfig(rows="nonexistent")

        with pytest.raises(
            AssertionError, match="Row dimension column 'nonexistent' not found in data"
        ):
            fm._analyze_data_dimensions(data, config)

    def test_missing_order_values_error(self) -> None:
        data = pd.DataFrame({"metric": ["accuracy", "loss"], "value": [0.9, 0.1]})
        fm = FigureManager()
        config = FacetingConfig(rows="metric", row_order=["accuracy", "loss", "f1"])

        with pytest.raises(
            AssertionError, match="Row order values \\['f1'\\] not found in data"
        ):
            fm._analyze_data_dimensions(data, config)


class TestGridComputation:
    def test_explicit_grid_layout(self) -> None:
        data = pd.DataFrame(
            {
                "metric": ["acc", "loss", "acc", "loss"],
                "model": ["gpt", "gpt", "bert", "bert"],
                "value": [0.9, 0.1, 0.85, 0.15],
            }
        )

        fm = FigureManager()
        config = FacetingConfig(rows="metric", cols="model")

        n_rows, n_cols, metadata = fm._compute_facet_grid(data, config)

        assert n_rows == 2  # acc, loss
        assert n_cols == 2  # bert, gpt
        assert metadata["grid_type"] == "explicit"
        assert len(metadata["fill_order"]) == 4
        assert set(metadata["row_values"]) == {"acc", "loss"}
        assert set(metadata["col_values"]) == {"bert", "gpt"}

    def test_wrapped_rows_layout(self) -> None:
        data = pd.DataFrame(
            {
                "metric": ["acc", "loss", "f1", "precision"],
                "value": [0.9, 0.1, 0.8, 0.75],
            }
        )

        fm = FigureManager()
        config = FacetingConfig(rows="metric", ncols=3)

        n_rows, n_cols, metadata = fm._compute_facet_grid(data, config)

        assert n_rows == 2  # ceil(4/3) = 2
        assert n_cols == 3
        assert metadata["grid_type"] == "wrapped_rows"
        assert len(metadata["fill_order"]) == 4

        expected_positions = [(0, 0), (0, 1), (0, 2), (1, 0)]
        assert metadata["fill_order"] == expected_positions

    def test_wrapped_cols_layout(self) -> None:
        data = pd.DataFrame(
            {
                "model": ["gpt", "bert", "llama", "t5", "bloom"],
                "value": [0.9, 0.85, 0.88, 0.82, 0.87],
            }
        )

        fm = FigureManager()
        config = FacetingConfig(cols="model", nrows=2)

        n_rows, n_cols, metadata = fm._compute_facet_grid(data, config)

        assert n_rows == 2
        assert n_cols == 3  # ceil(5/2) = 3
        assert metadata["grid_type"] == "wrapped_cols"
        assert len(metadata["fill_order"]) == 5

        expected_positions = [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]
        assert metadata["fill_order"] == expected_positions

    def test_invalid_grid_configuration_error(self) -> None:
        data = pd.DataFrame({"value": [1, 2, 3]})
        fm = FigureManager()
        config = FacetingConfig()  # No dimensions specified

        with pytest.raises(AssertionError, match="Invalid grid configuration"):
            fm._compute_facet_grid(data, config)

    def test_ordering_applied_correctly(self) -> None:
        data = pd.DataFrame(
            {
                "metric": ["loss", "accuracy"],
                "model": ["bert", "gpt"],
                "value": [0.1, 0.9],
            }
        )

        fm = FigureManager()
        config = FacetingConfig(
            rows="metric",
            cols="model",
            row_order=["accuracy", "loss"],
            col_order=["gpt", "bert"],
        )

        n_rows, n_cols, metadata = fm._compute_facet_grid(data, config)

        assert metadata["row_values"] == ["accuracy", "loss"]
        assert metadata["col_values"] == ["gpt", "bert"]


class TestTargetingResolution:
    def test_no_targeting_returns_all_positions(self) -> None:
        fm = FigureManager()
        config = FacetingConfig(rows="metric")

        positions = fm._resolve_targeting(config, 3, 2)

        expected = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]
        assert positions == expected

    def test_single_row_targeting(self) -> None:
        fm = FigureManager()
        config = FacetingConfig(rows="metric", target_row=1)

        positions = fm._resolve_targeting(config, 3, 2)

        expected = [(1, 0), (1, 1)]
        assert positions == expected

    def test_single_col_targeting(self) -> None:
        fm = FigureManager()
        config = FacetingConfig(cols="model", target_col=0)

        positions = fm._resolve_targeting(config, 2, 3)

        expected = [(0, 0), (1, 0)]
        assert positions == expected

    def test_single_position_targeting(self) -> None:
        fm = FigureManager()
        config = FacetingConfig(rows="metric", target_row=1, target_col=2)

        positions = fm._resolve_targeting(config, 3, 4)

        assert positions == [(1, 2)]

    def test_multiple_rows_targeting(self) -> None:
        fm = FigureManager()
        config = FacetingConfig(rows="metric", target_rows=[0, 2])

        positions = fm._resolve_targeting(config, 3, 2)

        expected = [(0, 0), (0, 1), (2, 0), (2, 1)]
        assert positions == expected

    def test_multiple_cols_targeting(self) -> None:
        fm = FigureManager()
        config = FacetingConfig(cols="model", target_cols=[1, 3])

        positions = fm._resolve_targeting(config, 2, 4)

        expected = [(0, 1), (0, 3), (1, 1), (1, 3)]
        assert positions == expected

    def test_multiple_targeting_combinations(self) -> None:
        fm = FigureManager()
        config = FacetingConfig(rows="metric", target_rows=[0, 1], target_cols=[1, 2])

        positions = fm._resolve_targeting(config, 3, 4)

        expected = [(0, 1), (0, 2), (1, 1), (1, 2)]
        assert positions == expected

    def test_targeting_validation_errors(self) -> None:
        fm = FigureManager()

        config = FacetingConfig(rows="metric", target_row=5)
        with pytest.raises(AssertionError, match="target_row=5 invalid for 3×2 grid"):
            fm._resolve_targeting(config, 3, 2)

        config = FacetingConfig(cols="model", target_col=-1)
        with pytest.raises(AssertionError, match="target_col=-1 invalid for 2×3 grid"):
            fm._resolve_targeting(config, 2, 3)

        config = FacetingConfig(rows="metric", target_rows=[0, 4])
        with pytest.raises(
            AssertionError, match="target_rows contains 4 which is invalid for 3×2 grid"
        ):
            fm._resolve_targeting(config, 3, 2)


class TestGridValidation:
    def test_grid_compatible_with_existing_plots(self) -> None:
        fm = FigureManager(figure=FigureConfig(rows=2, cols=3))

        fm._validate_facet_grid_against_existing(2, 3)

    def test_grid_incompatible_with_existing_plots_error(self) -> None:
        fm = FigureManager(figure=FigureConfig(rows=2, cols=3))

        fm.plot("scatter", 0, 0, pd.DataFrame({"x": [1, 2], "y": [3, 4]}), x="x", y="y")

        with pytest.raises(
            AssertionError,
            match="Computed facet grid 3×2 conflicts with existing FigureManager grid 2×3",
        ):
            fm._validate_facet_grid_against_existing(3, 2)

    def test_grid_state_management(self) -> None:
        fm = FigureManager()

        assert fm._facet_grid_info is None

        grid_info = {"test": "data"}
        fm._set_facet_grid_info(grid_info)

        assert fm._facet_grid_info == grid_info

    def test_has_existing_plots_detection(self) -> None:
        fm = FigureManager(figure=FigureConfig(rows=2, cols=2))

        has_plots_before = fm._has_existing_plots()

        fm.plot("scatter", 0, 0, pd.DataFrame({"x": [1, 2], "y": [3, 4]}), x="x", y="y")

        has_plots_after = fm._has_existing_plots()

        assert has_plots_after != has_plots_before or has_plots_after


class TestFacetedPlotStub:
    def test_parameter_resolution_override_logic(self) -> None:
        data = pd.DataFrame(
            {
                "metric": ["acc", "loss", "acc", "loss"],
                "model": ["gpt", "gpt", "bert", "bert"],
                "x_val": [0.9, 0.1, 0.85, 0.15],
                "y_val": [0.95, 0.05, 0.8, 0.2],
            }
        )

        fm = FigureManager(figure=FigureConfig(rows=2, cols=2))

        base_config = FacetingConfig(rows="metric", ncols=3)

        fm.plot_faceted(
            data, "scatter", faceting=base_config, cols="model", x="x_val", y="y_val"
        )

        resolved_config = fm._facet_grid_info["config"]
        assert resolved_config.rows == "metric"
        assert resolved_config.cols == "model"  # Override worked
        assert resolved_config.ncols is None  # Override cleared wrapped layout

    def test_input_validation(self) -> None:
        fm = FigureManager()

        with pytest.raises(AssertionError, match="data must be DataFrame"):
            fm.plot_faceted(
                "not a dataframe", "scatter", rows="metric", x="step", y="value"
            )

        data = pd.DataFrame({"metric": ["acc"], "step": [1], "value": [0.9]})
        with pytest.raises(AssertionError, match="x parameter is required"):
            fm.plot_faceted(data, "scatter", rows="metric", y="value")
        with pytest.raises(AssertionError, match="y parameter is required"):
            fm.plot_faceted(data, "scatter", rows="metric", x="step")

    def test_end_to_end_grid_computation_no_plotting(self) -> None:
        data = pd.DataFrame(
            {
                "metric": ["acc", "loss", "f1", "acc", "loss", "f1"],
                "model": ["gpt", "gpt", "gpt", "bert", "bert", "bert"],
                "dataset": ["train", "val", "train", "val", "train", "val"],
                "step": [1, 2, 3, 4, 5, 6],
                "value": [0.9, 0.1, 0.8, 0.85, 0.15, 0.75],
            }
        )

        fm = FigureManager(figure=FigureConfig(rows=3, cols=2))

        fm.plot_faceted(
            data,
            "line",
            rows="metric",
            cols="model",
            lines="dataset",
            x="step",
            y="value",
        )

        grid_info = fm._facet_grid_info

        assert grid_info is not None
        assert grid_info["layout_metadata"]["grid_type"] == "explicit"

    def test_config_validation_called(self) -> None:
        data = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
        fm = FigureManager()

        with pytest.raises(
            AssertionError, match="Must specify at least one of: rows, cols"
        ):
            fm.plot_faceted(data, "scatter")


class TestEdgeCasesAndRealWorldScenarios:
    def test_single_value_dimensions(self) -> None:
        data = pd.DataFrame({"metric": ["accuracy"], "model": ["gpt"], "value": [0.9]})

        fm = FigureManager()
        config = FacetingConfig(rows="metric", cols="model")

        n_rows, n_cols, metadata = fm._compute_facet_grid(data, config)

        assert n_rows == 1
        assert n_cols == 1
        assert metadata["fill_order"] == [(0, 0)]

    def test_large_grid_computation(self) -> None:
        metrics = [f"metric_{i}" for i in range(10)]
        models = [f"model_{i}" for i in range(8)]

        data = pd.DataFrame(
            {
                "metric": metrics * 8,
                "model": [m for m in models for _ in range(10)],
                "value": list(range(80)),
            }
        )

        fm = FigureManager()
        config = FacetingConfig(rows="metric", cols="model")

        n_rows, n_cols, metadata = fm._compute_facet_grid(data, config)

        assert n_rows == 10
        assert n_cols == 8
        assert len(metadata["fill_order"]) == 80

    def test_wrapped_layout_edge_cases(self) -> None:
        data = pd.DataFrame({"metric": ["acc", "loss", "f1"], "value": [0.9, 0.1, 0.8]})

        fm = FigureManager()
        config = FacetingConfig(rows="metric", ncols=2)

        n_rows, n_cols, metadata = fm._compute_facet_grid(data, config)

        assert n_rows == 2  # ceil(3/2) = 2
        assert n_cols == 2
        assert len(metadata["fill_order"]) == 3
        assert metadata["fill_order"] == [(0, 0), (0, 1), (1, 0)]

    def test_ml_training_data_scenario(self) -> None:
        training_data = pd.DataFrame(
            {
                "epoch": list(range(1, 25)),
                "metric": ["train_loss", "val_loss", "train_acc", "val_acc"] * 6,
                "model_size": ["small", "medium", "large"] * 8,
                "dataset": ["squad", "glue"] * 12,
                "value": [0.5 - i * 0.01 for i in range(24)],
            }
        )

        fm = FigureManager(figure=FigureConfig(rows=4, cols=2))

        fm.plot_faceted(
            training_data,
            "line",
            rows="metric",
            cols="dataset",
            lines="model_size",
            row_order=["train_loss", "val_loss", "train_acc", "val_acc"],
            x="epoch",
            y="value",
        )

        grid_info = fm._facet_grid_info

        assert grid_info is not None
        assert grid_info["layout_metadata"]["grid_type"] == "explicit"

        row_values = grid_info["layout_metadata"]["row_values"]
        assert row_values == ["train_loss", "val_loss", "train_acc", "val_acc"]
