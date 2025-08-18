"""
Defines the hierarchical theming system for dr_plotter.
"""

import itertools

DR_PLOTTER_STYLE_KEYS = [
    "title",
    "xlabel",
    "ylabel",
    "legend",
    "grid",
    "display_values",
    "xlabel_pos",
]


class Theme:
    """
    A container for styling attributes that can inherit from a parent theme.
    """

    def __init__(self, name, parent=None, **styles):
        self.name = name
        self.parent = parent
        self.styles = styles

    def get(self, key, default=None):
        """
        Gets a style attribute, falling back to the parent theme if not found.
        """
        if key in self.styles:
            return self.styles[key]
        if self.parent:
            return self.parent.get(key, default)
        return default


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
    # Cycles for multi-series plots
    color_cycle=itertools.cycle(BASE_COLORS),
    linestyle_cycle=itertools.cycle(["-", "--", ":", "-."]),
    marker_cycle=itertools.cycle(["o", "s", "^", "D", "v", "<", ">", "p"]),
    # Global defaults
    line_width=2.0,
    marker_size=50,
    alpha=1.0,
    grid_alpha=0.3,
    title_fontsize=14,
    label_fontsize=12,
    legend_fontsize=10,
    cmap="viridis",  # Default colormap for heatmaps/contours
)

# --- Plot-Specific Themes ---

LINE_THEME = Theme(
    name="line",
    parent=BASE_THEME,
    marker=None,  # Lines don't have markers by default
)

SCATTER_THEME = Theme(
    name="scatter",
    parent=BASE_THEME,
    linestyle="None",  # Scatters don't have lines by default
    alpha=0.7,
)

BAR_THEME = Theme(name="bar", parent=BASE_THEME, alpha=0.8)

HISTOGRAM_THEME = Theme(
    name="histogram",
    parent=BAR_THEME,  # Inherits from Bar theme
    edgecolor="white",
)

VIOLIN_THEME = Theme(
    name="violin",
    parent=BASE_THEME,
    showmeans=True,  # A good default for violin plots
)

HEATMAP_THEME = Theme(
    name="heatmap",
    parent=BASE_THEME,
    grid=False,  # Grids are distracting on heatmaps
    xlabel_pos="top",
)

BUMP_PLOT_THEME = Theme(
    name="bump",
    parent=LINE_THEME,  # It's a specialized line plot
    line_width=3.0,
    marker="o",  # Bumps should have markers
)

CONTOUR_THEME = Theme(
    name="contour", parent=BASE_THEME, levels=14, scatter_alpha=0.5, scatter_size=10
)

GROUPED_BAR_THEME = Theme(name="grouped_bar", parent=BAR_THEME, rotation=0)
