"""
Example 10: Line Plot Showcase - All line plot features.
Demonstrates all visual encoding options for line plots including multi-series.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.verification import verify_legend_visibility
from dr_plotter import consts
from plot_data import ExampleData
import sys

if __name__ == "__main__":
    parser = setup_arg_parser(description="Line Plot Showcase")
    args = parser.parse_args()

    with FigureManager(rows=2, cols=2, figsize=(15, 12)) as fm:
        fm.fig.suptitle("Line Plot Showcase: All Visual Encoding Options", fontsize=16)

        # Basic line
        basic_data = ExampleData.time_series()
        fm.plot("line", 0, 0, basic_data, x="time", y="value", title="Basic Line Plot")

        # Multiple lines with hue
        grouped_data = ExampleData.time_series_grouped()
        fm.plot(
            "line",
            0,
            1,
            grouped_data,
            x="time",
            y="value",
            hue_by="group",
            title="Multi-Series (hue)",
        )

        # Line style encoding
        fm.plot(
            "line",
            1,
            0,
            grouped_data,
            x="time",
            y="value",
            hue_by="group",
            style_by="group",
            title="Color + Line Style",
        )

        # Multi-metrics with METRICS encoding
        ml_data = ExampleData.ml_training_curves(epochs=30)
        fm.plot(
            "line",
            1,
            1,
            ml_data,
            x="epoch",
            y=["train_loss", "val_loss"],
            hue_by=consts.METRIC_COL_NAME,
            style_by="learning_rate",
            title="Multi-Metrics (METRICS)",
        )

        # Always show/save the plot first for debugging purposes
        show_or_save_plot(fm.fig, args, "10_line_showcase")

        # Then verify legend visibility and fail if issues are found
        print("\n" + "=" * 60)
        print("LEGEND VISIBILITY VERIFICATION")
        print("=" * 60)

        verification_result = verify_legend_visibility(
            fm.fig,
            expected_visible_count=3,  # We expect 3/4 subplots to have visible legends (basic line has no grouping)
            fail_on_missing=True,
        )

        if not verification_result["success"]:
            print("\n💥 EXAMPLE 10 FAILED: Legend visibility issues detected!")
            print("   - Expected 3 subplots to have visible legends")
            print("   - Subplot 0 (basic line) should NOT have a legend (no grouping)")
            print(
                "   - Subplots 1, 2, 3 should have legends (hue/style/METRICS encoding)"
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
                "   The line showcase should show legends for all visual encoding channels."
            )
            print("   Please check the legend manager implementation.")
            print("   📊 Plot has been saved for visual debugging.")

            # Exit with error code to fail the example
            sys.exit(1)

        print("\n🎉 SUCCESS: All expected legends are visible and properly positioned!")
