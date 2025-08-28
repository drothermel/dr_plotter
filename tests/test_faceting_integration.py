import pytest
import pandas as pd

from dr_plotter.faceting_config import FacetingConfig
from dr_plotter.figure_config import FigureConfig
from dr_plotter.figure import FigureManager


def create_test_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "metric": ["loss", "accuracy", "loss", "accuracy"] * 6,
            "dataset": ["train", "train", "val", "val"] * 6,
            "model_size": ["small", "medium", "large"] * 8,
            "epoch": list(range(1, 25)),
            "value": [0.8, 0.7, 0.6, 0.75, 0.82, 0.72] * 4,
        }
    )


def create_ml_training_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "metric": ["loss", "loss", "accuracy", "accuracy"] * 3,
            "dataset": ["train", "val"] * 6,
            "model_size": ["small", "medium", "large"] * 4,
            "epoch": list(range(1, 13)),
            "value": [
                0.9,
                0.85,
                0.8,
                0.75,
                0.88,
                0.83,
                0.82,
                0.78,
                0.86,
                0.81,
                0.84,
                0.79,
            ],
        }
    )


class TestBasicFacetedPlotting:
    def test_simple_line_plots_explicit_grid(self):
        data = create_test_data()

        with FigureManager(figure=FigureConfig(rows=2, cols=2, figsize=(10, 8))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="line",
                rows="metric",
                cols="dataset",
                x="epoch",
                y="value",
            )

            assert fm._facet_grid_info is not None
            assert fm._facet_grid_info["layout_metadata"]["grid_type"] == "explicit"

    def test_scatter_plots_with_hue_by_lines(self):
        data = create_test_data()

        with FigureManager(figure=FigureConfig(rows=2, cols=2, figsize=(10, 8))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="scatter",
                rows="metric",
                cols="dataset",
                lines="model_size",
                x="epoch",
                y="value",
            )

            config = fm._facet_grid_info["config"]
            assert config.lines == "model_size"

    def test_different_plot_types(self):
        data = create_test_data()

        plot_types = ["line", "scatter"]
        for plot_type in plot_types:
            with FigureManager(
                figure=FigureConfig(rows=2, cols=2, figsize=(8, 6))
            ) as fm:
                fm.plot_faceted(
                    data=data,
                    plot_type=plot_type,
                    rows="metric",
                    cols="dataset",
                    x="epoch",
                    y="value",
                )

                assert fm._facet_grid_info is not None

    def test_missing_data_combinations_handled(self):
        data = pd.DataFrame(
            {
                "metric": ["loss", "loss", "accuracy"],
                "dataset": ["train", "val", "train"],
                "epoch": [1, 2, 3],
                "value": [0.8, 0.7, 0.9],
            }
        )

        with FigureManager(figure=FigureConfig(rows=2, cols=2, figsize=(8, 6))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="line",
                rows="metric",
                cols="dataset",
                x="epoch",
                y="value",
            )

            assert fm._facet_grid_info is not None


class TestParameterResolution:
    def test_direct_params_override_config(self):
        data = create_test_data()

        config = FacetingConfig(rows="metric", cols="dataset", x="epoch", y="value")

        with FigureManager(figure=FigureConfig(rows=2, cols=3, figsize=(12, 8))) as fm:
            fm.plot_faceted(
                data=data, plot_type="line", faceting=config, cols="model_size"
            )

            resolved_config = fm._facet_grid_info["config"]
            assert resolved_config.cols == "model_size"
            assert resolved_config.rows == "metric"

    def test_plot_kwargs_passed_through(self):
        data = create_test_data()

        with FigureManager(figure=FigureConfig(rows=2, cols=2, figsize=(8, 6))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="line",
                rows="metric",
                cols="dataset",
                x="epoch",
                y="value",
                alpha=0.7,
                linewidth=2,
            )

            assert fm._facet_grid_info is not None


class TestDataPreparation:
    def test_data_subsetting_correctness(self):
        data = create_ml_training_data()

        with FigureManager(figure=FigureConfig(rows=2, cols=2, figsize=(8, 6))) as fm:
            config = FacetingConfig(rows="metric", cols="dataset", x="epoch", y="value")

            grid_rows, grid_cols, layout_metadata = fm._compute_facet_grid(data, config)
            data_subsets = fm._prepare_facet_data(data, config, layout_metadata)

            for (row_idx, col_idx), subset in data_subsets.items():
                row_value = layout_metadata["row_values"][row_idx]
                col_value = layout_metadata["col_values"][col_idx]

                expected_rows = data[
                    (data["metric"] == row_value) & (data["dataset"] == col_value)
                ]
                assert len(subset) == len(expected_rows)

    def test_empty_subsets_handled(self):
        data = pd.DataFrame(
            {
                "metric": ["loss", "accuracy", "loss"],
                "dataset": ["train", "train", "val"],
                "epoch": [1, 2, 3],
                "value": [0.8, 0.7, 0.6],
            }
        )

        with FigureManager(figure=FigureConfig(rows=2, cols=2, figsize=(8, 6))) as fm:
            config = FacetingConfig(rows="metric", cols="dataset", x="epoch", y="value")

            grid_rows, grid_cols, layout_metadata = fm._compute_facet_grid(data, config)
            data_subsets = fm._prepare_facet_data(data, config, layout_metadata)

            empty_subsets = [k for k, v in data_subsets.items() if v.empty]
            assert len(empty_subsets) > 0


class TestValidation:
    def test_missing_columns_error_messages(self):
        data = create_test_data()

        with pytest.raises(AssertionError) as exc_info:
            with FigureManager(figure=FigureConfig(rows=2, cols=2)) as fm:
                fm.plot_faceted(
                    data=data,
                    plot_type="line",
                    rows="nonexistent_column",
                    cols="dataset",
                    x="epoch",
                    y="value",
                )

        assert "Available columns:" in str(exc_info.value)
        assert "nonexistent_column" in str(exc_info.value)

    def test_unsupported_features_warnings(self):
        data = create_test_data()

        with pytest.raises(AssertionError) as exc_info:
            config = FacetingConfig(
                rows="metric", cols="dataset", ncols=3, x="epoch", y="value"
            )
            config.validate()

        assert "Cannot specify both" in str(exc_info.value)

    def test_targeting_not_supported(self):
        data = create_test_data()

        with pytest.raises(AssertionError) as exc_info:
            with FigureManager(figure=FigureConfig(rows=2, cols=2)) as fm:
                fm.plot_faceted(
                    data=data,
                    plot_type="line",
                    rows="metric",
                    cols="dataset",
                    target_row=0,
                    x="epoch",
                    y="value",
                )

        assert "Targeting not supported in Chunk 3" in str(exc_info.value)


class TestRealWorldScenarios:
    def test_ml_training_data_pattern(self):
        data = create_ml_training_data()

        with FigureManager(figure=FigureConfig(rows=2, cols=2, figsize=(12, 8))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="line",
                rows="metric",
                cols="dataset",
                lines="model_size",
                x="epoch",
                y="value",
            )

            config = fm._facet_grid_info["config"]
            assert config.rows == "metric"
            assert config.cols == "dataset"
            assert config.lines == "model_size"

    def test_ordering_applied_correctly(self):
        data = create_test_data()

        with FigureManager(figure=FigureConfig(rows=2, cols=3, figsize=(15, 8))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="line",
                rows="metric",
                cols="model_size",
                row_order=["accuracy", "loss"],
                col_order=["large", "medium", "small"],
                x="epoch",
                y="value",
            )

            config = fm._facet_grid_info["config"]
            assert config.row_order == ["accuracy", "loss"]
            assert config.col_order == ["large", "medium", "small"]


class TestExampleCompatibility:
    def test_simplify_existing_faceted_example(self):
        data = pd.DataFrame(
            {
                "step": list(range(1, 101)) * 6,
                "value": [
                    0.9 - i * 0.01 + j * 0.1 for i in range(100) for j in range(6)
                ],
                "metric": ["loss", "accuracy"] * 300,
                "recipe": ["C4", "Dolma1.7", "FineWeb-Edu"] * 200,
                "model_size": ["4M", "6M"] * 300,
            }
        )

        with FigureManager(figure=FigureConfig(rows=2, cols=3, figsize=(18, 10))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="line",
                rows="metric",
                cols="recipe",
                lines="model_size",
                x="step",
                y="value",
            )

            assert fm._facet_grid_info is not None

            grid_info = fm._facet_grid_info["layout_metadata"]
            assert len(grid_info["row_values"]) == 2
            assert len(grid_info["col_values"]) == 3
