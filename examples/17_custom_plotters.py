"""
Example 17: Custom Plotters - Creating new plotters using the registry.
Demonstrates how to create and register a custom plotter class.
"""

from typing import Any, Dict, List, Set
import pandas as pd
from dr_plotter.plotters.base import BasePlotter
from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.verification import verify_legend_visibility
from dr_plotter.theme import BASE_THEME, Theme, PlotStyles
from dr_plotter.types import VisualChannel
from dr_plotter import consts
from dr_plotter.legend import Legend
from plot_data import ExampleData
import sys


# Create a custom theme following the expected pattern
ERRORBAR_THEME = Theme(
    name="errorbar",
    parent=BASE_THEME,
    plot_styles=PlotStyles(
        capsize=5,
        capthick=2,
        elinewidth=1.5,
        alpha=0.8,
        fmt="o",
    ),
)


class ErrorBarPlotter(BasePlotter):
    """
    Custom plotter for error bar plots.
    Demonstrates declarative pattern for custom plotters following dr_plotter architecture.
    """

    plotter_name: str = "errorbar"
    plotter_params: List[str] = ["error"]  # Only custom params, x/y are handled by base
    param_mapping: Dict[str, str] = {"error": "error"}
    enabled_channels: Set[VisualChannel] = set()  # No visual channels for simplicity
    default_theme: Theme = ERRORBAR_THEME
    use_style_applicator: bool = True
    use_legend_manager: bool = True

    # Define what styling attributes are available
    component_schema: Dict[str, Dict[str, Set[str]]] = {
        "plot": {
            "main": {
                "capsize",
                "capthick",
                "elinewidth",
                "alpha",
                "color",
                "fmt",
            }
        },
    }

    def _draw(self, ax: Any, data: pd.DataFrame, legend: Legend, **kwargs: Any) -> None:
        """Render the error bar plot using standardized column names."""
        # Get error values - check if custom error column is provided
        error_col = self.kwargs.get("error")
        if error_col and error_col in data.columns:
            yerr = data[error_col]
        else:
            # Default: use 10% of absolute y values as error
            yerr = abs(data[consts.Y_COL_NAME]) * 0.1 + 0.1

        # Remove custom parameters that matplotlib doesn't understand
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != "error"}

        # Use standardized column names from consts
        ax.errorbar(
            data[consts.X_COL_NAME],
            data[consts.Y_COL_NAME],
            yerr=yerr,
            **filtered_kwargs,
        )


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
            x="category",
            y="mean_value",
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
            x="time",
            y="value",
            title="Custom Error Bars (default 10%)",
        )

        # Always show/save the plot first for debugging purposes
        show_or_save_plot(fm.fig, args, "17_custom_plotters")

        # Then verify legend visibility and fail if issues are found
        print("\n" + "=" * 60)
        print("LEGEND VISIBILITY VERIFICATION")
        print("=" * 60)

        verification_result = verify_legend_visibility(
            fm.fig,
            expected_visible_count=0,  # We expect 0 legends (custom plotter demo with no grouping)
            fail_on_missing=False,  # Don't fail for missing legends since we expect 0
        )

        if verification_result["visible_legends"] > 0:
            print("\n💥 EXAMPLE 17 FAILED: Unexpected legends detected!")
            print(
                "   - Expected 0 legends (custom plotter demo with no grouping variables)"
            )
            print(
                f"   - Found {verification_result['visible_legends']} unexpected legends"
            )

            print("\n📋 Detailed Issues:")
            for i, result in verification_result["details"].items():
                if result["visible"]:
                    print(f"   • Subplot {i}: Unexpected legend detected")

            print(
                "\n🔧 This indicates the legend management system is creating legends when it shouldn't."
            )
            print("   Custom plotter demos without grouping should not have legends.")
            print("   📊 Plot has been saved for visual debugging.")

            # Exit with error code to fail the example
            sys.exit(1)

        print(
            "\n🎉 SUCCESS: No unexpected legends found - custom plotter demo is clean as expected!"
        )
