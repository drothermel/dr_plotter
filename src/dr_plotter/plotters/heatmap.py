"""
Atomic plotter for heatmaps.
"""

import numpy as np
import matplotlib.pyplot as plt
from .base import BasePlotter
from ..theme import HEATMAP_THEME


class HeatmapPlotter(BasePlotter):
    """
    An atomic plotter for creating heatmaps.
    """

    def __init__(self, data, **kwargs):
        """
        Initialize the HeatmapPlotter.
        """
        super().__init__(data, **kwargs)
        self.x = None
        self.y = None
        self.theme = HEATMAP_THEME

    def render(self, ax):
        """
        Render the heatmap on the given axes.
        """
        plot_kwargs = {"cmap": self.theme.get("cmap")}
        plot_kwargs.update(self._filter_plot_kwargs())

        im = ax.imshow(self.data, **plot_kwargs)

        fig = ax.get_figure()
        fig.colorbar(im, ax=ax)

        ax.set_xticks(np.arange(len(self.data.columns)))
        ax.set_yticks(np.arange(len(self.data.index)))
        ax.set_xticklabels(self.data.columns)
        ax.set_yticklabels(self.data.index)

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
            for i in range(len(self.data.index)):
                for j in range(len(self.data.columns)):
                    ax.text(
                        j,
                        i,
                        f"{self.data.iloc[i, j]:.2f}",
                        ha="center",
                        va="center",
                        color="w",
                        fontsize=8,
                    )

        self._apply_styling(ax)
