"""
Defines the hierarchical theming system for dr_plotter.
"""

import itertools
from typing import Dict, List, Optional

DR_PLOTTER_STYLE_KEYS = [
    "title",
    "xlabel",
    "ylabel",
    "legend",
    "grid",
    "display_values",
    "xlabel_pos",
]


class Style:
    style_type = "general"

    def __init__(self, name=None, styles_to_merge: List["Style"] = [], **styles):
        self.name = name
        self.styles = {**styles}

        self.merged_names = []
        for style in styles_to_merge:
            self.merge_style(style)
            if style.name is not None:
                self.merged_names.append(style.name)

    def add(self, key, value):
        self.styles[key] = value

    def get(self, key, default=None):
        return self.styles.get(key, default)

    def merge_style(self, other: "Style"):
        self.styles.update(other.styles)


class PlotStyles(Style):
    style_type = "plot"


class AxesStyles(Style):
    style_type = "axes"


class FigureStyles(Style):
    style_type = "figure"


class Theme:
    def __init__(
        self,
        name,
        parent=None,
        plot_styles: Optional[PlotStyles | Dict] = None,
        axes_styles: Optional[AxesStyles | Dict] = None,
        figure_styles: Optional[FigureStyles | Dict] = None,
        **styles,
    ):
        self.name = name
        self.parent = parent
        self.all_styles = {}
        for cls, cls_dict in [
            (PlotStyles, plot_styles),
            (AxesStyles, axes_styles),
            (FigureStyles, figure_styles),
            (Style, styles),
        ]:
            if cls_dict is not None:
                self.all_styles[cls.style_type] = (
                    cls_dict if isinstance(cls_dict, cls) else cls(**cls_dict)
                )
            else:
                self.all_styles[cls.style_type] = cls()

    @property
    def general_styles(self):
        return self.get_all_styles(Style)

    @property
    def plot_styles(self):
        return self.get_all_styles(PlotStyles)

    @property
    def axes_styles(self):
        return self.get_all_styles(AxesStyles)

    @property
    def figure_styles(self):
        return self.get_all_styles(FigureStyles)

    def get_all_styles(self, cls):
        styles = {}
        if self.parent is not None:
            styles.update(self.parent.get_all_styles(cls))
        styles.update(self.all_styles[cls.style_type].styles)
        return styles

    def get(self, key, default=None, source=None):
        for source_type, source_styles in self.all_styles.items():
            if (source is None or source_type == source) and (
                key in source_styles.styles
            ):
                return source_styles.get(key)
        if self.parent:
            return self.parent.get(key, default=default, source=source)
        return default

    def add(self, key, value, source=None):
        source = source if source is not None else Style.style_type
        self.all_styles[source].add(key, value)


# --- Base Theme Definition ---
# Using a professional, colorblind-friendly palette inspired by seaborn's 'deep' palette.
BASE_COLORS = [
    "#4C72B0",
    "#55A868",
    "#C44E52",
    "#8172B2",
    "#CCB974",
    "#64B5CD",
    "#DA816D",
    "#8E8E8E",
]

BASE_THEME = Theme(
    name="base",
    axes_styles=AxesStyles(
        grid_alpha=0.3,
        label_fontsize=12,
        legend_fontsize=10,
        cmap="viridis",  # Default colormap for heatmaps/contours
    ),
    figure_styles=FigureStyles(
        title_fontsize=14,
    ),
    # Cycles for multi-series plots
    color_cycle=itertools.cycle(BASE_COLORS),
    linestyle_cycle=itertools.cycle(["-", "--", ":", "-."]),
    marker_cycle=itertools.cycle(["o", "s", "^", "D", "v", "<", ">", "p"]),
)

# --- Style Classes ---
DARK_X_AXIS_STYLE = AxesStyles(
    name="dark_x_axis",
    **{
        "axes.axisbelow": False,  # Put axes on top of grid
        "axes.grid": True,  # Enable grid
        "axes.grid.axis": "y",  # Only show horizontal grid lines
        "axes.spines.bottom": True,  # Ensure bottom spine is visible
    },
)
# --- Plot-Specific Themes ---

LINE_THEME = Theme(
    name="line",
    parent=BASE_THEME,
    plot_styles=PlotStyles(
        marker=None,  # Lines don't have markers by default
        linewidth=2.0,
    ),
)

SCATTER_THEME = Theme(
    name="scatter",
    parent=BASE_THEME,
    plot_styles=PlotStyles(
        alpha=0.7,
        s=500,
    ),
)

BAR_THEME = Theme(
    name="bar",
    parent=BASE_THEME,
    plot_styles=PlotStyles(
        alpha=0.8,
    ),
    axes_styles=AxesStyles(
        styles_to_merge=[DARK_X_AXIS_STYLE],
    ),
)

HISTOGRAM_THEME = Theme(
    name="histogram",
    parent=BAR_THEME,  # Inherits from Bar theme
    plot_styles=PlotStyles(
        edgecolor="white",
    ),
    axes_styles=AxesStyles(
        ylabel="Count",
    ),
)

VIOLIN_THEME = Theme(
    name="violin",
    parent=BASE_THEME,
    plot_styles=PlotStyles(
        showmeans=True,  # A good default for violin plots
    ),
    axes_styles=AxesStyles(
        styles_to_merge=[DARK_X_AXIS_STYLE],
    ),
    general_styles=Style(
        alpha=0.7,  # Semi-transparent for visibility of interior bars
        linewidth=1.5,
        edgecolor="black",
    ),
)

HEATMAP_THEME = Theme(
    name="heatmap",
    parent=BASE_THEME,
    axes_styles=AxesStyles(
        grid=False,  # Grids are distracting on heatmaps
        xlabel_pos="top",
    ),
)

BUMP_PLOT_THEME = Theme(
    name="bump",
    parent=LINE_THEME,  # It's a specialized line plot
    plot_styles=PlotStyles(
        linewidth=3.0,
        marker="o",  # Bumps should have markers
    ),
    axes_styles=AxesStyles(
        legend=False,  # Bump plots have direct labels, no legend needed
        ylabel="Rank",
    ),
)

CONTOUR_THEME = Theme(
    name="contour",
    parent=BASE_THEME,
    general_styles=Style(
        levels=14,
        scatter_alpha=0.5,
        scatter_size=10,
    ),
)

GROUPED_BAR_THEME = Theme(
    name="grouped_bar",
    parent=BAR_THEME,
    plot_styles=PlotStyles(
        rotation=0,
    ),
)
