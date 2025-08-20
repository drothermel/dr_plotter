"""
Example 19: Custom Plotter - Creating new plotters using the registry.
Demonstrates how to create and register a custom plotter class.
"""

import pandas as pd
from dr_plotter.plotters.base import BasePlotter
from dr_plotter.plotters.plot_data import PlotData
from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from plot_data import ExampleData


class CustomErrorBarPlotData(PlotData):
    """Validation for error bar plot data."""

    def __init__(self, data: pd.DataFrame, x: str, y: str, error: str = None):
        super().__init__(data)
        self.x = x
        self.y = y
        self.error = error

        # Validate required columns
        assert x in data.columns, f"Column '{x}' not found in data"
        assert y in data.columns, f"Column '{y}' not found in data"
        if error:
            assert error in data.columns, f"Column '{error}' not found in data"


class ErrorBarPlotter(BasePlotter):
    """
    Custom plotter for error bar plots.
    Automatically registers as 'errorbar' in the registry.
    """

    def __init__(self, data, x, y, error=None, **kwargs):
        super().__init__(data, **kwargs)
        self.x = x
        self.y = y
        self.error = error

    def prepare_data(self):
        """Prepare and validate data for error bar plotting."""
        self.plot_data = CustomErrorBarPlotData(
            self.raw_data, self.x, self.y, self.error
        ).data
        return self.plot_data

    def render(self, ax):
        """Render the error bar plot."""
        self.prepare_data()

        # Get error values
        if self.error:
            yerr = self.plot_data[self.error]
        else:
            # Default: use 10% of absolute y values as error
            yerr = abs(self.plot_data[self.y]) * 0.1 + 0.1  # Add small constant

        # Create error bar plot
        plot_kwargs = {
            "capsize": self._get_style("capsize", 5),
            "capthick": self._get_style("capthick", 2),
            "elinewidth": self._get_style("elinewidth", 1.5),
            "alpha": self._get_style("alpha", 0.8),
            "color": self._get_style("color", "blue"),
        }

        # Add any additional matplotlib kwargs
        plot_kwargs.update(self._filter_plot_kwargs())

        ax.errorbar(
            self.plot_data[self.x],
            self.plot_data[self.y],
            yerr=yerr,
            fmt="o",
            **plot_kwargs,
        )

        # Apply styling
        self._apply_styling(ax)


if __name__ == "__main__":
    parser = setup_arg_parser(description="Custom Plotter Example")
    args = parser.parse_args()

    # Verify our custom plotter is registered
    from dr_plotter.plotters import BasePlotter

    print("📋 Available plotters after custom registration:")
    for plotter_type in BasePlotter.list_plotters():
        print(f"   - {plotter_type}")
    print()

    # Create test data with error values
    base_data = ExampleData.categorical_data()
    error_data = (
        base_data.groupby("category").agg({"value": ["mean", "std"]}).reset_index()
    )

    # Flatten column names
    error_data.columns = ["category", "mean_value", "error"]

    with FigureManager(rows=1, cols=2, figsize=(12, 5)) as fm:
        fm.fig.suptitle("Custom Plotter: Error Bar Plots", fontsize=16)

        # Use custom plotter via registry
        fm.plot(
            "errorbar",
            0,
            0,
            error_data,
            "category",
            "mean_value",
            error="error",
            title="Custom Error Bars (with std)",
        )

        # Use custom plotter with default errors
        simple_data = ExampleData.time_series(periods=20)
        fm.plot(
            "errorbar",
            0,
            1,
            simple_data,
            "time",
            "value",
            title="Custom Error Bars (default 10%)",
        )

        show_or_save_plot(fm.fig, args, "19_custom_plotter")
