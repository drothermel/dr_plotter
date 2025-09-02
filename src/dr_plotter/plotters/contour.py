from __future__ import annotations
from typing import Any

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from mpl_toolkits.axes_grid1 import make_axes_locatable

from dr_plotter import consts
from dr_plotter.theme import CONTOUR_THEME, BASE_COLORS, Theme
from dr_plotter.types import (
    BasePlotterParamName,
    SubPlotterParamName,
    VisualChannel,
    Phase,
    ComponentSchema,
)
from .base import BasePlotter
from dr_plotter.configs import GroupingConfig


class ContourPlotter(BasePlotter):
    plotter_name: str = "contour"
    plotter_params: list[str] = []
    param_mapping: dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: set[VisualChannel] = set()
    default_theme: Theme = CONTOUR_THEME
    supports_legend: bool = False
    supports_grouped: bool = False

    component_schema: dict[Phase, ComponentSchema] = {
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
        },
        "axes": {
            "title": {"text", "fontsize", "color"},
            "xlabel": {"text", "fontsize", "color"},
            "ylabel": {"text", "fontsize", "color"},
            "grid": {"visible", "alpha", "color", "linestyle"},
            "colorbar": {"label", "fontsize", "color", "size", "pad"},
        },
    }

    def __init__(
        self,
        data: pd.DataFrame,
        grouping_cfg: GroupingConfig,
        theme: Theme | None = None,
        figure_manager: Any | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(data, grouping_cfg, theme, figure_manager, **kwargs)
        self.styler.register_post_processor(
            self.plotter_name, "colorbar", self._style_colorbar
        )

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

        self.xx, self.yy, self.Z = xx, yy, Z
        return self.plot_data

    def _draw(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        contour_kwargs = {
            "levels": self.styler.get_style("levels"),
            "cmap": self.styler.get_style("cmap"),
        }
        user_kwargs = kwargs.copy()
        for key in ["s", "scatter_size", "scatter_alpha"]:
            user_kwargs.pop(key, None)
        contour_kwargs.update(user_kwargs)

        scatter_kwargs = {
            "s": self.styler.get_style("scatter_size"),
            "alpha": self.styler.get_style("scatter_alpha"),
            "color": self.styler.get_style("scatter_color", BASE_COLORS[0]),
        }
        if "s" in kwargs:
            scatter_kwargs["s"] = kwargs["s"]
        if "scatter_size" in kwargs:
            scatter_kwargs["s"] = kwargs["scatter_size"]
        if "scatter_alpha" in kwargs:
            scatter_kwargs["alpha"] = kwargs["scatter_alpha"]

        contour = ax.contour(self.xx, self.yy, self.Z, **contour_kwargs)

        ax.scatter(data[consts.X_COL_NAME], data[consts.Y_COL_NAME], **scatter_kwargs)

        artists = {
            "colorbar": {
                "plot_object": contour,
                "ax": ax,
                "fig": ax.get_figure(),
            }
        }
        self.styler.apply_post_processing(self.plotter_name, artists)

        self._apply_styling(ax)

    def _style_colorbar(
        self, colorbar_info: dict[str, Any], styles: dict[str, Any]
    ) -> None:
        plot_object = colorbar_info["plot_object"]
        ax = colorbar_info["ax"]
        fig = colorbar_info["fig"]

        divider = make_axes_locatable(ax)
        size = styles.get("size", "5%")
        pad = styles.get("pad", 0.1)
        cax = divider.append_axes("right", size=size, pad=pad)

        cbar = fig.colorbar(plot_object, cax=cax)

        label_text = styles.get("label", self.kwargs.get("colorbar_label", "Density"))
        if label_text:
            cbar.set_label(
                label_text,
                fontsize=styles.get(
                    "fontsize",
                    self.styler.get_style("label_fontsize"),
                ),
                color=styles.get("color", self.theme.get("label_color")),
            )
