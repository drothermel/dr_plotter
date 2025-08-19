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


def scatter(
    data: pd.DataFrame,
    x: str,
    y,
    hue=None,
    size=None,
    marker=None,
    alpha=None,
    ax=None,
    **kwargs,
):
    """
    Create a scatter plot with multi-series support.

    Args:
        data: DataFrame containing the data
        x: Column name for x-axis
        y: Column name for y-axis, or list of column names for multiple metrics
        hue: Column name or consts.METRICS for color grouping
        size: Column name or consts.METRICS for marker size grouping
        marker: Column name or consts.METRICS for marker style grouping
        alpha: Column name or consts.METRICS for alpha/transparency grouping
        ax: Existing axes to plot on
        **kwargs: Additional styling parameters
    """
    # Fail fast on removed parameters
    if "style" in kwargs:
        raise TypeError(
            "scatter() got an unexpected keyword argument 'style'. Use 'marker' instead for scatter plots."
        )

    return _create_plot(
        ScatterPlotter, (data, x, y, hue, size, marker, alpha), ax, **kwargs
    )


def line(
    data: pd.DataFrame,
    x: str,
    y,
    hue=None,
    style=None,
    size=None,
    marker=None,
    alpha=None,
    ax=None,
    **kwargs,
):
    """
    Create a line plot with multi-series support.

    Args:
        data: DataFrame containing the data
        x: Column name for x-axis
        y: Column name for y-axis, or list of column names for multiple metrics
        hue: Column name or consts.METRICS for color grouping
        style: Column name or consts.METRICS for linestyle grouping
        size: Column name or consts.METRICS for line width grouping
        marker: Column name or consts.METRICS for marker grouping
        alpha: Column name or consts.METRICS for alpha/transparency grouping
        ax: Existing axes to plot on
        **kwargs: Additional styling parameters
    """
    return _create_plot(
        LinePlotter, (data, x, y, hue, style, size, marker, alpha), ax, **kwargs
    )


def bar(data: pd.DataFrame, x: str, y: str, hue: str = None, ax=None, **kwargs):
    """Create a bar plot with optional grouping."""
    return _create_plot(BarPlotter, (data, x, y, hue), ax, **kwargs)


def hist(data: pd.DataFrame, x: str, ax=None, **kwargs):
    """Create a histogram."""
    return _create_plot(HistogramPlotter, (data, x), ax, **kwargs)


def violin(
    data: pd.DataFrame, x: str = None, y: str = None, hue: str = None, ax=None, **kwargs
):
    """Create a violin plot."""
    return _create_plot(ViolinPlotter, (data, x, y, hue), ax, **kwargs)


def heatmap(data: pd.DataFrame, x: str, y: str, values: str, ax=None, **kwargs):
    """
    Create a heatmap from tidy/long format data.

    Args:
        data: DataFrame containing the data in tidy/long format
        x: Column name for heatmap columns (x-axis)
        y: Column name for heatmap rows (y-axis)
        values: Column name for cell values
        ax: Optional matplotlib axes
        **kwargs: Additional styling parameters
    """
    return _create_plot(HeatmapPlotter, (data, x, y, values), ax, **kwargs)


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
