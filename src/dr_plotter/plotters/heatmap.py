from typing import Any, Dict, List, Set

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
        },
    }

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

        # Use axes_grid1 for precise colorbar layout control
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)

        fig = ax.get_figure()
        cbar = fig.colorbar(im, cax=cax)
        # Use custom colorbar label if provided, otherwise default to values column name
        colorbar_label = self.kwargs.get("colorbar_label", self.values)
        cbar.set_label(colorbar_label)

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
