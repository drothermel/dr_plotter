from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt

from dr_plotter.legend_manager import LegendConfig
from dr_plotter.theme import Theme

type ColName = str


@dataclass
class SubplotLayoutConfig:
    rows: int = 1
    cols: int = 1
    layout_rect: Optional[List[float]] = None
    layout_pad: float = 0.5

    def validate(self) -> None:
        assert self.rows > 0, f"Rows must be positive, got {self.rows}"
        assert self.cols > 0, f"Cols must be positive, got {self.cols}"
        assert self.layout_pad >= 0, (
            f"Layout pad must be non-negative, got {self.layout_pad}"
        )
        if self.layout_rect:
            assert len(self.layout_rect) == 4, (
                f"Layout rect must have 4 values, got {len(self.layout_rect)}"
            )
            assert all(0 <= val <= 1 for val in self.layout_rect), (
                "Layout rect values must be between 0 and 1"
            )


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
class FigureCoordinationConfig:
    theme: Optional[Theme] = None
    shared_styling: Optional[bool] = None
    external_ax: Optional[plt.Axes] = None

    fig_kwargs: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if self.external_ax is not None:
            assert hasattr(self.external_ax, "get_figure"), (
                "external_ax must be a matplotlib Axes object"
            )


def create_figure_manager(
    layout: Optional[SubplotLayoutConfig] = None,
    legend: Optional[LegendConfig] = None,
    coordination: Optional[FigureCoordinationConfig] = None,
    faceting: Optional[SubplotFacetingConfig] = None,
) -> "FigureManager":
    from dr_plotter.figure import FigureManager

    layout = layout or SubplotLayoutConfig()
    coordination = coordination or FigureCoordinationConfig()

    layout.validate()
    coordination.validate()
    if faceting:
        faceting.validate()

    return FigureManager._create_from_configs(layout, legend, coordination, faceting)
