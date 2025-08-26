from typing import Any, Dict, Optional, Tuple

import matplotlib.pyplot as plt

from dr_plotter.cycle_config import CycleConfig
from dr_plotter.grouping_config import GroupingConfig
from dr_plotter.legend_manager import (
    LegendConfig,
    LegendEntry,
    LegendManager,
    LegendStrategy,
)
from dr_plotter.theme import BASE_THEME, Theme
from .plotters import BasePlotter


class FigureManager:
    def __init__(
        self,
        figure: Optional["FigureConfig"] = None,
        legend: Optional[LegendConfig] = None,
        theme: Optional[Any] = None,
        faceting: Optional["SubplotFacetingConfig"] = None,
    ) -> None:
        from dr_plotter.figure_config import (
            FigureConfig,
        )

        figure = figure or FigureConfig()
        legend = legend or LegendConfig()

        if theme and hasattr(theme, "legend_config") and theme.legend_config:
            legend = theme.legend_config

        figure.validate()
        legend.validate() if hasattr(legend, "validate") else None
        if faceting:
            faceting.validate()

        self._init_from_configs(figure, legend, theme, faceting)

    def _init_from_configs(
        self,
        figure: "FigureConfig",
        legend: Optional[LegendConfig],
        theme: Optional[Any] = None,
        faceting: Optional["SubplotFacetingConfig"] = None,
    ) -> None:
        figure.validate()

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

    @classmethod
    def _create_from_configs(
        cls,
        figure: "FigureConfig",
        legend: Optional[LegendConfig],
        theme: Optional[Any] = None,
        faceting: Optional["SubplotFacetingConfig"] = None,
    ) -> "FigureManager":
        instance = cls.__new__(cls)
        instance._init_from_configs(figure, legend, theme, faceting)
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

    def plot(
        self, plot_type: str, row: int, col: int, *args: Any, **kwargs: Any
    ) -> None:
        plotter_class = BasePlotter.get_plotter(plot_type)
        self._add_plot(plotter_class, args, row, col, **kwargs)
