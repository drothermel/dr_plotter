import pytest
from typing import Optional

from dr_plotter.faceting_config import FacetingConfig


class TestFacetingConfigBasicFunctionality:
    def test_default_initialization(self) -> None:
        config = FacetingConfig()

        assert config.rows is None
        assert config.cols is None
        assert config.lines is None
        assert config.ncols is None
        assert config.nrows is None
        assert config.empty_subplot_strategy == "warn"
        assert config.color_wrap is False

    def test_initialization_with_all_parameters(self) -> None:
        x_labels = [["Label 1", "Label 2"], ["Label 3", "Label 4"]]
        xlim = [[(0, 10), (5, 15)], [(0, 20), (10, 25)]]

        config = FacetingConfig(
            rows="metric",
            cols="model",
            lines="dataset",
            ncols=3,
            nrows=2,
            row_order=["acc", "loss"],
            col_order=["gpt", "bert"],
            lines_order=["train", "val", "test"],
            target_row=0,
            target_col=1,
            target_rows=[0, 1],
            target_cols=[0, 2],
            x="step",
            y="value",
            x_labels=x_labels,
            y_labels=x_labels,
            xlim=xlim,
            ylim=xlim,
            subplot_titles="auto",
            title_template="{metric} - {model}",
            shared_x="row",
            shared_y=True,
            empty_subplot_strategy="error",
            color_wrap=True,
        )

        assert config.rows == "metric"
        assert config.cols == "model"
        assert config.lines == "dataset"
        assert config.ncols == 3
        assert config.nrows == 2
        assert config.row_order == ["acc", "loss"]
        assert config.col_order == ["gpt", "bert"]
        assert config.lines_order == ["train", "val", "test"]
        assert config.target_row == 0
        assert config.target_col == 1
        assert config.target_rows == [0, 1]
        assert config.target_cols == [0, 2]
        assert config.x == "step"
        assert config.y == "value"
        assert config.x_labels == x_labels
        assert config.y_labels == x_labels
        assert config.xlim == xlim
        assert config.ylim == xlim
        assert config.subplot_titles == "auto"
        assert config.title_template == "{metric} - {model}"
        assert config.shared_x == "row"
        assert config.shared_y is True
        assert config.empty_subplot_strategy == "error"
        assert config.color_wrap is True

    def test_parameter_modification(self) -> None:
        config = FacetingConfig()

        config.rows = "new_metric"
        config.ncols = 4
        config.empty_subplot_strategy = "silent"

        assert config.rows == "new_metric"
        assert config.ncols == 4
        assert config.empty_subplot_strategy == "silent"


class TestFacetingConfigValidation:
    def test_valid_configurations_pass(self) -> None:
        valid_configs = [
            FacetingConfig(rows="metric"),
            FacetingConfig(cols="model"),
            FacetingConfig(rows="metric", cols="model"),
            FacetingConfig(rows="metric", ncols=3),
            FacetingConfig(cols="model", nrows=2),
            FacetingConfig(rows="metric", cols="model", shared_x="all"),
            FacetingConfig(rows="metric", cols="model", shared_y="row"),
            FacetingConfig(rows="metric", cols="model", shared_x=True, shared_y=False),
            FacetingConfig(rows="metric", empty_subplot_strategy="warn"),
            FacetingConfig(rows="metric", empty_subplot_strategy="error"),
            FacetingConfig(rows="metric", empty_subplot_strategy="silent"),
        ]

        for config in valid_configs:
            config.validate()

    def test_requires_at_least_one_dimension(self) -> None:
        config = FacetingConfig()

        with pytest.raises(
            AssertionError, match="Must specify at least one of: rows, cols"
        ):
            config.validate()

    def test_cannot_specify_both_explicit_grid_and_wrap_layout(self) -> None:
        config = FacetingConfig(rows="metric", cols="model", ncols=3)

        expected_msg = "Cannot specify both explicit grid \\(rows\\+cols\\) and wrap layout \\(ncols/nrows\\)"
        with pytest.raises(AssertionError, match=expected_msg):
            config.validate()

    def test_cannot_specify_both_target_row_and_target_rows(self) -> None:
        config = FacetingConfig(rows="metric", target_row=0, target_rows=[0, 1])

        expected_msg = "Cannot specify both target_row and target_rows"
        with pytest.raises(AssertionError, match=expected_msg):
            config.validate()

    def test_cannot_specify_both_target_col_and_target_cols(self) -> None:
        config = FacetingConfig(cols="model", target_col=1, target_cols=[0, 1])

        expected_msg = "Cannot specify both target_col and target_cols"
        with pytest.raises(AssertionError, match=expected_msg):
            config.validate()

    def test_ncols_must_be_positive_integer(self) -> None:
        config = FacetingConfig(rows="metric", ncols=0)

        with pytest.raises(AssertionError, match="ncols must be a positive integer"):
            config.validate()

        config = FacetingConfig(rows="metric", ncols=-2)

        with pytest.raises(AssertionError, match="ncols must be a positive integer"):
            config.validate()

    def test_nrows_must_be_positive_integer(self) -> None:
        config = FacetingConfig(cols="model", nrows=0)

        with pytest.raises(AssertionError, match="nrows must be a positive integer"):
            config.validate()

        config = FacetingConfig(cols="model", nrows=-1)

        with pytest.raises(AssertionError, match="nrows must be a positive integer"):
            config.validate()

    def test_shared_x_string_validation(self) -> None:
        config = FacetingConfig(rows="metric", shared_x="invalid")

        expected_msg = "shared_x string must be one of 'all', 'row', 'col'"
        with pytest.raises(AssertionError, match=expected_msg):
            config.validate()

    def test_shared_x_type_validation(self) -> None:
        config = FacetingConfig(rows="metric", shared_x=123)

        expected_msg = "shared_x must be bool or string"
        with pytest.raises(AssertionError, match=expected_msg):
            config.validate()

    def test_shared_y_string_validation(self) -> None:
        config = FacetingConfig(rows="metric", shared_y="bad")

        expected_msg = "shared_y string must be one of 'all', 'row', 'col'"
        with pytest.raises(AssertionError, match=expected_msg):
            config.validate()

    def test_shared_y_type_validation(self) -> None:
        config = FacetingConfig(rows="metric", shared_y=[])

        expected_msg = "shared_y must be bool or string"
        with pytest.raises(AssertionError, match=expected_msg):
            config.validate()

    def test_empty_subplot_strategy_validation(self) -> None:
        config = FacetingConfig(rows="metric", empty_subplot_strategy="invalid")

        expected_msg = "empty_subplot_strategy must be one of 'warn', 'error', 'silent'"
        with pytest.raises(AssertionError, match=expected_msg):
            config.validate()

    def test_validation_error_messages_include_current_values(self) -> None:
        config = FacetingConfig(rows="metric_name", cols="model_type", ncols=5)

        with pytest.raises(AssertionError) as exc_info:
            config.validate()

        error_msg = str(exc_info.value)
        assert "rows='metric_name'" in error_msg
        assert "cols='model_type'" in error_msg
        assert "ncols=5" in error_msg

    def test_validation_ncols_type_error_shows_type_info(self) -> None:
        config = FacetingConfig(rows="metric", ncols="invalid")

        with pytest.raises(AssertionError) as exc_info:
            config.validate()

        error_msg = str(exc_info.value)
        assert "ncols=invalid" in error_msg
        assert "type: <class 'str'>" in error_msg


class TestFacetingConfigEdgeCases:
    def test_none_values_in_lists(self) -> None:
        config = FacetingConfig(
            rows="metric", row_order=None, target_rows=None, x_labels=None
        )

        config.validate()
        assert config.row_order is None
        assert config.target_rows is None
        assert config.x_labels is None

    def test_empty_lists(self) -> None:
        config = FacetingConfig(
            rows="metric", row_order=[], target_rows=[], x_labels=[]
        )

        config.validate()
        assert config.row_order == []
        assert config.target_rows == []
        assert config.x_labels == []

    def test_complex_nested_list_structures(self) -> None:
        complex_labels = [
            [None, "Custom Label", None],
            ["Row 2 Col 1", None, "Row 2 Col 3"],
        ]
        complex_limits = [[None, (0.0, 1.0), None], [(10.5, 20.7), None, (-5.2, 15.8)]]

        config = FacetingConfig(
            rows="metric",
            cols="model",
            x_labels=complex_labels,
            y_labels=complex_labels,
            xlim=complex_limits,
            ylim=complex_limits,
        )

        config.validate()
        assert config.x_labels == complex_labels
        assert config.xlim == complex_limits

    def test_boundary_integer_values(self) -> None:
        config = FacetingConfig(rows="metric", ncols=1, target_row=0, target_col=0)

        config.validate()
        assert config.ncols == 1
        assert config.target_row == 0
        assert config.target_col == 0


class TestFacetingConfigIntegration:
    def test_import_from_main_package(self) -> None:
        from dr_plotter import FacetingConfig

        config = FacetingConfig(rows="metric")
        config.validate()
        assert config.rows == "metric"

    def test_import_from_module(self) -> None:
        from dr_plotter.faceting_config import FacetingConfig

        config = FacetingConfig(cols="model")
        config.validate()
        assert config.cols == "model"

    def test_type_hints_work_with_mypy(self) -> None:
        config: FacetingConfig = FacetingConfig(rows="metric")

        optional_config: Optional[FacetingConfig] = None
        optional_config = config

        assert optional_config is not None
        assert optional_config.rows == "metric"

    def test_configuration_serialization_compatibility(self) -> None:
        from dataclasses import asdict

        config = FacetingConfig(
            rows="metric",
            cols="model",
            shared_x="row",
            empty_subplot_strategy="silent",
        )

        config_dict = asdict(config)

        assert config_dict["rows"] == "metric"
        assert config_dict["cols"] == "model"
        assert config_dict["shared_x"] == "row"
        assert config_dict["empty_subplot_strategy"] == "silent"

        new_config = FacetingConfig(**config_dict)
        new_config.validate()

        assert new_config.rows == config.rows
        assert new_config.cols == config.cols


class TestFacetingConfigValidationCombinations:
    def test_multiple_validation_failures(self) -> None:
        config = FacetingConfig(
            target_row=0, target_rows=[0, 1], target_col=1, target_cols=[0, 1, 2]
        )

        with pytest.raises(AssertionError):
            config.validate()

    def test_all_valid_shared_axis_combinations(self) -> None:
        valid_shared_values = ["all", "row", "col", True, False, None]

        for shared_x in valid_shared_values:
            for shared_y in valid_shared_values:
                config = FacetingConfig(
                    rows="metric", shared_x=shared_x, shared_y=shared_y
                )
                config.validate()

    def test_all_valid_empty_subplot_strategies(self) -> None:
        strategies = ["warn", "error", "silent"]

        for strategy in strategies:
            config = FacetingConfig(rows="metric", empty_subplot_strategy=strategy)
            config.validate()
            assert config.empty_subplot_strategy == strategy

    def test_wrap_layout_combinations(self) -> None:
        valid_wrap_configs = [
            FacetingConfig(rows="metric", ncols=3),
            FacetingConfig(cols="model", nrows=2),
            FacetingConfig(rows="metric", ncols=1),
            FacetingConfig(cols="model", nrows=1),
        ]

        for config in valid_wrap_configs:
            config.validate()

    def test_explicit_grid_combinations(self) -> None:
        valid_grid_configs = [
            FacetingConfig(rows="metric", cols="model"),
            FacetingConfig(rows="metric", cols="model", lines="dataset"),
            FacetingConfig(rows="metric", cols="model", target_row=0),
            FacetingConfig(rows="metric", cols="model", target_rows=[0, 1]),
        ]

        for config in valid_grid_configs:
            config.validate()
