from typing import Any, Dict, List, Set, Optional

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

from dr_plotter import consts
from dr_plotter.plotters.base import (
    BasePlotter,
    BasePlotterParamName,
    SubPlotterParamName,
)
from dr_plotter.theme import HEATMAP_THEME, Theme
from dr_plotter.types import VisualChannel, Phase, ComponentSchema
from dr_plotter.configs import GroupingConfig


class HeatmapPlotter(BasePlotter):
    plotter_name: str = "heatmap"
    plotter_params: List[str] = ["values", "annot"]
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Set[VisualChannel] = set()
    default_theme: Theme = HEATMAP_THEME
    supports_legend: bool = False
    supports_grouped: bool = False

    component_schema: Dict[Phase, ComponentSchema] = {
        "plot": {
            "main": {
                "cmap",
                "vmin",
                "vmax",
                "aspect",
                "interpolation",
                "origin",
            },
            "text": {"color", "fontsize", "ha", "va"},
        },
        "axes": {
            "title": {"text", "fontsize", "color"},
            "xlabel": {"text", "fontsize", "color"},
            "ylabel": {"text", "fontsize", "color"},
            "grid": {"visible", "alpha", "color", "linestyle"},
            "colorbar": {"label", "fontsize", "color", "size", "pad"},
            "ticks": {
                "xticks",
                "yticks",
                "xticklabels",
                "yticklabels",
                "rotation",
                "alignment",
            },
            "cell_text": {"visible", "fontsize", "color", "ha", "va", "format"},
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
        self.styler.register_post_processor(
            self.plotter_name, "colorbar", self._style_colorbar
        )
        self.styler.register_post_processor(
            self.plotter_name, "ticks", self._style_ticks
        )
        self.styler.register_post_processor(
            self.plotter_name, "cell_text", self._style_cell_text
        )

    def _plot_specific_data_prep(self) -> None:
        plot_data = self.plot_data.pivot(
            index=consts.Y_COL_NAME,
            columns=consts.X_COL_NAME,
            values=self.values,
        )

        self.plot_data = plot_data.fillna(0)

    def _draw(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        if "cmap" not in kwargs:
            kwargs["cmap"] = self.styler.get_style("cmap")

        im = ax.imshow(data, **self._filtered_plot_kwargs)

        artists = {
            "colorbar": {
                "plot_object": im,
                "ax": ax,
                "fig": ax.get_figure(),
            },
            "ticks": ax,
            "cell_text": ax,
        }
        self.styler.apply_post_processing(self.plotter_name, artists)

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

        label_text = styles.get("label", self.kwargs.get("colorbar_label", self.values))
        if label_text:
            cbar.set_label(
                label_text,
                fontsize=styles.get(
                    "fontsize",
                    self.styler.get_style("label_fontsize"),
                ),
                color=styles.get("color", self.theme.get("label_color")),
            )

    def _style_ticks(self, ax: Any, styles: Dict[str, Any]) -> None:
        data = self.plot_data

        ax.set_xticks(np.arange(len(data.columns)))
        ax.set_yticks(np.arange(len(data.index)))
        ax.set_xticklabels(data.columns)
        ax.set_yticklabels(data.index)

        xlabel_pos = self.styler.get_style("xlabel_pos")
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

    def _style_cell_text(self, ax: Any, styles: Dict[str, Any]) -> None:
        if not styles.get("visible", True):
            return

        data = self.plot_data

        fontsize = styles.get("fontsize", 8)
        color = styles.get("color", "white")
        ha = styles.get("ha", "center")
        va = styles.get("va", "center")
        format_str = styles.get("format", ".2f")

        for i in range(len(data.index)):
            for j in range(len(data.columns)):
                cell_value = data.iloc[i, j]
                try:
                    if format_str.startswith(".") and format_str.endswith("f"):
                        text = f"{cell_value:{format_str}}"
                    elif format_str == "int":
                        text = str(int(cell_value))
                    else:
                        text = str(cell_value)
                except (ValueError, TypeError):
                    text = str(cell_value)

                ax.text(
                    j,
                    i,
                    text,
                    ha=ha,
                    va=va,
                    color=color,
                    fontsize=fontsize,
                )
