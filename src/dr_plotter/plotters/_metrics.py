import pandas as pd
import numpy as np
from .base import BasePlotter


class MetricsPlotter(BasePlotter):
    """
    Plotter for aggregated performance metrics.
    """

    def __init__(self, data: pd.DataFrame):
        """
        Initialize with a pandas DataFrame containing metrics.

        Args:
            data: A pandas DataFrame with one row per model/parameter.
        """
        super().__init__(data)

    def _plot_metric(
        self, ax, x_col: str, metric_col: str, plot_type: str = "bar", **kwargs
    ):
        """Generic method to plot any metric."""
        if plot_type == "bar":
            x_pos = np.arange(len(self.data))
            ax.bar(x_pos, self.data[metric_col], **kwargs)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(self.data[x_col], rotation=45, ha="right")
        elif plot_type == "line":
            ax.plot(self.data[x_col], self.data[metric_col], "o-", **kwargs)
        else:
            raise ValueError(f"Unknown plot type: {plot_type}")

        ax.set_xlabel(x_col)
        ax.set_ylabel(metric_col)
        ax.set_title(f"{metric_col} by {x_col}")

    def plot_rmse(self, ax, x_col: str, metric_col: str = "rmse", **kwargs):
        """Plot RMSE."""
        self._plot_metric(ax, x_col, metric_col, **kwargs)

    def plot_correlation(self, ax, x_col: str, metric_col: str = "correlation", **kwargs):
        """Plot correlation."""
        self._plot_metric(ax, x_col, metric_col, **kwargs)
