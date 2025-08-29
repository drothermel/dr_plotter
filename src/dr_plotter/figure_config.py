from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from dr_plotter.figure import FigureManager

type ColName = str


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

    x_labels: Optional[List[List[Optional[str]]]] = None
    y_labels: Optional[List[List[Optional[str]]]] = None

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

        if self.x_labels is not None:
            assert len(self.x_labels) == self.rows, (
                f"x_labels must have {self.rows} rows, got {len(self.x_labels)}"
            )
            for row_idx, row in enumerate(self.x_labels):
                assert len(row) == self.cols, (
                    f"x_labels row {row_idx} must have {self.cols} columns, got {len(row)}"
                )

        if self.y_labels is not None:
            assert len(self.y_labels) == self.rows, (
                f"y_labels must have {self.rows} rows, got {len(self.y_labels)}"
            )
            for row_idx, row in enumerate(self.y_labels):
                assert len(row) == self.cols, (
                    f"y_labels row {row_idx} must have {self.cols} columns, got {len(row)}"
                )


def create_figure_manager(
    figure: Optional[FigureConfig] = None,
    legend: Optional["LegendConfig"] = None,
    theme: Optional[Any] = None,
) -> "FigureManager":
    from dr_plotter.figure import FigureManager

    figure = figure or FigureConfig()

    figure.validate()

    return FigureManager._create_from_configs(figure, legend, theme)
