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
from .plotters.heatmap import HeatmapPlotter
from .plotters.bump import BumpPlotter
from .plotters.contour import ContourPlotter
from .plotters.grouped_bar import GroupedBarPlotter
from .utils import partition_kwargs

def _create_plot(plotter_class, plotter_args, ax=None, **kwargs):
    """Generic factory for creating and rendering a plot."""
    dr_plotter_kwargs, matplotlib_kwargs = partition_kwargs(kwargs)
    
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()

    plotter = plotter_class(*plotter_args, dr_plotter_kwargs, matplotlib_kwargs)
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

def violin(data: pd.DataFrame, x: str = None, y: str = None, hue: str = None, ax=None, **kwargs):
    """Create a violin plot."""
    return _create_plot(ViolinPlotter, (data, x, y, hue), ax, **kwargs)

def heatmap(data: pd.DataFrame, ax=None, **kwargs):
    """Create a heatmap."""
    return _create_plot(HeatmapPlotter, (data,), ax, **kwargs)

def bump_plot(data: pd.DataFrame, time_col: str, category_col: str, value_col: str, ax=None, **kwargs):
    """Create a bump plot to visualize rankings over time."""
    return _create_plot(BumpPlotter, (data, time_col, category_col, value_col), ax, **kwargs)

def gmm_level_set(data: pd.DataFrame, x: str, y: str, ax=None, **kwargs):
    """Create a GMM level set plot."""
    return _create_plot(ContourPlotter, (data, x, y), ax, **kwargs)

def grouped_bar(data: pd.DataFrame, x: str, y: str, hue: str, ax=None, **kwargs):
    """Create a grouped bar plot."""
    return _create_plot(GroupedBarPlotter, (data, x, y, hue), ax, **kwargs)