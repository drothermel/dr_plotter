from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import matplotlib.pyplot as plt


@dataclass
class FigureConfig:
    rows: int = 1
    cols: int = 1
    figsize: tuple[int, int] = (12, 8)
    tight_layout_pad: float = 0.5

    external_ax: plt.Axes | None = None
    shared_styling: bool | None = None

    figure_kwargs: dict[str, Any] = field(default_factory=dict)
    subplot_kwargs: dict[str, Any] = field(default_factory=dict)

    x_labels: list[list[str | None]] | None = None
    y_labels: list[list[str | None]] | None = None

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
