"""
Atomic plotter for violin plots.
"""

import numpy as np
from .base import BasePlotter
from dr_plotter.theme import VIOLIN_THEME
from .plot_data import ViolinPlotData


class ViolinPlotter(BasePlotter):
    """
    An atomic plotter for creating violin plots using declarative configuration.
    """

    # Declarative configuration
    default_theme = VIOLIN_THEME
    enabled_channels = {"hue": True}  # Violins support hue grouping
    data_validator = ViolinPlotData

    def __init__(self, data, x=None, y=None, hue_by=None, **kwargs):
        super().__init__(data, hue_by=hue_by, **kwargs)
        self.x = x
        self.y_param = y  # Store original y parameter

    def _draw(self, ax, data, **kwargs):
        """
        Draw the violin plot using matplotlib.

        Args:
            ax: Matplotlib axes
            data: DataFrame with the data to plot
            **kwargs: Plot-specific kwargs including color, alpha, label
        """
        # Set default showmeans if not provided
        if "showmeans" not in kwargs:
            kwargs["showmeans"] = self._get_style("showmeans")
        
        # Extract alpha and color for post-processing (violinplot doesn't accept them)
        alpha_val = kwargs.pop('alpha', 1.0)
        color_val = kwargs.pop('color', None)
        kwargs.pop('label', None)  # Remove label as well

        # For single (non-grouped) plots
        if not self._has_groups:
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
            if color_val:
                for pc in parts["bodies"]:
                    pc.set_facecolor(color_val)
                    pc.set_alpha(alpha_val)
        else:
            # For grouped plots, we need special violin positioning logic
            self._draw_grouped_violins(ax, data, **kwargs)

    def _draw_grouped_violins(self, ax, data, **kwargs):
        """Draw grouped violins with proper positioning."""
        x_categories = self.plot_data[self.x].unique()
        x_positions = np.arange(len(x_categories))
        
        # Extract styling that violinplot doesn't accept
        alpha_val = kwargs.pop('alpha', 0.8)
        color_val = kwargs.pop('color', 'blue')
        kwargs.pop('label', None)

        # Get all groups to calculate positioning
        group_cols = self.style_engine.get_grouping_columns(hue_by=self.hue_by)
        if group_cols:
            all_groups = list(self.plot_data.groupby(group_cols))
            n_groups = len(all_groups)
            width = 0.8
            violin_width = width / n_groups if n_groups > 0 else width

            # Find which group this data belongs to
            group_data_values = (
                data[group_cols].iloc[0]
                if len(group_cols) == 1
                else tuple(data[group_cols[i]].iloc[0] for i in range(len(group_cols)))
            )
            group_index = 0
            for i, (name, _) in enumerate(all_groups):
                if (
                    isinstance(name, tuple) and name == group_data_values
                ) or name == group_data_values:
                    group_index = i
                    break

            # Calculate position for this group
            for i, x_cat in enumerate(x_categories):
                position = (
                    x_positions[i] - width / 2 + (group_index + 0.5) * violin_width
                )
                dataset = data[data[self.x] == x_cat][self.y].dropna()

                if not dataset.empty:
                    parts = ax.violinplot(
                        dataset,
                        positions=[position],
                        widths=[violin_width],
                        **kwargs
                    )
                    # Apply color styling
                    for pc in parts["bodies"]:
                        pc.set_facecolor(color_val)
                        pc.set_edgecolor("black")
                        pc.set_alpha(alpha_val)
                    for part_name in ("cbars", "cmins", "cmaxes", "cmeans"):
                        if part_name in parts:
                            vp = parts[part_name]
                            vp.set_edgecolor(color_val)
                            vp.set_linewidth(1.5)

            # Set x-axis labels (only once)
            if not ax.get_xticklabels() or ax.get_xticklabels()[0].get_text() == "0":
                ax.set_xticks(x_positions)
                ax.set_xticklabels(x_categories)

    def _apply_styling(self, ax):
        """Apply styling and handle custom violin legend."""
        # For grouped violins, create legend patches
        if self._has_groups and self._get_style("legend") is not False:
            from matplotlib.patches import Patch

            group_cols = self.style_engine.get_grouping_columns(hue_by=self.hue_by)
            if group_cols:
                group_styles = self.style_engine.generate_styles(
                    self.plot_data, hue_by=self.hue_by
                )

                legend_handles = []
                for name, _ in self.plot_data.groupby(group_cols):
                    if isinstance(name, tuple):
                        group_key = tuple(zip(group_cols, name))
                        label = str(name[0]) if len(name) == 1 else str(name)
                    else:
                        group_key = tuple([(group_cols[0], name)])
                        label = str(name)

                    styles = group_styles.get(group_key, {})
                    color = styles.get("color", "blue")
                    legend_handles.append(Patch(facecolor=color, label=label))

                ax.legend(
                    handles=legend_handles, fontsize=self.theme.get("legend_fontsize")
                )

        # Call parent styling
        super()._apply_styling(ax)
