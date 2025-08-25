from typing import Any, List, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd

from dr_plotter.types import ColName

from .figure import FigureManager


def _fm_plot(
    plot_type: str,
    data: pd.DataFrame,
    x: Optional[ColName] = None,
    y: Optional[ColName | List[ColName]] = None,
    ax: Optional[plt.Axes] = None,
    **kwargs: Any,
) -> Tuple[plt.Figure, plt.Axes]:
    fm = FigureManager(external_ax=ax)
    fm.plot(plot_type, 0, 0, data, x=x, y=y, **kwargs)
    fm.finalize_layout()

    if ax is not None:
        return ax.get_figure(), ax
    return fm.fig, fm.get_axes(0, 0)


def scatter(
    data: pd.DataFrame,
    x: ColName,
    y: ColName,
    ax: Optional[plt.Axes] = None,
    **kwargs: Any,
) -> Tuple[plt.Figure, plt.Axes]:
    return _fm_plot("scatter", data, x=x, y=y, ax=ax, **kwargs)


def line(
    data: pd.DataFrame,
    x: ColName,
    y: ColName,
    ax: Optional[plt.Axes] = None,
    **kwargs: Any,
) -> Tuple[plt.Figure, plt.Axes]:
    return _fm_plot("line", data, x=x, y=y, ax=ax, **kwargs)


def bar(
    data: pd.DataFrame,
    x: ColName,
    y: ColName,
    ax: Optional[plt.Axes] = None,
    **kwargs: Any,
) -> Tuple[plt.Figure, plt.Axes]:
    return _fm_plot("bar", data, x=x, y=y, ax=ax, **kwargs)


def hist(
    data: pd.DataFrame,
    x: ColName,
    ax: Optional[plt.Axes] = None,
    **kwargs: Any,
) -> Tuple[plt.Figure, plt.Axes]:
    return _fm_plot("histogram", data, x=x, ax=ax, **kwargs)


def violin(
    data: pd.DataFrame,
    x: ColName,
    y: ColName,
    ax: Optional[plt.Axes] = None,
    **kwargs: Any,
) -> Tuple[plt.Figure, plt.Axes]:
    return _fm_plot("violin", data, x=x, y=y, ax=ax, **kwargs)


def heatmap(
    data: pd.DataFrame,
    x: ColName,
    y: ColName,
    values: ColName,
    ax: Optional[plt.Axes] = None,
    **kwargs: Any,
) -> Tuple[plt.Figure, plt.Axes]:
    return _fm_plot("heatmap", data, x=x, y=y, ax=ax, values=values, **kwargs)


def bump_plot(
    data: pd.DataFrame,
    time_col: ColName,
    category_col: ColName,
    value_col: ColName,
    ax: Optional[plt.Axes] = None,
    **kwargs: Any,
) -> Tuple[plt.Figure, plt.Axes]:
    return _fm_plot(
        "bump",
        data,
        time_col=time_col,
        category_col=category_col,
        value_col=value_col,
        ax=ax,
        **kwargs,
    )


def gmm_level_set(
    data: pd.DataFrame,
    x: ColName,
    y: ColName,
    ax: Optional[plt.Axes] = None,
    **kwargs: Any,
) -> Tuple[plt.Figure, plt.Axes]:
    return _fm_plot("contour", data, x=x, y=y, ax=ax, **kwargs)
