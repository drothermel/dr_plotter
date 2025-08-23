"""
Example 17: Custom Plotters - Creating new plotters using the registry.
Demonstrates how to create and register a custom plotter class.
"""

import itertools
from dr_plotter.plotters.base import BasePlotter
from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.verification import verify_legend_visibility
from plot_data import ExampleData
import sys


class ErrorBarPlotter(BasePlotter):
    """
    Custom plotter for error bar plots.
    Demonstrates declarative pattern for custom plotters.
    """

    plotter_name = "errorbar"
    plotter_params = {"x", "y", "error"}
    param_mapping = {"x": "x", "y": "y", "error": "error"}
    enabled_channels = {}
    default_theme = {
        "capsize": 5,
        "capthick": 2,
        "elinewidth": 1.5,
        "alpha": 0.8,
        "color": "blue",
        "color_cycle": itertools.cycle(["blue", "red", "green", "orange", "purple"]),
    }

    def _draw(self, ax, data, legend, **kwargs):
        """Render the error bar plot."""
        # Get error values
        if hasattr(self, "error") and self.error and self.error in data.columns:
            yerr = data[self.error]
        else:
            # Default: use 10% of absolute y values as error
            yerr = abs(data[self.y]) * 0.1 + 0.1  # Add small constant

        # Create error bar plot with theme defaults
        plot_kwargs = {
            "capsize": kwargs.get("capsize", self.theme.get("capsize", 5)),
            "capthick": kwargs.get("capthick", self.theme.get("capthick", 2)),
            "elinewidth": kwargs.get("elinewidth", self.theme.get("elinewidth", 1.5)),
            "alpha": kwargs.get("alpha", self.theme.get("alpha", 0.8)),
            "color": kwargs.get("color", self.theme.get("color", "blue")),
        }

        ax.errorbar(
            data[self.x],
            data[self.y],
            yerr=yerr,
            fmt="o",
            **plot_kwargs,
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
