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
        # Use imshow for the heatmap
        im = ax.imshow(self.data, **self.matplotlib_kwargs)

        # Create colorbar
        fig = ax.get_figure()
        fig.colorbar(im, ax=ax)

        # Set ticks and labels from DataFrame
        ax.set_xticks(np.arange(len(self.data.columns)))
        ax.set_yticks(np.arange(len(self.data.index)))
        ax.set_xticklabels(self.data.columns)
        ax.set_yticklabels(self.data.index)

        # Rotate the tick labels and set their alignment.
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                 rotation_mode="anchor")

        self.style.apply_grid(ax)
        self._apply_styling(ax)
