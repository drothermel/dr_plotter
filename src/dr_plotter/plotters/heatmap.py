"""
Atomic plotter for heatmaps.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from .base import BasePlotter
from dr_plotter.theme import HEATMAP_THEME
from .plot_data import HeatmapData


class HeatmapPlotter(BasePlotter):
    """
    An atomic plotter for creating heatmaps using declarative configuration.
    """

    # Declarative configuration
    plotter_name = "heatmap"
    plotter_params = {"x", "y", "values"}
    param_mapping = {"x": "x", "y": "y", "values": "values"}
    enabled_channels = {}  # No grouping support for heatmaps
    default_theme = HEATMAP_THEME
    data_validator = HeatmapData

    def _prepare_specific_data(self):
        """
        Convert tidy/long format data to matrix format for heatmap visualization.
        """
        # Convert from tidy/long to matrix format using pivot
        plot_data = self.plot_data.pivot(
            index=self.y,  # rows
            columns=self.x,  # columns
            values=self.values,  # cell values
        )

        # Handle any missing values by filling with 0
        return plot_data.fillna(0)

    def _draw(self, ax, data, legend, **kwargs):
        """
        Draw the heatmap using matplotlib.

        Args:
            ax: Matplotlib axes
            data: DataFrame in matrix format (pivoted data)
            **kwargs: Plot-specific kwargs
        """
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
            for i in range(len(data.index)):
                for j in range(len(data.columns)):
                    ax.text(
                        j,
                        i,
                        f"{data.iloc[i, j]:.2f}",
                        ha="center",
                        va="center",
                        color="w",
                        fontsize=8,
                    )
