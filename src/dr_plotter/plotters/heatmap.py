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
from dr_plotter.grouping_config import GroupingConfig


class HeatmapPlotter(BasePlotter):
    plotter_name: str = "heatmap"
    plotter_params: List[str] = ["values"]
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Set[VisualChannel] = set()
    default_theme: Theme = HEATMAP_THEME

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
        self.style_applicator.register_post_processor(
            self.plotter_name, "ticks", self._style_ticks
        )

    def _plot_specific_data_prep(self) -> None:
        # Convert from tidy/long to matrix format using pivot
        plot_data = self.plot_data.pivot(
            index=consts.Y_COL_NAME,  # rows
            columns=consts.X_COL_NAME,  # columns
            values=self.values,  # cell values
        )

        # Handle any missing values by filling with 0
        self.plot_data = plot_data.fillna(0)

    def _draw(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        # Set default cmap if not provided
        if "cmap" not in kwargs:
            kwargs["cmap"] = self._get_style("cmap")

        # Filter out parameters that imshow doesn't accept
        imshow_kwargs = {
            k: v for k, v in kwargs.items() if k not in ["color", "label", "alpha"]
        }

        im = ax.imshow(data, **imshow_kwargs)

        if self._get_style("display_values", True):
            text_styles = self.style_applicator.get_single_component_styles(
                "heatmap", "text"
            )
            for i in range(len(data.index)):
                for j in range(len(data.columns)):
                    ax.text(
                        j,
                        i,
                        f"{data.iloc[i, j]:.2f}",
                        ha=text_styles.get("ha", "center"),
                        va=text_styles.get("va", "center"),
                        color=text_styles.get("color", "w"),
                        fontsize=text_styles.get("fontsize", 8),
                    )

        # Store colorbar and ticks info for post-processing
        artists = {
            "colorbar": {
                "plot_object": im,
                "ax": ax,
                "fig": ax.get_figure(),
            },
            "ticks": ax,
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

        label_text = styles.get("label", self.kwargs.get("colorbar_label", self.values))
        if label_text:
            cbar.set_label(
                label_text,
                fontsize=styles.get("fontsize", self._get_style("label_fontsize")),
                color=styles.get("color", self.theme.get("label_color")),
            )

    def _style_ticks(self, ax: Any, styles: Dict[str, Any]) -> None:
        data = self.plot_data

        ax.set_xticks(np.arange(len(data.columns)))
        ax.set_yticks(np.arange(len(data.index)))
        ax.set_xticklabels(data.columns)
        ax.set_yticklabels(data.index)

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
