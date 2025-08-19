"""
Compound plotter for contour plots, specifically for GMM level sets.
"""

import numpy as np
from sklearn.mixture import GaussianMixture
from .base import BasePlotter
from dr_plotter.theme import CONTOUR_THEME
from .plot_data import ContourPlotData


class ContourPlotter(BasePlotter):
    """
    A compound plotter for creating contour plots of GMM level sets.
    """

    def __init__(self, data, x, y, **kwargs):
        """
        Initialize the ContourPlotter.
        """
        super().__init__(data, **kwargs)
        self.x = x
        self.y = y
        self.theme = CONTOUR_THEME

    def prepare_data(self):
        """Fit GMM and create a meshgrid for contour plotting."""
        # Create validated plot data first
        ContourPlotData(data=self.raw_data, x=self.x, y=self.y)

        # Fit GMM and create meshgrid
        gmm = GaussianMixture(n_components=3, random_state=0).fit(
            self.raw_data[[self.x, self.y]]
        )
        x_min, x_max = self.raw_data[self.x].min() - 1, self.raw_data[self.x].max() + 1
        y_min, y_max = self.raw_data[self.y].min() - 1, self.raw_data[self.y].max() + 1
        xx, yy = np.meshgrid(
            np.linspace(x_min, x_max, 100), np.linspace(y_min, y_max, 100)
        )
        Z = -gmm.score_samples(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)

        # Store prepared data
        self.xx, self.yy, self.Z = xx, yy, Z
        return self.raw_data

    def render(self, ax):
        """
        Render the GMM level set plot on the given axes.
        """
        self.prepare_data()

        contour_kwargs = {
            "levels": self.theme.get("levels"),
            "cmap": self.theme.get("cmap"),
        }
        contour_kwargs.update(self._filter_plot_kwargs())

        scatter_kwargs = {
            "s": self.theme.get("scatter_size"),
            "alpha": self.theme.get("scatter_alpha"),
            "color": self.theme.get("color_cycle").__next__(),
        }
        # Don't let contour kwargs leak into scatter
        filtered_scatter_kwargs = self._filter_plot_kwargs()
        for key in ["levels", "cmap"]:
            filtered_scatter_kwargs.pop(key, None)
        scatter_kwargs.update(filtered_scatter_kwargs)

        contour = ax.contour(self.xx, self.yy, self.Z, **contour_kwargs)
        fig = ax.get_figure()
        fig.colorbar(contour, ax=ax)

        ax.scatter(self.raw_data[self.x], self.raw_data[self.y], **scatter_kwargs)

        self._apply_styling(ax)
