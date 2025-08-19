"""
Atomic plotter for heatmaps.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .base import BasePlotter
from dr_plotter.theme import HEATMAP_THEME


class HeatmapPlotter(BasePlotter):
    """
    An atomic plotter for creating heatmaps.
    """

    def __init__(self, data, x, y, values, **kwargs):
        """
        Initialize the HeatmapPlotter.
        
        Args:
            data: A pandas DataFrame in tidy/long format
            x: Column name for heatmap columns (x-axis)
            y: Column name for heatmap rows (y-axis)
            values: Column name for cell values
            **kwargs: Additional styling parameters
        """
        super().__init__(data, **kwargs)
        self.x = x
        self.y = y
        self.values = values
        self.theme = HEATMAP_THEME
        self._prepare_data()

    def _prepare_data(self):
        """
        Convert tidy/long format data to matrix format for heatmap visualization.
        """
        # Validate basic structure
        assert isinstance(self.data, pd.DataFrame), "Data must be a pandas DataFrame"
        assert not self.data.empty, "DataFrame cannot be empty"
        
        # Validate required columns exist
        required_cols = [self.x, self.y, self.values]
        for col in required_cols:
            assert col in self.data.columns, f"Column '{col}' not found in data"
        
        # Convert from tidy/long to matrix format using pivot
        self.plot_data = self.data.pivot(
            index=self.y,      # rows
            columns=self.x,    # columns
            values=self.values # cell values
        )
        
        # Handle any missing values by filling with 0
        self.plot_data = self.plot_data.fillna(0)

    def render(self, ax):
        """
        Render the heatmap on the given axes.
        """
        plot_kwargs = {"cmap": self.theme.get("cmap")}
        plot_kwargs.update(self._filter_plot_kwargs())

        im = ax.imshow(self.plot_data, **plot_kwargs)

        fig = ax.get_figure()
        fig.colorbar(im, ax=ax)

        ax.set_xticks(np.arange(len(self.plot_data.columns)))
        ax.set_yticks(np.arange(len(self.plot_data.index)))
        ax.set_xticklabels(self.plot_data.columns)
        ax.set_yticklabels(self.plot_data.index)

        xlabel_pos = self._get_style("xlabel_pos")
        if xlabel_pos == "top":
            ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)
            plt.setp(
                ax.get_xticklabels(), rotation=-30, ha="right", rotation_mode="anchor"
            )
        else:
            ax.tick_params(top=False, bottom=True, labeltop=False, labelbottom=True)
            plt.setp(
                ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor"
            )

        if self._get_style("display_values", True):
            for i in range(len(self.plot_data.index)):
                for j in range(len(self.plot_data.columns)):
                    ax.text(
                        j,
                        i,
                        f"{self.plot_data.iloc[i, j]:.2f}",
                        ha="center",
                        va="center",
                        color="w",
                        fontsize=8,
                    )

        self._apply_styling(ax)
