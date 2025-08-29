import pandas as pd

from dr_plotter.figure import FigureManager
from dr_plotter.figure_config import FigureConfig
from dr_plotter.faceting import FacetStyleCoordinator


def create_test_data_with_consistent_dimension() -> pd.DataFrame:
    data = []
    for step in range(0, 100, 10):
        for metric in ["accuracy", "loss"]:
            for dataset in ["train", "val", "test"]:
                for model_size in ["7B", "13B"]:
                    data.append(
                        {
                            "step": step,
                            "metric": metric,
                            "dataset": dataset,
                            "model_size": model_size,
                            "value": 0.8
                            - step * 0.001
                            + hash(f"{metric}_{dataset}_{model_size}") % 10 * 0.01,
                        }
                    )
    return pd.DataFrame(data)


def create_scatter_data() -> pd.DataFrame:
    data = []
    for step in range(0, 50, 5):
        for metric in ["accuracy", "loss"]:
            for dataset in ["train", "val"]:
                for model_size in ["7B", "13B", "30B"]:
                    data.append(
                        {
                            "step": step,
                            "metric": metric,
                            "dataset": dataset,
                            "model_size": model_size,
                            "value": 0.7
                            + step * 0.002
                            + hash(f"{metric}_{dataset}_{model_size}") % 5 * 0.02,
                        }
                    )
    return pd.DataFrame(data)


def create_line_data() -> pd.DataFrame:
    data = []
    for step in range(0, 50, 10):
        for metric in ["accuracy", "loss"]:
            for dataset in ["train", "val"]:
                for model_size in ["7B", "13B", "30B"]:
                    data.append(
                        {
                            "step": step,
                            "metric": metric,
                            "dataset": dataset,
                            "model_size": model_size,
                            "trend_value": 0.75
                            + step * 0.001
                            + hash(f"{metric}_{dataset}_{model_size}") % 3 * 0.01,
                        }
                    )
    return pd.DataFrame(data)


class TestStyleCoordinatorModule:
    def test_dimension_value_registration(self):
        coordinator = FacetStyleCoordinator()

        coordinator.register_dimension_values("model", ["7B", "13B"])
        coordinator.register_dimension_values("model", ["30B"])
        coordinator.register_dimension_values("model", ["7B"])

        assert "model" in coordinator._dimension_values
        assert coordinator._dimension_values["model"] == {"7B", "13B", "30B"}
        assert "model" in coordinator._style_assignments
        assert len(coordinator._style_assignments["model"]) == 3

    def test_style_assignment_consistency(self):
        coordinator = FacetStyleCoordinator()

        coordinator.register_dimension_values("model", ["7B", "13B", "30B"])

        styles1 = coordinator._style_assignments["model"]["7B"]
        styles2 = coordinator._style_assignments["model"]["7B"]

        assert styles1 == styles2

        assert "color" in styles1
        assert "marker" in styles1
        assert (
            styles1["color"] != coordinator._style_assignments["model"]["13B"]["color"]
        )

    def test_subplot_styles_no_dimension(self):
        coordinator = FacetStyleCoordinator()
        data = pd.DataFrame({"x": [1, 2], "y": [3, 4]})

        result = coordinator.get_subplot_styles(0, 0, None, data, alpha=0.5)
        assert result == {"alpha": 0.5}

    def test_subplot_styles_single_value(self):
        coordinator = FacetStyleCoordinator()
        coordinator.register_dimension_values("model", ["7B", "13B"])

        data = pd.DataFrame({"model": ["7B", "7B"], "x": [1, 2], "y": [3, 4]})
        result = coordinator.get_subplot_styles(0, 0, "model", data, alpha=0.5)

        assert "alpha" in result
        assert "color" in result
        assert "marker" in result
        expected_color = coordinator._style_assignments["model"]["7B"]["color"]
        assert result["color"] == expected_color

    def test_subplot_styles_multiple_values(self):
        coordinator = FacetStyleCoordinator()
        coordinator.register_dimension_values("model", ["7B", "13B"])

        data = pd.DataFrame({"model": ["7B", "13B"], "x": [1, 2], "y": [3, 4]})
        result = coordinator.get_subplot_styles(0, 0, "model", data, alpha=0.5)

        assert "alpha" in result
        # For multiple values, the current implementation just returns base_kwargs
        # Advanced color coordination for multiple values will be implemented in future iterations


class TestStyleCoordination:
    def test_single_call_consistency(self):
        data = create_test_data_with_consistent_dimension()

        with FigureManager(figure=FigureConfig(rows=2, cols=3)) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="scatter",
                rows="metric",
                cols="dataset",
                lines="model_size",
                x="step",
                y="value",
            )

            style_coordinator = fm._facet_style_coordinator
            assert style_coordinator is not None
            assert "model_size" in style_coordinator._style_assignments

            model_styles = style_coordinator._style_assignments["model_size"]
            assert "7B" in model_styles
            assert "13B" in model_styles

            color_7b = model_styles["7B"]["color"]
            color_13b = model_styles["13B"]["color"]
            assert color_7b != color_13b

    def test_layered_faceting_consistency(self):
        scatter_data = create_scatter_data()
        line_data = create_line_data()

        with FigureManager(figure=FigureConfig(rows=2, cols=2)) as fm:
            fm.plot_faceted(
                data=scatter_data,
                plot_type="scatter",
                rows="metric",
                cols="dataset",
                lines="model_size",
                x="step",
                y="value",
                alpha=0.6,
            )

            style_coordinator_after_first = fm._facet_style_coordinator
            first_layer_styles = style_coordinator_after_first._style_assignments[
                "model_size"
            ].copy()

            fm.plot_faceted(
                data=line_data,
                plot_type="line",
                rows="metric",
                cols="dataset",
                lines="model_size",
                x="step",
                y="trend_value",
                linewidth=2,
            )

            style_coordinator_after_second = fm._facet_style_coordinator
            second_layer_styles = style_coordinator_after_second._style_assignments[
                "model_size"
            ]

            assert style_coordinator_after_first is style_coordinator_after_second

            for model_size in ["7B", "13B", "30B"]:
                assert first_layer_styles[model_size] == second_layer_styles[model_size]

    def test_targeting_with_style_coordination(self):
        data = create_test_data_with_consistent_dimension()

        with FigureManager(figure=FigureConfig(rows=2, cols=3)) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="scatter",
                rows="metric",
                cols="dataset",
                lines="model_size",
                x="step",
                y="value",
            )

            base_styles = fm._facet_style_coordinator._style_assignments[
                "model_size"
            ].copy()

            fm.plot_faceted(
                data=data,
                plot_type="line",
                rows="metric",
                cols="dataset",
                lines="model_size",
                target_row=0,
                target_cols=[1, 2],
                x="step",
                y="value",
                linewidth=3,
            )

            overlay_styles = fm._facet_style_coordinator._style_assignments[
                "model_size"
            ]

            for model_size in ["7B", "13B"]:
                assert base_styles[model_size] == overlay_styles[model_size]


class TestAdvancedStyleCoordination:
    def test_complex_ml_dashboard_layered_styling(self):
        training_data = pd.DataFrame(
            {
                "step": list(range(0, 100, 10)) * 24,
                "metric": ["train_loss", "val_loss", "train_acc", "val_acc"] * 60,
                "model_size": ["7B", "13B", "30B", "65B"] * 60,
                "dataset": ["squad", "glue", "c4"] * 80,
                "value": [0.8 - i * 0.001 for i in range(240)],
            }
        )

        trend_data = training_data[training_data["step"] % 50 == 0].copy()
        trend_data["trend_value"] = trend_data["value"] * 0.95

        ci_data = training_data.copy()
        ci_data["ci_lower"] = ci_data["value"] * 0.9
        ci_data["ci_upper"] = ci_data["value"] * 1.1

        with FigureManager(figure=FigureConfig(rows=4, cols=3, figsize=(18, 10))) as fm:
            fm.plot_faceted(
                data=training_data,
                plot_type="scatter",
                rows="metric",
                cols="dataset",
                lines="model_size",
                x="step",
                y="value",
                alpha=0.4,
                s=20,
            )

            fm.plot_faceted(
                data=trend_data,
                plot_type="line",
                rows="metric",
                cols="dataset",
                lines="model_size",
                x="step",
                y="trend_value",
                linewidth=2,
            )

            # Use all data but target specific rows instead of filtering data
            fm.plot_faceted(
                data=ci_data,
                plot_type="scatter",
                rows="metric",
                cols="dataset",
                lines="model_size",
                target_rows=[2, 3],  # Target accuracy metrics (train_acc, val_acc)
                x="step",
                y="ci_lower",
                alpha=0.2,
            )

            style_coordinator = fm._facet_style_coordinator
            assert style_coordinator is not None
            assert "model_size" in style_coordinator._style_assignments

            model_styles = style_coordinator._style_assignments["model_size"]
            for model_size in ["7B", "13B", "30B", "65B"]:
                assert model_size in model_styles


class TestIntegrationWithExistingPlotters:
    def test_backward_compatibility_preserved(self):
        data = create_test_data_with_consistent_dimension()

        with FigureManager(figure=FigureConfig(rows=1, cols=1)) as fm:
            fm.plot("scatter", 0, 0, data, x="step", y="value")

            assert fm._facet_style_coordinator is None


class TestPerformance:
    def test_style_coordination_performance(self):
        large_data = pd.DataFrame(
            {
                "step": list(range(1000)) * 20,
                "metric": ["accuracy", "loss"] * 10000,
                "model": [f"model_{i}" for i in range(20)] * 1000,
                "value": [0.5 + i * 0.0001 for i in range(20000)],
            }
        )

        import time

        start = time.time()
        with FigureManager(figure=FigureConfig(rows=2, cols=1)) as fm:
            fm.plot_faceted(
                large_data,
                "scatter",
                rows="metric",
                ncols=1,
                lines="model",
                x="step",
                y="value",
            )
        coordinated_time = time.time() - start

        assert coordinated_time < 10.0  # Should complete within 10 seconds
