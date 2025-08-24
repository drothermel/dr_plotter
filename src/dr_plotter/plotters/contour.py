from typing import Any, Dict, List, Set

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from mpl_toolkits.axes_grid1 import make_axes_locatable

from dr_plotter import consts
from dr_plotter.theme import CONTOUR_THEME, BASE_COLORS, Theme
from dr_plotter.types import BasePlotterParamName, SubPlotterParamName, VisualChannel
from .base import BasePlotter


type Phase = str
type ComponentSchema = Dict[str, Set[str]]


class ContourPlotter(BasePlotter):
    plotter_name: str = "contour"
    plotter_params: List[str] = []
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Set[VisualChannel] = set()
    default_theme: Theme = CONTOUR_THEME

    component_schema: Dict[Phase, ComponentSchema] = {
        "plot": {
            "contour": {
                "levels",
                "cmap",
                "alpha",
                "linewidths",
            },
            "scatter": {
                "color",
                "s",
                "alpha",
            },
        }
    }

    def _plot_specific_data_prep(self) -> pd.DataFrame:
        gmm = GaussianMixture(n_components=3, random_state=0).fit(
            self.plot_data[[consts.X_COL_NAME, consts.Y_COL_NAME]]
        )
        x_min, x_max = (
            self.plot_data[consts.X_COL_NAME].min() - 1,
            self.plot_data[consts.X_COL_NAME].max() + 1,
        )
        y_min, y_max = (
            self.plot_data[consts.Y_COL_NAME].min() - 1,
            self.plot_data[consts.Y_COL_NAME].max() + 1,
        )
        xx, yy = np.meshgrid(
            np.linspace(x_min, x_max, 100), np.linspace(y_min, y_max, 100)
        )
        Z = -gmm.score_samples(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)

        # Store prepared data as instance attributes
        self.xx, self.yy, self.Z = xx, yy, Z
        return self.plot_data

    def _draw(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        contour_kwargs = {
            "levels": self._get_style("levels"),
            "cmap": self._get_style("cmap"),
        }
        # Add user contour kwargs (filter out scatter-specific ones)
        user_kwargs = kwargs.copy()
        for key in ["s", "scatter_size", "scatter_alpha"]:
            user_kwargs.pop(key, None)
        contour_kwargs.update(user_kwargs)

        scatter_kwargs = {
            "s": self._get_style("scatter_size"),
            "alpha": self._get_style("scatter_alpha"),
            "color": BASE_COLORS[0],
        }
        # Add user scatter kwargs
        if "s" in kwargs:
            scatter_kwargs["s"] = kwargs["s"]
        if "scatter_size" in kwargs:
            scatter_kwargs["s"] = kwargs["scatter_size"]
        if "scatter_alpha" in kwargs:
            scatter_kwargs["alpha"] = kwargs["scatter_alpha"]

        contour = ax.contour(self.xx, self.yy, self.Z, **contour_kwargs)

        # Use axes_grid1 for precise colorbar layout control
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)

        fig = ax.get_figure()
        cbar = fig.colorbar(contour, cax=cax)
        # Use custom colorbar label if provided, otherwise default to "Density"
        colorbar_label = self.kwargs.get("colorbar_label", "Density")
        cbar.set_label(colorbar_label)

        ax.scatter(data[consts.X_COL_NAME], data[consts.Y_COL_NAME], **scatter_kwargs)
