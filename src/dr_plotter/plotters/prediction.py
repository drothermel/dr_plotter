import pandas as pd
import numpy as np
from .base import BasePlotter
from scipy import stats


class PredictionPlotter(BasePlotter):
    """Plotter for prediction quality analysis."""

    def __init__(self, data: pd.DataFrame):
        """
        Initialize with a pandas DataFrame containing predictions and actuals.

        Args:
            data: A pandas DataFrame with 'predicted' and 'actual' columns.
        """
        super().__init__(data)

    def plot_predicted_vs_actual_scatter(
        self, predicted_col: str = "predicted", actual_col: str = "actual", **kwargs
    ):
        """Create scatter plot of predictions vs actual values."""
        fig, ax = self._setup_figure()

        # Main scatter plot
        ax.scatter(
            self.data[predicted_col],
            self.data[actual_col],
            alpha=self.style.ALPHA["scatter"],
            s=self.style.SCATTER_SIZE["default"],
            **kwargs,
        )

        # Perfect prediction line (y=x)
        min_val = min(self.data[predicted_col].min(), self.data[actual_col].min())
        max_val = max(self.data[predicted_col].max(), self.data[actual_col].max())
        ax.plot(
            [min_val, max_val],
            [min_val, max_val],
            color=self.style.COLORS["accent_3"],
            linestyle="--",
            alpha=self.style.ALPHA["reference"],
            linewidth=self.style.LINE_WEIGHTS["reference"],
            label="Perfect Prediction",
        )

        ax.set_xlabel("Predicted Values")
        ax.set_ylabel("Actual Values")
        ax.set_title("Predicted vs Actual Values")
        ax.legend(fontsize=self.style.FONT_SIZES["legend"])
        return fig, ax

    def plot_error_distribution(
        self, predicted_col: str = "predicted", actual_col: str = "actual", bins: int = 30, **kwargs
    ):
        """Create histogram of prediction errors."""
        fig, ax = self._setup_figure()
        errors = self.data[predicted_col] - self.data[actual_col]

        ax.hist(errors, bins=bins, alpha=self.style.ALPHA["bars"], **kwargs)

        # Zero line
        ax.axvline(
            x=0,
            color=self.style.COLORS["accent_3"],
            linestyle="--",
            alpha=self.style.ALPHA["reference"],
            linewidth=self.style.LINE_WEIGHTS["reference"],
        )

        ax.set_xlabel("Prediction Error")
        ax.set_ylabel("Frequency")
        ax.set_title("Distribution of Prediction Errors")
        return fig, ax
