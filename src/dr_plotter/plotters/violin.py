"""
Atomic plotter for violin plots.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from .base import BasePlotter


class ViolinPlotter(BasePlotter):
    """
    An atomic plotter for creating violin plots, with support for grouping via `hue`.
    """

    def __init__(self, data, x, y, hue, dr_plotter_kwargs, matplotlib_kwargs):
        """
        Initialize the ViolinPlotter.

        Args:
            data: A pandas DataFrame.
            x: The column for the x-axis (main categories).
            y: The column for the y-axis (values).
            hue: The column for grouping and coloring violins within each x category.
            dr_plotter_kwargs: High-level styling options for dr_plotter.
            matplotlib_kwargs: Low-level kwargs to pass to matplotlib.
        """
        super().__init__(data, dr_plotter_kwargs, matplotlib_kwargs)
        self.x = x
        self.y = y
        self.hue = hue

    def _render_simple(self, ax):
        """Render a simple or single-grouped violin plot."""
        if self.x and self.y:
            groups = self.data[self.x].unique()
            dataset = [self.data[self.data[self.x] == group][self.y].dropna() for group in groups]
            ax.violinplot(dataset, **self.matplotlib_kwargs)
            ax.set_xticks(np.arange(1, len(groups) + 1))
            ax.set_xticklabels(groups)
        elif self.y:
            ax.violinplot(self.data[self.y].dropna(), **self.matplotlib_kwargs)
        else:
            numeric_cols = self.data.select_dtypes(include='number').columns
            dataset = [self.data[col].dropna() for col in numeric_cols]
            ax.violinplot(dataset, **self.matplotlib_kwargs)
            ax.set_xticks(np.arange(1, len(numeric_cols) + 1))
            ax.set_xticklabels(numeric_cols)

    def _render_grouped(self, ax):
        """Render a grouped violin plot using the `hue` semantic."""
        x_categories = self.data[self.x].unique()
        hue_categories = self.data[self.hue].unique()
        n_hues = len(hue_categories)
        
        # Calculate positions for each violin
        width = 0.8  # Width of the group of violins
        violin_width = width / n_hues
        x_positions = np.arange(len(x_categories))

        # Get a color cycle
        colors = plt.cm.get_cmap('viridis', n_hues)

        for i, x_cat in enumerate(x_categories):
            for j, hue_cat in enumerate(hue_categories):
                # Position of the individual violin
                position = x_positions[i] - width/2 + (j + 0.5) * violin_width
                
                # Filter data for the specific group and hue
                dataset = self.data[(self.data[self.x] == x_cat) & (self.data[self.hue] == hue_cat)][self.y].dropna()
                
                if not dataset.empty:
                    parts = ax.violinplot(dataset, positions=[position], widths=[violin_width], **self.matplotlib_kwargs)
                    # Apply color to all parts of the violin
                    for pc in parts['bodies']:
                        pc.set_facecolor(colors(j))
                        pc.set_edgecolor('black')
                        pc.set_alpha(0.8)
                    for part_name in ('cbars', 'cmins', 'cmaxes', 'cmeans'):
                        if part_name in parts:
                            vp = parts[part_name]
                            vp.set_edgecolor(colors(j))
                            vp.set_linewidth(1.5)

        # Create legend handles for hues
        from matplotlib.patches import Patch
        legend_handles = [Patch(facecolor=colors(i), label=hue_cat) for i, hue_cat in enumerate(hue_categories)]
        self.dr_plotter_kwargs['_legend_handles'] = legend_handles

        # Set x-ticks and labels to the center of the groups
        ax.set_xticks(x_positions)
        ax.set_xticklabels(x_categories)

    def render(self, ax):
        """
        Render the violin plot on the given axes.

        Args:
            ax: A matplotlib Axes object.
        """
        if self.hue and self.x and self.y:
            self._render_grouped(ax)
        else:
            self._render_simple(ax)

        self.style.apply_grid(ax)
        self._apply_styling(ax)

    def _apply_styling(self, ax):
        """Override to handle custom legend for grouped plots."""
        if self.dr_plotter_kwargs.get('legend') and '_legend_handles' in self.dr_plotter_kwargs:
            ax.legend(handles=self.dr_plotter_kwargs['_legend_handles'])
            # Avoid calling the default legend
            self.dr_plotter_kwargs['legend'] = False
        super()._apply_styling(ax)
