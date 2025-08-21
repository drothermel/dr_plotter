"""
Atomic plotter for bar plots with optional grouping support.
"""

import numpy as np

from dr_plotter.theme import BAR_THEME

from .base import BasePlotter
from .plot_data import BarPlotData


class BarPlotter(BasePlotter):
    """
    An atomic plotter for creating bar plots with optional grouping support using declarative configuration.
    """

    # Declarative configuration
    plotter_name = "bar"
    plotter_params = {"x", "y", "hue"}
    param_mapping = {"x": "x", "y": "y"}
    enabled_channels = {"hue": True}  # Bars support hue grouping
    default_theme = BAR_THEME
    data_validator = BarPlotData

    def _draw_simple(self, ax, data, legend, **kwargs):
        """
        Draw a simple (ungrouped) bar plot.
        
        Args:
            ax: Matplotlib axes
            data: DataFrame with the data to plot
            legend: Legend builder object (unused for bar plots as they create their own legend entries)
            **kwargs: Plot-specific kwargs including color, alpha, label
        """
        ax.bar(data[self.x], data[self.y], **kwargs)
        self._style_zero_line(ax)
    
    def _draw_grouped(self, ax, data, group_position, legend, **kwargs):
        """
        Draw bars for a single group with proper positioning.
        
        Args:
            ax: Matplotlib axes
            data: DataFrame with the data to plot (specific to one group)
            group_position: Dict with positioning info (index, total, width, offset, x_categories)
            legend: Legend builder object (unused for bar plots as they create their own legend entries)
            **kwargs: Plot-specific kwargs including color, alpha, label
        """
        
        # Use shared x_categories from all groups if available
        x_categories = group_position.get('x_categories')
        if x_categories is None:
            x_categories = data[self.x].unique()
        
        # Map data to positions based on shared categories
        x_positions = []
        y_values = []
        for i, cat in enumerate(x_categories):
            cat_data = data[data[self.x] == cat]
            if not cat_data.empty:
                x_positions.append(i + group_position['offset'])
                y_values.append(cat_data[self.y].values[0])
        
        # Draw bars at offset positions
        if x_positions:
            ax.bar(x_positions, y_values, 
                   width=group_position['width'], **kwargs)
        
        # Set x-axis labels (only on first group to avoid duplication)
        if group_position['index'] == 0:
            ax.set_xticks(np.arange(len(x_categories)))
            ax.set_xticklabels(x_categories)
            
        # Style zero line (only once, when last group is drawn)
        if group_position['index'] == group_position['total'] - 1:
            self._style_zero_line(ax)
    
    def _style_zero_line(self, ax):
        """Add a thick, dark horizontal line at y=0 behind the bars."""
        ax.axhline(y=0, linewidth=2.0, color='#333333', zorder=0.5)
