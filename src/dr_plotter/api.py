"""
High-level API for creating plots.
"""

import matplotlib.pyplot as plt
import pandas as pd

from .plotters import (
    ScatterPlotter,
    LinePlotter,
    BarPlotter,
    HistogramPlotter,
    ViolinPlotter,
    HeatmapPlotter,
    BumpPlotter,
    ContourPlotter,
    GroupedBarPlotter,
)


def _create_plot(plotter_class, plotter_args, ax=None, **kwargs):
    """Generic factory for creating a figure and then rendering a plot."""
    if ax is None:
        fig, ax = plt.subplots(constrained_layout=True)
    else:
        fig = ax.get_figure()

    plotter = plotter_class(*plotter_args, **kwargs)
    plotter.render(ax)
    return fig, ax


def scatter(data: pd.DataFrame, x: str, y: str, ax=None, **kwargs):
    """Create a scatter plot."""
    return _create_plot(ScatterPlotter, (data, x, y), ax, **kwargs)


def line(data: pd.DataFrame, x: str, y: str, ax=None, **kwargs):
    """Create a line plot."""
    return _create_plot(LinePlotter, (data, x, y), ax, **kwargs)


def bar(data: pd.DataFrame, x: str, y: str, ax=None, **kwargs):
    """Create a bar plot."""
    return _create_plot(BarPlotter, (data, x, y), ax, **kwargs)


def hist(data: pd.DataFrame, x: str, ax=None, **kwargs):
    """Create a histogram."""
    return _create_plot(HistogramPlotter, (data, x), ax, **kwargs)


def violin(
    data: pd.DataFrame, x: str = None, y: str = None, hue: str = None, ax=None, **kwargs
):
    """Create a violin plot."""
    return _create_plot(ViolinPlotter, (data, x, y, hue), ax, **kwargs)


def heatmap(data: pd.DataFrame, ax=None, **kwargs):
    """Create a heatmap."""
    return _create_plot(HeatmapPlotter, (data,), ax, **kwargs)


def bump_plot(
    data: pd.DataFrame,
    time_col: str,
    category_col: str,
    value_col: str,
    ax=None,
    **kwargs,
):
    """Create a bump plot to visualize rankings over time."""
    return _create_plot(
        BumpPlotter, (data, time_col, category_col, value_col), ax, **kwargs
    )


def gmm_level_set(data: pd.DataFrame, x: str, y: str, ax=None, **kwargs):
    """Create a GMM level set plot."""
    return _create_plot(ContourPlotter, (data, x, y), ax, **kwargs)


def grouped_bar(data: pd.DataFrame, x: str, y: str, hue: str, ax=None, **kwargs):
    """Create a grouped bar plot."""
    return _create_plot(GroupedBarPlotter, (data, x, y, hue), ax, **kwargs)
