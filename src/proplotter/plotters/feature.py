import pandas as pd
import numpy as np
from .base import BasePlotter


class FeaturePlotter(BasePlotter):
    """Plotter for feature engineering visualization."""

    def __init__(self, data: pd.DataFrame):
        """
        Initialize with a pandas DataFrame.

        Args:
            data: A pandas DataFrame.
        """
        super().__init__(data)

    def plot_slope_calculation_overlay(
        self, x_col: str, y_col: str, window_start: float, window_end: float, **kwargs
    ):
        """Show training curve with slope calculation overlay for specified window."""
        fig, ax = self._setup_figure()

        # Plot full curve
        ax.plot(
            self.data[x_col],
            self.data[y_col],
            color=self.style.COLORS["accent_1"],
            linewidth=self.style.LINE_WEIGHTS["main"],
            alpha=self.style.ALPHA["lines"],
            label="Curve",
            **kwargs,
        )

        # Highlight window region
        ax.axvspan(
            window_start,
            window_end,
            alpha=self.style.ALPHA["regions"],
            color=self.style.COLORS["primary_4"],
            label="Window",
        )

        # Calculate and plot slope line
        window_data = self.data[
            (self.data[x_col] >= window_start) & (self.data[x_col] <= window_end)
        ]
        if len(window_data) >= 2:
            first_point = window_data.iloc[0]
            last_point = window_data.iloc[-1]

            first_x = first_point[x_col]
            last_x = last_point[x_col]
            first_y = first_point[y_col]
            last_y = last_point[y_col]

            # Plot slope line
            ax.plot(
                [first_x, last_x],
                [first_y, last_y],
                color=self.style.COLORS["accent_2"],
                linewidth=self.style.LINE_WEIGHTS["reference"],
                linestyle="-",
                alpha=1.0,
                label="Slope Calculation Line",
            )

        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"Slope Calculation Overlay")
        ax.legend(fontsize=self.style.FONT_SIZES["legend"])
        return fig, ax

    def plot_window_boundaries_demo(self, x_col: str, y_col: str, windows: list, **kwargs):
        """Demonstrate how window boundaries are defined on the curve."""
        fig, ax = self._setup_figure()

        # Plot full curve
        ax.plot(
            self.data[x_col],
            self.data[y_col],
            color=self.style.COLORS["accent_1"],
            linewidth=self.style.LINE_WEIGHTS["main"],
            alpha=self.style.ALPHA["lines"],
            label="Curve",
            **kwargs,
        )

        # Highlight each window with different colors
        colors = self.style.get_category_colors(len(windows))

        for i, window in enumerate(windows):
            window_start, window_end = window
            ax.axvspan(
                window_start,
                window_end,
                alpha=self.style.ALPHA["regions"],
                color=colors[i],
                label=f"Window {i+1}",
            )

        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"Window Boundaries Demo")
        ax.legend(fontsize=self.style.FONT_SIZES["legend"], bbox_to_anchor=(1.05, 1))
        return fig, ax
