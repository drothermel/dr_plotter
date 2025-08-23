"""
Example 11: Bar Plot Showcase - All bar plot features.
Demonstrates single and grouped bar plots.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.verification import verify_legend_visibility
from plot_data import ExampleData
import sys

if __name__ == "__main__":
    parser = setup_arg_parser(description="Bar Plot Showcase")
    args = parser.parse_args()

    with FigureManager(rows=1, cols=2, figsize=(15, 6)) as fm:
        fm.fig.suptitle("Bar Plot Showcase: Single and Grouped Bars", fontsize=16)

        # Simple bar chart
        simple_data = ExampleData.categorical_data()
        simple_summary = simple_data.groupby("category")["value"].mean().reset_index()
        fm.plot(
            "bar",
            0,
            0,
            simple_summary,
            x="category",
            y="value",
            title="Simple Bar Chart",
        )

        # Grouped bar chart
        grouped_data = ExampleData.grouped_categories()
        grouped_summary = (
            grouped_data.groupby(["category", "group"])["value"].mean().reset_index()
        )
        fm.plot(
            "bar",
            0,
            1,
            grouped_summary,
            x="category",
            y="value",
            hue_by="group",
            title="Grouped Bar Chart",
        )

        # Always show/save the plot first for debugging purposes
        show_or_save_plot(fm.fig, args, "11_bar_showcase")

        # Then verify legend visibility and fail if issues are found
        print("\n" + "=" * 60)
        print("LEGEND VISIBILITY VERIFICATION")
        print("=" * 60)

        verification_result = verify_legend_visibility(
            fm.fig,
            expected_visible_count=1,  # We expect 1/2 subplots to have visible legends (grouped bar only)
            fail_on_missing=True,
        )

        if not verification_result["success"]:
            print("\n💥 EXAMPLE 11 FAILED: Legend visibility issues detected!")
            print("   - Expected 1 subplot to have visible legends")
            print("   - Subplot 0 (simple bar) should NOT have a legend (no grouping)")
            print("   - Subplot 1 (grouped bar) should have a legend (hue_by grouping)")
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
            print("   The bar showcase should show legend only for grouped bar chart.")
            print("   Please check the legend manager implementation.")
            print("   📊 Plot has been saved for visual debugging.")

            # Exit with error code to fail the example
            sys.exit(1)

        print("\n🎉 SUCCESS: All expected legends are visible and properly positioned!")
