"""
Atomic plotter for violin plots.
"""

import numpy as np

from dr_plotter.theme import VIOLIN_THEME

from .base import BasePlotter
from .plot_data import ViolinPlotData


class ViolinPlotter(BasePlotter):
    """
    An atomic plotter for creating violin plots using declarative configuration.
    """

    # Declarative configuration
    plotter_name = "violin"
    plotter_params = {"x", "y", "hue"}
    param_mapping = {"x": "x", "y": "y"}
    enabled_channels = {"hue": True}  # Violins support hue grouping
    default_theme = VIOLIN_THEME
    data_validator = ViolinPlotData
    
    def _draw_simple(self, ax, data, legend, **kwargs):
        """
        Draw a simple (ungrouped) violin plot.

        Args:
            ax: Matplotlib axes
            data: DataFrame with the data to plot
            legend: Legend builder object for adding custom legend entries
            **kwargs: Plot-specific kwargs including color, alpha, label
        """
        # Set default showmeans if not provided
        if "showmeans" not in kwargs:
            kwargs["showmeans"] = self._get_style("showmeans")
        
        # Extract alpha and color for post-processing (violinplot doesn't accept them)
        alpha_val = kwargs.pop('alpha', 0.7)  # Default to 0.7 for visibility of interior bars
        color_val = kwargs.pop('color', None)
        label_val = kwargs.pop('label', None)  # Remove label but save for legend

        # Simple violin plot for the provided data group
        if self.x and self.y:
            groups = data[self.x].unique()
            dataset = [
                data[data[self.x] == group][self.y].dropna() for group in groups
            ]
            parts = ax.violinplot(dataset, **kwargs)
            ax.set_xticks(np.arange(1, len(groups) + 1))
            ax.set_xticklabels(groups)
        elif self.y:
            parts = ax.violinplot(data[self.y].dropna(), **kwargs)
        else:
            numeric_cols = data.select_dtypes(include="number").columns
            dataset = [data[col].dropna() for col in numeric_cols]
            parts = ax.violinplot(dataset, **kwargs)
            ax.set_xticks(np.arange(1, len(numeric_cols) + 1))
            ax.set_xticklabels(numeric_cols)
        
        # Apply color and alpha to violin parts
        if color_val and 'bodies' in parts:
            for pc in parts["bodies"]:
                pc.set_facecolor(color_val)
                pc.set_edgecolor("black")  # Black edge for better definition
                pc.set_alpha(alpha_val)
            
            # Also color the interior bars to match the violin body
            for part_name in ("cbars", "cmins", "cmaxes", "cmeans"):
                if part_name in parts:
                    vp = parts[part_name]
                    vp.set_edgecolor(color_val)
                    vp.set_linewidth(1.5)
            
            # Create a proxy artist for the legend if label is provided
            if label_val:
                legend.add_patch(label=label_val, facecolor=color_val, 
                               edgecolor='black', alpha=alpha_val)
        
        # Style zero line after drawing
        self._style_zero_line(ax)
    
    def _draw_grouped(self, ax, data, group_position, legend, **kwargs):
        """
        Draw violins for a single group with proper positioning.
        
        Args:
            ax: Matplotlib axes
            data: DataFrame with the data to plot (specific to one group)
            group_position: Dict with positioning info (index, total, width, offset)
            legend: Legend builder object for adding custom legend entries
            **kwargs: Plot-specific kwargs including color, alpha, label
        """
        # Set default showmeans if not provided
        if "showmeans" not in kwargs:
            kwargs["showmeans"] = self._get_style("showmeans")
        
        # Extract alpha and color for post-processing (violinplot doesn't accept them)
        alpha_val = kwargs.pop('alpha', 0.7)  # Default to 0.7 for visibility of interior bars
        color_val = kwargs.pop('color', None)
        label_val = kwargs.pop('label', None)  # Remove label but save for legend
        
        # Get x categories from the data
        if self.x and self.y:
            # Use shared x_categories from all groups if available
            x_categories = group_position.get('x_categories')
            if x_categories is None:
                x_categories = data[self.x].unique()
            
            # Build dataset only for categories present in this group
            dataset = []
            positions = []
            for i, cat in enumerate(x_categories):
                cat_data = data[data[self.x] == cat][self.y].dropna()
                if not cat_data.empty:
                    dataset.append(cat_data)
                    positions.append(i + group_position['offset'])
            
            # Draw violins at offset positions with adjusted width
            if dataset:
                parts = ax.violinplot(dataset, positions=positions, 
                                    widths=group_position['width'], **kwargs)
            else:
                parts = {}
            
            # Set x-axis labels (only on first group to avoid duplication)
            if group_position['index'] == 0:
                ax.set_xticks(np.arange(len(x_categories)))
                ax.set_xticklabels(x_categories)
        elif self.y:
            # Single violin for all y data
            parts = ax.violinplot([data[self.y].dropna()], 
                                positions=[group_position['offset']], 
                                widths=group_position['width'], **kwargs)
        else:
            # Handle case with no explicit x/y
            numeric_cols = data.select_dtypes(include="number").columns
            dataset = [data[col].dropna() for col in numeric_cols]
            positions = np.arange(len(numeric_cols)) + group_position['offset']
            parts = ax.violinplot(dataset, positions=positions,
                                widths=group_position['width'], **kwargs)
            if group_position['index'] == 0:
                ax.set_xticks(np.arange(len(numeric_cols)))
                ax.set_xticklabels(numeric_cols)
        
        # Apply color and alpha to violin parts
        if color_val and 'bodies' in parts:
            for pc in parts["bodies"]:
                pc.set_facecolor(color_val)
                pc.set_edgecolor("black")  # Black edge for better definition
                pc.set_alpha(alpha_val)
            
            # Also color the interior bars to match the violin body
            for part_name in ("cbars", "cmins", "cmaxes", "cmeans"):
                if part_name in parts:
                    vp = parts[part_name]
                    vp.set_edgecolor(color_val)
                    vp.set_linewidth(1.5)
            
            # Create a proxy artist for the legend if label is provided
            if label_val:
                legend.add_patch(label=label_val, facecolor=color_val, 
                               edgecolor='black', alpha=alpha_val)
        
        # Style zero line (only once, when last group is drawn)
        if group_position['index'] == group_position['total'] - 1:
            self._style_zero_line(ax)
    
    def _style_zero_line(self, ax):
        """Add a thick, dark horizontal line at y=0 behind the violins."""
        ax.axhline(y=0, linewidth=2.0, color='#333333', zorder=0.5)