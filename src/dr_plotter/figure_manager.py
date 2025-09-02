from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from dr_plotter.configs import (
    CycleConfig,
    FacetingConfig,
    FigureConfig,
    GroupingConfig,
    LegendConfig,
    PlotConfig,
)
from dr_plotter.faceting.faceting_core import (
    get_grid_dimensions,
    handle_empty_subplots,
    plot_faceted_data,
    prepare_faceted_subplots,
)
from dr_plotter.faceting.style_coordination import FacetStyleCoordinator
from dr_plotter.legend_manager import (
    LegendEntry,
    LegendManager,
)
from dr_plotter.plotters.base import BasePlotter
from dr_plotter.theme import Theme
from dr_plotter.utils import get_axes_from_grid


class FigureManager:
    def __init__(self, config: PlotConfig | None = None, **kwargs: Any) -> None:
        assert not any(k in kwargs for k in {"figure", "legend", "theme"})
        config = PlotConfig() if config is None else config
        figure_config, legend_config, theme = config._to_legacy_configs()

        assert theme is not None, "Theme is required"
        assert figure_config is not None, "FigureConfig is required"
        assert legend_config is not None, "LegendConfig is required"

        figure_config.validate()
        legend_config.validate()

        self._init_from_configs(figure_config, legend_config, theme)

    def _init_from_configs(
        self,
        figure: FigureConfig,
        legend: LegendConfig,
        theme: Theme,
    ) -> None:
        figure.validate()

        self.figure_config = figure
        self._layout_pad = figure.tight_layout_pad
        self.rows = figure.rows
        self.cols = figure.cols

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

        # This needs fixing
        legend_config = next(
            (c for c in [legend, theme.legend_config] if c is not None), LegendConfig()
        )
        self.legend_manager = LegendManager(self, legend_config)
        self.legend_config = self.legend_manager.config
        self._layout_rect = [
            self.legend_config.layout_left_margin,
            self.legend_config.layout_bottom_margin,
            self.legend_config.layout_right_margin,
            self.legend_config.layout_top_margin,
        ]

        self.shared_styling = figure.shared_styling
        self.shared_cycle_config = CycleConfig(theme) if self.shared_styling else None

        self._facet_grid_info: dict[str, Any] | None = None
        self._facet_style_coordinator: FacetStyleCoordinator | None = None

    def _create_figure_axes(
        self,
        external_ax: plt.Axes | None,
        figure_kwargs: dict[str, Any],
        subplot_kwargs: dict[str, Any],
        figsize: tuple[int, int],
        rows: int,
        cols: int,
    ) -> tuple[plt.Figure, plt.Axes, bool]:
        if external_ax is not None:
            return external_ax.get_figure(), external_ax, True

        combined_kwargs = {**figure_kwargs, **subplot_kwargs}
        if "figsize" not in combined_kwargs:
            combined_kwargs["figsize"] = figsize

        fig, axes = plt.subplots(
            rows, cols, constrained_layout=False, **combined_kwargs
        )
        return fig, axes, False

    def __enter__(self) -> FigureManager:
        return self

    def register_legend_entry(self, entry: LegendEntry) -> None:
        self.legend_manager.registry.add_entry(entry)

    def finalize_legends(self) -> None:
        self.legend_manager.finalize()

    def finalize_layout(self) -> None:
        self.finalize_legends()
        self._apply_axis_labels()
        rect = self._layout_rect if any(self._layout_rect) else None
        self.fig.tight_layout(rect=rect, pad=self._layout_pad)

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

        return any(ax.get_title() for ax in axes_to_check)

    def get_axes(self, row: int | None = None, col: int | None = None) -> plt.Axes:
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
        ax = self.axes if self.external_mode else self.get_axes(row, col)

        kwargs["grouping_cfg"] = GroupingConfig()
        kwargs["grouping_cfg"].set_kwargs(kwargs)

        plotter = plotter_class(*plotter_args, figure_manager=self, **kwargs)
        plotter.render(ax)

    def _resolve_faceting_config(
        self,
        faceting: FacetingConfig | None,
        **kwargs: Any,
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

        config_dict = dict(faceting.__dict__.items())
        config_dict.update({k: v for k, v in faceting_params.items() if v is not None})

        return FacetingConfig(**config_dict)

    def plot_faceted(
        self,
        data: pd.DataFrame,
        plot_type: str,
        faceting: FacetingConfig | None = None,
        **kwargs: Any,
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
        self._validate_grid_dimensions(grid_shape)
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

    def _validate_grid_dimensions(self, grid_shape: tuple[int, int]) -> None:
        computed_rows, computed_cols = grid_shape
        figure_rows, figure_cols = self.figure_config.rows, self.figure_config.cols

        if (computed_rows, computed_cols) != (figure_rows, figure_cols):
            assert False, (
                f"Grid dimension mismatch: "
                f"FigureConfig({figure_rows}×{figure_cols}) "
                f"vs required({computed_rows}×{computed_cols}). "
                f"Fix: "
                f"FigureConfig(rows={computed_rows}, cols={computed_cols})"
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

    def plot(
        self, plot_type: str, row: int, col: int, *args: Any, **kwargs: Any
    ) -> None:
        plotter_class = BasePlotter.get_plotter(plot_type)
        self._add_plot(plotter_class, args, row, col, **kwargs)
