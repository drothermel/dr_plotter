"""
Atomic plotter for violin plots.
"""

from typing import Dict, List

import numpy as np

from dr_plotter import consts
from dr_plotter.theme import VIOLIN_THEME, Theme
from dr_plotter.types import BasePlotterParamName, SubPlotterParamName, VisualChannel

from .base import BasePlotter


class ViolinPlotter(BasePlotter):
    """
    An atomic plotter for creating violin plots using declarative configuration.
    """

    # Required Configuration
    plotter_name: str = "violin"
    plotter_params: List[str] = []
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Dict[VisualChannel, bool] = {"hue": True}
    default_theme: Theme = VIOLIN_THEME

    def _draw(self, ax, data, legend, **kwargs):
        kwargs["showmeans"] = kwargs.get("showmeans", self._get_style("showmeans"))
        self.theme.add("color", kwargs.pop("color", None), source="general")
        self.theme.add("label", kwargs.pop("label", None), source="general")

        if self._has_groups:
            self._render_with_grouped_method(ax, legend)
        else:
            self._draw_simple(ax, data, legend, **kwargs)
        self._style_zero_line(ax)

    def style_parts(self, parts, legend):
        # Apply color and alpha to violin parts
        color_val = self.theme.get("color")
        alpha_val = self.theme.get("alpha")
        label_val = self.theme.get("label")
        edgecolor_val = self.theme.get("edgecolor")

        if color_val and "bodies" in parts:
            for pc in parts["bodies"]:
                pc.set_facecolor(color_val)
                pc.set_edgecolor(edgecolor_val)  # Black edge for better definition
                pc.set_alpha(alpha_val)

            # Also color the interior bars to match the violin body
            for part_name in ("cbars", "cmins", "cmaxes", "cmeans"):
                if part_name in parts:
                    vp = parts[part_name]
                    vp.set_edgecolor(color_val)
                    vp.set_linewidth(self.theme.general_styles.get("linewidth"))

            # Create a proxy artist for the legend if label is provided
            if label_val:
                legend.add_patch(
                    label=label_val,
                    facecolor=color_val,
                    edgecolor=edgecolor_val,
                    alpha=alpha_val,
                )

    def _draw_simple(self, ax, data, legend, **kwargs):
        groups = []
        group_data = [data]
        if consts.X_COL_NAME in data.columns:  # multiple violins
            groups = data[consts.X_COL_NAME].unique()
            group_data = [data[data[consts.X_COL_NAME] == group] for group in groups]
        datasets = [gd[consts.Y_COL_NAME].dropna() for gd in group_data]
        parts = ax.violinplot(datasets, **kwargs)
        # If multipe, plot the xtick labels
        if len(groups) > 0:
            ax.set_xticks(np.arange(1, len(groups) + 1))
            ax.set_xticklabels(groups)
        self.style_parts(parts, legend)

    def _draw_grouped(self, ax, data, group_position, legend, **kwargs):
        if consts.X_COL_NAME in data.columns:
            # Get x categories from the data
            # Use shared x_categories from all groups if available
            x_categories = group_position.get("x_categories")
            if x_categories is None:
                x_categories = data[consts.X_COL_NAME].unique()

            # Build dataset only for categories present in this group
            dataset = []
            positions = []
            for i, cat in enumerate(x_categories):
                cat_data = data[data[consts.X_COL_NAME] == cat][
                    consts.Y_COL_NAME
                ].dropna()
                if not cat_data.empty:
                    dataset.append(cat_data)
                    positions.append(i + group_position["offset"])

            # Draw violins at offset positions with adjusted width
            if dataset:
                parts = ax.violinplot(
                    dataset,
                    positions=positions,
                    widths=group_position["width"],
                    **kwargs,
                )
            else:
                parts = {}

            # Set x-axis labels (only on first group to avoid duplication)
            if group_position["index"] == 0:
                ax.set_xticks(np.arange(len(x_categories)))
                ax.set_xticklabels(x_categories)
        else:
            # Single violin for all y data
            parts = ax.violinplot(
                [data[consts.Y_COL_NAME].dropna()],
                positions=[group_position["offset"]],
                widths=group_position["width"],
                **kwargs,
            )
        self.style_parts(parts, legend)
