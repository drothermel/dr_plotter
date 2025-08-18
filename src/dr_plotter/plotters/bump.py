"""
Compound plotter for bump plots.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from .base import BasePlotter


class BumpPlotter(BasePlotter):
    """
    A compound plotter for creating bump plots to visualize rankings over time.
    """

    def __init__(self, data, time_col, category_col, value_col, dr_plotter_kwargs, matplotlib_kwargs):
        """
        Initialize the BumpPlotter.

        Args:
            data: A pandas DataFrame.
            time_col: The column representing time.
            category_col: The column representing the categories to rank.
            value_col: The column whose values will determine the rank.
            dr_plotter_kwargs: High-level styling options for dr_plotter.
            matplotlib_kwargs: Low-level kwargs to pass to matplotlib.
        """
        super().__init__(data, dr_plotter_kwargs, matplotlib_kwargs)
        self.time_col = time_col
        self.category_col = category_col
        self.value_col = value_col
        self.x = time_col # For default labeling
        self.y = 'Rank'   # For default labeling

    def _prepare_data(self):
        """Calculate ranks for each category at each time point."""
        self.data['rank'] = self.data.groupby(self.time_col)[self.value_col].rank(method='first', ascending=False)
        return self.data

    def render(self, ax):
        """
        Render the bump plot on the given axes.

        Args:
            ax: A matplotlib Axes object.
        """
        plot_data = self._prepare_data()
        categories = plot_data[self.category_col].unique()
        
        # Get a color cycle
        colors = plt.cm.get_cmap('viridis', len(categories))

        for i, category in enumerate(categories):
            category_data = plot_data[plot_data[self.category_col] == category].sort_values(by=self.time_col)
            
            # Draw lines with markers
            ax.plot(category_data[self.time_col], category_data['rank'], 
                    color=colors(i), marker='o', **self.matplotlib_kwargs)

            # Add text labels at the end of the lines
            last_point = category_data.iloc[-1]
            text = ax.text(last_point[self.time_col], last_point['rank'], f' {category}', 
                           va='center', color=colors(i), fontweight='bold')
            # Add a white outline to the text for legibility
            text.set_path_effects([path_effects.Stroke(linewidth=2, foreground='white'),
                                   path_effects.Normal()])

        # Invert y-axis so rank 1 is at the top
        ax.invert_yaxis()

        max_rank = int(plot_data['rank'].max())
        ax.set_yticks(range(1, max_rank + 1))

        # Add some padding to the x-axis to make room for labels
        ax.margins(x=0.15)

        self.style.apply_grid(ax)
        self._apply_styling(ax)