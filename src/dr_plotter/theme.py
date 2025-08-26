import itertools
from typing import Any, Dict, List, Optional

from dr_plotter import consts
from dr_plotter.legend_manager import LegendConfig

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

    def __init__(
        self,
        name: Optional[str] = None,
        styles_to_merge: List["Style"] = [],
        **styles: Any,
    ) -> None:
        self.name = name
        self.styles: Dict[str, Any] = {**styles}
        self.merged_names: List[str] = []
        for style in styles_to_merge:
            self.merge_style(style)
            if style.name is not None:
                self.merged_names.append(style.name)

    def add(self, key: str, value: Any) -> None:
        self.styles[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.styles.get(key, default)

    def merge_style(self, other: "Style") -> None:
        self.styles.update(other.styles)


class PlotStyles(Style):
    style_type = "plot"


class PostStyles(Style):
    style_type = "post"


class AxesStyles(Style):
    style_type = "axes"


class FigureStyles(Style):
    style_type = "figure"


class Theme:
    def __init__(
        self,
        name: str,
        parent: Optional["Theme"] = None,
        plot_styles: Optional[PlotStyles | Dict] = None,
        post_styles: Optional[PostStyles | Dict] = None,
        axes_styles: Optional[AxesStyles | Dict] = None,
        figure_styles: Optional[FigureStyles | Dict] = None,
        legend_config: Optional[LegendConfig] = None,
        **styles: Any,
    ) -> None:
        self.name = name
        self.parent = parent
        self.legend_config = (
            legend_config
            or (parent.legend_config if parent else None)
            or LegendConfig()
        )
        self.all_styles: Dict[str, Style] = {}
        for cls, cls_dict in [
            (PlotStyles, plot_styles),
            (PostStyles, post_styles),
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
    def general_styles(self) -> Dict[str, Any]:
        return self.get_all_styles(Style)

    @property
    def plot_styles(self) -> Dict[str, Any]:
        return self.get_all_styles(PlotStyles)

    @property
    def post_styles(self) -> Dict[str, Any]:
        return self.get_all_styles(PostStyles)

    @property
    def axes_styles(self) -> Dict[str, Any]:
        return self.get_all_styles(AxesStyles)

    @property
    def figure_styles(self) -> Dict[str, Any]:
        return self.get_all_styles(FigureStyles)

    def get_all_styles(self, cls: type) -> Dict[str, Any]:
        styles: Dict[str, Any] = {}
        if self.parent is not None:
            styles.update(self.parent.get_all_styles(cls))
        styles.update(self.all_styles[cls.style_type].styles)
        return styles

    def get(self, key: str, default: Any = None, source: Optional[str] = None) -> Any:
        for source_type, source_styles in self.all_styles.items():
            if (source is None or source_type == source) and (
                key in source_styles.styles
            ):
                return source_styles.get(key)
        if self.parent:
            return self.parent.get(key, default=default, source=source)
        return default

    def add(self, key: str, value: Any, source: Optional[str] = None) -> None:
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
        cmap="viridis",
    ),
    figure_styles=FigureStyles(
        title_fontsize=14,
    ),
    **{
        consts.get_cycle_key("hue"): itertools.cycle(BASE_COLORS),
        consts.get_cycle_key("style"): itertools.cycle(["-", "--", ":", "-."]),
        consts.get_cycle_key("marker"): itertools.cycle(
            ["o", "s", "^", "D", "v", "<", ">", "p"]
        ),
        consts.get_cycle_key("size"): itertools.cycle([1.0, 1.5, 2.0, 2.5]),
        consts.get_cycle_key("alpha"): itertools.cycle([1.0, 0.7, 0.5, 0.3]),
    },
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
        marker=None,
        linewidth=2.0,
    ),
)

SCATTER_THEME = Theme(
    name="scatter",
    parent=BASE_THEME,
    plot_styles=PlotStyles(
        alpha=1.0,
        s=50,
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
    parent=BAR_THEME,
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
        showmeans=True,
    ),
    axes_styles=AxesStyles(
        styles_to_merge=[DARK_X_AXIS_STYLE],
    ),
    general_styles=Style(
        alpha=0.7,
        linewidth=1.5,
        edgecolor="black",
    ),
)

HEATMAP_THEME = Theme(
    name="heatmap",
    parent=BASE_THEME,
    axes_styles=AxesStyles(
        grid=False,
        xlabel_pos="top",
    ),
)

BUMP_PLOT_THEME = Theme(
    name="bump",
    parent=LINE_THEME,
    plot_styles=PlotStyles(
        linewidth=3.0,
        marker="o",
    ),
    axes_styles=AxesStyles(
        legend=False,
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
