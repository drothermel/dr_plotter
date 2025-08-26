from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

import matplotlib.pyplot as plt

from dr_plotter.legend_manager import LegendConfig
from dr_plotter.theme import Theme

type ColName = str


@dataclass
class SubplotFacetingConfig:
    facet_by: Optional[ColName] = None
    group_by: Optional[ColName] = None
    x_col: Optional[ColName] = None
    y_col: Optional[ColName] = None

    facet_rows: Optional[ColName] = None
    facet_cols: Optional[ColName] = None
    wrap_facets: Optional[int] = None

    def validate(self) -> None:
        if self.facet_by and self.group_by:
            assert self.facet_by != self.group_by, (
                f"Facet and group columns must be different: {self.facet_by}"
            )
        if self.wrap_facets is not None:
            assert self.wrap_facets > 0, (
                f"Wrap facets must be positive, got {self.wrap_facets}"
            )


@dataclass
class FigureConfig:
    rows: int = 1
    cols: int = 1
    figsize: Tuple[int, int] = (12, 8)
    tight_layout_pad: float = 0.5

    external_ax: Optional[plt.Axes] = None
    shared_styling: Optional[bool] = None

    figure_kwargs: Dict[str, Any] = field(default_factory=dict)
    subplot_kwargs: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        assert self.rows > 0, f"Rows must be positive, got {self.rows}"
        assert self.cols > 0, f"Cols must be positive, got {self.cols}"
        assert len(self.figsize) == 2, (
            f"Figsize must have 2 values, got {len(self.figsize)}"
        )
        assert all(val > 0 for val in self.figsize), "Figsize values must be positive"
        assert self.tight_layout_pad >= 0, (
            f"Layout pad must be non-negative, got {self.tight_layout_pad}"
        )
        if self.external_ax is not None:
            assert hasattr(self.external_ax, "get_figure"), (
                "external_ax must be a matplotlib Axes object"
            )


def create_figure_manager(
    figure: Optional[FigureConfig] = None,
    legend: Optional[LegendConfig] = None,
    theme: Optional[Theme] = None,
    faceting: Optional[SubplotFacetingConfig] = None,
) -> "FigureManager":
    from dr_plotter.figure import FigureManager

    figure = figure or FigureConfig()

    figure.validate()
    if faceting:
        faceting.validate()

    return FigureManager._create_from_configs(figure, legend, theme, faceting)
