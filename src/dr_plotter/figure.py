from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd

from dr_plotter.cycle_config import CycleConfig
from dr_plotter.faceting_config import FacetingConfig
from dr_plotter.figure_config import FigureConfig
from dr_plotter.grouping_config import GroupingConfig
from dr_plotter.legend_manager import (
    LegendConfig,
    LegendEntry,
    LegendManager,
    LegendStrategy,
)
from dr_plotter.theme import BASE_THEME, Theme
from dr_plotter.faceting import (
    compute_grid_dimensions,
    compute_grid_layout_metadata,
    resolve_target_positions,
    analyze_data_dimensions,
    prepare_subplot_data_subsets,
    validate_faceting_data_requirements,
    validate_nested_list_dimensions,
    FacetStyleCoordinator,
)
from .plotters import BasePlotter


class FigureManager:
    def __init__(
        self,
        figure: Optional["FigureConfig"] = None,
        legend: Optional[LegendConfig] = None,
        theme: Optional[Any] = None,
    ) -> None:
        figure = figure or FigureConfig()
        legend = legend or LegendConfig()

        if theme and hasattr(theme, "legend_config") and theme.legend_config:
            legend = theme.legend_config

        figure.validate()
        legend.validate() if hasattr(legend, "validate") else None

        self._init_from_configs(figure, legend, theme)

    def _init_from_configs(
        self,
        figure: "FigureConfig",
        legend: Optional[LegendConfig],
        theme: Optional[Any] = None,
    ) -> None:
        figure.validate()

        self.figure_config = figure
        self._setup_layout_configuration(figure)

        fig, axes, external_mode = self._create_figure_axes(
            figure.external_ax,
            figure.figure_kwargs,
            figure.subplot_kwargs,
            figure.figsize,
            figure.rows,
            figure.cols,
        )
        self.fig = fig
        self.figure = fig
        self.axes = axes
        self.external_mode = external_mode

        legend_manager = self._build_legend_system(legend, theme)
        self.legend_config = legend_manager.config
        self.legend_manager = legend_manager

        self._coordinate_styling(theme, figure.shared_styling)

        self._facet_grid_info: Optional[Dict[str, Any]] = None
        self._facet_style_coordinator: Optional[FacetStyleCoordinator] = None

    @classmethod
    def _create_from_configs(
        cls,
        figure: "FigureConfig",
        legend: Optional[LegendConfig],
        theme: Optional[Any] = None,
    ) -> "FigureManager":
        instance = cls.__new__(cls)
        instance._init_from_configs(figure, legend, theme)
        return instance

    def _create_figure_axes(
        self,
        external_ax: Optional[plt.Axes],
        figure_kwargs: Dict[str, Any],
        subplot_kwargs: Dict[str, Any],
        figsize: Tuple[int, int],
        rows: int,
        cols: int,
    ) -> Tuple[plt.Figure, plt.Axes, bool]:
        if external_ax is not None:
            return external_ax.get_figure(), external_ax, True

        combined_kwargs = {**figure_kwargs, **subplot_kwargs}
        if "figsize" not in combined_kwargs:
            combined_kwargs["figsize"] = figsize

        fig, axes = plt.subplots(
            rows, cols, constrained_layout=False, **combined_kwargs
        )
        return fig, axes, False

    def _setup_layout_configuration(self, figure: "FigureConfig") -> None:
        self._layout_rect = None
        self._layout_pad = figure.tight_layout_pad
        self.rows = figure.rows
        self.cols = figure.cols

    def _build_legend_system(
        self,
        legend_config: Optional[LegendConfig],
        theme: Optional[Theme],
    ) -> LegendManager:
        effective_config = (
            legend_config
            or (
                theme.legend_config
                if theme and hasattr(theme, "legend_config")
                else None
            )
            or LegendConfig()
        )

        return LegendManager(self, effective_config)

    def _coordinate_styling(
        self,
        theme: Optional[Theme],
        shared_styling: Optional[bool],
    ) -> None:
        self.shared_styling = shared_styling

        if self._should_use_shared_cycle_config():
            theme_for_cycle = theme or BASE_THEME
            self.shared_cycle_config = CycleConfig(theme_for_cycle)
        else:
            self.shared_cycle_config = None

    def _should_use_shared_cycle_config(self) -> bool:
        if self.shared_styling is not None:
            return self.shared_styling

        coordination_strategies = {
            LegendStrategy.GROUPED_BY_CHANNEL,
            LegendStrategy.FIGURE_BELOW,
        }
        return self.legend_config.strategy in coordination_strategies

    def __enter__(self) -> "FigureManager":
        return self

    def register_legend_entry(self, entry: LegendEntry) -> None:
        self.legend_manager.registry.add_entry(entry)

    def finalize_legends(self) -> None:
        self.legend_manager.finalize()

    def finalize_layout(self) -> None:
        self.finalize_legends()
        self._apply_axis_labels()

        needs_legend_space = (
            self.legend_config.strategy == LegendStrategy.GROUPED_BY_CHANNEL
            or self.legend_config.strategy == LegendStrategy.FIGURE_BELOW
        )

        if self._layout_rect is not None:
            self.fig.tight_layout(rect=self._layout_rect, pad=self._layout_pad)
        elif needs_legend_space:
            rect = [
                self.legend_config.layout_left_margin,
                self.legend_config.layout_bottom_margin,
                self.legend_config.layout_right_margin,
                self.legend_config.layout_top_margin,
            ]
            self.fig.tight_layout(rect=rect, pad=self._layout_pad)
        elif self.fig._suptitle is not None:
            self.fig.tight_layout(rect=[0, 0, 1, 0.95], pad=self._layout_pad)
        elif self._has_subplot_titles():
            self.fig.tight_layout(rect=[0, 0, 1, 0.95], pad=self._layout_pad)
        else:
            self.fig.tight_layout(pad=self._layout_pad)

    def _apply_axis_labels(self) -> None:
        if self.external_mode:
            return

        if self.figure_config.x_labels is not None:
            for row_idx, row_labels in enumerate(self.figure_config.x_labels):
                for col_idx, label in enumerate(row_labels):
                    ax = self.get_axes(row_idx, col_idx)
                    if label is not None:
                        ax.set_xlabel(label)
                    else:
                        ax.set_xlabel("")

        if self.figure_config.y_labels is not None:
            for row_idx, row_labels in enumerate(self.figure_config.y_labels):
                for col_idx, label in enumerate(row_labels):
                    ax = self.get_axes(row_idx, col_idx)
                    if label is not None:
                        ax.set_ylabel(label)
                    else:
                        ax.set_ylabel("")

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        self.finalize_layout()
        return False

    def _has_subplot_titles(self) -> bool:
        if hasattr(self.axes, "flat"):
            axes_to_check = self.axes.flat
        elif hasattr(self.axes, "__iter__") and not isinstance(self.axes, str):
            axes_to_check = self.axes
        else:
            axes_to_check = [self.axes]

        for ax in axes_to_check:
            if ax.get_title():
                return True
        return False

    def get_axes(
        self, row: Optional[int] = None, col: Optional[int] = None
    ) -> plt.Axes:
        if self.external_mode:
            return self.axes

        if not hasattr(self.axes, "__len__"):
            return self.axes
        if self.axes.ndim == 1:
            idx = col if col is not None else row
            return self.axes[idx]
        if row is not None and col is not None:
            return self.axes[row, col]
        elif row is not None:
            return self.axes[row, :]
        elif col is not None:
            return self.axes[:, col]
        return self.axes

    def _add_plot(
        self,
        plotter_class: type,
        plotter_args: tuple,
        row: int,
        col: int,
        **kwargs: Any,
    ) -> None:
        if self.external_mode:
            ax = self.axes
        else:
            ax = self.get_axes(row, col)

        kwargs["grouping_cfg"] = GroupingConfig()
        kwargs["grouping_cfg"].set_kwargs(kwargs)

        plotter = plotter_class(*plotter_args, figure_manager=self, **kwargs)
        plotter.render(ax)

    def _analyze_data_dimensions(
        self, data: pd.DataFrame, config: FacetingConfig
    ) -> Dict[str, List[str]]:
        return analyze_data_dimensions(data, config)

    def _compute_facet_grid(
        self, data: pd.DataFrame, config: FacetingConfig
    ) -> Tuple[int, int, Dict[str, Any]]:
        dimensions = self._analyze_data_dimensions(data, config)

        n_rows, n_cols = compute_grid_dimensions(data, config, dimensions)
        layout_metadata = compute_grid_layout_metadata(data, config, dimensions)

        return n_rows, n_cols, layout_metadata

    def _resolve_targeting(
        self, config: FacetingConfig, grid_rows: int, grid_cols: int
    ) -> List[Tuple[int, int]]:
        return resolve_target_positions(config, grid_rows, grid_cols)

    def _validate_facet_grid_against_existing(
        self, new_rows: int, new_cols: int
    ) -> None:
        if not self._has_existing_plots():
            return

        current_rows = self.rows
        current_cols = self.cols

        assert new_rows == current_rows and new_cols == current_cols, (
            f"Computed facet grid {new_rows}×{new_cols} conflicts with existing FigureManager grid {current_rows}×{current_cols}. "
            f"Cannot change grid dimensions when plots already exist."
        )

    def _set_facet_grid_info(self, grid_info: Dict[str, Any]) -> None:
        self._facet_grid_info = grid_info

    def _has_existing_plots(self) -> bool:
        if self.external_mode:
            ax = self.axes
            return bool(ax.get_children())

        if hasattr(self.axes, "flat"):
            axes_to_check = self.axes.flat
        elif hasattr(self.axes, "__iter__") and not isinstance(self.axes, str):
            axes_to_check = self.axes
        else:
            axes_to_check = [self.axes]

        for ax in axes_to_check:
            if ax.get_children():
                return True
        return False

    def _resolve_faceting_config(
        self, faceting: Optional[FacetingConfig], **kwargs
    ) -> FacetingConfig:
        faceting_params = {}

        faceting_param_names = {
            "rows",
            "cols",
            "lines",
            "ncols",
            "nrows",
            "target_row",
            "target_col",
            "target_rows",
            "target_cols",
            "row_order",
            "col_order",
            "lines_order",
            "x",
            "y",
            "x_labels",
            "y_labels",
            "xlim",
            "ylim",
            "subplot_titles",
            "title_template",
            "shared_x",
            "shared_y",
            "empty_subplot_strategy",
            "color_wrap",
        }

        for param_name in faceting_param_names:
            if param_name in kwargs:
                faceting_params[param_name] = kwargs[param_name]

        if faceting is None:
            return FacetingConfig(**faceting_params)

        config_dict = {k: v for k, v in faceting.__dict__.items()}
        for key, value in faceting_params.items():
            if value is not None:
                config_dict[key] = value

        has_rows = config_dict.get("rows") is not None
        has_cols = config_dict.get("cols") is not None
        has_ncols = config_dict.get("ncols") is not None
        has_nrows = config_dict.get("nrows") is not None

        if has_rows and has_cols and (has_ncols or has_nrows):
            config_dict["ncols"] = None
            config_dict["nrows"] = None

        return FacetingConfig(**config_dict)

    def plot_faceted(
        self,
        data: pd.DataFrame,
        plot_type: str,
        faceting: Optional[FacetingConfig] = None,
        **kwargs,
    ) -> None:
        config = None
        try:
            if data.empty:
                assert False, (
                    "Cannot create faceted plot with empty DataFrame. "
                    "Please provide data with at least one row."
                )

            config = self._resolve_faceting_config(faceting, **kwargs)

            if not config.rows and not config.cols:
                self.plot(
                    plot_type,
                    0,
                    0,
                    data,
                    x=config.x,
                    y=config.y,
                    hue_by=config.lines,
                    **kwargs,
                )
                return

            if len(data) < 1000:
                return self._plot_faceted_standard_pipeline(
                    data, plot_type, config, **kwargs
                )

            return self._plot_faceted_optimized_pipeline(
                data, plot_type, config, **kwargs
            )

        except Exception as error:
            self._handle_faceting_errors_gracefully(error, data, config)

    def _plot_faceted_standard_pipeline(
        self, data: pd.DataFrame, plot_type: str, config: FacetingConfig, **kwargs
    ) -> None:
        valid_plot_types = ["line", "scatter", "bar", "fill_between", "heatmap"]
        if plot_type not in valid_plot_types:
            assert False, (
                f"Unsupported plot type: '{plot_type}'\n"
                f"Supported types: {valid_plot_types}\n"
                f"Note: All standard dr_plotter plot types should work with faceting."
            )

        self._validate_faceting_inputs(data, config)

        try:
            grid_rows, grid_cols, layout_metadata = self._compute_facet_grid(
                data, config
            )
        except Exception as e:
            assert False, (
                f"Failed to compute faceting grid: {str(e)}\n"
                f"Data shape: {data.shape}\n"
                f"Faceting config: rows='{config.rows}', cols='{config.cols}', "
                f"ncols={config.ncols}, nrows={config.nrows}\n"
                f"Check that your data contains the specified dimension columns."
            )

        self._validate_facet_grid_against_existing(grid_rows, grid_cols)

        if config.x_labels is not None:
            try:
                validate_nested_list_dimensions(
                    config.x_labels, grid_rows, grid_cols, "x_labels"
                )
            except AssertionError as e:
                assert False, (
                    f"x_labels configuration error: {str(e)}\n"
                    f"Computed grid: {grid_rows} rows × {grid_cols} cols\n"
                    f"x_labels shape: {len(config.x_labels)} rows × {len(config.x_labels[0]) if config.x_labels else 0} cols\n"
                    f"Tip: x_labels must match the computed grid dimensions."
                )

        if config.y_labels is not None:
            try:
                validate_nested_list_dimensions(
                    config.y_labels, grid_rows, grid_cols, "y_labels"
                )
            except AssertionError as e:
                assert False, (
                    f"y_labels configuration error: {str(e)}\n"
                    f"Computed grid: {grid_rows} rows × {grid_cols} cols\n"
                    f"y_labels shape: {len(config.y_labels)} rows × {len(config.y_labels[0]) if config.y_labels else 0} cols\n"
                    f"Tip: y_labels must match the computed grid dimensions."
                )

        if config.xlim is not None:
            try:
                validate_nested_list_dimensions(
                    config.xlim, grid_rows, grid_cols, "xlim"
                )
            except AssertionError as e:
                assert False, (
                    f"xlim configuration error: {str(e)}\n"
                    f"Computed grid: {grid_rows} rows × {grid_cols} cols\n"
                    f"Tip: xlim must match the computed grid dimensions."
                )

        if config.ylim is not None:
            try:
                validate_nested_list_dimensions(
                    config.ylim, grid_rows, grid_cols, "ylim"
                )
            except AssertionError as e:
                assert False, (
                    f"ylim configuration error: {str(e)}\n"
                    f"Computed grid: {grid_rows} rows × {grid_cols} cols\n"
                    f"Tip: ylim must match the computed grid dimensions."
                )

        target_positions = self._resolve_targeting(config, grid_rows, grid_cols)

        data_subsets = self._prepare_facet_data(
            data, config, layout_metadata, target_positions
        )

        from dr_plotter.faceting.data_preparation import handle_empty_subplots

        data_subsets = handle_empty_subplots(
            data_subsets, config.empty_subplot_strategy
        )

        style_coordinator = self._get_or_create_style_coordinator()
        if config.lines is not None:
            dimension_analysis = analyze_data_dimensions(data, config)
            lines_values = dimension_analysis.get("lines", [])
            style_coordinator.register_dimension_values(config.lines, lines_values)

        plot_kwargs = {
            k: v for k, v in kwargs.items() if not hasattr(FacetingConfig, k)
        }
        self._execute_faceted_plotting(
            data_subsets,
            target_positions,
            config,
            plot_type,
            style_coordinator,
            **plot_kwargs,
        )

        self._store_faceting_state(
            config, layout_metadata, grid_rows, grid_cols, data_subsets
        )

        if config.lines and hasattr(self, "legend_manager") and self.legend_manager:
            self._coordinate_faceted_legends(config, data)

    def _plot_faceted_optimized_pipeline(
        self, data: pd.DataFrame, plot_type: str, config: FacetingConfig, **kwargs
    ) -> None:
        self._validate_faceting_inputs(data, config)

        grid_info = self._compute_facet_grid_optimized(data, config)
        grid_rows, grid_cols = grid_info[0], grid_info[1]
        layout_metadata = grid_info[2]

        target_positions = self._resolve_targeting(config, grid_rows, grid_cols)
        data_subsets = self._prepare_facet_data(
            data, config, layout_metadata, target_positions
        )

        from dr_plotter.faceting.data_preparation import handle_empty_subplots

        data_subsets = handle_empty_subplots(
            data_subsets, config.empty_subplot_strategy
        )

        style_coordinator = self._get_or_create_style_coordinator()
        if config.lines is not None:
            dimension_analysis = analyze_data_dimensions(data, config)
            lines_values = dimension_analysis.get("lines", [])
            style_coordinator.register_dimension_values(config.lines, lines_values)

        plot_kwargs = {
            k: v for k, v in kwargs.items() if not hasattr(FacetingConfig, k)
        }
        self._execute_faceted_plotting(
            data_subsets,
            target_positions,
            config,
            plot_type,
            style_coordinator,
            **plot_kwargs,
        )

        self._store_faceting_state(
            config, layout_metadata, grid_rows, grid_cols, data_subsets
        )

    def _compute_facet_grid_optimized(
        self, data: pd.DataFrame, config: FacetingConfig
    ) -> Tuple[int, int, Dict[str, Any]]:
        return self._compute_facet_grid(data, config)

    def _validate_faceting_inputs(
        self, data: pd.DataFrame, config: FacetingConfig
    ) -> None:
        from dr_plotter.faceting.validation import (
            validate_common_mistakes,
            validate_subplot_data_coverage,
        )

        validate_faceting_data_requirements(data, config)
        config.validate()

        assert config.rows is not None or config.cols is not None, (
            "Must specify at least one of: rows, cols"
        )

        if config.x is None:
            assert False, "x parameter is required for plotting"
        if config.y is None:
            assert False, "y parameter is required for plotting"

        validate_common_mistakes(config, data)
        validate_subplot_data_coverage(data, config)
        self._validate_faceting_compatibility_with_existing_features(config)

    def _prepare_facet_data(
        self,
        data: pd.DataFrame,
        config: FacetingConfig,
        layout_metadata: Dict[str, Any],
        target_positions: List[Tuple[int, int]],
    ) -> Dict[Tuple[int, int], pd.DataFrame]:
        row_values = layout_metadata["row_values"]
        col_values = layout_metadata["col_values"]
        grid_type = layout_metadata["grid_type"]
        fill_order = layout_metadata.get("fill_order")

        return prepare_subplot_data_subsets(
            data,
            row_values,
            col_values,
            config.rows,
            config.cols,
            grid_type,
            fill_order,
            target_positions,
        )

    def _execute_faceted_plotting(
        self,
        data_subsets: Dict[Tuple[int, int], pd.DataFrame],
        target_positions: List[Tuple[int, int]],
        config: FacetingConfig,
        plot_type: str,
        style_coordinator: FacetStyleCoordinator,
        **plot_kwargs,
    ) -> None:
        for row_idx, col_idx in target_positions:
            if (row_idx, col_idx) not in data_subsets:
                continue

            subset_data = data_subsets[(row_idx, col_idx)]
            if subset_data.empty:
                continue

            plot_params = plot_kwargs.copy()
            plot_params["x"] = config.x
            plot_params["y"] = config.y

            if config.lines is not None:
                plot_params["hue_by"] = config.lines

            coordinated_styles = style_coordinator.get_subplot_styles(
                row_idx, col_idx, config.lines, subset_data, **plot_params
            )

            self._apply_subplot_configuration(row_idx, col_idx, config)
            self.plot(plot_type, row_idx, col_idx, subset_data, **coordinated_styles)

    def _apply_subplot_configuration(
        self, row: int, col: int, config: FacetingConfig
    ) -> None:
        if (
            config.x_labels is not None
            and len(config.x_labels) > row
            and len(config.x_labels[row]) > col
        ):
            label = config.x_labels[row][col]
            if label is not None:
                ax = self.fig.axes[row * self.figure_config.cols + col]
                ax.set_xlabel(label)

        if (
            config.y_labels is not None
            and len(config.y_labels) > row
            and len(config.y_labels[row]) > col
        ):
            label = config.y_labels[row][col]
            if label is not None:
                ax = self.fig.axes[row * self.figure_config.cols + col]
                ax.set_ylabel(label)

        if (
            config.xlim is not None
            and len(config.xlim) > row
            and len(config.xlim[row]) > col
        ):
            limits = config.xlim[row][col]
            if limits is not None:
                ax = self.fig.axes[row * self.figure_config.cols + col]
                ax.set_xlim(limits)

        if (
            config.ylim is not None
            and len(config.ylim) > row
            and len(config.ylim[row]) > col
        ):
            limits = config.ylim[row][col]
            if limits is not None:
                ax = self.fig.axes[row * self.figure_config.cols + col]
                ax.set_ylim(limits)

    def _store_faceting_state(
        self,
        config: FacetingConfig,
        layout_metadata: Dict[str, Any],
        grid_rows: int,
        grid_cols: int,
        data_subsets: Dict[Tuple[int, int], pd.DataFrame],
    ) -> None:
        enhanced_metadata = layout_metadata.copy()
        enhanced_metadata["n_rows"] = grid_rows
        enhanced_metadata["n_cols"] = grid_cols

        self._facet_grid_info = {
            "config": config,
            "layout_metadata": enhanced_metadata,
            "data_subsets": data_subsets,
            "last_plot_type": None,
            "subplot_styles": {},
        }

    def _handle_faceting_errors_gracefully(
        self, error: Exception, data: pd.DataFrame, config: Optional[FacetingConfig]
    ) -> None:
        error_context = {
            "data_shape": data.shape,
            "data_columns": data.columns.tolist(),
            "config_summary": {
                "rows": config.rows if config else None,
                "cols": config.cols if config else None,
                "lines": config.lines if config else None,
                "ncols": config.ncols if config else None,
                "nrows": config.nrows if config else None,
            }
            if config
            else None,
        }

        error_msg = f"Faceted plotting failed: {str(error)}\n"
        error_msg += "\nContext:\n"
        error_msg += f"• Data shape: {error_context['data_shape']}\n"
        error_msg += f"• Available columns: {error_context['data_columns'][:5]}..."
        if len(error_context["data_columns"]) > 5:
            error_msg += f" (and {len(error_context['data_columns']) - 5} more)\n"
        else:
            error_msg += "\n"
        error_msg += f"• Faceting config: {error_context['config_summary']}\n"

        if "Missing columns" in str(error) or "Missing required columns" in str(error):
            error_msg += "\nRecovery suggestions:\n"
            error_msg += "• Check that column names match exactly (case-sensitive)\n"
            error_msg += "• Use data.head() to inspect your data structure\n"
            error_msg += "• Verify data loading worked correctly\n"
        elif "grid" in str(error).lower():
            error_msg += "\nGrid-related recovery suggestions:\n"
            error_msg += (
                "• Ensure FigureManager grid size matches your data dimensions\n"
            )
            error_msg += "• Check if you need wrapped layout (ncols/nrows)\n"
            error_msg += "• Consider filtering data to reduce grid size\n"
        elif "empty" in str(error).lower():
            error_msg += "\nEmpty data recovery suggestions:\n"
            error_msg += "• Check data filtering - you may have filtered out all data\n"
            if config and config.rows and config.cols:
                error_msg += f"• Use data.groupby(['{config.rows}', '{config.cols}']).size() to check coverage\n"
            error_msg += "• Set empty_subplot_strategy='warn' to allow empty subplots\n"

        assert False, error_msg

    def _coordinate_faceted_legends(
        self, config: FacetingConfig, data: pd.DataFrame
    ) -> None:
        if config.lines and config.lines in data.columns:
            legend_values = sorted(data[config.lines].unique(), key=str)

            style_coordinator = self._get_or_create_style_coordinator()
            legend_entries = []

            for value in legend_values:
                if value in style_coordinator._style_assignments.get(config.lines, {}):
                    style = style_coordinator._style_assignments[config.lines][value]
                    legend_entry = {
                        "label": str(value),
                        "color": style.get("color", "#1f77b4"),
                        "marker": style.get("marker", "o"),
                        "linestyle": style.get("linestyle", "-"),
                    }
                    legend_entries.append(legend_entry)

            if legend_entries and hasattr(
                self.legend_manager, "add_coordinated_entries"
            ):
                self.legend_manager.add_coordinated_entries(legend_entries)

    def _validate_faceting_compatibility_with_existing_features(
        self, config: FacetingConfig
    ) -> None:
        if (
            hasattr(self, "external_mode")
            and self.external_mode
            and (config.rows or config.cols)
        ):
            print(
                "Warning: Faceting with external axes may not work as expected. "
                "Consider using FigureManager without external_ax for faceting."
            )

        if hasattr(self, "figure_config"):
            fig_rows, fig_cols = self.figure_config.rows, self.figure_config.cols

        if hasattr(self, "legend_manager") and self.legend_manager and config.lines:
            pass

    def _ensure_plot_kwargs_consistency(self, **kwargs) -> Dict[str, Any]:
        consistent_kwargs = {}

        for key, value in kwargs.items():
            if key in ["color", "c"]:
                consistent_kwargs["color"] = value
            elif key in ["marker", "m"]:
                consistent_kwargs["marker"] = value
            elif key in ["linestyle", "ls"]:
                consistent_kwargs["linestyle"] = value
            else:
                consistent_kwargs[key] = value

        return consistent_kwargs

    def _get_or_create_style_coordinator(self) -> FacetStyleCoordinator:
        if self._facet_style_coordinator is None:
            theme_info = None
            if hasattr(self, "_theme") and self._theme:
                theme_info = {
                    "color_cycle": getattr(self._theme, "color_cycle", None),
                    "marker_cycle": getattr(self._theme, "marker_cycle", None),
                    "line_style_cycle": getattr(self._theme, "line_style_cycle", None),
                }

            self._facet_style_coordinator = FacetStyleCoordinator(theme=theme_info)
        return self._facet_style_coordinator

    def plot(
        self, plot_type: str, row: int, col: int, *args: Any, **kwargs: Any
    ) -> None:
        is_faceted_plot = (
            hasattr(self, "_facet_grid_info") and self._facet_grid_info is not None
        )

        if is_faceted_plot:
            kwargs = self._apply_faceting_plot_enhancements(row, col, **kwargs)

        plotter_class = BasePlotter.get_plotter(plot_type)
        self._add_plot(plotter_class, args, row, col, **kwargs)

    def _apply_faceting_plot_enhancements(
        self, row: int, col: int, **kwargs
    ) -> Dict[str, Any]:
        if "_coordinated_colors" in kwargs:
            coordinated_colors = kwargs.pop("_coordinated_colors")
            coordinated_markers = kwargs.pop("_coordinated_markers", None)

            if len(coordinated_colors) == 1:
                kwargs["color"] = coordinated_colors[0]
            elif len(coordinated_colors) > 1:
                kwargs["palette"] = coordinated_colors

        return kwargs
