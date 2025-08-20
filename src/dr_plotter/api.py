"""
High-level API for creating plots.
"""

import pandas as pd
from .figure import FigureManager


def scatter(
    data: pd.DataFrame,
    x: str,
    y,
    hue_by=None,
    size_by=None,
    marker_by=None,
    alpha_by=None,
    ax=None,
    **kwargs,
):
    """
    Create a scatter plot with multi-series support.

    Args:
        data: DataFrame containing the data
        x: Column name for x-axis
        y: Column name for y-axis, or list of column names for multiple metrics
        hue_by: Column name or consts.METRICS for color grouping
        size_by: Column name or consts.METRICS for marker size grouping
        marker_by: Column name or consts.METRICS for marker style grouping
        alpha_by: Column name or consts.METRICS for alpha/transparency grouping
        ax: Existing axes to plot on
        **kwargs: Additional styling parameters
    """
    # Fail fast on removed parameters
    if "style" in kwargs:
        raise TypeError(
            "scatter() got an unexpected keyword argument 'style'. Use 'marker' instead for scatter plots."
        )

    fm = FigureManager(external_ax=ax) if ax is not None else FigureManager()
    fm.scatter(0, 0, data, x, y, hue_by, size_by, marker_by, alpha_by, **kwargs)

    if ax is not None:
        return ax.get_figure(), ax
    else:
        return fm.fig, fm.get_axes(0, 0)


def line(
    data: pd.DataFrame,
    x: str,
    y,
    hue_by=None,
    style_by=None,
    size_by=None,
    marker_by=None,
    alpha_by=None,
    ax=None,
    **kwargs,
):
    """
    Create a line plot with multi-series support.

    Args:
        data: DataFrame containing the data
        x: Column name for x-axis
        y: Column name for y-axis, or list of column names for multiple metrics
        hue_by: Column name or consts.METRICS for color grouping
        style_by: Column name or consts.METRICS for linestyle grouping
        size_by: Column name or consts.METRICS for line width grouping
        marker_by: Column name or consts.METRICS for marker grouping
        alpha_by: Column name or consts.METRICS for alpha/transparency grouping
        ax: Existing axes to plot on
        **kwargs: Additional styling parameters
    """
    fm = FigureManager(external_ax=ax) if ax is not None else FigureManager()
    fm.line(0, 0, data, x, y, hue_by, style_by, size_by, marker_by, alpha_by, **kwargs)

    if ax is not None:
        return ax.get_figure(), ax
    else:
        return fm.fig, fm.get_axes(0, 0)


def bar(data: pd.DataFrame, x: str, y: str, hue_by: str = None, ax=None, **kwargs):
    """Create a bar plot with optional grouping."""
    fm = FigureManager(external_ax=ax) if ax is not None else FigureManager()
    fm.bar(0, 0, data, x, y, hue_by, **kwargs)

    if ax is not None:
        return ax.get_figure(), ax
    else:
        return fm.fig, fm.get_axes(0, 0)


def hist(data: pd.DataFrame, x: str, ax=None, **kwargs):
    """Create a histogram."""
    fm = FigureManager(external_ax=ax) if ax is not None else FigureManager()
    fm.hist(0, 0, data, x, **kwargs)

    if ax is not None:
        return ax.get_figure(), ax
    else:
        return fm.fig, fm.get_axes(0, 0)


def violin(
    data: pd.DataFrame,
    x: str = None,
    y: str = None,
    hue_by: str = None,
    ax=None,
    **kwargs,
):
    """Create a violin plot."""
    fm = FigureManager(external_ax=ax) if ax is not None else FigureManager()
    fm.violin(0, 0, data, x, y, hue_by, **kwargs)

    if ax is not None:
        return ax.get_figure(), ax
    else:
        return fm.fig, fm.get_axes(0, 0)


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
    fm = FigureManager(external_ax=ax) if ax is not None else FigureManager(constrained_layout=True)
    fm.heatmap(0, 0, data, x, y, values, **kwargs)

    if ax is not None:
        return ax.get_figure(), ax
    else:
        return fm.fig, fm.get_axes(0, 0)


def bump_plot(
    data: pd.DataFrame,
    time_col: str,
    category_col: str,
    value_col: str,
    ax=None,
    **kwargs,
):
    """Create a bump plot to visualize rankings over time."""
    fm = FigureManager(external_ax=ax) if ax is not None else FigureManager()
    fm.bump_plot(0, 0, data, time_col, category_col, value_col, **kwargs)

    if ax is not None:
        return ax.get_figure(), ax
    else:
        return fm.fig, fm.get_axes(0, 0)


def gmm_level_set(data: pd.DataFrame, x: str, y: str, ax=None, **kwargs):
    """Create a GMM level set plot."""
    fm = FigureManager(external_ax=ax) if ax is not None else FigureManager()
    fm.gmm_level_set(0, 0, data, x, y, **kwargs)

    if ax is not None:
        return ax.get_figure(), ax
    else:
        return fm.fig, fm.get_axes(0, 0)
