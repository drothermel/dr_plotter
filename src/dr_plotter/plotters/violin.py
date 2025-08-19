"""
Atomic plotter for violin plots.
"""

import numpy as np
from .base import BasePlotter
from dr_plotter.theme import VIOLIN_THEME
from dr_plotter.plotters.style_engine import StyleEngine
from .plot_data import ViolinPlotData


class ViolinPlotter(BasePlotter):
    """
    An atomic plotter for creating violin plots, with support for grouping via `hue`.
    """

    def __init__(self, data, x=None, y=None, hue=None, **kwargs):
        super().__init__(data, **kwargs)
        self.x = x
        self.y_param = y  # Store original y parameter
        self.hue = hue
        self.theme = VIOLIN_THEME
        
        # Create style engine with only hue channel enabled (violins only use color)
        self.style_engine = StyleEngine(self.theme, enabled_channels={'hue': True})

    def prepare_data(self):
        """
        Prepare and validate data for violin plotting.
        """
        # Gets multi-metric support for free
        self.plot_data, self.y, self.metric_column = self._prepare_multi_metric_data(
            self.y_param, self.x, 
            auto_hue_groupings={'hue': self.hue}
        )
        
        # Update hue if auto-set to METRICS
        if self.metric_column and self.hue is None:
            self.hue = self.metric_column
        
        # Create validated plot data for single metrics
        if self.metric_column is None:
            validated_data = ViolinPlotData(
                data=self.plot_data,
                x=self.x,
                y=self.y
            )
            self.plot_data = validated_data.data
        
        # Process grouping parameters
        self.hue = self._process_grouping_params(self.hue)
        
        # Validate hue column if provided
        if self.hue is not None:
            from .plot_data.base_validation import validate_columns_exist, validate_categorical_columns
            validate_columns_exist(self.plot_data, [self.hue])
            validate_categorical_columns(self.plot_data, [self.hue])
        
        return self.plot_data

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
        """Render grouped violins using unified style system."""
        x_categories = self.plot_data[self.x].unique()
        x_positions = np.arange(len(x_categories))
        
        # Generate styles using unified engine (same pattern as Line/Scatter!)
        group_styles = self.style_engine.generate_styles(
            self.plot_data, hue=self.hue
        )
        
        # Get grouping columns (will be [self.hue])
        group_cols = self.style_engine.get_grouping_columns(hue=self.hue)
        
        # Use standard groupby pattern (same as Line/Scatter!)
        if group_cols:
            grouped = self.plot_data.groupby(group_cols)
            n_groups = len(list(grouped))
            width = 0.8
            violin_width = width / n_groups if n_groups > 0 else width
            
            # Create mapping from hue values to styles
            hue_to_style = {}
            for name, group_data in grouped:
                group_key = tuple([(group_cols[0], name)])
                styles = group_styles.get(group_key, {})
                hue_to_style[name] = styles.get('color', 'blue')
        
        # Plot violins with proper positioning
        for i, x_cat in enumerate(x_categories):
            if group_cols:
                for j, (hue_val, color) in enumerate(hue_to_style.items()):
                    position = x_positions[i] - width / 2 + (j + 0.5) * violin_width
                    dataset = self.plot_data[
                        (self.plot_data[self.x] == x_cat) & (self.plot_data[self.hue] == hue_val)
                    ][self.y].dropna()

                    if not dataset.empty:
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
