"""
High-level API for creating plots.
"""

import matplotlib.pyplot as plt
import pandas as pd

from .plotters.scatter import ScatterPlotter
from .plotters.line import LinePlotter
from .plotters.bar import BarPlotter
from .plotters.histogram import HistogramPlotter
from .plotters.violin import ViolinPlotter

DR_PLOTTER_STYLE_KEYS = ['title', 'xlabel', 'ylabel', 'legend']

def _partition_kwargs(kwargs):
    """Partitions kwargs into dr_plotter specific and matplotlib specific."""
    dr_plotter_kwargs = {}
    matplotlib_kwargs = {}
    for key, value in kwargs.items():
        if key in DR_PLOTTER_STYLE_KEYS:
            dr_plotter_kwargs[key] = value
        else:
            matplotlib_kwargs[key] = value
    return dr_plotter_kwargs, matplotlib_kwargs

def scatter(data: pd.DataFrame, x: str, y: str, ax=None, **kwargs):
    """Create a scatter plot."""
    dr_plotter_kwargs, matplotlib_kwargs = _partition_kwargs(kwargs)
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()

    plotter = ScatterPlotter(data, x, y, dr_plotter_kwargs, matplotlib_kwargs)
    plotter.render(ax)
    return fig, ax

def line(data: pd.DataFrame, x: str, y: str, ax=None, **kwargs):
    """Create a line plot."""
    dr_plotter_kwargs, matplotlib_kwargs = _partition_kwargs(kwargs)
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()

    plotter = LinePlotter(data, x, y, dr_plotter_kwargs, matplotlib_kwargs)
    plotter.render(ax)
    return fig, ax

def bar(data: pd.DataFrame, x: str, y: str, ax=None, **kwargs):
    """Create a bar plot."""
    dr_plotter_kwargs, matplotlib_kwargs = _partition_kwargs(kwargs)
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()

    plotter = BarPlotter(data, x, y, dr_plotter_kwargs, matplotlib_kwargs)
    plotter.render(ax)
    return fig, ax

def hist(data: pd.DataFrame, x: str, ax=None, **kwargs):
    """Create a histogram."""
    dr_plotter_kwargs, matplotlib_kwargs = _partition_kwargs(kwargs)
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()

    plotter = HistogramPlotter(data, x, dr_plotter_kwargs, matplotlib_kwargs)
    plotter.render(ax)
    return fig, ax

def violin(data: pd.DataFrame, x: str = None, y: str = None, ax=None, **kwargs):
    """Create a violin plot."""
    dr_plotter_kwargs, matplotlib_kwargs = _partition_kwargs(kwargs)
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()

    plotter = ViolinPlotter(data, x, y, dr_plotter_kwargs, matplotlib_kwargs)
    plotter.render(ax)
    return fig, ax