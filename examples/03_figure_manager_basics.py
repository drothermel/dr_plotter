"""
Example 3: FigureManager Basics - Multi-subplot layouts.
Shows how to create complex figures with multiple subplots using FigureManager.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.verification import verify_legend_visibility
from plot_data import ExampleData
import sys

if __name__ == "__main__":
    parser = setup_arg_parser(description="FigureManager Basics Example")
    args = parser.parse_args()

    # Create a 2x2 figure
    with FigureManager(rows=2, cols=2, figsize=(12, 10)) as fm:
        fm.fig.suptitle("FigureManager: Multi-Subplot Layout", fontsize=16)

        # Top left: Scatter plot
        scatter_data = ExampleData.simple_scatter()
        fm.plot("scatter", 0, 0, scatter_data, x="x", y="y", title="Scatter Plot")

        # Top right: Line plot
        line_data = ExampleData.time_series()
        fm.plot("line", 0, 1, line_data, x="time", y="value", title="Line Plot")

        # Bottom left: Bar plot
        bar_data = ExampleData.categorical_data()
        bar_summary = bar_data.groupby("category")["value"].mean().reset_index()
        fm.plot("bar", 1, 0, bar_summary, x="category", y="value", title="Bar Plot")

        # Bottom right: Histogram
        hist_data = ExampleData.distribution_data()
        fm.plot("histogram", 1, 1, hist_data, x="values", title="Histogram")

        # Always show/save the plot first for debugging purposes
        show_or_save_plot(fm.fig, args, "03_figure_manager_basics")

        # Then verify legend visibility and fail if issues are found
        print("\n" + "=" * 60)
        print("LEGEND VISIBILITY VERIFICATION")
        print("=" * 60)

        verification_result = verify_legend_visibility(
            fm.fig,
            expected_visible_count=0,  # We expect 0 legends (all basic plots with no grouping)
            fail_on_missing=False,  # Don't fail for missing legends since we expect 0
        )

        if verification_result["visible_legends"] > 0:
            print("\n💥 EXAMPLE 3 FAILED: Unexpected legends detected!")
            print(
                "   - Expected 0 legends (all basic plots with no grouping variables)"
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
            print("   Basic plots without grouping variables should not have legends.")
            print("   📊 Plot has been saved for visual debugging.")

            # Exit with error code to fail the example
            sys.exit(1)

        print(
            "\n🎉 SUCCESS: No unexpected legends found - all plots are clean as expected!"
        )
