"""
Atomic plotter for violin plots.
"""

import numpy as np
from .base import BasePlotter
from dr_plotter.theme import VIOLIN_THEME


class ViolinPlotter(BasePlotter):
    """
    An atomic plotter for creating violin plots, with support for grouping via `hue`.
    """

    def __init__(self, data, x=None, y=None, hue=None, **kwargs):
        super().__init__(data, **kwargs)
        self.x = x
        self.y = y
        self.hue = hue
        self.theme = VIOLIN_THEME

    def _get_plot_kwargs(self):
        """Prepare the kwargs for the matplotlib violinplot function."""
        plot_kwargs = {"showmeans": self.theme.get("showmeans")}
        plot_kwargs.update(self._filter_plot_kwargs())
        return plot_kwargs

    def _render_simple(self, ax):
        plot_kwargs = self._get_plot_kwargs()
        if self.x and self.y:
            groups = self.plot_data[self.x].unique()
            dataset = [
                self.plot_data[self.plot_data[self.x] == group][self.y].dropna()
                for group in groups
            ]
            ax.violinplot(dataset, **plot_kwargs)
            ax.set_xticks(np.arange(1, len(groups) + 1))
            ax.set_xticklabels(groups)
        elif self.y:
            ax.violinplot(self.plot_data[self.y].dropna(), **plot_kwargs)
        else:
            numeric_cols = self.plot_data.select_dtypes(include="number").columns
            dataset = [self.plot_data[col].dropna() for col in numeric_cols]
            ax.violinplot(dataset, **plot_kwargs)
            ax.set_xticks(np.arange(1, len(numeric_cols) + 1))
            ax.set_xticklabels(numeric_cols)

    def _render_grouped(self, ax):
        x_categories = self.plot_data[self.x].unique()
        hue_categories = self.plot_data[self.hue].unique()
        n_hues = len(hue_categories)

        width = 0.8
        violin_width = width / n_hues
        x_positions = np.arange(len(x_categories))
        hue_colors = {
            hue_cat: next(self.theme.get("color_cycle")) for hue_cat in hue_categories
        }

        for i, x_cat in enumerate(x_categories):
            for j, hue_cat in enumerate(hue_categories):
                position = x_positions[i] - width / 2 + (j + 0.5) * violin_width
                dataset = self.plot_data[
                    (self.plot_data[self.x] == x_cat) & (self.plot_data[self.hue] == hue_cat)
                ][self.y].dropna()

                if not dataset.empty:
                    color = hue_colors[hue_cat]
                    plot_kwargs = self._get_plot_kwargs()
                    parts = ax.violinplot(
                        dataset,
                        positions=[position],
                        widths=[violin_width],
                        **plot_kwargs,
                    )
                    for pc in parts["bodies"]:
                        pc.set_facecolor(color)
                        pc.set_edgecolor("black")
                        pc.set_alpha(0.8)
                    for part_name in ("cbars", "cmins", "cmaxes", "cmeans"):
                        if part_name in parts:
                            vp = parts[part_name]
                            vp.set_edgecolor(color)
                            vp.set_linewidth(1.5)

        from matplotlib.patches import Patch

        legend_handles = [
            Patch(facecolor=hue_colors[hue_cat], label=hue_cat)
            for hue_cat in hue_categories
        ]
        self.kwargs["_legend_handles"] = legend_handles

        ax.set_xticks(x_positions)
        ax.set_xticklabels(x_categories)

    def render(self, ax):
        self.prepare_data()
        
        if self.hue and self.x and self.y:
            self._render_grouped(ax)
        else:
            self._render_simple(ax)
        self._apply_styling(ax)

    def _apply_styling(self, ax):
        if self.kwargs.get("legend") and "_legend_handles" in self.kwargs:
            ax.legend(
                handles=self.kwargs["_legend_handles"],
                fontsize=self.theme.get("legend_fontsize"),
            )
            self.kwargs["legend"] = False
        super()._apply_styling(ax)
