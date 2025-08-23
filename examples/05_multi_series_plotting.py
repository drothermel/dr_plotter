"""
Example 5: Multi-Series Plotting - Visual encoding channels.
Demonstrates all visual encoding options: hue, style, size, marker, alpha.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.verification import verify_legend_visibility
from plot_data import ExampleData
import sys

if __name__ == "__main__":
    parser = setup_arg_parser(description="Multi-Series Plotting Example")
    args = parser.parse_args()

    with FigureManager(rows=2, cols=2, figsize=(15, 12)) as fm:
        fm.fig.suptitle("Multi-Series: All Visual Encoding Channels", fontsize=16)

        # Complex data with multiple grouping variables
        complex_data = ExampleData.complex_encoding_data()

        # Scatter: hue + marker encoding
        fm.plot(
            "scatter",
            0,
            0,
            complex_data,
            x="x",
            y="y",
            hue_by="experiment",
            marker_by="condition",
            title="Scatter: hue + marker",
        )

        # Scatter: hue + size encoding
        fm.plot(
            "scatter",
            0,
            1,
            complex_data,
            x="x",
            y="y",
            hue_by="condition",
            size_by="performance",
            title="Scatter: hue + size",
        )

        # Line plot with grouped time series
        grouped_ts = ExampleData.time_series_grouped(periods=30, groups=4)

        # Line: hue + style encoding
        fm.plot(
            "line",
            1,
            0,
            grouped_ts,
            x="time",
            y="value",
            hue_by="group",
            style_by="group",
            title="Line: hue + style",
        )

        # Scatter: alpha encoding for emphasis
        fm.plot(
            "scatter",
            1,
            1,
            complex_data,
            x="x",
            y="y",
            hue_by="experiment",
            alpha_by="algorithm",
            title="Scatter: hue + alpha",
        )

        # Always show/save the plot first for debugging purposes
        show_or_save_plot(fm.fig, args, "05_multi_series_plotting")

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
            print("\n💥 EXAMPLE 5 FAILED: Legend visibility issues detected!")
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
                "   The multi-series plotting should show legends for all visual encodings."
            )
            print("   Please check the legend manager implementation.")
            print("   📊 Plot has been saved for visual debugging.")

            # Exit with error code to fail the example
            sys.exit(1)

        print("\n🎉 SUCCESS: All legends are visible and properly positioned!")
