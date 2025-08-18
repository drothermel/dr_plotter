import pandas as pd
from .plotters.comparison import ComparisonPlotter
from .plotters.feature import FeaturePlotter
from .plotters.metrics import MetricsPlotter
from .plotters.prediction import PredictionPlotter
from .plotters.curve import CurvePlotter


def scatter(data: pd.DataFrame, x_col: str, y_col: str, **kwargs):
    """Create a scatter plot."""
    plotter = PredictionPlotter(data)
    return plotter.plot_predicted_vs_actual_scatter(x_col, y_col, **kwargs)


def line(data: pd.DataFrame, x_col: str, y_col: str, **kwargs):
    """Create a line plot."""
    plotter = CurvePlotter(data)
    return plotter.plot_curve(x_col, y_col, **kwargs)


def bar(data: pd.DataFrame, x_col: str, y_col: str, **kwargs):
    """Create a bar plot."""
    plotter = MetricsPlotter(data)
    fig, ax = plotter._setup_figure()
    plotter._plot_metric(ax, x_col, y_col, plot_type="bar", **kwargs)
    return fig, ax


def hist(data: pd.DataFrame, x_col: str, **kwargs):
    """Create a histogram."""
    plotter = PredictionPlotter(data)
    fig, ax = plotter._setup_figure()
    ax.hist(data[x_col], **kwargs)
    ax.set_xlabel(x_col)
    ax.set_ylabel("Frequency")
    ax.set_title(f"Distribution of {x_col}")
    return fig, ax
