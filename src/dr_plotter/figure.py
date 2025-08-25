from typing import Any, List, Optional

import matplotlib.pyplot as plt

from dr_plotter.cycle_config import CycleConfig
from dr_plotter.grouping_config import GroupingConfig
from dr_plotter.legend_manager import (
    LegendConfig,
    LegendEntry,
    LegendManager,
    LegendStrategy,
)
from dr_plotter.theme import BASE_THEME
from .plotters import BasePlotter


class FigureManager:
    def __init__(
        self,
        rows: int = 1,
        cols: int = 1,
        external_ax: Optional[plt.Axes] = None,
        layout_rect: Optional[List[float]] = None,
        layout_pad: Optional[float] = 0.5,
        legend_config: Optional[LegendConfig] = None,
        legend_strategy: Optional[str] = None,
        legend_position: Optional[str] = None,
        legend_ncol: Optional[int] = None,
        legend_spacing: Optional[float] = None,
        plot_margin_bottom: Optional[float] = None,
        legend_y_offset: Optional[float] = None,
        legend_max_col: Optional[int] = None,
        theme: Optional[Any] = None,
        shared_styling: Optional[bool] = None,
        **fig_kwargs: Any,
    ) -> None:
        self._layout_rect = layout_rect
        self._layout_pad = layout_pad if layout_pad is not None else 0.5
        self.rows = rows
        self.cols = cols

        if external_ax is not None:
            self.fig = external_ax.get_figure()
            self.axes = external_ax
            self.external_mode = True
        else:
            self.fig, self.axes = plt.subplots(
                rows, cols, constrained_layout=False, **fig_kwargs
            )
            self.external_mode = False

        self.figure = self.fig

        self.shared_cycle_config: Optional[CycleConfig] = None

        base_config = None
        if legend_config:
            base_config = legend_config
        elif theme and hasattr(theme, "legend_config"):
            base_config = theme.legend_config

        self.legend_config = self._build_legend_config(
            base_config,
            legend_strategy,
            legend_position,
            legend_ncol,
            legend_spacing,
            plot_margin_bottom,
            legend_y_offset,
            legend_max_col,
        )

        self.shared_styling = shared_styling

        if self._should_use_shared_cycle_config():
            theme_for_cycle = theme if theme else BASE_THEME
            self.shared_cycle_config = CycleConfig(theme_for_cycle)
        else:
            self.shared_cycle_config = None

        self.legend_manager = LegendManager(self, self.legend_config)

    def _should_use_shared_cycle_config(self) -> bool:
        if self.shared_styling is not None:
            return self.shared_styling

        coordination_strategies = {
            LegendStrategy.GROUPED_BY_CHANNEL,
            LegendStrategy.FIGURE_BELOW,
        }
        return self.legend_config.strategy in coordination_strategies

    def _build_legend_config(
        self,
        base_config: Optional[LegendConfig],
        legend_strategy: Optional[str],
        legend_position: Optional[str],
        legend_ncol: Optional[int],
        legend_spacing: Optional[float],
        plot_margin_bottom: Optional[float],
        legend_y_offset: Optional[float],
        legend_max_col: Optional[int],
    ) -> LegendConfig:
        if base_config:
            config = LegendConfig(
                strategy=base_config.strategy,
                position=base_config.position,
                ncol=base_config.ncol,
                spacing=base_config.spacing,
                collect_strategy=base_config.collect_strategy,
                deduplication=base_config.deduplication,
                remove_axes_legends=base_config.remove_axes_legends,
            )
        else:
            config = LegendConfig()

        if legend_strategy:
            strategy_map = {
                "figure_below": LegendStrategy.FIGURE_BELOW,
                "split": LegendStrategy.GROUPED_BY_CHANNEL,
                "per_axes": LegendStrategy.PER_AXES,
                "none": LegendStrategy.NONE,
            }
            config.strategy = strategy_map.get(legend_strategy, LegendStrategy.PER_AXES)

        if legend_position:
            config.position = legend_position

        if legend_ncol is not None:
            config.ncol = legend_ncol

        if legend_spacing is not None:
            config.spacing = legend_spacing

        if plot_margin_bottom is not None:
            config.layout_bottom_margin = plot_margin_bottom

        if legend_y_offset is not None:
            config.bbox_y_offset = legend_y_offset

        if legend_max_col is not None:
            config.max_col = legend_max_col

        return config

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
