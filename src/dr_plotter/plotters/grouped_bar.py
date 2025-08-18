"""
Compound plotter for grouped bar plots.
"""

import pandas as pd
import numpy as np
from .base import BasePlotter


class GroupedBarPlotter(BasePlotter):
    """
    A compound plotter for creating grouped bar plots.
    """

    def __init__(self, data, x, y, hue, dr_plotter_kwargs, matplotlib_kwargs):
        """
        Initialize the GroupedBarPlotter.

        Args:
            data: A pandas DataFrame in a "tidy" format.
            x: The column for the x-axis (main groups).
            y: The column for the y-axis (values).
            hue: The column for the sub-categories to group by.
            dr_plotter_kwargs: High-level styling options for dr_plotter.
            matplotlib_kwargs: Low-level kwargs to pass to matplotlib.
        """
        super().__init__(data, dr_plotter_kwargs, matplotlib_kwargs)
        self.x = x
        self.y = y
        self.hue = hue

    def render(self, ax):
        """
        Render the grouped bar plot on the given axes.

        Args:
            ax: A matplotlib Axes object.
        """
        # Pivot the data to get it into the right shape for plotting
        pivoted_data = self.data.pivot(index=self.x, columns=self.hue, values=self.y)
        
        # Let pandas do the heavy lifting for plotting the grouped bars
        pivoted_data.plot(kind='bar', ax=ax, width=0.8, **self.matplotlib_kwargs)

        # Apply standard styling
        self.style.apply_grid(ax)
        self._apply_styling(ax)
        ax.tick_params(axis='x', rotation=0)
