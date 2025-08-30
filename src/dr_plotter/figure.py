from typing import Any, Dict, Optional, Tuple, Union

import matplotlib.pyplot as plt
import pandas as pd

from dr_plotter.cycle_config import CycleConfig
from dr_plotter.plot_config import PlotConfig
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
from dr_plotter.positioning_calculator import (
    FigureDimensions,
    PositioningCalculator,
    PositioningConfig,
)
from dr_plotter.utils import get_axes_from_grid
from dr_plotter.theme import BASE_THEME, Theme
from dr_plotter.faceting.faceting_core import (
    prepare_faceted_subplots,
    plot_faceted_data,
    get_grid_dimensions,
    handle_empty_subplots,
)
from dr_plotter.faceting.style_coordination import FacetStyleCoordinator


class FigureManager:
    def __init__(
        self,
        config: Optional[PlotConfig] = None,
        figure: Optional["FigureConfig"] = None,
        legend: Optional[Union[str, LegendConfig]] = None,
        theme: Optional[Any] = None,
    ) -> None:
        if config is not None:
            figure, legend, theme = config._to_legacy_configs()

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
                calculator = PositioningCalculator(positioning_config)
                rect = calculator.calculate_layout_rect(figure_dimensions)
                if rect:
                    self.fig.tight_layout(rect=rect, pad=self._layout_pad)
                else:
                    self.fig.tight_layout(pad=self._layout_pad)
            else:
                if self.fig._suptitle is not None or self._has_subplot_titles():
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
        assert not data.empty, "Cannot create faceted plot with empty DataFrame"

        config = self._resolve_faceting_config(faceting, **kwargs)
        config.validate()

        assert config.x is not None, "x parameter is required for faceted plotting"
        assert config.y is not None, "y parameter is required for faceted plotting"
        assert config.rows or config.cols, "Must specify rows or cols for faceting"

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

        grid_shape = get_grid_dimensions(data, config)
        self._validate_grid_dimensions(grid_shape[0], grid_shape[1], config)

        data_subsets = prepare_faceted_subplots(data, config, grid_shape)
        data_subsets = handle_empty_subplots(
            data_subsets, config.empty_subplot_strategy
        )

        style_coordinator = self._get_or_create_style_coordinator()
        if config.lines:
            lines_values = sorted(data[config.lines].unique())
            style_coordinator.register_dimension_values(config.lines, lines_values)

        plot_kwargs = {
            k: v for k, v in kwargs.items() if not hasattr(FacetingConfig, k)
        }

        plot_faceted_data(
            self, data_subsets, plot_type, config, style_coordinator, **plot_kwargs
        )

    def _validate_grid_dimensions(
        self, computed_rows: int, computed_cols: int, config: FacetingConfig
    ) -> None:
        figure_rows, figure_cols = self.figure_config.rows, self.figure_config.cols

        if (computed_rows, computed_cols) != (figure_rows, figure_cols):
            assert False, (
                f"Grid dimension mismatch: FigureConfig({figure_rows}×{figure_cols}) "
                f"vs required({computed_rows}×{computed_cols}). "
                f"Fix: FigureConfig(rows={computed_rows}, cols={computed_cols})"
            )

    def _get_or_create_style_coordinator(self) -> FacetStyleCoordinator:
        if (
            not hasattr(self, "_facet_style_coordinator")
            or self._facet_style_coordinator is None
        ):
            theme_info = None
            if hasattr(self, "_theme") and self._theme:
                theme_info = {
                    "color_cycle": getattr(self._theme, "color_cycle", None),
                    "marker_cycle": getattr(self._theme, "marker_cycle", None),
                }
            self._facet_style_coordinator = FacetStyleCoordinator(theme=theme_info)
        return self._facet_style_coordinator
