"""
Example 7: Grouped Plotting - Bar and violin plots with grouping.
Demonstrates the grouped plotting functionality for bar and violin plots.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.verification import verify_legend_visibility
from plot_data import ExampleData
import sys

if __name__ == "__main__":
    parser = setup_arg_parser(description="Grouped Plotting Example")
    args = parser.parse_args()

    with FigureManager(rows=2, cols=2, figsize=(15, 12)) as fm:
        fm.fig.suptitle("Grouped Plotting: Side-by-Side Comparisons", fontsize=16)

        # Simple grouping: 2 groups for clear comparison
        simple_grouped = ExampleData.grouped_categories(n_groups=2)

        # Simple grouped bar charts
        fm.plot(
            "bar",
            0,
            0,
            simple_grouped,
            x="category",
            y="value",
            hue_by="group",
            title="2-Group Bar Chart",
        )

        # Simple grouped violin plots
        fm.plot(
            "violin",
            0,
            1,
            simple_grouped,
            x="category",
            y="value",
            hue_by="group",
            title="2-Group Violin Plot",
        )

        # Complex grouping: 4 groups for more complex comparison
        complex_grouped = ExampleData.grouped_categories(n_groups=4)
        fm.plot(
            "bar",
            1,
            0,
            complex_grouped,
            x="category",
            y="value",
            hue_by="group",
            title="4-Group Bar Chart",
        )

        # Complex grouped violin plots
        fm.plot(
            "violin",
            1,
            1,
            complex_grouped,
            x="category",
            y="value",
            hue_by="group",
            title="4-Group Violin Plot",
        )

        # Always show/save the plot first for debugging purposes
        show_or_save_plot(fm.fig, args, "07_grouped_plotting")

        # Then verify legend visibility and fail if issues are found
        print("\n" + "=" * 60)
        print("LEGEND VISIBILITY VERIFICATION")
        print("=" * 60)

        verification_result = verify_legend_visibility(
            fm.fig,
            expected_visible_count=4,  # We expect 4 subplots to have visible legends
            fail_on_missing=True,
        )

        if not verification_result["success"]:
            print("\n💥 EXAMPLE 7 FAILED: Legend visibility issues detected!")
            print("   - Expected all 4 subplots to have visible legends")
            print(
                f"   - Only {verification_result['visible_legends']} legends are actually visible"
            )
            print(f"   - {verification_result['missing_legends']} legends are missing")

            print("\n📋 Detailed Issues:")
            for issue in verification_result["issues"]:
                print(f"   • Subplot {issue['subplot']}: {issue['reason']}")
                print(
                    f"     (exists: {issue['exists']}, marked_visible: {issue['marked_visible']}, has_content: {issue['has_content']})"
                )

            print("\n🔧 This indicates a bug in the legend management system.")
            print(
                "   The grouped plotting should show legends for all hue_by grouping variables."
            )
            print("   Please check the legend manager implementation.")
            print("   📊 Plot has been saved for visual debugging.")

            # Exit with error code to fail the example
            sys.exit(1)

        print("\n🎉 SUCCESS: All legends are visible and properly positioned!")
