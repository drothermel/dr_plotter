"""
Example 12: Violin Plot Showcase - All violin plot features.
Demonstrates single and grouped violin plots.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.verification import verify_legend_visibility
from plot_data import ExampleData
import sys

if __name__ == "__main__":
    parser = setup_arg_parser(description="Violin Plot Showcase")
    args = parser.parse_args()

    with FigureManager(rows=1, cols=2, figsize=(15, 6)) as fm:
        fm.fig.suptitle("Violin Plot Showcase: Distribution Shapes", fontsize=16)

        # Simple violin plot
        simple_data = ExampleData.categorical_data()
        fm.plot(
            "violin",
            0,
            0,
            simple_data,
            x="category",
            y="value",
            title="Simple Violin Plot",
        )

        # Grouped violin plot
        grouped_data = ExampleData.grouped_categories()
        fm.plot(
            "violin",
            0,
            1,
            grouped_data,
            x="category",
            y="value",
            hue_by="group",
            title="Grouped Violin Plot",
        )

        # Always show/save the plot first for debugging purposes
        show_or_save_plot(fm.fig, args, "12_violin_showcase")

        # Then verify legend visibility and fail if issues are found
        print("\n" + "=" * 60)
        print("LEGEND VISIBILITY VERIFICATION")
        print("=" * 60)

        verification_result = verify_legend_visibility(
            fm.fig,
            expected_visible_count=1,  # We expect 1/2 subplots to have visible legends (grouped violin only)
            fail_on_missing=True,
        )

        if not verification_result["success"]:
            print("\n💥 EXAMPLE 12 FAILED: Legend visibility issues detected!")
            print("   - Expected 1 subplot to have visible legends")
            print(
                "   - Subplot 0 (simple violin) should NOT have a legend (no grouping)"
            )
            print(
                "   - Subplot 1 (grouped violin) should have a legend (hue_by grouping)"
            )
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
                "   The violin showcase should show legend only for grouped violin plot."
            )
            print("   Please check the legend manager implementation.")
            print("   📊 Plot has been saved for visual debugging.")

            # Exit with error code to fail the example
            sys.exit(1)

        print("\n🎉 SUCCESS: All expected legends are visible and properly positioned!")
