import pandas as pd
import numpy as np
from .base import BasePlotter


class ComparisonPlotter(BasePlotter):
    """Plotter for comparing multiple models."""

    def __init__(self, results: dict):
        """
        Initialize with a dictionary of results.

        Args:
            results: A dictionary where keys are model names and values are
                     DataFrames with 'true' and 'predicted' columns.
        """
        self.results = results
        super().__init__(data=None)  # No single dataframe for this plotter

    def display_performance_table(self):
        """Display a table of performance metrics for each model."""
        table_data = []
        for name, df in self.results.items():
            rmse = np.sqrt(np.mean((df["predicted"] - df["true"]) ** 2))
            mae = np.mean(np.abs(df["predicted"] - df["true"]))
            r2 = np.corrcoef(df["predicted"], df["true"])[0, 1] ** 2
            table_data.append(
                {
                    "Model": name,
                    "RMSE": rmse,
                    "MAE": mae,
                    "R-squared": r2,
                }
            )
        return pd.DataFrame(table_data).set_index("Model")

    def plot_error_by_horizon(self, metric="rmse"):
        """Plot the error of each model by prediction horizon."""
        fig, ax = self._setup_figure()
        for name, df in self.results.items():
            errors = []
            horizons = sorted(df["target_percentage"].unique())
            for horizon in horizons:
                subset = df[df["target_percentage"] == horizon]
                if metric == "rmse":
                    error = np.sqrt(
                        np.mean((subset["predicted"] - subset["true"]) ** 2)
                    )
                elif metric == "mae":
                    error = np.mean(np.abs(subset["predicted"] - subset["true"]))
                else:
                    raise ValueError(f"Unknown metric: {metric}")
                errors.append(error)
            ax.plot(horizons, errors, label=name, marker="o")

        ax.set_xlabel("Prediction Horizon (%)")
        ax.set_ylabel(metric.upper())
        ax.set_title(f"{metric.upper()} by Prediction Horizon")
        ax.legend()
        return fig, ax

    def plot_error_distribution(self, target_col=None):
        """Create a violin plot of errors for each model."""
        fig, ax = self._setup_figure()
        all_errors = []
        model_names = []
        for name, df in self.results.items():
            errors = df["predicted"] - df["true"]
            all_errors.append(errors.dropna())
            model_names.append(name)

        ax.violinplot(all_errors, showmeans=True)
        ax.set_xticks(np.arange(1, len(model_names) + 1))
        ax.set_xticklabels(model_names, rotation=45, ha="right")
        ax.set_ylabel("Prediction Error (Predicted - Actual)")

        # Set title with target column if provided
        if target_col:
            target_col_display = target_col.replace("-", " ").title()
            ax.set_title(f"{target_col_display} Error Distribution by Model")
        else:
            ax.set_title("Error Distribution by Model")
        return fig, ax
