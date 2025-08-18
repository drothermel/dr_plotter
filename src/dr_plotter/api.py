"""
High-level API for creating plots.
"""

import matplotlib.pyplot as plt
import pandas as pd

from .plotters.scatter import ScatterPlotter
from .plotters.line import LinePlotter
from .plotters.bar import BarPlotter
from .plotters.histogram import HistogramPlotter


def scatter(data: pd.DataFrame, x: str, y: str, ax=None, **kwargs):
    """
    Create a scatter plot.

    Args:
        data: A pandas DataFrame.
        x: The column for the x-axis.
        y: The column for the y-axis.
        ax: A matplotlib Axes object to plot on. If None, a new figure and axes are created.
        **kwargs: Styling options for the scatter plot.

    Returns:
        A tuple of (figure, axes).
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()

    plotter = ScatterPlotter(data=data, x=x, y=y, **kwargs)
    plotter.render(ax)

    return fig, ax


def line(data: pd.DataFrame, x: str, y: str, ax=None, **kwargs):
    """
    Create a line plot.

    Args:
        data: A pandas DataFrame.
        x: The column for the x-axis.
        y: The column for the y-axis.
        ax: A matplotlib Axes object to plot on. If None, a new figure and axes are created.
        **kwargs: Styling options for the line plot.

    Returns:
        A tuple of (figure, axes).
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()

    plotter = LinePlotter(data=data, x=x, y=y, **kwargs)
    plotter.render(ax)

    return fig, ax


def bar(data: pd.DataFrame, x: str, y: str, ax=None, **kwargs):
    """
    Create a bar plot.

    Args:
        data: A pandas DataFrame.
        x: The column for the x-axis (categories).
        y: The column for the y-axis (values).
        ax: A matplotlib Axes object to plot on. If None, a new figure and axes are created.
        **kwargs: Styling options for the bar plot.

    Returns:
        A tuple of (figure, axes).
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()

    plotter = BarPlotter(data=data, x=x, y=y, **kwargs)
    plotter.render(ax)

    return fig, ax


def hist(data: pd.DataFrame, x: str, ax=None, **kwargs):
    """
    Create a histogram.

    Args:
        data: A pandas DataFrame.
        x: The column for the data to be binned.
        ax: A matplotlib Axes object to plot on. If None, a new figure and axes are created.
        **kwargs: Styling options for the histogram.

    Returns:
        A tuple of (figure, axes).
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()

    plotter = HistogramPlotter(data=data, x=x, **kwargs)
    plotter.render(ax)

    return fig, ax
