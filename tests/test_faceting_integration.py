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


def create_test_data_with_three_datasets() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "metric": ["loss", "accuracy"] * 36,
            "dataset": ["train", "val", "test"] * 24,
            "model_size": ["small", "medium", "large"] * 24,
            "epoch": list(range(1, 73)),
            "value": [0.8, 0.7, 0.6, 0.75, 0.82, 0.72] * 12,
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


def create_test_data_with_multiple_metrics() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "metric": ["loss", "accuracy", "precision", "recall", "f1", "auc"] * 20,
            "dataset": ["train", "val", "test"] * 40,
            "model_size": ["small", "medium", "large"] * 40,
            "step": list(range(1, 121)),
            "value": [0.8 - i * 0.005 for i in range(120)],
        }
    )


def create_test_data_with_multiple_models() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "model": ["bert", "roberta", "gpt", "t5", "llama"] * 24,
            "dataset": ["squad", "glue"] * 60,
            "metric": ["accuracy", "f1"] * 60,
            "step": list(range(1, 121)),
            "value": [0.9 - i * 0.003 for i in range(120)],
        }
    )


class TestWrappedLayouts:
    def test_rows_with_ncols_layout(self):
        data = create_test_data_with_multiple_metrics()

        with FigureManager(figure=FigureConfig(rows=2, cols=3, figsize=(15, 10))) as fm:
            fm.plot_faceted(
                data=data, plot_type="line", rows="metric", ncols=3, x="step", y="value"
            )

            grid_info = fm._facet_grid_info
            assert grid_info["layout_metadata"]["grid_type"] == "wrapped_rows"
            assert grid_info["layout_metadata"]["n_rows"] == 2
            assert grid_info["layout_metadata"]["n_cols"] == 3

    def test_cols_with_nrows_layout(self):
        data = create_test_data_with_multiple_models()

        with FigureManager(figure=FigureConfig(rows=3, cols=2, figsize=(10, 15))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="scatter",
                cols="model",
                nrows=3,
                x="step",
                y="value",
            )

            grid_info = fm._facet_grid_info
            assert grid_info["layout_metadata"]["grid_type"] == "wrapped_cols"
            assert grid_info["layout_metadata"]["n_rows"] == 3
            assert grid_info["layout_metadata"]["n_cols"] == 2


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


class TestTargetingSystem:
    def test_single_row_targeting(self):
        data = create_test_data()

        with FigureManager(figure=FigureConfig(rows=2, cols=2, figsize=(10, 8))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="line",
                rows="metric",
                cols="dataset",
                target_row=0,
                x="epoch",
                y="value",
            )

            grid_info = fm._facet_grid_info
            data_subsets = grid_info["data_subsets"]

            assert (0, 0) in data_subsets
            assert (0, 1) in data_subsets
            assert (1, 0) not in data_subsets
            assert (1, 1) not in data_subsets

    def test_single_col_targeting(self):
        data = create_test_data()

        with FigureManager(figure=FigureConfig(rows=2, cols=2, figsize=(10, 8))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="scatter",
                rows="metric",
                cols="dataset",
                target_col=1,
                x="epoch",
                y="value",
            )

            grid_info = fm._facet_grid_info
            data_subsets = grid_info["data_subsets"]

            assert (0, 1) in data_subsets
            assert (1, 1) in data_subsets
            assert (0, 0) not in data_subsets
            assert (1, 0) not in data_subsets

    def test_multiple_positions_targeting(self):
        data = create_test_data_with_three_datasets()

        with FigureManager(figure=FigureConfig(rows=2, cols=3, figsize=(15, 8))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="scatter",
                rows="metric",
                cols="dataset",
                target_cols=[0, 2],
                x="epoch",
                y="value",
                alpha=0.6,
            )

            grid_info = fm._facet_grid_info
            data_subsets = grid_info["data_subsets"]

            assert (0, 0) in data_subsets
            assert (1, 0) in data_subsets
            assert (0, 1) not in data_subsets
            assert (1, 1) not in data_subsets

    def test_targeting_with_wrapped_layouts(self):
        data = create_test_data_with_multiple_metrics()

        with FigureManager(figure=FigureConfig(rows=2, cols=3, figsize=(15, 10))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="line",
                rows="metric",
                ncols=3,
                target_rows=[0],
                x="step",
                y="value",
            )

            grid_info = fm._facet_grid_info
            data_subsets = grid_info["data_subsets"]

            assert (0, 0) in data_subsets
            assert (0, 1) in data_subsets
            assert (0, 2) in data_subsets
            assert (1, 0) not in data_subsets
            assert (1, 1) not in data_subsets
            assert (1, 2) not in data_subsets


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
            target_positions = fm._resolve_targeting(config, grid_rows, grid_cols)
            data_subsets = fm._prepare_facet_data(
                data, config, layout_metadata, target_positions
            )

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
            target_positions = fm._resolve_targeting(config, grid_rows, grid_cols)
            data_subsets = fm._prepare_facet_data(
                data, config, layout_metadata, target_positions
            )

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


class TestPerSubplotConfiguration:
    def test_nested_x_labels_application(self):
        data = create_test_data()

        x_labels = [["Training Steps", "Validation Steps"], ["Time", "Iterations"]]

        with FigureManager(figure=FigureConfig(rows=2, cols=2, figsize=(10, 8))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="line",
                rows="metric",
                cols="dataset",
                x_labels=x_labels,
                x="epoch",
                y="value",
            )

            axes = fm.fig.axes
            assert axes[0].get_xlabel() == "Training Steps"
            assert axes[1].get_xlabel() == "Validation Steps"
            assert axes[2].get_xlabel() == "Time"
            assert axes[3].get_xlabel() == "Iterations"

    def test_nested_y_labels_application(self):
        data = create_test_data()

        y_labels = [["Loss Value", "Accuracy %"], [None, "Performance"]]

        with FigureManager(figure=FigureConfig(rows=2, cols=2, figsize=(10, 8))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="scatter",
                rows="metric",
                cols="dataset",
                y_labels=y_labels,
                x="epoch",
                y="value",
            )

            axes = fm.fig.axes
            assert axes[0].get_ylabel() == "Loss Value"
            assert axes[1].get_ylabel() == "Accuracy %"
            assert axes[3].get_ylabel() == "Performance"

    def test_nested_axis_limits(self):
        data = create_test_data()

        xlim = [[(0, 20), None], [None, (5, 15)]]

        ylim = [[None, (0.6, 1.0)], [(0.5, 0.9), None]]

        with FigureManager(figure=FigureConfig(rows=2, cols=2, figsize=(10, 8))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="scatter",
                rows="metric",
                cols="dataset",
                xlim=xlim,
                ylim=ylim,
                x="epoch",
                y="value",
            )

            axes = fm.fig.axes
            assert axes[0].get_xlim() == (0, 20)
            assert axes[1].get_ylim() == (0.6, 1.0)
            assert axes[2].get_ylim() == (0.5, 0.9)
            assert axes[3].get_xlim() == (5, 15)

    def test_per_subplot_config_with_targeting(self):
        data = create_test_data()

        x_labels = [["Target Label", "Not Applied"], ["Not Applied", "Not Applied"]]

        with FigureManager(figure=FigureConfig(rows=2, cols=2, figsize=(10, 8))) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="line",
                rows="metric",
                cols="dataset",
                target_row=0,
                target_col=0,
                x_labels=x_labels,
                x="epoch",
                y="value",
            )

            axes = fm.fig.axes
            assert axes[0].get_xlabel() == "Target Label"


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


class TestAdvancedRealWorldScenarios:
    def test_comprehensive_advanced_features(self):
        training_data = pd.DataFrame(
            {
                "step": list(range(100)) * 12,
                "metric": ["train_loss", "val_loss", "train_acc", "val_acc"] * 300,
                "model_size": ["7B", "13B", "30B"] * 400,
                "dataset": ["squad", "glue"] * 600,
                "value": [0.8 - i * 0.003 + (i % 25) * 0.0005 for i in range(1200)],
            }
        )

        x_labels = [
            ["Training Steps", "Training Steps"],
            ["Validation Steps", "Validation Steps"],
        ]

        ylim = [
            [(0.2, 1.0), (0.0, 1.0)],
            [(0.2, 1.0), (0.0, 1.0)],
        ]

        with FigureManager(figure=FigureConfig(rows=2, cols=2, figsize=(12, 8))) as fm:
            fm.plot_faceted(
                data=training_data,
                plot_type="line",
                rows="metric",
                ncols=2,
                lines="model_size",
                x_labels=x_labels,
                ylim=ylim,
                target_rows=[0],
                x="step",
                y="value",
                alpha=0.8,
            )

            grid_info = fm._facet_grid_info
            assert grid_info["layout_metadata"]["grid_type"] == "wrapped_rows"
            assert len(grid_info["data_subsets"]) == 2
            assert grid_info["layout_metadata"]["n_rows"] == 2
            assert grid_info["layout_metadata"]["n_cols"] == 2

            axes = fm.fig.axes
            assert axes[0].get_xlabel() == "Training Steps"
            assert axes[1].get_xlabel() == "Training Steps"
            assert axes[0].get_ylim() == (0.2, 1.0)
            assert axes[1].get_ylim() == (0.0, 1.0)
