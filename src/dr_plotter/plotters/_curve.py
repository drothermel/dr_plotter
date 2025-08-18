import pandas as pd
import numpy as np
from .base import BasePlotter


class CurvePlotter(BasePlotter):
    """Plotter for training progression analysis."""

    def __init__(self, data: pd.DataFrame):
        """
        Initialize with a pandas DataFrame.

        Args:
            data: A pandas DataFrame.
        """
        super().__init__(data)

    def plot_curve(self, x_col: str, y_col: str, **kwargs):
        """Plot a single curve."""
        fig, ax = self._setup_figure()

        ax.plot(self.data[x_col], self.data[y_col], **kwargs)

        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"{y_col} vs {x_col}")
        return fig, ax

    def plot_curve_comparison(
        self, x_col: str, y_col: str, group_by: str, **kwargs
    ):
        """Plot multiple curves on the same axis for comparison."""
        fig, ax = self._setup_figure()

        groups = self.data[group_by].unique()
        colors = self.style.get_category_colors(len(groups))

        for i, group in enumerate(groups):
            group_data = self.data[self.data[group_by] == group]
            ax.plot(
                group_data[x_col],
                group_data[y_col],
                color=colors[i],
                label=group,
                **kwargs,
            )

        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"{y_col} vs {x_col} by {group_by}")
        ax.legend(fontsize=self.style.FONT_SIZES["legend"], bbox_to_anchor=(1.05, 1))
        return fig, ax
