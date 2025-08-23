"""
Example 9: Scatter Plot Showcase - All scatter plot features.
Demonstrates all visual encoding options for scatter plots.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.verification import verify_legend_visibility
from plot_data import ExampleData
import sys

if __name__ == "__main__":
    parser = setup_arg_parser(description="Scatter Plot Showcase")
    args = parser.parse_args()

    with FigureManager(rows=2, cols=2, figsize=(15, 12)) as fm:
        fm.fig.suptitle(
            "Scatter Plot Showcase: All Visual Encoding Options", fontsize=16
        )

        # Basic scatter
        basic_data = ExampleData.simple_scatter()
        fm.plot("scatter", 0, 0, basic_data, x="x", y="y", title="Basic Scatter")

        # Color encoding (hue)
        grouped_data = ExampleData.time_series_grouped(periods=30)
        fm.plot(
            "scatter",
            0,
            1,
            grouped_data,
            x="time",
            y="value",
            hue_by="group",
            title="Color Encoding (hue)",
        )

        # Size encoding
        complex_data = ExampleData.complex_encoding_data()
        fm.plot(
            "scatter",
            1,
            0,
            complex_data,
            x="x",
            y="y",
            hue_by="experiment",
            size_by="performance",
            title="Color + Size Encoding",
        )

        # Marker encoding
        fm.plot(
            "scatter",
            1,
            1,
            complex_data,
            x="x",
            y="y",
            hue_by="condition",
            marker_by="algorithm",
            title="Color + Marker Encoding",
        )

        # Always show/save the plot first for debugging purposes
        show_or_save_plot(fm.fig, args, "09_scatter_showcase")

        # Then verify legend visibility and fail if issues are found
        print("\n" + "=" * 60)
        print("LEGEND VISIBILITY VERIFICATION")
        print("=" * 60)

        verification_result = verify_legend_visibility(
            fm.fig,
            expected_visible_count=3,  # We expect 3/4 subplots to have visible legends (basic scatter has no grouping)
            fail_on_missing=True,
        )

        if not verification_result["success"]:
            print("\n💥 EXAMPLE 9 FAILED: Legend visibility issues detected!")
            print("   - Expected 3 subplots to have visible legends")
            print(
                "   - Subplot 0 (basic scatter) should NOT have a legend (no grouping)"
            )
            print(
                "   - Subplots 1, 2, 3 should have legends (color/size/marker encoding)"
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
                "   The scatter showcase should show legends for all visual encoding channels."
            )
            print("   Please check the legend manager implementation.")
            print("   📊 Plot has been saved for visual debugging.")

            # Exit with error code to fail the example
            sys.exit(1)

        print("\n🎉 SUCCESS: All expected legends are visible and properly positioned!")
