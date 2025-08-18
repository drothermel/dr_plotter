"""
Atomic plotter for heatmaps.
"""

import numpy as np
import matplotlib.pyplot as plt
from .base import BasePlotter


class HeatmapPlotter(BasePlotter):
    """
    An atomic plotter for creating heatmaps.
    """

    def __init__(self, data, dr_plotter_kwargs, matplotlib_kwargs):
        """
        Initialize the HeatmapPlotter.

        Args:
            data: A 2D pandas DataFrame.
            dr_plotter_kwargs: High-level styling options for dr_plotter.
            matplotlib_kwargs: Low-level kwargs to pass to matplotlib.
        """
        super().__init__(data, dr_plotter_kwargs, matplotlib_kwargs)
        self.x = None # Heatmaps use columns
        self.y = None # Heatmaps use index

    def render(self, ax):
        """
        Render the heatmap on the given axes.

        Args:
            ax: A matplotlib Axes object.
        """
        if 'cmap' not in self.matplotlib_kwargs:
            self.matplotlib_kwargs['cmap'] = 'viridis'

        im = ax.imshow(self.data, **self.matplotlib_kwargs)

        fig = ax.get_figure()
        fig.colorbar(im, ax=ax)

        ax.set_xticks(np.arange(len(self.data.columns)))
        ax.set_yticks(np.arange(len(self.data.index)))
        ax.set_xticklabels(self.data.columns)
        ax.set_yticklabels(self.data.index)

        # Handle xlabel position
        xlabel_pos = self.dr_plotter_kwargs.get('xlabel_pos', 'top')
        if xlabel_pos == 'top':
            ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)
            plt.setp(ax.get_xticklabels(), rotation=-30, ha="right", rotation_mode="anchor")
        else:
            ax.tick_params(top=False, bottom=True, labeltop=False, labelbottom=True)
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        ax.grid(False)

        if self.dr_plotter_kwargs.get('display_values', True):
            for i in range(len(self.data.index)):
                for j in range(len(self.data.columns)):
                    ax.text(j, i, f'{self.data.iloc[i, j]:.2f}', 
                            ha="center", va="center", color="w", fontsize=8)

        self._apply_styling(ax)
