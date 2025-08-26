from typing import Any, Dict, List, Set, Optional

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
from dr_plotter.grouping_config import GroupingConfig


class ContourPlotter(BasePlotter):
    plotter_name: str = "contour"
    plotter_params: List[str] = []
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Set[VisualChannel] = set()
    default_theme: Theme = CONTOUR_THEME
    supports_legend: bool = False
    supports_grouped: bool = False

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
        theme: Optional[Theme] = None,
        figure_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(data, grouping_cfg, theme, figure_manager, **kwargs)
        self.style_applicator.register_post_processor(
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

        # Store prepared data as instance attributes
        self.xx, self.yy, self.Z = xx, yy, Z
        return self.plot_data

    def _draw(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        contour_kwargs = {
            "levels": self.style_applicator.get_style_with_fallback("levels"),
            "cmap": self.style_applicator.get_style_with_fallback("cmap"),
        }
        # Add user contour kwargs (filter out scatter-specific ones)
        user_kwargs = kwargs.copy()
        for key in ["s", "scatter_size", "scatter_alpha"]:
            user_kwargs.pop(key, None)
        contour_kwargs.update(user_kwargs)

        scatter_kwargs = {
            "s": self.style_applicator.get_style_with_fallback("scatter_size"),
            "alpha": self.style_applicator.get_style_with_fallback("scatter_alpha"),
            "color": self.style_applicator.get_style_with_fallback(
                "scatter_color", BASE_COLORS[0]
            ),
        }
        # Add user scatter kwargs
        if "s" in kwargs:
            scatter_kwargs["s"] = kwargs["s"]
        if "scatter_size" in kwargs:
            scatter_kwargs["s"] = kwargs["scatter_size"]
        if "scatter_alpha" in kwargs:
            scatter_kwargs["alpha"] = kwargs["scatter_alpha"]

        contour = ax.contour(self.xx, self.yy, self.Z, **contour_kwargs)

        ax.scatter(data[consts.X_COL_NAME], data[consts.Y_COL_NAME], **scatter_kwargs)

        # Store colorbar info for post-processing
        artists = {
            "colorbar": {
                "plot_object": contour,
                "ax": ax,
                "fig": ax.get_figure(),
            }
        }
        self.style_applicator.apply_post_processing(self.plotter_name, artists)

        # Apply base post-processing for title, xlabel, ylabel, grid
        self._apply_styling(ax)

    def _style_colorbar(
        self, colorbar_info: Dict[str, Any], styles: Dict[str, Any]
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
                    self.style_applicator.get_style_with_fallback("label_fontsize"),
                ),
                color=styles.get("color", self.theme.get("label_color")),
            )
