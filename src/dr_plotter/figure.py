from typing import Any, Dict, List, Optional, Tuple, Union

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
    resolve_legend_config,
)
from dr_plotter.positioning_calculator import FigureDimensions
from dr_plotter.utils import get_axes_from_grid
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
        legend: Optional[Union[str, LegendConfig]] = None,
        theme: Optional[Any] = None,
    ) -> None:
        figure = figure or FigureConfig()

        if legend is None:
            legend = LegendConfig()
        else:
            legend = resolve_legend_config(legend)

        if theme and hasattr(theme, "legend_config") and theme.legend_config:
            legend = theme.legend_config

        figure.validate()
        legend.validate() if hasattr(legend, "validate") else None

        self._init_from_configs(figure, legend, theme)

    def _init_from_configs(
        self,
        figure: "FigureConfig",
        legend: Optional[Union[str, LegendConfig]],
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
        legend: Optional[Union[str, LegendConfig]],
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
        legend_config: Optional[Union[str, LegendConfig]],
        theme: Optional[Theme],
    ) -> LegendManager:
        if legend_config is not None:
            effective_config = resolve_legend_config(legend_config)
        elif theme and hasattr(theme, "legend_config") and theme.legend_config:
            effective_config = theme.legend_config
        else:
            effective_config = LegendConfig()

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
        else:
            figure_dimensions = FigureDimensions(
                width=self.fig.get_figwidth(),
                height=self.fig.get_figheight(),
                rows=self.rows,
                cols=self.cols,
                has_title=self.fig._suptitle is not None,
                has_subplot_titles=self._has_subplot_titles(),
            )

            positioning_config = self.legend_config.positioning_config
            if positioning_config:
                from dr_plotter.positioning_calculator import PositioningCalculator

                calculator = PositioningCalculator(positioning_config)
                rect = calculator.calculate_layout_rect(figure_dimensions)
                if rect:
                    self.fig.tight_layout(rect=rect, pad=self._layout_pad)
                else:
                    self.fig.tight_layout(pad=self._layout_pad)
            else:
                if self.fig._suptitle is not None or self._has_subplot_titles():
                    from dr_plotter.positioning_calculator import (
                        PositioningCalculator,
                        PositioningConfig,
                    )

                    default_config = PositioningConfig()
                    calculator = PositioningCalculator(default_config)
                    rect = calculator.calculate_layout_rect(figure_dimensions)
                    if rect:
                        self.fig.tight_layout(rect=rect, pad=self._layout_pad)
                    else:
                        self.fig.tight_layout(pad=self._layout_pad)
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

        return get_axes_from_grid(self.axes, row, col)

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

    def _validate_grid_dimensions(
        self, computed_rows: int, computed_cols: int, config: FacetingConfig
    ) -> None:
        figure_rows, figure_cols = self.figure_config.rows, self.figure_config.cols

        if (computed_rows, computed_cols) != (figure_rows, figure_cols):
            assert False, (
                f"Grid dimension mismatch:\n"
                f"  FigureConfig: {figure_rows}×{figure_cols} subplot grid\n"
                f"  Required by faceting data: {computed_rows}×{computed_cols}\n"
                f"  \n"
                f"Fix: Update FigureConfig(rows={computed_rows}, cols={computed_cols})\n"
                f"  \n"
                f"For axis sharing, use:\n"
                f"  subplot_kwargs={{'sharex': True, 'sharey': True}}"
            )

    def _resolve_faceting_config(
        self, faceting: Optional[FacetingConfig], **kwargs
    ) -> FacetingConfig:
        faceting_params = {}

        faceting_param_names = {
            "rows",
            "cols",
            "lines",
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

        return FacetingConfig(**config_dict)

    def plot_faceted(
        self,
        data: pd.DataFrame,
        plot_type: str,
        faceting: Optional[FacetingConfig] = None,
        **kwargs,
    ) -> None:
        assert not data.empty, (
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

        return self._plot_faceted_optimized_pipeline(data, plot_type, config, **kwargs)

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

        grid_rows, grid_cols, layout_metadata = self._compute_facet_grid(data, config)

        self._validate_grid_dimensions(grid_rows, grid_cols, config)

        self._validate_facet_grid_against_existing(grid_rows, grid_cols)

        if config.x_labels is not None:
            validate_nested_list_dimensions(
                config.x_labels, grid_rows, grid_cols, "x_labels"
            )

        if config.y_labels is not None:
            validate_nested_list_dimensions(
                config.y_labels, grid_rows, grid_cols, "y_labels"
            )

        if config.xlim is not None:
            validate_nested_list_dimensions(config.xlim, grid_rows, grid_cols, "xlim")

        if config.ylim is not None:
            validate_nested_list_dimensions(config.ylim, grid_rows, grid_cols, "ylim")

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

        self._validate_grid_dimensions(grid_rows, grid_cols, config)

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
            pass

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
            kwargs.pop("_coordinated_markers", None)

            if len(coordinated_colors) == 1:
                kwargs["color"] = coordinated_colors[0]
            elif len(coordinated_colors) > 1:
                kwargs["palette"] = coordinated_colors

        return kwargs
