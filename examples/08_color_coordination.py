"""
Example 8: Color Coordination - Cross-subplot consistency.
Demonstrates consistent colors across multiple subplots using FigureManager.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.verification import verify_legend_visibility
from plot_data import ExampleData
import sys

if __name__ == "__main__":
    parser = setup_arg_parser(description="Color Coordination Example")
    args = parser.parse_args()

    with FigureManager(rows=2, cols=2, figsize=(15, 12)) as fm:
        fm.fig.suptitle(
            "Color Coordination: Consistent Colors Across Subplots", fontsize=16
        )

        # Use the same grouped data across all plots
        grouped_data = ExampleData.time_series_grouped()

        # All plots use the same hue variable, so colors should be consistent
        fm.plot(
            "line",
            0,
            0,
            grouped_data,
            x="time",
            y="value",
            hue_by="group",
            title="Line Plot",
        )

        fm.plot(
            "scatter",
            0,
            1,
            grouped_data,
            x="time",
            y="value",
            hue_by="group",
            title="Scatter Plot",
        )

        # For bar/violin plots, we need categorical data to show proper grouping
        # Create categorical data where each group appears in multiple categories
        categorical_data = ExampleData.grouped_categories(n_groups=3)

        # IMPORTANT: Rename groups to match time series data for color coordination
        # Change "Group_1", "Group_2", "Group_3" to "Group_A", "Group_B", "Group_C"
        group_mapping = {
            "Group_1": "Group_A",
            "Group_2": "Group_B",
            "Group_3": "Group_C",
        }
        categorical_data["group"] = categorical_data["group"].map(group_mapping)

        # Grouped bar plot - shows multiple groups per category
        fm.plot(
            "bar",
            1,
            0,
            categorical_data,
            x="category",
            y="value",
            hue_by="group",
            title="Grouped Bar Plot",
        )

        # Grouped violin plot - shows multiple groups per category
        fm.plot(
            "violin",
            1,
            1,
            categorical_data,
            x="category",
            y="value",
            hue_by="group",
            title="Grouped Violin Plot",
        )

        # Always show/save the plot first for debugging purposes
        show_or_save_plot(fm.fig, args, "08_color_coordination")

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
            print("\n💥 EXAMPLE 8 FAILED: Legend visibility issues detected!")
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
                "   The color coordination should show consistent legends across all subplots."
            )
            print("   Please check the legend manager implementation.")
            print("   📊 Plot has been saved for visual debugging.")

            # Exit with error code to fail the example
            sys.exit(1)

        print("\n🎉 SUCCESS: All legends are visible and properly positioned!")
