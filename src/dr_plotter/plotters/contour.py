"""
Compound plotter for contour plots, specifically for GMM level sets.
"""

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from .base import BasePlotter

class ContourPlotter(BasePlotter):
    """
    A compound plotter for creating contour plots of GMM level sets.
    """

    def __init__(self, data, x, y, dr_plotter_kwargs, matplotlib_kwargs):
        """
        Initialize the ContourPlotter.

        Args:
            data: A pandas DataFrame.
            x: The column for the x-axis data points.
            y: The column for the y-axis data points.
            dr_plotter_kwargs: High-level styling options for dr_plotter.
            matplotlib_kwargs: Low-level kwargs to pass to matplotlib.
        """
        super().__init__(data, dr_plotter_kwargs, matplotlib_kwargs)
        self.x = x
        self.y = y

    def _prepare_data(self):
        """Fit GMM and create a meshgrid for contour plotting."""
        # Fit a Gaussian Mixture Model
        gmm = GaussianMixture(n_components=3, random_state=0).fit(self.data[[self.x, self.y]])

        # Create a meshgrid
        x_min, x_max = self.data[self.x].min() - 1, self.data[self.x].max() + 1
        y_min, y_max = self.data[self.y].min() - 1, self.data[self.y].max() + 1
        xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100),
                             np.linspace(y_min, y_max, 100))
        
        # Calculate the log probability density
        Z = -gmm.score_samples(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)

        return xx, yy, Z

    def render(self, ax):
        """
        Render the GMM level set plot on the given axes.

        Args:
            ax: A matplotlib Axes object.
        """
        xx, yy, Z = self._prepare_data()

        # Plot the contour and create a colorbar
        contour = ax.contour(xx, yy, Z, levels=14, **self.matplotlib_kwargs)
        fig = ax.get_figure()
        fig.colorbar(contour, ax=ax)

        # Overlay the original data points
        ax.scatter(self.data[self.x], self.data[self.y], s=10, alpha=0.5)

        self.style.apply_grid(ax)
        self._apply_styling(ax)
