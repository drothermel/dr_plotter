import itertools
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt

from dr_plotter.grouping import GroupingConfig
from .plotters import BasePlotter


class FigureManager:
    def __init__(
        self,
        rows: int = 1,
        cols: int = 1,
        external_ax: Optional[plt.Axes] = None,
        layout_rect: Optional[List[float]] = None,
        layout_pad: Optional[float] = 0.5,
        **fig_kwargs: Any,
    ) -> None:
        self._layout_rect = layout_rect
        self._layout_pad = layout_pad if layout_pad is not None else 0.5

        if external_ax is not None:
            self.fig = external_ax.get_figure()
            self.axes = external_ax
            self.external_mode = True
        else:
            self.fig, self.axes = plt.subplots(
                rows, cols, constrained_layout=False, **fig_kwargs
            )
            self.external_mode = False

        self._shared_hue_styles: Dict[Any, Any] = {}
        self._shared_style_cycles: Optional[Dict[str, Any]] = None

    def __enter__(self) -> "FigureManager":
        return self

    def finalize_layout(self) -> None:
        if self._layout_rect is not None:
            self.fig.tight_layout(rect=self._layout_rect, pad=self._layout_pad)
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

    def _get_shared_style_cycles(self) -> Dict[str, Any]:
        if self._shared_style_cycles is None:
            from .theme import BASE_THEME

            self._shared_style_cycles = {
                "color": itertools.cycle(BASE_THEME.get("color_cycle")),
                "linestyle": itertools.cycle(BASE_THEME.get("linestyle_cycle")),
                "marker": itertools.cycle(BASE_THEME.get("marker_cycle")),
            }
        return self._shared_style_cycles

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

        kwargs["_figure_manager"] = self
        kwargs["_shared_hue_styles"] = self._shared_hue_styles
        kwargs["grouping_cfg"] = GroupingConfig()
        kwargs["grouping_cfg"].set_kwargs(kwargs)

        plotter = plotter_class(*plotter_args, **kwargs)
        plotter.render(ax)

    def plot(
        self, plot_type: str, row: int, col: int, *args: Any, **kwargs: Any
    ) -> None:
        plotter_class = BasePlotter.get_plotter(plot_type)
        self._add_plot(plotter_class, args, row, col, **kwargs)
